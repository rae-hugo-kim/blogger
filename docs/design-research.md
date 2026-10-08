# 블로그 디자인 조사 노트 (2026-10-01)

## 요약

- 인기 개인 블로그와 상용 블로그 서비스 24곳을 2026-10-01에 캡처하고, 글 화면의 계산된 스타일을 실측했어요. 장문 본문은 16~20px(24곳 중 19곳, 중앙값 약 17px), 행간은 1.6 안팎(한글 서비스 1.6~2.0), 본문 폭은 600~730px(14곳, 중앙값 700px)에 모여요.
- 본문색이 순흑인 곳은 4곳뿐이고, 강조색은 하나만 쓰는 것이 일반적이에요. 다크가 기본인 곳은 Daring Fireball 1곳이에요. 지금 블로그는 OS 설정과 무관하게 다크로 열려요.
- 국내 서비스는 한 줄이 41~48자(네이버 55자)로 WCAG 1.4.8의 CJK 권고 40자를 대부분 넘어요. 그래서 시안은 한 줄 40자 이하를 기준으로 잡았어요.
- 이 근거로 시안 5개(다크 네이비, 차콜 기준선, 화이트+블루 클린 리스트, 페이퍼 세리프, 미니멀 모노크롬)를 같은 토큰 스키마·같은 CSS 규칙·같은 콘텐츠로 만들었어요. 대비는 WCAG 2.x 비율과 APCA Lc를 함께 봐요.
- v2(2026-10-02)에서는 사용자 피드백대로 의미 없는 그라데이션, 카드 스택, AI 템플릿 요소를 걷어냈어요. 콘텐츠는 멤버 캐릭터가 등장하는 가상 글과 생성 삽화로 바꿨어요.

## 1. 범위와 방법

| 항목 | 내용 |
|---|---|
| 조사일 | 2026-10-01 |
| 대상 | 국내 서비스·기업 5, 해외 서비스 5, 해외 개인 5, HN 역대 상위 개인 4, 개인·다크 레퍼런스 5 — 총 24곳 |
| 캡처 | 1280×800 뷰포트, DPR 1, 홈 1장 + 대표 글 1장(webp). 다크 레퍼런스는 `prefers-color-scheme: dark` 에뮬레이션 |
| 실측 | 공용 프로브 `refs/measure.js`로 첫 본문 문단의 배경·글자색·글꼴·크기·행간·폭·링크색을 `getComputedStyle`로 읽었어요. 프로브가 본문을 놓친 곳(Paul Graham, Maggie Appleton, GitHub 블로그)은 가장 긴 본문 문단으로 다시 쟀어요 |
| 웹 조사 | 내장 웹 검색과 1차 출처 직접 열람(원문 HTML·JSON·CSV)을 교차했어요. Tavily MCP는 5회 모두 연결 실패였고, Exa는 이 세션에 연결돼 있지 않았어요 |
| 원자료 | `artifacts/design/2026-10-01-blog-redesign/refs/` (캡처 48장 + 그룹별 JSON, 로컬 전용·gitignore) |

## 2. 인기의 근거

| 대상 | 수치 | 출처 |
|---|---|---|
| WordPress | CMS 식별 사이트의 58.7%, 전체 웹의 40.2% (1년 전 60.7%) | [W3Techs](https://w3techs.com/technologies/details/cm-wordpress), [추이](https://w3techs.com/technologies/history_overview/content_management) |
| Substack | 유료 구독 500만 건 (2025-03-11) | [Substack](https://post.substack.com/p/5-million) |
| Ghost | 활성 고객 30,579, ARR $11,099,649 (2026-10-01 공개 지표) | [Ghost about](https://ghost.org/about/) |
| Medium | 2024-08 첫 흑자 전환 | [TechCrunch](https://techcrunch.com/2025/07/11/mediums-ceo-explains-what-it-took-to-stop-losing-2-6m-monthly/) |
| 네이버 블로그 | 2025년 글 3.3억 건, 순방문자 4,500만 | [네이버 보도자료](https://www.navercorp.com/media/pressReleasesDetail?seq=34202) |
| 브런치스토리 | 작가 9만 5,000여 명 (10주년) | [카카오](https://www.kakaocorp.com/page/detail/11710) |
| 한국 개발자 블로그 1,977곳 | 티스토리 24.3%, 자체 도메인 23.0%, github.io 16.8%, velog 13.4%, Medium 11.1%, 브런치 7.5%, 네이버 3.9% | [awesome-devblog db.yml](https://raw.githubusercontent.com/awesome-devblog/awesome-devblog/refs/heads/main/db.yml) 직접 집계 |
| HN 개인 블로그 역대 점수 | paulgraham 99,908 · krebsonsecurity 93,949 · simonwillison 80,897 · daringfireball 59,975 · jvns 52,289 · danluu 51,648 | [HN Popularity Contest 원데이터](https://hn-popularity.cdn.refactoringenglish.com/hn-data.csv) |
| HN 2025년 1위 | simonwillison.net (21,061점, 3년 연속 1위) | [2025 Top 5](https://refactoringenglish.com/blog/2025-hn-top-5/) |

티스토리·velog·Hashnode·dev.to는 공식 사용자 수를 공개하지 않아서 추정치를 쓰지 않았어요.

## 3. 실측 비교표

글 화면 기준이에요(프로브가 놓친 곳은 보정값). 한 줄 글자 수는 한글 1em, 라틴 0.5em을 한 글자로 잡은 근사치예요. 대비는 WCAG 2.x 비율과 APCA Lc(절댓값)예요.

| 사이트 | 분류 | 홈 형식 | 배경 | 본문색 | 대비(WCAG · Lc) | 본문 글꼴 | 크기 / 행간 | 본문 폭 | 한 줄 글자 수 | iframe |
|---|---|---|---|---|---|---|---|---|---|---|
| 브런치스토리 (brunch) | 국내 서비스·기업 | 매거진 큐레이션 | `#ffffff` | `#333333` | 12.6 · 99 | Noto Sans DemiLight | 14.67px / 2.00 | 700px | ≈48자(한글) | 차단 |
| velog | 국내 서비스·기업 | 3열 카드 피드 | `#ffffff` | `#212529` | 15.4 · 102 | -apple-system | 18px / 1.70 | 768px | ≈43자(한글) | 허용 |
| 티스토리 — 향로 ‘기억보단 기록을’ | 국내 서비스·기업 | 3열 카드 + 사이드바 | `#ffffff` | `#333333` | 12.6 · 99 | -apple-system | 16px / 1.25 | 700px | ≈44자(한글) | 허용 |
| 네이버 블로그 | 국내 서비스·기업 | 포털형 피드 | `#ffffff` | `#444444` | 9.7 · 93 | se-nanumgothic | 16px / 1.80 | 886px | ≈55자(한글) | 허용 |
| 토스 기술 블로그 (toss.tech) | 국내 서비스·기업 | 히어로 + 목록·사이드바 | `#ffffff` | `#333d4b` | 11.0 · 95 | Toss Product Sans | 17px / 1.60 | 700px | ≈41자(한글) | 허용 |
| Medium — The Airbnb Tech Blog | 해외 서비스 | 퍼블리케이션 목록(썸네일) | `#ffffff` | `#242424` | 15.5 · 102 | source-serif-pro | 20px / 1.60 | 680px | ≈68자 | 차단 |
| Substack — Lenny's Newsletter | 해외 서비스 | 뉴스레터(히어로 + 인기 글) | `#ffffff` | `#363737` | 11.9 · 97 | Spectral | 19px / 1.60 | 728px | ≈77자 | 차단 |
| Ghost (Casper 기본 테마 데모) | 해외 서비스 | 그라디언트 히어로 + 그리드 | `#ffffff` | `#15171a` | 18.0 · 105 | -apple-system | 20px / 1.45 | 720px | ≈72자 | 허용 |
| Hashnode — Town Hall | 해외 서비스 | 고정 글 + 카드 | `#ffffff` | `#364153` | 10.3 · 94 | Inter | 18px / 1.70 | 672px | ≈75자 | 허용 |
| DEV Community (Forem) | 해외 서비스 | 3단 커뮤니티 피드 | `#ffffff` | `#37352f` | 12.3 · 98 | -apple-system | 20px / 1.50 | 678px | ≈68자 | 차단 |
| Paul Graham | 해외 개인 | 제목 목록 | `#ffffff` | `#000000` | 21.0 · 106 | Verdana | 13px / normal | 435px | ≈67자 | 허용 |
| Simon Willison's Weblog | 해외 개인 | 날짜별 타임라인 + 사이드바 | `#fdfdfd` | `#000000` | 20.6 · 105 | Helvetica Neue | 16px / 1.45 | 560px | ≈70자 | 허용 |
| overreacted (Dan Abramov) | 해외 개인 | 1단 텍스트 목록 | `#ffffff` | `#222222` | 15.9 · 103 | Merriweather | 16px / 1.75 | 632px | ≈79자 | 허용 |
| Josh W. Comeau | 해외 개인 | 일러스트 히어로 + 목록 | `#ffffff` | `#0a0c10` | 19.6 · 106 | Wotfard | 18px / 1.50 | 686px | ≈76자 | 허용 |
| Lee Robinson | 해외 개인 | 소개 + 텍스트 목록 | `#ffffff` | `#282828` | 14.7 · 102 | Iowan Old Style Local | 17px / 1.60 | 600px | ≈71자 | 허용 |
| Krebs on Security | HN 역대 상위 | 전문 노출 피드 + 사이드바 | `#ffffff` | `#555555` | 7.5 · 86 | Roboto | 16.8px / 1.40 | 782px | ≈93자 | 허용 |
| Daring Fireball | HN 역대 상위 | 사이드 내비 + 좁은 본문(다크) | `#4a525a` | `#eeeeee` | 6.8 · 81 | Verdana | 12px / 1.80 | 425px | ≈71자 | 허용 |
| Julia Evans | HN 역대 상위 | 카드형 아카이브 목록 | `#ffffff` | `#000000` | 21.0 · 106 | PT Serif | 16px / 1.25 | 570px | ≈71자 | 허용 |
| Dan Luu | HN 역대 상위 | 전폭 제목 목록 | `#ffffff` | `#000000` | 21.0 · 106 | Times New Roman | 16px / normal | 1264px | ≈158자 | 허용 |
| Maggie Appleton | 개인·다크 | 디지털 가든 섹션 카드 | `#f6f5f1` | `#353534` | 11.3 · 92 | Canela Text | 22px / 2.00 | 1008px | ≈92자 | 차단 |
| DaleSeo (달레의 데브블로그) | 개인·다크 | 2열 카드 | `#ffffff` | `#1b2e46` | 13.8 · 100 | Spoqa Han Sans Neo | 18px / 1.60 | 700px | ≈39자(한글) | 허용 |
| Herman's blog (Bear Blog) | 개인·다크 | 1단 텍스트 | `#ffffff` | `#444444` | 9.7 · 93 | Verdana | 16px / 1.60 | 720px | ≈90자 | 차단 |
| Tailwind CSS Blog (다크 에뮬레이션) | 개인·다크 | 날짜 레일 타임라인 | `#030712` | `#d1d5dc` | 13.7 · 81 | Inter | 14px / 2.00 | 768px | ≈110자 | 허용 |
| The GitHub Blog | 개인·다크 | 대표 글 히어로 + 피드 | `#ffffff` | `#1f2328` | 15.8 · 103 | Mona Sans | 18px / 1.67 | 699px | ≈78자 | 차단 |

표에서 읽히는 점을 정리하면 다음과 같아요.

- 다크 배경은 WCAG 비율이 높아도 Lc가 낮게 나와요. Tailwind 다크는 13.7:1인데 Lc 81이고, Daring Fireball은 6.8:1에 Lc 81이에요. 같은 WCAG 비율의 라이트 사이트보다 실제 체감 대비가 낮다는 뜻이에요.
- 라틴 사이트의 한 줄은 대부분 67~79자로 Bringhurst 45~75자, Butterick 45~90자 범위 안에 있어요. 한글 서비스만 CJK 기준(40자)을 넘는 쪽으로 치우쳐 있어요.
- iframe 임베드는 17곳이 허용하고 7곳(브런치 DENY, Medium·Substack·dev.to·Maggie Appleton·Bear Blog·GitHub SAMEORIGIN)이 막아요. 그래서 비교 HTML은 캡처를 기본으로 보여 주고, 허용하는 곳만 라이브로 띄워요.

## 4. 읽기 타이포그래피 규약

| 규약 | 내용 | 출처 |
|---|---|---|
| WCAG 2.2 SC 1.4.8 (AAA) | 한 줄 80자 이하, CJK는 40자 이하. 줄간격 1.5 이상, 문단 간격은 줄간격의 1.5배 이상, 양끝맞춤 금지 | [W3C Understanding 1.4.8](https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html) |
| WCAG 2.2 SC 1.4.3 (AA) | 본문 대비 4.5:1, 큰 글자 3:1 | [W3C Understanding 1.4.3](https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html) |
| Bringhurst | 1단 본문 45~75자, 66자가 이상적 | [web.dev 인용](https://web.dev/learn/design/typography) |
| Butterick | 평균 45~90자 | [Practical Typography](https://practicaltypography.com/line-length.html) |
| Baymard | 50~75자, 구현은 `max-width: 약 70ch` | [Baymard](https://baymard.com/research-articles/line-length-readability) |
| W3C klreq (2026-03-21 Draft Note) | 한글 줄 나눔 단위는 글자 또는 어절, 비례 줄간격 예시 160% | [klreq](https://www.w3.org/TR/klreq/) |
| APCA | WCAG 2.x는 어두운 색의 대비를 과대평가해 다크 모드 지침으로 쓸 수 없다고 명시해요. 본문 Lc 90 권장·75 최소, 보조 텍스트 60 | [APCA in a Nutshell](https://git.apcacontrast.com/documentation/APCA_in_a_Nutshell.html) |
| 한글 웹 조판 | 한글은 베이스라인이 낮아 빽빽해 보이므로 행간을 넓게, 줄바꿈은 `word-break: keep-all` | [parksb](https://parksb.github.io/article/37.html), [lqez 2018 실측](https://lqez.github.io/blog/hangul-typo-on-web.html) |
| 세리프 vs 산세리프 | 서체 친숙도가 더 중요하고 웹 본문은 산세리프 관행이 자리 잡았어요. 한글 명조 웹폰트는 용량 부담이 커요 | [parksb](https://parksb.github.io/article/37.html) |
| Pretendard | GitHub stars 3,593, npm 월 827,312회 다운로드(2026-09) | [저장소](https://github.com/orioncactus/pretendard), [npm](https://api.npmjs.org/downloads/point/last-month/pretendard) |

lqez의 한국 사이트 실측은 2018년 자료라서, 이 노트에서는 3절의 2026-10-01 실측값을 우선해요.

## 5. 홈 형식 분류

| 형식 | 특징 | 레퍼런스 |
|---|---|---|
| 텍스트 인덱스 | 날짜와 제목만 나열하고 썸네일이 없어요. 본문 폭이 좁고 페이지가 가벼워요 | Paul Graham, Dan Luu, Bear Blog, Lee Robinson, overreacted |
| 카드 피드 | 썸네일·제목·요약·태그 카드를 1~3열로 반복해요 | velog, dev.to, Hashnode, DaleSeo, 티스토리 |
| 매거진 | 대표 글 히어로와 카테고리 내비, 큰 커버 이미지가 있어요 | Toss, GitHub 블로그, 브런치 |
| 뉴스레터·퍼블리케이션 | 구독 CTA가 레이아웃의 1급 요소예요 | Substack, Ghost, Medium 퍼블리케이션, Krebs on Security |
| 디지털 가든 | 성숙도 배지와 주제 클러스터로 묶어요 | [Maggie Appleton](https://maggieappleton.com/garden-history) |
| 독스·타임라인 | 날짜 레일과 목차 중심의 문서형 골격이에요 | Tailwind CSS 블로그, Simon Willison |

## 6. 시안에 반영한 결정

### 6.1 공통 규칙

| 결정 | 근거 |
|---|---|
| 모든 시안이 같은 역할 토큰 49개(색 20·글꼴 6·글자 12·레이아웃 4·모양 7)를 정의하고, 간격·글자 크기·움직임 스케일 25개는 공유해요 | 고른 시안을 그대로 `design/tokens.css`로 옮기기 위해서예요 (`.omp/rules/harness-design_contract.md` R1) |
| 시안 CSS에는 색·글꼴 리터럴과 미디어 쿼리 밖 px 리터럴을 쓰지 않아요. 빌드가 검사해요 | 계약 밖 리터럴 0건을 시안 단계부터 지키기 위해서예요 (R4) |
| 한글 본문은 17~18px, 행간 1.75~1.85, 한 줄 40자 이하 | 3절 실측(중앙값 약 17px, 한글 서비스 1.6~2.0)과 WCAG 1.4.8 CJK 40자, klreq 160% |
| 줄바꿈은 `word-break: keep-all` + `overflow-wrap: anywhere` | 어절 단위 줄 나눔(klreq)과 긴 URL 처리 |
| 본문색은 순흑을 피하고 강조색은 하나만 써요 | 24곳 중 20곳이 먹색 계열, 단일 강조색이 일반적 |
| 대비는 WCAG 4.5:1과 APCA Lc 75(본문)·60(보조)을 함께 통과해야 해요 | 다크 시안 2개가 있고, APCA는 다크에서 WCAG 2.x의 과대평가를 보정해요 |
| 시안마다 기본 모드는 1개예요. 계약은 라이트·다크 쌍을 모두 정의하고, 사이트 기본은 **라이트 + OS 설정 따름 + 토글 유지**예요(현행 `defaultAppearance: dark`를 바꿔요) | 사용자 결정(2026-10-01 반대 모드 포함, 2026-10-08 기본 모드) |
| 의미 없는 그라데이션을 쓰지 않아요. 빌드가 시안 CSS의 `linear-/radial-/conic-gradient`를 거부해요 | 사용자 피드백(2026-10-01) |
| 카드를 쌓는 레이아웃과 카드로 만든 메뉴를 쓰지 않아요. 글 목록은 행, 사이드 메뉴는 목록·아코디언·햄버거(`<details>`)예요 | 사용자 피드백(2026-10-01): 카드 스택은 사람들이 AI가 만든 디자인으로 가장 쉽게 인식해요 |
| AI 템플릿 요소를 걷어내요: 통계 숫자 블록, ⌘K 배지, 영문 대문자 라벨, 알약 칩. 태그는 글자 링크(`#hugo`)예요 | 사용자 결정(2026-10-01) |
| Hugo·Blowfish는 따로 드러내지 않고 푸터 크레딧만 둬요 | 사용자 결정(2026-10-01): 상용 서비스 대신 직접 구축했다는 사실이면 충분해요 |
| 썸네일은 캐릭터 시트 정본으로 만든 3:2 삽화이고 프레임은 직각이에요. 멤버는 글 속 등장인물이고 필자는 Rae 한 사람이에요 | `references/characters/_sheets/rules.md`(삽화 규격·직각 프레임), 사용자 결정(2026-10-01) |
| 삽화는 자체 밤 배경(#0F2630/#123540)을 가져서 라이트 테마에서는 어두운 판으로 보여요. 라이트 시안은 크기·캡션·여백을 고정한 판으로 다뤄요 | `rae.md` §7 미검증 TODO(라이트 모드 노출) |

### 6.2 시안별 방향 (v2, 2026-10-02 개정)

| 시안 | 형식 | 근거로 삼은 레퍼런스 |
|---|---|---|
| 1. 다크 네이비 테크 에디토리얼 | 상자 없는 대표 글(큰 표지) + 연도별 날짜 레일 목록(행 오른쪽 작은 삽화), 오른쪽은 괘선 목록·아코디언(연재·분류·태그·등장인물), 3단 글 화면(메타 레일·본문·목차) | Tailwind 블로그(날짜 레일), GitHub 블로그(대표 글 + 피드), Josh Comeau(우측 목차), DaleSeo(네이비 잉크) |
| 2. 차콜 기준선 (현행) | 현행 Blowfish `profile` 홈(테마 기본값, `hugo.yaml`에 `homepage.layout` 없음)과 기본 글 화면을 실측값으로 재현하고, 글마다 feature 이미지를 넣었을 때 Blowfish가 그리는 모습(왼쪽 300px 썸네일)을 보여 줘요. 대조군이라 카드·AI 템플릿 정리는 적용하지 않았어요 | 배포 중인 사이트(https://rae-hugo-kim.github.io/blogger/), `themes/blowfish/layouts/partials/article-link/simple.html` |
| 3. 화이트+블루 클린 리스트 | 큰 표지의 대표 글 + 가로줄로 나눈 목록(글 왼쪽·삽화 오른쪽), 밑줄 분류 탭, 오른쪽 평문 목록. v1의 3열 카드 그리드는 폐기했어요 | Toss(목록형), DaleSeo, Hashnode, velog |
| 4. 페이퍼 세리프 리딩 | 중앙 마스트헤드 + 연재 블록 + 활자 목록, 명조 본문. 삽화는 테두리·캡션을 단 고정 폭 도판으로만 써요 | 브런치, Medium, Substack, Maggie Appleton, Lee Robinson |
| 5. 미니멀 모노크롬 인덱스 | 연도별 날짜·제목 색인(행에 등장인물 글자), 장식 없는 1단. 삽화는 글 상세 표지·본문 그림과 연재 회차에만 써요 | Paul Graham, Bear Blog, Lee Robinson, overreacted, Simon Willison |

시안의 실제 값은 `artifacts/design/2026-10-01-blog-redesign/samples/<id>/tokens.css`가 원천이에요. 비교 화면은 `artifacts/design/2026-10-01-blog-redesign.html`이에요. 목업용 썸네일 7컷은 `scripts/chargen.py` 기본 auth 경로로 생성했고, 프롬프트와 원본은 `references/characters/_mock-2026-10-01/`(로컬 전용)에 있어요.

## 7. 한계와 남은 리스크

- Tavily MCP가 연결되지 않아 지시받은 2엔진 교차 확인 중 한 축을 1차 출처 직접 열람으로 대신했어요. Tavily가 복구되면 2절 플랫폼 수치를 다시 확인하는 것이 좋아요.
- 캡처는 한 시점·한 글 기준이에요. 광고, 로그인 상태, A/B 테스트에 따라 화면이 달라질 수 있어요.
- 캡처 환경에 없는 글꼴(Verdana, Times New Roman, Georgia 등)은 대체 글꼴로 렌더됐어요. 실측값의 `font-family`는 사이트가 지정한 값이에요.
- 한 줄 글자 수는 평균 글자 폭 가정에 따른 근사치예요.
- 캡처 이미지는 저작권 대상인 타사 화면이라 저장소에 올리지 않아요(`artifacts/`는 gitignore).
