# 캐릭터시트 (characters)

블로그에서 재사용하는 나·팀원 캐릭터의 설정 문서를 모아두는 곳이에요.
이 폴더는 **로컬 전용**이에요 (`.gitignore`, public repo 노출 방지) — README만 규칙 문서로 추적돼요.

## 무엇을 두나요

| 위치 | 내용 | git 추적 |
|---|---|---|
| `docs/characters/rules.md` | 세트 공통 생성 규칙 (헌법: 팔레트·스타일·금지 요소·생성 목록) | X (로컬 전용) |
| `docs/characters/<슬러그>.md` | 캐릭터당 1파일 (`rae` `bob` `chan` `josh`) — 컨셉, 스펙, 생성 프롬프트, 네거티브 | X (로컬 전용) |
| `assets/img/characters/<슬러그>/` | 채택 확정된 이미지 (모든 글에서 재사용 — 블로그에 공개됨) | O |
| `references/characters/<슬러그>/` | 생성 후보·원본 덤프 | X (로컬 전용) |

## 이미지 참조 방법

Blowfish 렌더 훅이 `페이지 번들 → assets/` 순으로 이미지를 찾으므로,
`assets/img/characters/rae/portrait.png`는 어느 글에서든 아래처럼 참조해요:

```markdown
![rae](img/characters/rae/portrait.png)
```

## 규칙

- 파일·폴더명은 ASCII 슬러그로 고정해요 (`rae`, `portrait.png`). 여러 글이 참조하므로 이름 변경은 링크 전수 수정과 함께.
- 시트는 git에 안 올라가므로 **백업이 없어요**. 원본(외부 작업 문서)을 마스터로 유지하거나 별도 비공개 백업을 두세요.
- `assets/img/characters/`에 승격한 이미지는 repo와 블로그 양쪽에 **공개**돼요. 승격 전에 공개 가능 여부를 확인하세요.
- 생성 후보는 `references/characters/<슬러그>/`에 쌓고, 채택본만 `assets/img/characters/<슬러그>/`로 승격해요.
