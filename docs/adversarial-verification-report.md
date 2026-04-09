# Adversarial Cross-Verification Report

**Date**: 2026-04-08
**Verifier**: Architect Agent (Opus)
**Input**: 3 independent code reviews (OMC, Superpowers, Codex)
**Method**: 각 이슈를 실제 코드 대조로 검증, 합의/불일치 분석, 오탐 식별

---

## 1. Consensus Issues (3개 리뷰어 합의 -- 최고 신뢰도)

| Issue | A | B | C | Final Severity |
|-------|---|---|---|----------------|
| 의존성 매니페스트 없음 | HIGH | HIGH | MEDIUM | **HIGH** |
| CI drafts 경로 불일치 | LOW* | CRITICAL | HIGH | **CRITICAL** |
| Broad `except Exception` | HIGH | HIGH | MEDIUM | **HIGH** |

*Review A는 "content/drafts vs drafts 혼란"으로 LOW 분류했으나 동일 이슈

---

## 2. Two-Reviewer Agreement (2개 합의, 1개 누락)

| Issue | Agreed By | Final Severity |
|-------|-----------|----------------|
| 테스트가 실제 프로젝트 디렉토리에 쓰기 | A, B | **HIGH** |
| 통합테스트 page bundle 불일치 | A, B | **HIGH** |
| main 직접 push | A, B | **MEDIUM** |
| AI 응답 스키마 검증 없음 | A, B | **MEDIUM** |
| 하드코딩된 모델명 | A, B | **LOW** |
| CSS `!important` | A, B | **LOW (의도적 설계)** |
| `enableSitemap` 중복 | A, B | **LOW (문서화 목적)** |

---

## 3. Single-Reviewer Findings (검증 결과)

| Issue | Claimed By | Claimed Severity | Verified Severity | Notes |
|-------|------------|------------------|-------------------|-------|
| `.env` 미사용 API 키 | A | CRITICAL | **MEDIUM** | gitignore 되어있어 노출 위험 낮음. 로컬 credential sprawl 수준 |
| `.env*` glob 패턴 누락 | C | HIGH | **MEDIUM** | `.env.local` 등 실제 존재하지 않지만 예방 차원 필요 |
| `shutil.copy2` 심볼릭 링크 | C | HIGH | **LOW** | 공격자가 drafts에 심볼릭 링크를 넣으려면 이미 repo 쓰기 권한 필요 |
| AI가 프론트매터 덮어쓰기 | C | MEDIUM | **FALSE POSITIVE** | `refine.py:152-179`에서 기존값 우선 보존 확인 |
| 이중 배포 | C | MEDIUM | **MEDIUM** | draft push → refine + deploy → refine push → deploy 재실행 확인 |
| API timeout 미설정 | B | MEDIUM | **MEDIUM** | 기본 600초, CI에서 20개 처리 시 최대 200분 블로킹 가능 |
| `cancel-in-progress: false` | B | LOW | **FALSE POSITIVE** | Pages 배포에서는 취소가 오히려 위험 |
| README 미갱신 | C | LOW | **LOW** | 템플릿 README가 그대로 남아있음 |
| `baseURL` 하드코딩 | C | LOW | **LOW** | GitHub Pages 프로젝트 사이트 표준 패턴 |

---

## 4. False Positives (오탐)

| Issue | Claimed By | Why False Positive |
|-------|------------|--------------------|
| AI가 기존 프론트매터 덮어쓰기 | C (MEDIUM) | `refine.py:152`에서 `fm = dict(existing_fm)`으로 기존값 보존. AI 값은 빈 필드에만 적용 |
| `cancel-in-progress: false` | B (LOW) | Pages 배포 중 취소하면 사이트 깨짐. 현재 설정이 올바름 |
| CSS `!important` | A, B (LOW) | 의도적 디자인 결정. 주석으로 명시됨. 테마 유틸리티 클래스 오버라이드의 유일한 방법 |
| `enableSitemap: true` | A, B (LOW) | 명시적 설정은 문서화 목적으로 유효 |
| `baseURL` 하드코딩 | C (LOW) | GitHub Pages 표준 패턴 |

---

## 5. Issues No Reviewer Caught

1. `refine.yml`이 `actions/checkout@v4`를 `persist-credentials: false` 없이 사용
2. 테스트 `test_drafts_to_content_pipeline`이 `PROJECT_ROOT / "drafts"` (잘못된 경로)를 생성하여 CI 경로 버그를 마스킹
3. `.python-version` 또는 tool-versions 파일 없음 (로컬/CI Python 버전 불일치 가능)

---

## 6. Final Integrated Issue List (우선순위 정렬)

| # | Severity | Issue | Confirmed By | Action Required |
|---|----------|-------|--------------|-----------------|
| 1 | **CRITICAL** | CI drafts 경로 불일치 -- 파이프라인 작동 불가 | B, C, 코드 증거 | `refine.yml` paths를 `content/drafts/**`로, `--drafts-dir content/drafts`로 수정 |
| 2 | **HIGH** | 의존성 매니페스트 없음 | A, B, C | `requirements.txt` 추가 (pinned versions) |
| 3 | **HIGH** | Broad `except Exception` in `_ai_refine` | A, B, C | `json.JSONDecodeError`, `anthropic.APIError` 등 구분 처리 |
| 4 | **HIGH** | 통합테스트 page bundle 불일치 | A, B, 코드 증거 | `test_drafts_to_content_pipeline`을 `slug/index.md` 구조로 수정 |
| 5 | **HIGH** | 테스트가 실제 프로젝트 디렉토리에 쓰기 | A, B | `tmp_path` 사용으로 전환 |
| 6 | **MEDIUM** | 이중 배포 (draft push 시) | C, 코드 증거 | `refine.yml`에 `paths-ignore` 추가 또는 PR 기반 플로우 |
| 7 | **MEDIUM** | AI 응답 type 검증 없음 | A, B | `json.loads` 결과 type 체크 추가 |
| 8 | **MEDIUM** | `.env*` glob 패턴 누락 | C | `.gitignore`에서 `.env` → `.env*`로 변경 |
| 9 | **MEDIUM** | API timeout 미설정 | B | `Anthropic(timeout=60.0)` 추가 |
| 10 | **MEDIUM** | main 직접 push (refine workflow) | A, B | PR 기반 플로우 또는 `[skip ci]` 추가 |
| 11 | **LOW** | `.env`에 미사용 API 키 | A | `OPENAI_API_KEY`, `GEMINI_API_KEY` 제거 |
| 12 | **LOW** | 하드코딩된 모델명 | A, B | 환경변수로 추출 |
| 13 | **LOW** | README가 템플릿 설명 | C | 실제 프로젝트 설명으로 갱신 |

---

## 7. Reviewer Performance

| Metric | OMC (A) | Superpowers (B) | Codex (C) |
|--------|---------|-----------------|-----------|
| Total issues found | 12 | 12 | 9 |
| Confirmed valid | 10 | 11 | 7 |
| False positives | 0 | 1 | 2 |
| Unique findings | 1 (unused .env keys) | 1 (API timeout) | 3 (symlink, .env glob, README) |
| CRITICAL accuracy | Overstated (.env→MEDIUM) | Accurate (CI path) | N/A |
| Missed CRITICAL | CI path (rated LOW) | None | None |

**Best overall**: Superpowers Code Reviewer (B) -- 가장 높은 정확도, CRITICAL 이슈 정확히 식별

---

## 8. Verification Status

**STATUS: VERIFIED -- REQUEST CHANGES**

CRITICAL 1건과 HIGH 4건이 수정되기 전까지 프로덕션 배포 부적합. 개인 블로그 프로젝트임을 감안하면 MEDIUM 이하는 점진적 개선 가능.
