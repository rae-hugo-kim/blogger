"""chargen OpenAI 모델 체인 계약 (2026-09-21 결정).

기본 gpt-image-2.5-flare, 불만족/비응답 시 sunburst → 2 순 — 선호 순서,
prefix 중복 배제(2가 2.5를 삼키지 않음), 모델 단위 폴백을 방어한다.
"""

import importlib.util
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent

# 2026-09-21 실측 계정 모델 목록
ACCOUNT_MODELS = [
    "chatgpt-image-latest",
    "gpt-image-1",
    "gpt-image-1-mini",
    "gpt-image-1.5",
    "gpt-image-2",
    "gpt-image-2-2026-04-21",
    "gpt-image-2.5-flare",
    "gpt-image-2.5-flare-2026-09-08",
    "gpt-image-2.5-sunburst",
    "gpt-image-2.5-sunburst-2026-09-08",
]


@pytest.fixture()
def chargen():
    spec = importlib.util.spec_from_file_location(
        "chargen", PROJECT_ROOT / "scripts" / "chargen.py"
    )
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def patch_models(monkeypatch, chargen, models):
    class FakeResp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"data": [{"id": m} for m in models]}

    monkeypatch.setattr(chargen.requests, "get", lambda *a, **k: FakeResp())


def test_chain_prefers_flare_then_sunburst_then_2(chargen, monkeypatch):
    """결정된 순서 그대로 — 사전순(sunburst > flare)이 아니라 flare가 1순위."""
    patch_models(monkeypatch, chargen, ACCOUNT_MODELS)
    chain = chargen.resolve_openai_models("k", verbose=False)
    assert chain[:3] == [
        "gpt-image-2.5-flare-2026-09-08",
        "gpt-image-2.5-sunburst-2026-09-08",
        "gpt-image-2-2026-04-21",
    ]


def test_gpt2_slot_excludes_25_family(chargen, monkeypatch):
    """"gpt-image-2" prefix가 2.5 계열을 삼키면 3순위 폴백이 2.5 재시도로 무력화된다."""
    patch_models(monkeypatch, chargen, ACCOUNT_MODELS)
    chain = chargen.resolve_openai_models("k", verbose=False)
    assert not chain[2].startswith("gpt-image-2.5")


def test_pinned_model_bypasses_chain(chargen, monkeypatch):
    patch_models(monkeypatch, chargen, ACCOUNT_MODELS)
    assert chargen.resolve_openai_models("k", False, pinned="gpt-image-2") == ["gpt-image-2"]
    with pytest.raises(RuntimeError, match="계정에 없음"):
        chargen.resolve_openai_models("k", False, pinned="gpt-image-99")


def test_generate_falls_back_in_chain_order(chargen, monkeypatch):
    """1순위 비응답 → 2순위로 생성 성공, 3순위는 호출하지 않는다."""
    calls = []

    def fake_request(key, model, *a):
        calls.append(model)
        if model == "flare":
            raise RuntimeError("timeout")
        return [b"png"]

    monkeypatch.setattr(chargen, "resolve_openai_models", lambda *a, **k: ["flare", "sunburst", "g2"])
    monkeypatch.setattr(chargen, "_openai_request", fake_request)
    images = chargen.generate_openai("k", "p", [], "1024x1024", 1, False, False)
    assert images == [b"png"]
    assert calls == ["flare", "sunburst"]


def test_generate_raises_when_all_models_fail(chargen, monkeypatch):
    def fake_request(key, model, *a):
        raise RuntimeError(f"{model} down")

    monkeypatch.setattr(chargen, "resolve_openai_models", lambda *a, **k: ["flare", "g2"])
    monkeypatch.setattr(chargen, "_openai_request", fake_request)
    with pytest.raises(RuntimeError) as exc:
        chargen.generate_openai("k", "p", [], "1024x1024", 1, False, False)
    assert "flare" in str(exc.value) and "g2" in str(exc.value)


def _fake_codex_run(returncode, write_bytes):
    """codex exec 대역: -C 디렉토리에 out.png을 write_bytes로 남기고 returncode 반환."""
    from pathlib import Path
    import subprocess

    def run(cmd, **kwargs):
        td = cmd[cmd.index("-C") + 1]
        if write_bytes is not None:
            (Path(td) / "out.png").write_bytes(write_bytes)
        return subprocess.CompletedProcess(cmd, returncode, stdout="", stderr="boom")

    return run


def test_codex_rejects_nonzero_exit_even_with_file(chargen, monkeypatch):
    """리뷰 확정 medium: 파일이 있어도 비정상 종료면 성공 처리 금지."""
    monkeypatch.setattr(chargen.subprocess, "run", _fake_codex_run(1, b"png-bytes"))
    with pytest.raises(RuntimeError, match="비정상 종료"):
        chargen.generate_codex("p", [], "1024x1024", 1, False, False)


def test_codex_rejects_empty_file(chargen, monkeypatch):
    """exit 0이어도 0바이트 PNG를 게시하지 않는다."""
    monkeypatch.setattr(chargen.subprocess, "run", _fake_codex_run(0, b""))
    with pytest.raises(RuntimeError, match="파일 미생성/빈 파일"):
        chargen.generate_codex("p", [], "1024x1024", 1, False, False)


def test_codex_success_returns_blob(chargen, monkeypatch):
    monkeypatch.setattr(chargen.subprocess, "run", _fake_codex_run(0, b"png-bytes"))
    assert chargen.generate_codex("p", [], "1024x1024", 1, False, False) == [b"png-bytes"]
