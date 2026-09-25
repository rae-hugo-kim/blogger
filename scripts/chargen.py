"""Character image generator for the blog character pipeline.

기본 경로: `codex exec` + image_generation — ChatGPT 계정 인증(~/.codex/auth.json),
API 키 불요. 모델 셀렉션 불가 (2026-09-22 결정: 디테일 차이가 필요한 경우는 드묾).

모델 셀렉션이 확실히 필요할 때만 API 경로를 명시 지정한다:
  --provider openai      → gpt-image-2.5-flare 기본, 비응답 시 sunburst → 2 순 자동 폴백
  -m <model>             → 특정 모델 고정 (--provider openai 함의)
  --provider gemini      → Gemini API (Nano Banana)
경로 간 자동 폴백은 없다 — API 사용은 항상 명시적 지시.

API 키는 scripts/openv.sh(1Password) 주입 또는 저장소 루트 `.env`(gitignore됨):
  OPENAI_API_KEY=... / GEMINI_API_KEY=...

사용 예:
  python3 scripts/chargen.py "prompt text" -o references/characters/bob -N bob-v3   # auth 경로
  scripts/openv.sh python3 scripts/chargen.py -P prompt.txt -m gpt-image-2.5-sunburst \
      -r references/characters/rae/canonical-front-side.png -o /tmp/cmp -N rae-cmp  # API 비교 생성
"""

import argparse
import base64
import subprocess
import sys
import tempfile
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
SIZES = ("1024x1024", "1536x1024", "1024x1536")
SIZE_TO_RATIO = {"1024x1024": "1:1", "1536x1024": "3:2", "1024x1536": "2:3"}
OPENAI_MODEL_PREFERENCE = (
    "gpt-image-2.5-flare",
    "gpt-image-2.5-sunburst",
    "gpt-image-2",
    "gpt-image-1.5",
    "gpt-image-1",
)
GEMINI_MODEL = "gemini-3-pro-image-preview"
CODEX_TIMEOUT = 1200  # 초 — auth 경로 컷당 6~10분 실측(rules.md) + 여유


def load_env() -> dict:
    """환경변수 + .env 병합 (환경변수 우선)."""
    import os

    merged = {}
    env_file = REPO_ROOT / ".env"
    if env_file.is_file():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            merged[key.strip()] = value.strip().strip('"').strip("'")
    merged.update({k: v for k, v in os.environ.items() if k.endswith("_API_KEY")})
    return merged


def resolve_openai_models(key: str, verbose: bool, pinned: str | None = None) -> list:
    """가용 모델 목록에서 선호 순서대로 폴백 체인을 만든다 (pinned 지정 시 그것만).

    선호 항목은 prefix 매칭이라 겹친다 (예: "gpt-image-2"는 2.5 계열도 포함) —
    앞선 선호 prefix에 걸린 모델을 제외해 슬롯별로 서로 다른 세대를 뽑는다.
    """
    resp = requests.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {key}"},
        timeout=30,
    )
    resp.raise_for_status()
    available = {m["id"] for m in resp.json().get("data", [])}
    if pinned:
        if pinned not in available:
            raise RuntimeError(f"지정 모델이 계정에 없음: {pinned}")
        return [pinned]
    chain = []
    for i, preferred in enumerate(OPENAI_MODEL_PREFERENCE):
        earlier = OPENAI_MODEL_PREFERENCE[:i]
        matches = sorted(
            m for m in available
            if m.startswith(preferred) and not any(m.startswith(e) for e in earlier)
        )
        if matches:
            chain.append(matches[-1])
    if not chain:
        image_models = sorted(m for m in available if "image" in m and m.startswith("gpt"))
        chain = image_models[-1:]
    if not chain:
        raise RuntimeError("OpenAI 계정에서 gpt-image 계열 모델을 찾지 못함")
    if verbose:
        print(f"[openai] model chain: {' -> '.join(chain)}")
    return chain


def _openai_request(key, model, prompt, refs, size, n, transparent):
    headers = {"Authorization": f"Bearer {key}"}
    if refs:
        files = [("image[]", (p.name, p.read_bytes(), "image/png")) for p in refs]
        data = {"model": model, "prompt": prompt, "size": size, "n": str(n)}
        if transparent:
            data["background"] = "transparent"
        resp = requests.post(
            "https://api.openai.com/v1/images/edits",
            headers=headers, data=data, files=files, timeout=600,
        )
    else:
        payload = {"model": model, "prompt": prompt, "size": size, "n": n}
        if transparent:
            payload["background"] = "transparent"
        resp = requests.post(
            "https://api.openai.com/v1/images/generations",
            headers=headers, json=payload, timeout=600,
        )
    if resp.status_code != 200:
        raise RuntimeError(f"OpenAI {resp.status_code}: {resp.text[:500]}")
    return [base64.b64decode(item["b64_json"]) for item in resp.json()["data"]]


def generate_openai(key, prompt, refs, size, n, transparent, verbose, pinned=None):
    chain = resolve_openai_models(key, verbose, pinned)
    errors = []
    for idx, model in enumerate(chain):
        try:
            images = _openai_request(key, model, prompt, refs, size, n, transparent)
        except Exception as exc:  # 모델 단위 폴백 (flare → sunburst → 2 순)
            errors.append(f"{model}: {exc}")
            if idx + 1 < len(chain):
                print(f"[openai] {model} 실패 — {chain[idx + 1]}로 폴백", file=sys.stderr)
            continue
        if verbose:
            print(f"[openai] model: {model}")
        return images
    raise RuntimeError("; ".join(errors))


def generate_gemini(key, prompt, refs, size, n, transparent, verbose, pinned=None):
    if transparent and verbose:
        print("[gemini] 경고: 투명 배경 미지원 — 무시됨")
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{GEMINI_MODEL}:generateContent?key={key}"
    )
    parts = [{"text": prompt}]
    for p in refs:
        parts.append({
            "inline_data": {
                "mime_type": "image/png",
                "data": base64.b64encode(p.read_bytes()).decode(),
            }
        })
    body = {
        "contents": [{"parts": parts}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": SIZE_TO_RATIO[size]},
        },
    }
    images = []
    for i in range(n):
        resp = requests.post(url, json=body, timeout=600)
        if resp.status_code == 400 and "imageConfig" in resp.text:
            del body["generationConfig"]["imageConfig"]  # 파라미터 미지원 폴백
            resp = requests.post(url, json=body, timeout=600)
        if resp.status_code != 200:
            raise RuntimeError(f"Gemini {resp.status_code}: {resp.text[:500]}")
        got = [
            base64.b64decode(part["inlineData"]["data"])
            for cand in resp.json().get("candidates", [])
            for part in cand.get("content", {}).get("parts", [])
            if "inlineData" in part
        ]
        if not got:
            raise RuntimeError("Gemini 응답에 이미지 없음 (안전 필터 가능성)")
        images.extend(got)
        if n > 1 and i < n - 1:
            time.sleep(3)  # rate limit 완화
    return images


def generate_codex(prompt, refs, size, n, transparent, verbose):
    """auth 경로(기본): `codex exec` + image_generation — ChatGPT 계정 인증, 모델 셀렉션 불가.

    컷마다 새 대화로 실행한다 (같은 스레드 연속 생성은 이전 결과에 수렴 — rules.md 실증).
    """
    blobs = []
    for i in range(n):
        with tempfile.TemporaryDirectory() as td:
            target = Path(td) / "out.png"
            instruction = (
                "Use the image_generation tool to create exactly ONE image and save the "
                f"resulting file to {target} (PNG). Aspect ratio {SIZE_TO_RATIO[size]} ({size}). "
                + ("Transparent background. " if transparent else "")
                + ("The attached image(s) are the canonical character reference — keep the "
                   "character identical. " if refs else "")
                + "Do nothing else. Image prompt:\n\n" + prompt
            )
            cmd = ["codex", "exec", "--enable", "image_generation", "--ephemeral",
                   "--skip-git-repo-check", "-s", "workspace-write", "-C", td, instruction]
            for r in refs:  # 프롬프트 positional 뒤에 -i (가변 인자가 positional을 삼킴)
                cmd += ["-i", str(r)]
            if verbose:
                print(f"[codex] cut {i + 1}/{n} 생성 중 (컷당 수 분 소요)")
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=CODEX_TIMEOUT)
            blob = target.read_bytes() if target.is_file() else b""
            if res.returncode != 0 or not blob:
                tail = ((res.stdout or "") + "\n" + (res.stderr or ""))[-800:]
                reason = "파일 미생성/빈 파일" if not blob else "비정상 종료"
                raise RuntimeError(f"codex 생성 실패 (exit {res.returncode}, {reason}): {tail}")
            blobs.append(blob)
    return blobs


def main() -> int:
    ap = argparse.ArgumentParser(description="캐릭터 파이프라인 이미지 생성기")
    ap.add_argument("prompt", nargs="?", help="프롬프트 텍스트 (또는 -P 파일)")
    ap.add_argument("-P", "--prompt-file", type=Path, help="프롬프트 파일 경로")
    ap.add_argument("-r", "--ref", type=Path, action="append", default=[],
                    help="참조 이미지 (정본 앵커). 반복 가능")
    ap.add_argument("-s", "--size", choices=SIZES, default="1024x1024")
    ap.add_argument("-n", "--count", type=int, default=1, help="후보 수")
    ap.add_argument("-o", "--out", type=Path, required=True, help="출력 디렉토리")
    ap.add_argument("-N", "--name", default="gen", help="파일명 접두어")
    ap.add_argument("--transparent", action="store_true", help="투명 배경 (auth/OpenAI)")
    ap.add_argument("-m", "--model", default=None,
                    help="OpenAI 모델 고정 — API 경로 함의, 폴백 체인 생략 (비교 생성용)")
    ap.add_argument("--provider", choices=("auth", "openai", "gemini"), default=None,
                    help="auth=codex(ChatGPT 계정, 기본) / openai·gemini=API 명시 지정")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if bool(args.prompt) == bool(args.prompt_file):
        ap.error("prompt 인자와 -P 중 정확히 하나를 지정")
    if args.model is not None and not args.model.strip():
        ap.error("-m/--model 값이 비어 있음 — 모델 ID를 지정하거나 옵션을 생략")
    if args.model and args.provider in ("auth", "gemini"):
        ap.error(f"--model은 API(OpenAI) 전용 — --provider {args.provider}와 함께 쓸 수 없음")
    provider = args.provider or ("openai" if args.model else "auth")
    prompt = args.prompt or args.prompt_file.read_text().strip()
    for ref in args.ref:
        if not ref.is_file():
            ap.error(f"참조 이미지 없음: {ref}")

    if provider == "auth":
        try:
            images = generate_codex(prompt, args.ref, args.size, args.count,
                                    args.transparent, args.verbose)
        except Exception as exc:
            print(f"생성 실패 (auth/codex): {exc}", file=sys.stderr)
            print("모델 셀렉션·API 경로가 필요하면 --provider openai 또는 -m <model>로 명시 지정",
                  file=sys.stderr)
            return 1
    else:
        env = load_env()
        key_names = {"openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}
        key = env.get(key_names[provider])
        if not key:
            print(f"생성 실패: {key_names[provider]} 미설정 — scripts/openv.sh로 주입하거나 .env에 기입",
                  file=sys.stderr)
            return 1
        fn = {"openai": generate_openai, "gemini": generate_gemini}[provider]
        try:
            images = fn(key, prompt, args.ref, args.size, args.count,
                        args.transparent, args.verbose, args.model)
        except Exception as exc:  # 경로 간 자동 폴백 없음 — API 사용은 명시적 지시(2026-09-22)
            print(f"생성 실패 ({provider}): {exc}", file=sys.stderr)
            return 1

    args.out.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%m%d-%H%M%S")
    for i, blob in enumerate(images, 1):
        path = args.out / f"{args.name}-{stamp}-{i:02d}.png"
        path.write_bytes(blob)
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
