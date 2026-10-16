# Current Scope: 2-모델 초안 생성 파이프라인 (argon + fable)

**Created**: 2026-10-16
**Seed**: docs/harness/seed.yaml (task_id 20261016-125459-7a89)
**Plan attack**: docs/harness/plan-attack-report.md (run 1, WARN — 반영 완료)

## MUST
- `samples/<톤>/*.md` 코퍼스 컨벤션 (에세이·작업노트·리딩노트) — `.gitignore` 등재, `samples/README.md`(저자 원본만 투입)만 추적
- `scripts/draft_prompt.py` — `.draft/outline.md` → 톤 매핑 → 샘플 + 공통/톤 가이드 + 얼개를 자료 구획으로 결정적 조립(`.draft/prompt.md`), 전체 입력 예산 기준 최신순 파일 단위 절단 + 경고
- `.omp/agents/drafter-argon.md` (gemini-4-argon), `.omp/agents/drafter-fable.md` (claude-fable-5-1) — 프롬프트 파일을 읽어 `.draft/draft-argon.md`, `.draft/draft-fable.md`만 작성
- `/skill:draft <slug> [--force]` — 조립 → 두 에이전트 병렬 호출 → 차이 요약표 + 추천 출력; 둘 다 있으면 중단, 한쪽만 있으면 누락 측만 생성, `--force`만 양쪽 재생성

## SHOULD
- 실행 시 샘플 편수·토큰 수 출력

## MUST NOT
- CI 실행
- `index.md` 자동 생성 (선택은 사용자)
- 자동 게시
- `samples/` 본문 git 추적
- `.draft/` 밖에 파이프라인 파일 생성 (게시 번들 복사 차단)

## OUT OF SCOPE
- 두 초안 병합 단계
- 외부 원본 수집 자동화
- 톤 가이드(docs/tone-*.md) 개정
- `scripts/normalize.py` 변경

## Acceptance Criteria
- [x] `samples/`가 `.gitignore`에 등재되고 `samples/README.md`(톤 폴더 컨벤션, 저자 원본만 투입)만 추적된다
- [x] `scripts/draft_prompt.py`가 categories → 톤 폴더 매핑(미지정 → 작업노트, 특허 → 에세이, 복수 → 표 순서 첫 매칭, 미지 → 작업노트)을 수행하고 pytest가 검증한다
- [x] `scripts/draft_prompt.py`가 빈 샘플 폴더 또는 절단 후 0편이면 비정상 종료하고, 입력 예산 초과 시 최신순(date → mtime, 동률 파일명 역순) 파일 단위 절단 + 제외 편수 경고를 수행하며 pytest가 검증한다
- [x] `.draft/draft-argon.md`와 `draft-fable.md`가 둘 다 있으면 중단하고 `--force`에서만 덮어쓰며, 한쪽만 있으면 누락 측만 생성하도록 판정하고 pytest가 검증한다
- [x] 실제 outline 1건으로 `/skill:draft` 실행 시 두 초안이 생성되고, 둘 다 프런트매터에 outline의 categories와 `draft: true`를 가지며 outline의 모든 헤딩 아래에 산문 단락이 존재한다 (실행 로그 + 산출물)
- [x] `/skill:draft` 종료 시 차이 요약표(구조·톤·샘플 유사도, 문장 근거)와 추천이 출력되고, 한쪽만 성공하면 부분 실패 경고가 출력된다 (실행 로그)
- [x] 지시문이 삽입된 샘플로 조립해도 샘플이 자료 구획 안에 머문다 — `.omp/evals/draft-pipeline.md`에 케이스 기록, pytest로 구획 검증
