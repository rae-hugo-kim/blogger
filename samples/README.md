# samples/ — 저자 글 코퍼스 (git 미추적)

`/skill:draft` 가 초안을 쓸 때 "내 글답게" 쓰도록 모델에 통째로 넣는 샘플이에요.
이 README만 추적되고 나머지는 `.gitignore` 대상이에요 (`samples/*`, `!samples/README.md`).

## 폴더 = 톤

`docs/tone-guide.md` 의 categories → 문체 표와 같은 이름이에요. 얼개(`.draft/outline.md`)의
`categories` 로 폴더 하나가 골라지고, 그 폴더의 `.md` 전부가 투입돼요.

| 폴더 | 얼개 categories | 문체 가이드 |
|---|---|---|
| `samples/에세이/` | `에세이`, `특허` | `docs/tone-essay.md` |
| `samples/리딩노트/` | `리딩노트` | `docs/tone-note.md` |
| `samples/작업노트/` | `작업노트`, 미지정, 그 외 | `docs/tone-tech.md` |

## 넣을 것 / 넣지 말 것

- 넣을 것: 직접 쓴 원본 글 (fmkorea 연재분, 황견적 개발일지, 이세계 표류기, 과거 블로그 글 등). 파일당 한 편, `.md`.
- 넣지 말 것: AI 정제본·퇴고본(`drafts/archive/` 의 refine 산출물 등). 문체가 오염돼요.
- dot-파일과 `.md` 가 아닌 파일은 무시돼요.

## 프런트매터 (선택)

```yaml
---
date: 2025-03-14      # 있으면 최신순 정렬에 사용, 없으면 파일 mtime
---
```

예산(기본 600k 토큰, 문자 수 ÷ 2 근사, 20% 여유)을 넘으면 오래된 글부터 파일 단위로
빠지고 실행 로그에 제외 편수가 찍혀요. 본문 중간 절단은 하지 않아요.
