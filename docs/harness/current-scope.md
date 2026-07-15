# Current Scope: blogger

**Created**: 2026-03-31
**Revised**: 2026-07-15 — refine AI 파이프라인 퇴역 (사용자 결정: 원샷 자동화는 파이프라인의 목적이 아님)

## MUST
- 블로그 기본 구조 (글 목록, 글 상세, 카테고리/태그)
- 게시 정규화 (non-AI: drafts/ → content/posts/ 번들 조립, `scripts/normalize.py`)
- 커스텀 디자인 (Hugo 템플릿 활용)
- 배포 (GitHub Pages)

## SHOULD
- 적대적 검증/상호교차편집 시스템으로 콘텐츠 완성도 향상
- 댓글 시스템 (추후 추가 가능)

## MUST NOT
- 회원가입/인증 기능
- CI에서의 AI 콘텐츠 재작성 (2026-07-15 퇴역 — 퇴고는 사람/에이전트 대화형으로 수행)

## OUT OF SCOPE
- 다국어 지원
- CMS 웹 관리자 패널

## Acceptance Criteria
- [x] hugo serve로 로컬에서 글 목록/상세 페이지가 정상 렌더링된다 (12 tests passed)
- [x] 실제 도메인(GitHub Pages)에 배포되어 접속 가능하다 (2026-07-15 https://rae-hugo-kim.github.io/blogger/ 응답 확인 — Hugo 출력 서빙 중)
- [x] drafts/<slug>/를 scripts/normalize.py로 조립하면 프론트매터가 채워진 draft:true 번들이 생성된다 (2026-07-15 개정: push-트리거 CI 자동화 퇴역 → 로컬 non-AI 정규화. pytest 57 passed)
- [x] 정규화된 번들의 프론트매터(title, description, tags, date 등)가 완전히 채워져 있다 — 휴리스틱 채움은 리뷰용 placeholder로 auto-filled warning 표면화 (pytest 57 passed)
- [x] 블로그 톤/형식 가이드가 퇴고 진입점에 배선되어 있다 (2026-07-15 개정: AI 문체 변환 퇴역 → 퇴고 주체가 톤 가이드를 컨텍스트로 로드. INDEX.md·docs/tone-guide.md 재배선)

## Scope Change Log
- 2026-07-15: MUST "콘텐츠 정제 파이프라인 (Git 기반 자동화: drafts/ → 정제 초안)"을
  "게시 정규화 (non-AI)"로 교체. 근거: refine CI 3개월 무가동(총 1회 실행 = 자기 셋업 커밋),
  산출물 draft-01..20 전부 draft:true 미게재, 사용자 명시 결정("원샷 자동화는 파이프라인의
  목적이 아니다"). 산문 퇴고는 에이전트/사람의 대화형 작업으로 이동, AC 3·5를 그에 맞게 개정.
  (구 원고는 미추적 drafts/archive/로 이관 — git 히스토리에는 잔존, 앞으로 추적하지 않음.)
