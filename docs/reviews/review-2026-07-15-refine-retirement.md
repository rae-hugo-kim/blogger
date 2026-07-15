# Review: refine AI 파이프라인 퇴역 — non-AI 게시 정규화로 축소

- date: 2026-07-15
- diff-hash: 9b0607edca795ff7de11936abdb940a0106e5c99bc47c535326dcc138bde1171
- models: claude, gpt-5
- scope: 스테이징된 54파일 (+873/−6146) — scripts/normalize.py 신규, refine.py·refine.yml·content/drafts·content/posts/draft-01..20 삭제, tests 재작성, docs/harness seed v2·scope 개정, tone docs 재배선

## Verdict: PASS

## 리뷰 구성 (이종 2패스)

1. **Claude 패스** (reviewer 에이전트, 읽기 전용 적대 리뷰): PASS WITH NOTES — BLOCKER/HIGH 0, MEDIUM 1, LOW 4.
2. **GPT 패스** (adversary 에이전트, 독립 교차 검증): PASS WITH NOTES — BLOCKER/HIGH 0, Claude M1/L1–L4 전부 교차 확인. "스테이징된 퇴역분에 공개 배포 잔존 경로 없음" 확인 (deploy는 `hugo build --minify`, `--buildDrafts` 없음, tracked content는 hello-world뿐).

## 발견 및 처분

|ID|심각도|내용|처분|
|---|---|---|---|
|M1|MEDIUM|hardlink가 `_is_asset` 제외를 우회 가능 — docstring이 구현보다 넓게 약속|**수정됨**: docstring을 실제 범위(dot-엔트리/symlink)로 축소, hardlink 미감지를 명시적 수용 리스크로 문서화 (동일 FS + 고의 생성 필요 — 우발 유출 위협모델 밖). 57 tests 재통과|
|L1|LOW|drafts_dir 부재/공집합 시 조용한 무동작 (exit 0, 무출력)|기록 — 후속 개선 후보|
|L2|LOW|불량 드래프트 1건이 배치 중단 (per-file 예외 경계 없음)|기록 — 완료마커 설계로 재실행 복구 가능|
|L3|LOW|`Index.md` 등 대소문자 변형이 에셋으로 복사|기록 — 유출 경로 아님|
|L4|LOW|symlink 검사 TOCTOU (이론적)|조치 불필요 — 단일 사용자 로컬 도구, 위협모델 밖|

## 검증

- pytest 57 passed (asset hygiene 회귀 3종: nested dot-엔트리, top-level/nested symlink 역참조 차단 포함)
- verifier 에이전트 7/7 AC PASS (스테이징 삭제·산출물 보존·dead path 0 검증)
- `normalize.py --dry-run` 실측: 활성 5슬러그만 처리, `drafts/archive/` 제외 확인
