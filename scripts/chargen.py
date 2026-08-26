"""Character image generator for the blog character pipeline.

기본: OpenAI GPT Images API (최신 gpt-image 모델 자동 선택),
폴백: Google Gemini (Nano Banana, gemini-3-pro-image-preview).

키는 환경변수 또는 저장소 루트 `.env`(gitignore됨)에서 읽는다:
  OPENAI_API_KEY=...   # 기본 공급자
  GEMINI_API_KEY=...   # 폴백 공급자

사용 예:
  python3 scripts/chargen.py "prompt text" -o references/characters/bob -N bob-v3
  python3 scripts/chargen.py -P prompt.txt -r references/characters/rae/canonical-front-side.png \
      -s 1536x1024 -n 2 -o references/characters/rae -N rae-scene
"""

import argparse
import base64
import sys
import time
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parent.parent
SIZES = ("1024x1024", "1536x1024", "1024x1536")
SIZE_TO_RATIO = {"1024x1024": "1:1", "1536x1024": "3:2", "1024x1536": "2:3"}
OPENAI_MODEL_PREFERENCE = ("gpt-image-2", "gpt-image-1.5", "gpt-image-1")
GEMINI_MODEL = "gemini-3-pro-image-preview"


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


def pick_openai_model(key: str, verbose: bool) -> str:
    """가용 모델 목록에서 선호 순서대로 gpt-image 계열을 고른다."""
    resp = requests.get(
        "https://api.openai.com/v1/models",
        headers={"Authorization": f"Bearer {key}"},
        timeout=30,
    )
    resp.raise_for_status()
    available = {m["id"] for m in resp.json().get("data", [])}
    for preferred in OPENAI_MODEL_PREFERENCE:
        matches = sorted(m for m in available if m.startswith(preferred))
        if matches:
            if verbose:
                print(f"[openai] model: {matches[-1]}")
            return matches[-1]
    image_models = sorted(m for m in available if "image" in m and m.startswith("gpt"))
    if image_models:
        return image_models[-1]
    raise RuntimeError("OpenAI 계정에서 gpt-image 계열 모델을 찾지 못함")


def generate_openai(key, prompt, refs, size, n, transparent, verbose):
    model = pick_openai_model(key, verbose)
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


def generate_gemini(key, prompt, refs, size, n, transparent, verbose):
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
    ap.add_argument("--transparent", action="store_true", help="투명 배경 (OpenAI 전용)")
    ap.add_argument("--provider", choices=("auto", "openai", "gemini"), default="auto")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    if bool(args.prompt) == bool(args.prompt_file):
        ap.error("prompt 인자와 -P 중 정확히 하나를 지정")
    prompt = args.prompt or args.prompt_file.read_text().strip()
    for ref in args.ref:
        if not ref.is_file():
            ap.error(f"참조 이미지 없음: {ref}")

    env = load_env()
    chain = {
        "auto": [("openai", generate_openai), ("gemini", generate_gemini)],
        "openai": [("openai", generate_openai)],
        "gemini": [("gemini", generate_gemini)],
    }[args.provider]
    key_names = {"openai": "OPENAI_API_KEY", "gemini": "GEMINI_API_KEY"}

    errors = []
    for provider, fn in chain:
        key = env.get(key_names[provider])
        if not key:
            errors.append(f"{provider}: {key_names[provider]} 미설정 (.env 또는 환경변수)")
            continue
        try:
            images = fn(key, prompt, args.ref, args.size, args.count,
                        args.transparent, args.verbose)
        except Exception as exc:  # 공급자 단위 폴백
            errors.append(f"{provider}: {exc}")
            continue
        args.out.mkdir(parents=True, exist_ok=True)
        stamp = time.strftime("%m%d-%H%M%S")
        for i, blob in enumerate(images, 1):
            path = args.out / f"{args.name}-{stamp}-{i:02d}.png"
            path.write_bytes(blob)
            print(path)
        return 0

    print("생성 실패:", file=sys.stderr)
    for err in errors:
        print(f"  - {err}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
