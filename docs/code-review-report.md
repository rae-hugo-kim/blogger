# Code Review Report

**Date**: 2026-04-08
**Project**: blogger (Hugo blog + AI content refinement pipeline)
**Reviewers**: OMC Code Reviewer (Opus), Superpowers Code Reviewer (Opus), Codex CLI (GPT-5.4)

---

## Executive Summary

3개의 독립적인 리뷰어가 프로젝트 전체를 검토했습니다. 총 13개 이슈가 식별되었으며, CI 파이프라인이 현재 작동하지 않는 CRITICAL 이슈 1개가 포함되어 있습니다.

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| HIGH | 4 |
| MEDIUM | 5 |
| LOW | 3 |

**종합 판정**: REQUEST CHANGES

---

## Review A: OMC Code Reviewer (Opus)

### Findings

| # | Severity | Issue | Location |
|---|----------|-------|----------|
| A1 | CRITICAL | `.env`에 미사용 API 키 존재 (OPENAI, GEMINI) | `.env:4-6` |
| A2 | HIGH | Broad `except Exception`이 모든 AI 정제 에러를 무음 처리 | `scripts/refine.py:232` |
| A3 | HIGH | 의존성 매니페스트 파일 없음 (requirements.txt / pyproject.toml) | Project root |
| A4 | HIGH | `process_drafts`는 page bundle glob인데 통합테스트는 flat file 생성 | `scripts/refine.py:242`, `tests/test_step2_pipeline.py:287` |
| A5 | MEDIUM | `refine.yml`이 main에 직접 push (branch protection 우회) | `.github/workflows/refine.yml:40-47` |
| A6 | MEDIUM | AI 응답에 스키마 검증 없음 (type 미확인) | `scripts/refine.py:228-231` |
| A7 | MEDIUM | `shutil.copy2`가 .DS_Store 등 불필요한 파일도 복사 | `scripts/refine.py:251-252` |
| A8 | MEDIUM | 테스트가 실제 프로젝트 디렉토리에 직접 쓰기 | `tests/test_step2_pipeline.py:175-193` |
| A9 | MEDIUM | 하드코딩된 모델명 (`claude-sonnet-4-5-20250929`) | `scripts/refine.py:218` |
| A10 | LOW | `content/drafts/` vs `drafts/` 디렉토리 혼란 | Project structure |
| A11 | LOW | CSS `!important` override가 테마 업데이트에 취약 | `assets/css/custom.css:11` |
| A12 | LOW | `enableSitemap: true` 중복 (Hugo 기본값) | `hugo.yaml:7` |

### Positive Observations
- Clean `.gitignore` 설정
- Dataclass 기반 구조화된 refine.py
- AI 미사용 시 graceful degradation
- 포괄적인 테스트 스위트

---

## Review B: Superpowers Code Reviewer (Opus)

### Findings

| # | Severity | Issue | Location |
|---|----------|-------|----------|
| B1 | CRITICAL | CI workflow drafts 경로가 실제 `content/drafts/`와 불일치 -- 파이프라인 작동 불가 | `.github/workflows/refine.yml:8,32` |
| B2 | HIGH | 의존성 매니페스트 파일 없음 | Project root |
| B3 | HIGH | Broad `except Exception` -- 401/rate limit 등 구분 불가 | `scripts/refine.py:232` |
| B4 | HIGH | 테스트가 실제 프로젝트 디렉토리에 직접 쓰기 | `tests/test_step2_pipeline.py:175-192` |
| B5 | MEDIUM | `refine.yml`이 main에 직접 push | `.github/workflows/refine.yml:40-47` |
| B6 | MEDIUM | API 호출에 timeout 미설정 (기본 600초) | `scripts/refine.py:217-222` |
| B7 | MEDIUM | 하드코딩된 모델명 | `scripts/refine.py:218` |
| B8 | MEDIUM | `_extract_tags`가 noisy 단어 태그 생성 | `scripts/refine.py:104-121` |
| B9 | MEDIUM | 통합테스트가 flat file 생성 (page bundle 불일치) | `tests/test_step2_pipeline.py:287` |
| B10 | LOW | `deploy.yml` `cancel-in-progress: false` | `.github/workflows/deploy.yml:16` |
| B11 | LOW | CSS `!important` override | `assets/css/custom.css:11` |
| B12 | LOW | `enableSitemap: true` 중복 | `hugo.yaml:8` |

### Positive Observations
- Well-structured pipeline architecture
- Graceful AI degradation
- Comprehensive test coverage
- Good `.gitignore` security posture
- Clean frontmatter priority chain
- Comprehensive tone guide

---

## Review C: Codex CLI (GPT-5.4)

### Findings

| # | Severity | Issue | Location |
|---|----------|-------|----------|
| C1 | HIGH | `shutil.copy2` 심볼릭 링크 추적 -- CI가 main에 push하므로 정보 유출 가능 | `scripts/refine.py:250-253` |
| C2 | HIGH | `.gitignore`가 `.env`만 무시 -- `.env.local`, `.env.production` 등 누출 가능 | `.gitignore:23-24` |
| C3 | HIGH | Drafts 경로 불일치 -- 스크립트/워크플로우/테스트/실제 위치 모두 다름 | `scripts/refine.py:237,242,268` |
| C4 | MEDIUM | AI 응답이 기존 프론트매터를 덮어쓰기 가능 | `scripts/refine.py:145-170` |
| C5 | MEDIUM | 에러 시 무음 실패 -- CI가 정제되지 않은 콘텐츠를 배포 가능 | `scripts/refine.py:232,234` |
| C6 | MEDIUM | 의존성 관리 재현 불가 | `.github/workflows/refine.yml:26-27` |
| C7 | MEDIUM | 워크플로우 토폴로지 -- 드래프트 push 시 이중 배포 발생 | `.github/workflows/refine.yml:3,39` |
| C8 | LOW | `baseURL` 하드코딩 | `hugo.yaml:1` |
| C9 | LOW | README가 실제 프로젝트가 아닌 템플릿을 설명 | `README.md:3,45` |

### Verification Results
- `hugo build`: PASS (23 pages, 86ms)
- `pytest`: 30 pass, **1 fail** (`test_drafts_to_content_pipeline` -- 경로 불일치 확인)
