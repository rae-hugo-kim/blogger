# Completion Attack Report — task 20261016-125459-7a89 (run 1)

**Date**: 2026-10-16  
**Agents**: architect (task), security-reviewer, test-engineer (task)  
**Result**: PASS (CRITICAL 0 — architect HIGH 1/MEDIUM 5, security MEDIUM 3, test-engineer HIGH 3/MEDIUM 4)

## 반영 결정

| 발견 | 처리 |
|---|---|
| [architect HIGH][test HIGH] AC6 비교표·추천 실행 로그 부재 | `.omp/evals/draft-pipeline.md` E10 행 + 실측 4축 표·추천 기록 |
| [architect MED] AC1 README 미추적 | 커밋에 `samples/README.md` 포함 |
| [architect MED] 제외 경고 문구 ≠ 알고리즘 | "(최신순 탐색, 파일 단위)" 로 수정 |
| [architect MED] out_of_scope "톤 가이드 개정" 충돌 | `docs/tone-guide.md` 변경 되돌림 — 진입점은 `samples/README.md` + 스킬 description |
| [architect MED][security MED-3] 에이전트 쓰기 범위 소프트 | 스킬 3단계에 실행 전후 `drafts/<slug>/` 파일 목록 비교 검사 추가; eval 에 E2·E3·E4·E5·E10 재실행 조건 명시 |
| [architect MED] 부분 재생성 시 프롬프트 재조립 | 누락 측만 생성할 때 기존 `prompt.md` 재사용 + 경고 (`test_build_reuses_prompt_when_regenerating_only_the_missing_side`) |
| [security MED-1] slug 경로 탈출 | `_validate_slug` (`[A-Za-z0-9][A-Za-z0-9._-]*`, `..` 금지) + CLI 테스트 6케이스 |
| [security MED-2] symlink·비UTF-8·대용량 | symlink 제외(폴더·파일), `UnicodeDecodeError` → 경로 포함 `DraftError`, 예산×4 바이트 초과 파일은 읽지 않고 제외 + 테스트 3건 |
| [test HIGH] 가이드 부재·인코딩·categories 타입 → raw traceback | `_read_guide`, `_categories` 로 `DraftError` 변환 + 테스트 |
| [test HIGH] 깨진 date 무경고 폴백 | `_sample_sort_at` 가 warnings 에 파일명 기록 + 테스트 |
| [test MED] 코드펜스 헤딩·헤딩 0개 | 펜스 제외 테스트, 헤딩 0개 → `DraftError` + 테스트 |
| [test MED] AC1 자동 가드 없음 | 미반영 — git 상태 확인으로 충분 (README 1건) |

재검증: `python3 -m pytest tests/ -q` → 107 passed (신규 42).

---

## 원문

### Architect

## GATE 3.5 Architect 공격 — seed.yaml 대비 누락 점검

검증 실행: `python3 -m pytest tests/test_step4_draft_prompt.py -q` → **28 passed in 0.42s**.

### AC별 판정 (7개)

| AC | 요구 | 증거 | 판정 |
|---|---|---|---|
| AC1 | `samples/` gitignore + `README.md`만 추적 | `.gitignore:8-9` (`samples/*`, `!samples/README.md`), `git check-ignore -v samples/작업노트/x.md` → `:8` 적중 / `samples/README.md` → `:9` 부정 매치, `git add -An samples/` → `add 'samples/README.md'` 단 1건. 단 `git ls-files samples/` 는 현재 공집합 | 조건부 충족 (F1) |
| AC2 | 톤 매핑 + pytest | `scripts/draft_prompt.py:34-46` (`TONE_TABLE` 에세이/특허/리딩노트, `DEFAULT_TONE`=작업노트·tone-tech), `tests/…:74 test_resolve_tone_follows_tone_guide_table` (파라미터 6종) | 충족 |
| AC3 | 빈 폴더·0편 종료, 최신순 파일 단위 절단 + 제외 경고 | `draft_prompt.py:162-192` (폴더 없음/빈 폴더 `DraftError`, 0편 `DraftError`, 파일 단위 제외, `warnings` 기록), 테스트 `:81, :98, :108, :129, :139, :149, :158` | 충족 (경고 문구만 F3) |
| AC4 | 양쪽 존재 중단 / `--force` 덮어쓰기 / 한쪽만 누락 측 | `draft_prompt.py:238-247`, 테스트 `:168, :172, :179, :184, :265`, 실측 `.omp/evals/draft-pipeline.md:25` (E7 PASS, sha256 불변) | 충족 |
| AC5 | 실제 실행으로 두 초안 생성, categories·`draft:true`, 헤딩마다 산문 | `drafts/smoke-draft/.draft/draft-{argon,fable}.md` 프런트매터 `categories: ["작업노트"]` + `draft: true`, 헤딩 4개 동일 순서(`## 왜 또…/어떻게…/삽질 기록/다음`), eval `:22-23` (E4·E5 PASS, 단락 수 기록) | 충족 |
| AC6 | 종료 시 차이 요약표(구조·톤·샘플 유사도, 문장 근거) + 추천 / 부분 실패 경고 | 절차는 `.omp/skills/draft/SKILL.md:62-73`, 부분 실패 실측은 eval `:26` (E8 PASS). **요약표·추천의 실행 로그는 어떤 산출물에도 없음** — eval 표(17-27행)에 해당 행 없고 `:31-33` 은 서술형 "관찰"뿐 | 부분 충족 (F2) |
| AC7 | 지시문 삽입 샘플이 자료 구획 안에 머묾 + eval 기록 + pytest | `draft_prompt.py:207-213` (`<<<`→전각 치환), `tests/…:226 test_assemble_keeps_injected_sample_inside_the_samples_section`, eval `:19-21` (E1·E2·E3 PASS, 삽입 문구 명시) | 충족 |

### constraint별 판정 (12개)

| # | constraint (seed 행) | 증거 | 위반 |
|---|---|---|---|
| 1 | CI 미실행, `/skill:draft` 로만 (`:12`) | `.github/workflows/` 는 `deploy.yml` 1개뿐이고 `draft_prompt`·`samples` 참조 0건, `SKILL.md:4` "Local only — never from CI" | 없음 |
| 2 | `index.md` 자동 생성 금지 (`:13`) | `SKILL.md:25, 71, 79`, 코드에 `index.md` 쓰기 경로 없음 | 없음 |
| 3 | 자동 게시 없음 (`:14`) | 에이전트가 `draft: true` 기입 (`drafter-argon.md:18`), 스모크 산출물 프런트매터 확인 | 없음 |
| 4 | 파이프라인 파일 전부 `.draft/` (`:15`) | `draft_prompt.py:254, 272-273` (`draft_dir = root/drafts/slug/.draft`), `SKILL.md:24`, `normalize.py:199-204` dot-엔트리 제외, eval `:27` (E9 PASS) | 없음 |
| 5 | samples 본문 미추적 + README에 저자 원본만 (`:16`) | `.gitignore:8-9`, `samples/README.md:19-20` ("AI 정제본·퇴고본 … 넣지 말 것") | 없음 (F1 별건) |
| 6 | 모델 `model:` 프런트매터 고정 (`:17`) | `drafter-argon.md:4` `gemini-4-argon`, `drafter-fable.md:4` `claude-fable-5-1`, eval `:24` (E6 실측 PASS) | 없음 |
| 7 | 톤 매핑 = tone-guide 표, 복수는 표 순서 (`:18`) | `TONE_TABLE` 순서(에세이→특허→리딩노트) == `docs/tone-guide.md:13-16` 행 순서, `resolve_tone:42-46` 첫 매칭 | 없음 |
| 8 | "교정만" 은 퇴고 단계 규칙임을 명시 (`:19`) | `drafter-argon.md:20` / `drafter-fable.md:20` ("…describe the later editing stage; in this drafting stage you are expected to expand bullets into prose"), eval `:33` 실측 | 없음 |
| 9 | 자료 구획 조립 + 쓰기 대상 1개 제한 (`:20`) | `PROMPT_HEADER:200-204`, `_section/_escape:207-213`, 에이전트 `:23, :28` | 없음, 단 강제력 소프트 (F5) |
| 10 | 전체 입력 예산·안전 여유·파일 단위 절단·정렬 (`:21`) | `:51-66` (600k, ÷2, 20% 여유, 출력 여유 40k, 고정비 차감 시 `DraftError`), `:174` 정렬 `(sort_at, name)` reverse | 없음, 경고 문구만 F3 |
| 11 | 양쪽 존재 중단 / `--force` / 한쪽만 누락 측 (`:22`) | `plan_outputs:238-247` + 테스트 4건 | 없음 |
| 12 | 결정적 Python + pytest (`:23`) | `scripts/draft_prompt.py` (AI 호출 0), pytest 28건 통과 | 없음 |

### out_of_scope 점검 (5개)

| 항목 | 상태 |
|---|---|
| 두 초안 병합 | 미구현 — `SKILL.md:79` 에서 명시적 제외 ✓ |
| 외부 원본 수집 자동화 | 미구현, `samples/README.md:19` 가 수동 투입 명시 ✓ |
| 톤 가이드 개정 | **`docs/tone-guide.md` 에 섹션 추가됨** (F4) |
| `scripts/normalize.py` 변경 | `git status --porcelain` 에 미등장 = 무변경 ✓ |
| CI에서의 AI 생성 | 워크플로 변경 없음 ✓ |

### 발견 목록

**[HIGH] AC6의 "차이 요약표 + 추천" 실행 로그가 영속 산출물에 없습니다**
- 근거: `.omp/evals/draft-pipeline.md:17-27` 의 케이스 표는 E1–E9 중 AC6 비교·추천 행이 없고, 기록은 `:31-33` "관찰 (판정 외)" 의 서술 3줄뿐입니다. seed `:31` 은 "구조·톤·샘플 유사도, 문장 근거 포함" 표와 추천을 요구하고, `docs/harness/test-plan.md:40` 은 체크만 되어 있습니다. 부분 실패 쪽(E8)만 실측 증거가 있습니다.
- 수정: eval 문서에 실제 출력한 4축 비교표와 추천 문장(초안 인용 포함)을 E10 행으로 붙여 넣으세요.

**[MEDIUM] AC1의 "추적된다"가 아직 미성립입니다**
- 근거: `git ls-files samples/` 공집합, `git status --porcelain` 에 `?? samples/`. ignore 규칙은 정확해 `git add -An samples/` 가 `samples/README.md` 한 건만 추가합니다.
- 수정: 커밋에 `samples/README.md` 를 포함해 AC1 을 실제 git 상태로 입증하세요.

**[MEDIUM] 제외 경고 문구가 실제 알고리즘과 다릅니다**
- 근거: `scripts/draft_prompt.py:183-185` 는 "예산 초과로 N편 제외 (오래된 순, 파일 단위)" 라고 쓰지만, `:177-182` 는 최신순 순회 중 남은 예산에 들어가면 담는 greedy 라서 큰 최신 글이 빠지고 더 오래된 작은 글이 남을 수 있습니다.
- 수정: 문구를 "예산 초과로 제외(파일 단위)" 로 바꾸거나, 제외를 오래된 순으로 확정하도록 선택 로직을 바꾸세요.

**[MEDIUM] out_of_scope "톤 가이드 개정" 항목과 `docs/tone-guide.md` 변경이 충돌합니다**
- 근거: `git diff docs/tone-guide.md` 는 `:30-36` "얼개에서 초안 생성 (`/skill:draft`)" 섹션 추가 1건(순수 add)이며, 매핑 표(`:11-16`)·퇴고 규칙은 무변경입니다. seed `:37` 은 `docs/tone-*.md` 개정을 범위 밖으로 두었습니다.
- 수정: 입구 문서를 `samples/README.md` 로만 두거나, 이 추가가 "정본 매핑 불변 + 포인터 추가"임을 seed/스코프 문서에 1줄로 예외 기록하세요.

**[MEDIUM] 에이전트 쓰기 대상 제한이 프롬프트 문장뿐입니다**
- 근거: `.omp/agents/drafter-argon.md:6` `tools: read, write` 는 경로 제약이 없고, 제한은 `:23, :28` 의 자연어 지시입니다(fable 동일). seed `:20` 은 "쓰기 대상을 … 하나로 제한한다"를 요구하며, 현재 보증은 eval `:20-21` (E2·E3) 의 1회 실측뿐입니다.
- 수정: eval 문서에 "프롬프트 표면 변경 시 E2·E3 재실행 필수"를 회귀 조건으로 고정하고(현재 `:3-5` 문구를 케이스 번호까지 명시), 재실행 결과를 run 날짜와 함께 누적하세요.

**[MEDIUM] 부분 실패 복구 시 프롬프트 재조립 비용이 계약에 없습니다**
- 근거: `draft_prompt.py:270-274` 는 `plan_outputs` 가 누락 측만 돌려줘도 `prompt.md` 를 무조건 다시 씁니다. 그 사이 `samples/` 가 바뀌면 두 초안이 서로 다른 입력으로 만들어지는데, `SKILL.md:62` 의 비교는 동일 입력 쌍을 전제합니다(`plan-attack-report.md:34` 의 "같은 입력으로 실행해 성공한 쌍일 때만 비교" 권고).
- 수정: 재실행이 누락 측만 생성할 때는 기존 `prompt.md` 를 재사용하거나, 재조립 시 "입력이 바뀌었을 수 있음" 경고를 `warnings` 에 넣으세요.

누락된 AC 구현·테스트는 없습니다. CRITICAL 0건이라 게이트 차단 사유는 없습니다.

RESULT: PASS

### Security reviewer

보안 리뷰 결과예요. CRITICAL은 없고 MEDIUM 3건이에요. 조립 단계의 구획 격리와 게시 유출 차단은 견고하지만, slug 경로 검증과 samples/ 심볼릭 링크 처리, 에이전트 쓰기 범위의 기술적 강제가 빠져 있어요.

## 점검 결과

### (a) 프롬프트 주입 — 이상 없음
- `scripts/draft_prompt.py:214-220` `_escape` 가 `<<<` 를 전각으로 치환하고, `_section` 이 본문 전체(샘플 파일명 헤더 `### sample: <name>` 포함)에 적용해요. `str.replace` 는 좌→우 비중첩 치환이라 치환 후 ASCII `<` 가 연속 3개 남을 수 없고, `_SECTION_RE` 는 `[a-z-]+` 이름의 ASCII 마커만 인식해요. 역변환(전각→ASCII) 코드는 어디에도 없어요.
- 파일명에 개행·마커를 넣어도 `sample_blocks` 전체가 `_escape` 를 거치므로 구획 탈출이 안 돼요. `### sample:` 헤더 위조는 가능하지만 samples 구획 안에 머무르는 표시용 문자열이라 영향이 없어요.
- outline 프런트매터는 `yaml.safe_load`(`:85`)로 파싱해요.

### (d) 게시 유출 — 이상 없음
- `.gitignore:6` `drafts/` 전체 비추적 → 샘플 전문이 복사된 `.draft/prompt.md` 도 git에 안 들어가요. `samples/*` + `!samples/README.md` 규칙도 정확해요.
- `scripts/normalize.py:189,199-204` 가 dot-엔트리와 symlink를 전 깊이에서 제외해요. 평가 E9 로 확인돼 있어요.

## 발견 목록

### MEDIUM-1. slug 경로 검증 없음 — 번들 밖 읽기·쓰기
- 근거: `scripts/draft_prompt.py:256` `draft_dir = root / "drafts" / slug / ".draft"`. pathlib 는 `..` 를 정규화하지 않고, 절대경로 결합 시 앞부분을 버려요. `main()` 의 `slug` 인자에 어떤 검증도 없고 `tests/test_step4_draft_prompt.py` 에 관련 케이스가 없어요.
- 영향: `prompt.md`(`:270`)가 레포 밖에 쓰이고, 스킬 2단계가 그 경로를 PROMPT/OUTPUT 로 에이전트에 넘겨 `draft-*.md` 도 레포 밖에 생성돼요. "모든 산출물은 `.draft/` 아래" 제약(seed constraints 4번째)이 깨져요.
- 재현(실행하지 않았어요, `[INFERENCE]`):
  ```bash
  mkdir -p /tmp/x/.draft && printf -- '---\ncategories: [작업노트]\n---\n# h\n- b\n' > /tmp/x/.draft/outline.md
  python3 scripts/draft_prompt.py /tmp/x        # → /tmp/x/.draft/prompt.md 생성
  python3 scripts/draft_prompt.py ../../tmp/x   # 동일
  ```
- 수정 한 줄: `build()` 진입 시 `slug` 에 `/`·`\`·`..`·선행 `.` 을 거부하거나, `draft_dir.resolve().is_relative_to((root / "drafts").resolve())` 를 확인하고 아니면 `DraftError`.

### MEDIUM-2. samples/ 심볼릭 링크를 따라가 임의 로컬 파일을 외부 모델 2곳으로 전송
- 근거: `scripts/draft_prompt.py:165-166` `p.is_file() and p.suffix == ".md"` — `is_file()` 은 symlink 를 따라가요. `normalize.py:189,203` 은 같은 위협모델에서 symlink 를 명시 제외하는데, 여기는 그 선례를 따르지 않았어요. 폴더(`samples/작업노트`) 자체가 symlink 인 경우도 `is_dir()`(`:162`)가 통과시켜요.
- 영향: `~/.ssh/id_ed25519` 같은 파일을 `.md` 이름의 링크로 넣으면 본문이 `prompt.md` 에 들어가 gemini·claude 양쪽에 전송돼요. 저자 로컬 디렉터리라 공격자 모델은 약하지만, 코퍼스를 외부에서 받아 넣는 흐름(seed out_of_scope "사용자가 md로 모아 넣는다")이 있어 우발 유출 경로가 돼요.
- 재현: `ln -s ~/.ssh/id_ed25519 samples/작업노트/zz-key.md && python3 scripts/draft_prompt.py smoke-draft --force && grep -c 'PRIVATE KEY' drafts/smoke-draft/.draft/prompt.md`
- 수정 한 줄: `:165` 필터에 `not p.is_symlink()` 를 추가하고, 비-UTF-8 파일은 `UnicodeDecodeError` 를 `DraftError` 로 감싸요(현재는 트레이스백으로 종료, `:171`). 부수적으로 예산 비교 전에 `read_text` 로 전체를 읽으므로(`:171`) 수 GB 파일은 메모리를 소진해요 — `p.stat().st_size > budget_chars*4` 면 읽지 않고 제외하면 돼요.

### MEDIUM-3. 에이전트 쓰기 범위가 프롬프트 수준으로만 제한됨
- 근거: `.omp/agents/drafter-argon.md:6`, `drafter-fable.md:6` `tools: read, write` — 경로 제한 메커니즘이 없어요(`.omp/` 전체에 `allowedPaths`/sandbox 류 설정 없음, `.omp/hooks/` 미존재). 쓰기 제한은 `<Constraints>` 의 "write only the OUTPUT path" 한 줄에 의존해요.
- 영향: 샘플·얼개 주입이 모델을 설득하면 `drafts/<slug>/index.md`(자동 게시 금지 제약)나 `content/posts/` 에 쓸 수 있어요. 평가 E2·E3 은 두 모델이 현재 거부함을 보였지만 모델·프롬프트 변경 시 재발 가능하고, 스킬 3단계 검사는 OUTPUT 파일만 보고 다른 경로 생성 여부는 확인하지 않아요.
- 재현: `.omp/evals/draft-pipeline.md` E2 절차(`zz-injection-probe.md`) 그대로.
- 수정 한 줄: 스킬 3단계 검사에 "`drafts/<slug>/` 하위 신규 파일이 `.draft/draft-*.md` 외에 있으면 해당 대상 실패 + 경고" 를 추가하고(`git status --porcelain drafts/<slug>` 또는 실행 전후 `ls` 비교), 가능하면 OMP 쓰기 훅으로 `drafts/*/.draft/draft-*.md` 외 경로 거부를 강제해요.

## 검토 범위
`scripts/draft_prompt.py` 전체(1–308), `.omp/agents/drafter-{argon,fable}.md`, `.omp/skills/draft/SKILL.md`, `.gitignore`, `scripts/normalize.py:188-222`, `.omp/evals/draft-pipeline.md`, `docs/harness/seed.yaml`, `tests/test_step4_draft_prompt.py`(traversal/symlink 케이스 부재 확인). 파일 편집·명령 실행은 하지 않았어요.

RESULT: PASS

### Test engineer

# 테스트 커버리지 공격 — task 20261016-125459-7a89

**실행 결과**: `python3 -m pytest tests/test_step4_draft_prompt.py -q` → **28 passed** (0.43s), 전체 스위트 `python3 -m pytest -q` → **93 passed** (2.49s). 실패 0.

## 1. test-plan ↔ 테스트/스모크 매핑

| # | test-plan 항목 | 대응 테스트 / 스모크 | 판정 |
|---|---|---|---|
| L8–9 | 모델 식별 프로브 argon·fable | `.omp/evals/draft-pipeline.md:24` (E6) | ○ |
| L19 | `resolve_tone` 6케이스 | `tests/…:66-76` parametrize 6건 | ○ |
| L20 | 정렬 date→mtime→파일명 역순 | `tests/…:81` `test_select_samples_orders_by_date_then_mtime_then_name_desc` | ○ |
| L21 | 예산 초과 제외 + warnings | `tests/…:108` `…drops_oldest_when_over_budget_and_warns` | ○ |
| L22 | 단일 초과 파일은 파일 단위 제외 | `tests/…:139` `…excludes_oversized_file_whole_never_truncates` | ○ |
| L23 | 폴더 없음/빈 폴더 → `DraftError` | `tests/…:158` `…missing_or_empty_folder_is_an_error` | ○ |
| L23 | **전부 제외돼 0편 → `DraftError`** | `tests/…:136` (budget 49 → raises)에서 **간접**만. 예외 메시지("전부 초과")를 구분하지 않아 빈 폴더 분기와 동일 판정 | △ |
| L24 | `plan_outputs` 4케이스 | `tests/…:168,172,179,184` | ○ |
| L25 | `parse_outline` 없음/깨짐/헤딩 추출 | `tests/…:192,209,217` | ○ |
| L26 | `assemble` 구획 4개 + 주입 격리 | `tests/…:226` + eval E1 | ○ |
| L27 | 혼합 date 표현 정렬 | `tests/…:98` `…handles_mixed_date_representations` | ○ |
| L28 | `sample_budget_chars` 차감·소진 | `tests/…:121` | ○ |
| L29 | 닫는 `---` 누락·최상위 목록 | `tests/…:198-206` parametrize 2건 | ○ |
| L30 | CLI `--budget-tokens 10` | `tests/…:283` | ○ |
| L31 | CLI 생성 + JSON 필드 + 오류 | `tests/…:253,265,276` | ○ |
| L34 | 얼개가 `.draft/` 밖 | `tests/…:209` (`match=r"\.draft/outline\.md"`) | ○ |
| L35 | 예산 경계 포함/초과 | `tests/…:129` (단일) + `:108` (합 = size×2 포함) | ○ |
| L36 | non-`.md`·dot-파일 무시 | `tests/…:149` | ○ |
| L39 | 스모크 생성·프런트매터·헤딩 산문 | eval E4, E5 | ○ |
| L40 | **차이 요약표 + 추천 출력** | eval 표 E1–E9 중 **대응 케이스 없음** (E8은 부분 실패만) | ✗ |
| L41 | 부분 실패 | eval E8 | ○ |
| L42 | 출력 보호 실측(sha256) | eval E7 | ○ |
| L43 | 에이전트 행동 경계 | eval E2, E3 | ○ |
| L44 | 게시 제외(`.draft/`) | eval E9 + 자동 일반화: `tests/test_step2_pipeline.py:497` | ○ |
| AC1 | samples gitignore + README | 자동 테스트·eval 기록 **없음** (수동 git 확인만) | △ |

## 2. 미테스트 분기 (`scripts/draft_prompt.py`)

실제로 임시 레포를 만들어 각 분기를 실행해 확인했습니다(프로브는 `/tmp`에서 돌리고 삭제, 레포 파일 무변경).

### HIGH — AC6 전반부(차이 요약표·추천)의 기록된 증거가 레포에 없음
- 증거: `docs/harness/test-plan.md:40`은 "종료 시 차이 요약표 + 추천 출력(AC6)"을 체크했지만, 유일한 기록물인 `.omp/evals/draft-pipeline.md`의 케이스 표(E1–E9)에 해당 행이 없습니다. E8(`:26`)은 "비교 생략 + 부분 실패 경고"만 판정하고, 비교 내용은 "관찰 (판정 외)"(`:29-33`)에 서술로만 남아 있습니다. 스킬 계약은 `.omp/skills/draft/SKILL.md:62,71`에 정의돼 있습니다.
- 한 줄 수정: eval 표에 `E10 | 둘 다 성공 시 비교표+추천 | 표 4행·인용 포함·추천 1편 | 세션 출력 | PASS` 행을 추가하고 실제 출력 발췌를 붙입니다.

### HIGH — `DraftError` 아닌 예외 3분기가 미테스트이며 raw traceback으로 종료
- 증거(실측, exit=1이지만 안내 메시지 없음):
  - 가이드 파일 부재 → `scripts/draft_prompt.py:263-264`의 `read_text` → `FileNotFoundError: … docs/tone-tech.md`
  - 샘플 인코딩 오류(비-UTF-8 1편) → `scripts/draft_prompt.py:172`의 `p.read_text(encoding="utf-8")` → `UnicodeDecodeError: … byte 0xff in position 25` (**어느 파일인지 메시지에 없음**; `samples/`는 사용자가 수동으로 채우는 untracked 코퍼스라 cp949 유입 확률이 실질적입니다)
  - `categories: 3`(비문자열 스칼라) → `scripts/draft_prompt.py:261`의 `list(categories)` → `TypeError: 'int' object is not iterable`
- 한 줄 수정: 세 지점을 `try/except (OSError, UnicodeDecodeError, TypeError)`로 감싸 경로를 포함한 `DraftError`로 변환하고, 각 케이스에 CLI 테스트(exit≠0 + stderr에 파일 경로)를 추가합니다.

### HIGH — 깨진 `date` 문자열이 무경고로 mtime 폴백 → 최신순 계약 왜곡
- 증거: `scripts/draft_prompt.py:144`의 `except ValueError: return None` 분기가 테스트에 없습니다(`tests/…:98`은 정상 표현 4종만). 실측: `date: 어제`인 샘플이 mtime(2026-10-16)으로 승격돼 `date: 2026-01-01` 샘플보다 **앞선 1위**로 정렬됐고 `warnings`는 비어 있었습니다. AC3(`seed.yaml:28`)의 "최신순(date → 없으면 mtime)"은 "date가 있으나 깨진" 경우를 정의하지 않습니다.
- 한 줄 수정: `_sample_sort_at`에서 파싱 실패 시 `SampleSelection.warnings`에 파일명을 남기고, 해당 케이스 단위 테스트를 추가합니다.

### MEDIUM — `categories` 정규화 분기(`str`/`dict`) 미테스트
- 증거: `scripts/draft_prompt.py:260-262`의 `isinstance(categories, str)` 분기를 타는 테스트가 없습니다(단위 테스트는 `resolve_tone`에 리스트만 전달, CLI 픽스처 `tests/…:53-54`도 리스트). 실측: `categories: 에세이` → 정상(`tone=에세이`), `categories: {a: b}` → 조용히 키 목록으로 변환돼 기본 톤으로 처리됩니다(`{에세이: null}`이면 에세이로 매칭).
- 한 줄 수정: `build()` 레벨(또는 CLI) 테스트에 스칼라 `categories` 케이스를 추가하고, 매핑 타입은 `DraftError`로 거부합니다.

### MEDIUM — 코드펜스 내 헤딩 제외(`_CODE_BLOCK_RE`)가 미테스트
- 증거: `scripts/draft_prompt.py:72,111`이 코드블록을 제거한 뒤 헤딩을 뽑지만, 얼개에 펜스를 넣은 테스트가 없습니다(`tests/…:192`는 펜스 없는 얼개). 실측: 펜스 안 `## 코드 안 헤딩`만 있는 얼개는 `headings: []`로 통과합니다.
- 한 줄 수정: `test_parse_outline_extracts_frontmatter_and_headings`에 펜스 안 가짜 헤딩을 넣고 제외를 단언합니다.

### MEDIUM — 헤딩 0개 얼개가 경고 없이 통과
- 증거: `scripts/draft_prompt.py:111-112`는 `headings`가 비어도 통과시키고 `build()` 요약(`:270`)에 `headings: []`만 남깁니다. AC5(`seed.yaml:30`)의 "모든 헤딩 아래 산문" 판정이 공집합으로 자동 성립합니다. 해당 테스트 없음.
- 한 줄 수정: 헤딩 0개면 `DraftError`(또는 warnings)로 표면화하고 테스트를 추가합니다.

### MEDIUM — AC1(samples gitignore)에 자동 가드 없음
- 증거: `docs/harness/test-plan.md:49`가 수동 git 명령으로만 매핑하고, eval에도 기록이 없습니다. 제가 실측한 현재 상태는 정상입니다 — `git check-ignore -v samples/작업노트/x.md` → `.gitignore:8:samples/*`, `samples/README.md`는 `.gitignore:9:!samples/README.md`로 비무시, `git add -An samples/` → `add 'samples/README.md'` 단 1건. 즉 **현 상태는 AC1 충족**이고, 빠진 것은 회귀 가드입니다(실패 시 저자 원본 코퍼스가 공개 레포로 유입).
- 한 줄 수정: `subprocess`로 `git check-ignore`를 호출해 "본문 무시 + README 비무시"를 단언하는 pytest 1건을 추가합니다.

### MEDIUM — `--budget-tokens` 음수/0에 대한 입력 검증·테스트 없음
- 증거: `--budget-tokens -5` 실행 시 `sample_budget_chars`(`scripts/draft_prompt.py:58-66`)가 `사용 가능 -8자…` 같은 혼란스러운 문구로 실패합니다. argparse 수준 검증과 테스트가 없습니다.
- 한 줄 수정: `type=` 검증으로 양수만 허용하고 거부 테스트를 추가합니다.

### MEDIUM — `select_samples` 0편 분기와 빈 폴더 분기가 테스트에서 구분되지 않음
- 증거: `tests/…:136`은 `pytest.raises(dp.DraftError)`만 확인해 `scripts/draft_prompt.py:187-191`("전부 초과")인지 `:167`("폴더가 비어 있음")인지 가릴 수 없습니다. test-plan L23은 두 경로를 별개로 주장합니다.
- 한 줄 수정: `match="전부 초과"` / `match="비어 있음"`으로 메시지를 고정합니다.

### MEDIUM — `.draft/` 이름 특정 게시 제외 회귀 테스트 없음
- 증거: 자동 가드는 `tests/test_step2_pipeline.py:494-523`의 일반 dot-엔트리 테스트뿐이고(`.omc`, `.DS_Store`, 중첩), `seed.yaml:15`가 명시한 `.draft/`는 eval E9의 1회 수동 실행(`.omp/evals/draft-pipeline.md:27`)으로만 확인됩니다.
- 한 줄 수정: `TestAssetHygiene`에 `.draft/{outline,prompt,draft-argon}.md` 번들을 넣어 미복사를 단언하는 케이스를 추가합니다.

## 3. 공격 결론

CRITICAL 0건입니다. 미테스트 분기는 모두 ① 종료 코드 ≠ 0으로 실패하거나(가이드 부재·인코딩·타입 오류) ② 기존 파일을 건드리지 않은 채 조용히 열화되는(정렬 왜곡·헤딩 0개) 유형으로, 데이터 손실이나 출력 보호 우회로 이어지지 않습니다 — 쓰기(`scripts/draft_prompt.py:266-267`)는 모든 검증 뒤에 한 번만 일어나고, `test_cli_fails_when_fixed_cost_exhausts_total_budget`가 실패 시 `prompt.md` 미생성을 고정합니다. AC1–AC7은 전부 통과한 증거에 매핑되며, 유일한 증거 공백(AC6 전반부)은 기록 누락이지 구현 결함이 아닙니다.

RESULT: PASS
---

## 3-pass 코드 리뷰 (reviewer, 2026-10-16)

- Run 1 (`docs/reviews/review-2026-10-16-193753.*`, hash e4cd7e84…): PASS WITH NOTES — HIGH 3 / MEDIUM 4 / LOW 7. 이질성 실측: adversary = openai-codex/gpt-6-astra.
- HIGH 3건 전부 반영 후 재리뷰 (아래 run 2): (1) `outline.md`·`prompt.md` symlink 거부, (2) 부분 재생성 시 `prompt.md` 부재면 `--force` 요구, (3) 달력 밖 날짜(`ValueError`)·`OSError` 를 `DraftError` 로 변환. 테스트 5건 추가 (`reviewer HIGH 반영` 절), 전체 112 passed.
- MEDIUM 4건 처리: 스킬 3단계 파일 목록 비교가 병렬 배치·내용 변경을 못 잡음 → 후속(스킬 문구는 실행 전후 목록 비교로 유지, 내용 해시 비교는 다음 사이클); 재사용 프롬프트와 JSON `headings/tone` 불일치 가능 → `--force` 요구로 입력 동일성 전제 강화(완전 해결 아님, 후속); 검사 실패 파일 보존 → 재시도가 `plan_outputs` 에 막힘 → 스킬 §4 안내대로 `--force` 사용(의도된 보호); `MODEL:` 식별자 접두사 표기 불일치 → 스킬 3단계는 접미 일치로 판정.
- Run 2 (`docs/reviews/review-2026-10-16-194854.*`, hash 35bd507a…): PASS WITH NOTES — HIGH 1 / MEDIUM 3. HIGH #2 해결, #1·#3 부분 해결로 판정.

## 잔여 (문서화된 미해결, 다음 사이클)
- [HIGH] `drafts/<slug>`·`.draft` 상위 디렉터리와 `draft-*.md` 자체가 symlink 인 경우 미검사 — `drafts/` 는 git 미추적 로컬 폴더라 자해성 케이스로 보고 보류. 보강 시 `draft_dir.resolve()` 가 `(root/"drafts").resolve()` 아래인지 확인하고 `plan_outputs` 에서 링크를 거부.
- [MEDIUM] `prompt.md` 쓰기·샘플 읽기의 `OSError` 가 `DraftError` 로 변환되지 않음(환경 장애 시 traceback).
- [MEDIUM] `date: !!timestamp not-a-date` 가 PyYAML 에서 `AttributeError` 로 새어 나옴.
- [MEDIUM] `test_build_partial_regeneration_without_prompt_requires_force` 가 `prompt.md` 미생성까지는 단언하지 않음.
- [하네스] `node --test .omp/extensions/harness/tests/harness-wiring.test.mjs` W3 가 소비자 에이전트(`.omp/agents/drafter-*.md`)를 화이트리스트 미등재로 실패 — 하네스 테스트의 소비자 레포 가드 누락. 상류(rae-hugo-kim/omp) 이슈 대상이며 커밋 게이트는 이 스위트를 실행하지 않음.
