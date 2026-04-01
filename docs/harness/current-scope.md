# Current Scope: blogger

**Created**: 2026-03-31

## MUST
- 블로그 기본 구조 (글 목록, 글 상세, 카테고리/태그)
- 콘텐츠 정제 파이프라인 (Git 기반 자동화: drafts/ → 정제 초안)
- 커스텀 디자인 (Hugo 템플릿 활용)
- 배포 (GitHub Pages, Vercel 추가 고려)

## SHOULD
- 적대적 검증/상호교차편집 시스템으로 콘텐츠 완성도 향상
- 댓글 시스템 (추후 추가 가능)

## MUST NOT
- 회원가입/인증 기능

## OUT OF SCOPE
- 다국어 지원
- CMS 웹 관리자 패널

## Acceptance Criteria
- [x] hugo serve로 로컬에서 글 목록/상세 페이지가 정상 렌더링된다 (12 tests passed)
- [ ] 실제 도메인(GitHub Pages 또는 Vercel)에 배포되어 접속 가능하다 (배포 후 확인)
- [x] drafts/ 폴더에 md 파일을 push하면 SEO 메타, 태그, 요약이 자동 생성된 정제 초안이 만들어진다 (로컬 테스트 통과, CI 실행은 배포 후)
- [x] 정제된 초안의 프론트매터(title, description, tags, date 등)가 완전히 채워져 있다 (17 tests passed)
- [ ] 블로그 톤/형식 가이드에 따라 문체가 통일된 초안이 생성된다 (톤 가이드 작성 후)
