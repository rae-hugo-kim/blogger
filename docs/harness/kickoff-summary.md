## Kickoff Summary: blogger

**Date**: 2026-03-31
**Type**: New Project

### JTBD
- User: 본인 (개인 기술 블로그 운영자)
- Problem: 특정 도메인(기술/개발)에 대해 다양한 창구에서 다양한 글투와 무게감으로 작성한 글을 모아 정제하고 싶음
- Success: 외부에서 작성한 md 문서를 블로그의 톤과 형식에 맞게 자동 수정한 초안을 제공하고, SEO 최적화된 커스텀 디자인 블로그로 발행하여 실서비스로 운영

### Context
- Repo type: single (claude harness 템플릿에서 초기화)
- Tech stack: Hugo (정적 사이트 생성기) + Git 기반 콘텐츠 정제 파이프라인
- Build cmd: hugo build (설정 후)
- Test cmd: hugo serve (로컬 검증)
- Existing patterns: harness 훅 체계 (scope-gate, acceptance-gate 등)
- Risks/constraints: AI 정제 파이프라인은 CI/CD 통합 필요, Hugo 테마 선정 필요

### Scope
- MUST:
  - 블로그 기본 구조 (글 목록, 글 상세, 카테고리/태그)
  - 콘텐츠 정제 파이프라인 (Git 기반 자동화: drafts/ 폴더에 md push → 정제된 초안 생성)
  - 커스텀 디자인 (Hugo 템플릿 활용)
  - 배포 (GitHub Pages 정적 배포, Vercel 추가 고려)
- SHOULD:
  - 적대적 검증/상호교차편집 시스템으로 콘텐츠 완성도 향상
  - 댓글 시스템 (추후 추가 가능)
- MUST NOT:
  - 회원가입/인증 기능
- OUT OF SCOPE:
  - 다국어 지원
  - CMS 웹 관리자 패널

### Acceptance Criteria
1. `hugo serve`로 로컬에서 글 목록/상세 페이지가 정상 렌더링된다
2. 실제 도메인(GitHub Pages 또는 Vercel)에 배포되어 접속 가능하다
3. `drafts/` 폴더에 md 파일을 push하면 SEO 메타, 태그, 요약이 자동 생성된 정제 초안이 만들어진다
4. 정제된 초안의 프론트매터(title, description, tags, date 등)가 완전히 채워져 있다
5. 블로그 톤/형식 가이드에 따라 문체가 통일된 초안이 생성된다

### Edge Cases
- 이미 프론트매터가 있는 md 파일이 투입된 경우 → 기존 값 존중, 빈 필드만 채움
- 코드 블록이 많은 기술 문서 → 코드 블록 내용은 정제하지 않음
- 매우 짧은 메모 수준의 글 → 최소 분량 미달 시 경고

### Backpressure
- Verification method: hugo build + 배포 URL 접속 + 정제 파이프라인 테스트
- How to run:
  1. `hugo build` → 빌드 성공 확인
  2. `hugo serve` → 로컬에서 페이지 렌더링 확인
  3. drafts/에 테스트 md push → 정제 초안 생성 확인
  4. 배포 URL 접속 확인

---
Kickoff complete. Ready for implementation.
Next: `/startdev` or manual planning.
