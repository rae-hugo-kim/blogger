## Kickoff Summary: 2-모델 초안 생성 파이프라인 (argon + fable)

**Date**: 2026-10-16
**Type**: Feature
**task_id**: 20261016-125459-7a89

### JTBD
- User: 블로그 저자 본인(rae)
- Problem: 글 한 편을 처음부터 쓰는 비용이 커서 얼개만 있는 아이디어가 `drafts/`에 쌓이고, 기존 퇴고 흐름은 완성된 산문이 있어야만 시작된다.
- Success: `drafts/<slug>/.draft/outline.md`(categories + 헤딩/불릿) 하나로 저자 글 샘플을 컨텍스트로 받은 두 모델 초안이 나오고, 세션의 차이 요약·추천을 보고 하나를 골라 기존 퇴고 → `scripts/normalize.py` → 사람 리뷰 흐름에 넣을 수 있다.

### Context
- Repo type: single (Hugo 블로그 + Python 스크립트 + OMP 하네스 2026.88)
- Tech stack: Hugo, Python 3 (`scripts/normalize.py`, `scripts/chargen.py`), pytest (`tests/` 5파일)
- Build/Test: `python3 -m pytest tests/ -q`, `node --test .omp/extensions/harness/tests/*.test.mjs`
- Patterns:
  - 커스텀 에이전트 `model:` 프런트매터로 모델 고정 (`.omp/agents/adversary.md` → `@advisor`, `verifier.md` → `["@task","@default"]`)
  - 출력 보호: `normalize.py` `process_drafts`는 출력 존재 시 스킵, `--force <slug>`만 재처리
  - 톤 매핑: `docs/tone-guide.md` categories → `tone-essay.md` / `tone-note.md` / `tone-tech.md`
  - 크리덴셜: 1Password `scripts/openv.sh` (이번 설계는 OMP 에이전트 호출이라 직접 API 키 불필요)
- Models: `gemini-4-argon` (Google, 1M ctx), `claude-fable-5-1` (Anthropic, 1M ctx) — `omp models`에서 확인
- Corpus: 레포 내 약 12k 단어 (`content/posts` 1편, `drafts/` 7편, `drafts/archive/` 16편); 외부 원본(fmkorea·황견적 개발일지·이세계 표류기)은 미수집
- Risks/constraints: 2026-07-15 결정 승계(CI AI 재작성 금지, 자동 게시 없음); `drafts/`는 gitignore; archive에 AI 정제본 혼입 가능

### Decisions (interview)
| 항목 | 결정 |
|---|---|
| 샘플 코퍼스 | 레포 글 + 외부 원본, `samples/<톤>/*.md` (git 미추적) |
| 모델 역할 | 둘 다 초안 생성 → 비교 선택 |
| 실행 형태 | OMP 스킬 `/skill:draft` + 커스텀 에이전트 2개 |
| 얼개 입력 | `drafts/<slug>/.draft/outline.md` (plan attack 후 `.draft/` 아래로 이동 결정) |
| 비교·선택 | 파일 2개 생성 + 세션이 차이 요약표·추천, 선택은 사용자 |
| 샘플 투입 | outline categories와 같은 톤 폴더 전부, 상한 초과 시 최신순 절단 + 경고 |
| 출력 보호 | 둘 다 있으면 중단, 한쪽만 있으면 누락 측만 생성, `--force`로만 양쪽 재생성 |

### Plan Attack (Step 3.5)
- Run 1 결과: WARN (CRITICAL 0 / HIGH 5 / MEDIUM 2) — `docs/harness/plan-attack-report.md`
- 반영: 부분 실패 계약, 전체 입력 예산·절단 정의, 생성 품질 검사, 자료 구획(신뢰 경계), 파이프라인 파일을 `drafts/<slug>/.draft/` 아래로 배치(사용자 결정 — `normalize.py` dot-엔트리 제외 규칙으로 게시 번들 복사 차단)

### Scope
- MUST:
  1. `samples/<톤>/*.md` 코퍼스 컨벤션 (에세이·작업노트·리딩노트), `.gitignore` 등재 + `samples/README.md`(저자 원본만 투입)만 추적
  2. `scripts/draft_prompt.py`: `.draft/outline.md` → 톤 매핑 → 샘플 + 공통/톤 가이드 + 얼개를 자료 구획으로 결정적 조립(`.draft/prompt.md`); 전체 입력 예산 기준 최신순(date → mtime, 동률 파일명 역순) 파일 단위 절단 + 경고
  3. `.omp/agents/drafter-argon.md` (gemini-4-argon), `.omp/agents/drafter-fable.md` (claude-fable-5-1): 프롬프트 파일을 읽어 `.draft/draft-argon.md`, `.draft/draft-fable.md`만 작성
  4. `/skill:draft <slug> [--force]`: 조립 → 두 에이전트 병렬 호출 → 차이 요약표(구조·톤·샘플 유사도, 문장 근거) + 추천 출력; 둘 다 있으면 중단, 한쪽만 있으면 누락 측만 생성, `--force`만 양쪽 재생성
- SHOULD: 실행 시 샘플 편수·토큰 수 출력
- MUST NOT: CI 실행, `index.md` 자동 생성, 자동 게시, `samples/` 본문 git 추적, `.draft/` 밖 파이프라인 파일 생성
- OUT OF SCOPE: 두 초안 병합 단계, 외부 원본 수집 자동화, 톤 가이드 개정, `scripts/normalize.py` 변경

### Acceptance Criteria
1. `samples/`가 `.gitignore`에 등재되고 `samples/README.md`(톤 폴더 컨벤션, 저자 원본만 투입)만 추적된다.
2. `scripts/draft_prompt.py`가 categories → 톤 폴더 매핑(미지정 → 작업노트, 특허 → 에세이, 복수 → 표 순서 첫 매칭, 미지 → 작업노트)을 수행하고 pytest가 검증한다.
3. `scripts/draft_prompt.py`가 빈 샘플 폴더 또는 절단 후 0편이면 비정상 종료하고, 입력 예산 초과 시 최신순 파일 단위 절단 + 제외 편수 경고를 수행하며 pytest가 검증한다.
4. `.draft/draft-argon.md`와 `draft-fable.md`가 둘 다 있으면 중단하고 `--force`에서만 덮어쓰며, 한쪽만 있으면 누락 측만 생성하도록 판정하고 pytest가 검증한다.
5. 실제 outline 1건으로 `/skill:draft` 실행 시 두 초안이 생성되고, 둘 다 프런트매터에 outline의 categories와 `draft: true`를 가지며 outline의 모든 헤딩 아래에 산문 단락이 존재한다 (실행 로그 + 산출물).
6. `/skill:draft` 종료 시 차이 요약표와 추천이 출력되고, 한쪽만 성공하면 비교 대신 부분 실패 경고가 출력된다 (실행 로그).
7. 지시문이 삽입된 샘플로 조립해도 샘플이 자료 구획 안에 머문다 — `.omp/evals/draft-pipeline.md`에 케이스 기록, pytest로 구획 검증.

### Edge Cases
- `.draft/outline.md` 없음 또는 프런트매터 파싱 실패 → 안내 후 중단
- categories 복수(예: 에세이+특허) → tone-guide 표 순서로 첫 매칭
- 한 모델 비활성/실패 → 부분 실패: 성공분 보존, 비교·추천 생략, 재실행 시 누락 측만 생성
- 샘플 총량이 입력 예산 초과 → 최신순 파일 단위 절단, 제외 편수 경고; 절단 후 0편이면 중단
- 단일 샘플이 예산보다 큼 → 파일 단위 제외(본문 중간 절단 없음)

### Backpressure
- Method: pytest (AC 2·3·4·7) + 실제 outline 1건 스모크 실행 (AC 5·6) + 프롬프트 표면 변경 시 `.omp/evals/draft-pipeline.md` 기록
- Command: `python3 -m pytest tests/ -q`; `/skill:draft <slug>` 실행 로그

### Estimate
- risk: medium, files: 10, depth: high, model: claude-fable-5-1, effort: high

---
Kickoff complete. Ready for implementation.
Next: `/startdev` or manual planning.
