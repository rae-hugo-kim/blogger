# Test Plan Status: blogger

기준일: 2026-03-31

## 현재 점검 결과

- `hugo` CLI: 미설치 (`hugo build` 실행 불가)
- Hugo 사이트 설정 파일: 없음 (`hugo.toml`, `config.*`)
- Hugo 콘텐츠 디렉터리: 없음 (`content/`)
- 초안 입력 디렉터리: 없음 (`drafts/`)
- Python 파이프라인: 없음 (`*.py`)
- GitHub Actions 워크플로: 없음 (`.github/workflows/*`)
- `pytest`: 실행 가능하지만 테스트 0건 수집

## Step 1: Hugo 블로그 기본 구조 (AC1)

### Smoke Tests

- [ ] `hugo build` 명령이 에러 없이 성공한다
  - 사유: `hugo` 명령어가 설치되어 있지 않음
- [ ] `public/` 디렉토리에 `index.html`이 생성된다
  - 사유: 빌드를 수행할 수 없음
- [ ] `public/posts/` 하위에 샘플 포스트 HTML이 생성된다
  - 사유: 샘플 포스트와 Hugo 콘텐츠가 아직 없음

### Rendering Tests

- [ ] 글 목록 페이지에 포스트 제목이 포함되어 있다
  - 사유: 렌더링할 포스트가 없음
- [ ] 글 상세 페이지에 본문 내용이 포함되어 있다
  - 사유: 렌더링할 포스트가 없음
- [ ] 태그 페이지가 생성된다 (`public/tags/`)
  - 사유: 태그가 있는 콘텐츠와 빌드 결과가 없음
- [ ] 카테고리 페이지가 생성된다 (`public/categories/`)
  - 사유: 카테고리가 있는 콘텐츠와 빌드 결과가 없음

## Step 2: 콘텐츠 정제 파이프라인 (AC3, AC4, AC5)

### Unit Tests (pytest)

- [ ] 프론트매터 없는 md -> title, description, tags, date 등 프론트매터 생성
  - 사유: 관련 Python 스크립트와 테스트가 없음
- [ ] 이미 프론트매터 있는 md -> 기존 값 유지, 빈 필드만 채움
  - 사유: 관련 Python 스크립트와 테스트가 없음
- [ ] 코드 블록이 포함된 md -> 코드 블록 내용 변경 없음
  - 사유: 관련 Python 스크립트와 테스트가 없음
- [ ] SEO description 길이가 150-160자 범위 이내
  - 사유: 관련 Python 스크립트와 테스트가 없음
- [ ] tags가 최소 1개 이상 생성됨
  - 사유: 관련 Python 스크립트와 테스트가 없음

### Edge Cases

- [ ] 빈 파일 입력 -> 에러 메시지 또는 스킵
  - 사유: 관련 Python 스크립트와 테스트가 없음
- [ ] 코드 블록만 있는 파일 -> 본문 없이도 처리 가능
  - 사유: 관련 Python 스크립트와 테스트가 없음
- [ ] 매우 짧은 메모 (3줄 미만) -> 경고 포함하여 처리
  - 사유: 관련 Python 스크립트와 테스트가 없음
- [ ] 한글/영문 혼합 문서 -> 정상 처리
  - 사유: 관련 Python 스크립트와 테스트가 없음
- [ ] 이미지 참조가 있는 md -> 이미지 경로 유지
  - 사유: 관련 Python 스크립트와 테스트가 없음

### Integration Tests

- [ ] `drafts/` 폴더의 md 파일이 정제 스크립트를 거쳐 `content/posts/`에 초안 생성
  - 사유: 입력 폴더, 정제 스크립트, 출력 폴더가 아직 없음
- [ ] GitHub Actions 워크플로 YAML이 유효한 구문이다
  - 사유: 워크플로 파일이 아직 없음

## Step 3: 배포 (AC2)

### Deployment Tests

- [ ] GitHub Actions 워크플로가 Hugo build를 실행한다
  - 사유: 워크플로 파일이 아직 없음
- [ ] build 결과물이 `gh-pages` 브랜치에 push된다
  - 사유: 배포 파이프라인이 아직 없음

## 다음에 체크 순서

1. `hugo` 설치
2. `hugo new site`로 기본 사이트 생성
3. Blowfish 테마 연결
4. 샘플 포스트 1개 추가
5. `hugo build` 기준 Step 1 재검증
6. Python 정제 스크립트와 `pytest` 추가
7. GitHub Actions 배포 워크플로 추가 후 Step 2, 3 검증
