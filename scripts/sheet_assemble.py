"""Reference character sheet assembler.

생성된 부품 컷(정본/후면/표정/클린)을 한 장의 레퍼런스 시트로 조립한다.
팔레트 스와치·소품 규칙·디자인 포인트는 프로그램으로 그려서 글자 왜곡이 없다.

사용:
  python3 scripts/sheet_assemble.py bob
  → references/characters/bob/SHEET-bob.png

부품 파일 규약 (references/characters/<slug>/):
  canonical-front-side.png  터너라운드 정면+측면 (필수)
  turn-back-01.png          후면 (있으면 배치)
  expressions-01.png        표정 3버스트 스트립 (있으면 배치)
  clean-body-01.png         소품 없는 클린 전신 (있으면 배치)

PALETTES/DESIGN 데이터는 docs/characters/<slug>.md 스펙과 동기 유지할 것.
"""

import argparse
import time
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent / "references" / "characters"
BG = (19, 19, 19)          # #131313 블로그 다크 배경
FG = (232, 220, 196)       # #E8DCC4 크림 — 본문 라벨
DIM = (140, 132, 118)      # 보조 라벨
ACCENT = (255, 185, 87)    # #FFB957 — 패널 제목

PALETTES = {
    "rae": [
        ("#E8DCC4", "cream anchor"), ("#7A573E", "fur"), ("#D9C9A8", "outline"),
        ("#FFB957", "amber cable"), ("#22D3EE", "cyan ESC"), ("#B8B2A4", "props"),
        ("#123540", "sea"), ("#0F2630", "night sky"),
    ],
    "bob": [
        ("#E8DCC4", "cream anchor"), ("#A97B4F", "fur"), ("#D9B98C", "fur lit"),
        ("#FFB957", "amber yuzu"), ("#22D3EE", "cyan prompt"), ("#B8B2A4", "laptop"),
        ("#123540", "water"), ("#0F2630", "night sky"),
    ],
    "chan": [
        ("#E8DCC4", "facial disc"), ("#7A6248", "feathers"), ("#D9C9A8", "barring"),
        ("#FFB957", "amber spine"), ("#F59E0B", "iris"), ("#22D3EE", "cyan ribbon"),
        ("#123540", "shelf shadow"), ("#0F2630", "wall"),
    ],
    "josh": [
        ("#E8DCC4", "cream anchor"), ("#5F4732", "fur"), ("#C9AE8C", "belly"),
        ("#FFB957", "amber spool"), ("#F59E0B", "maple pin"), ("#22D3EE", "cyan LED"),
        ("#B8B2A4", "printer"), ("#123540", "desk"), ("#0F2630", "wall"),
    ],
}
SPECIES = {"rae": "SEA OTTER", "bob": "CAPYBARA", "chan": "EAGLE-OWL", "josh": "BEAVER"}

# 소품 규칙(왼쪽 열) / 디자인 포인트(오른쪽 열) — 시트 스펙 요약
DESIGN = {
    "rae": {
        "props": [
            "60% 기계식 키보드 — 배 위. ESC만 시안 아티산 키캡 #22D3EE (유일 시안)",
            "마우스 — 양 앞발로 가슴에 꼭 안음 (애착 돌 은유). 웜그레이 #B8B2A4",
            "코일 케이블 — 앰버 #FFB957, 항공 커넥터. 닻 은유: 물속으로 완만한 사선",
            "변수 슬롯: 마우스 자리 = 대비 아이템 (체크리스트 / 백업 외장하드 / 여분 케이블)",
        ],
        "points": [
            "감정 코어 = 불안한 기록자: 동그란 점눈 + 八자 눈썹, 걱정이 디폴트",
            "크림 #E8DCC4가 얼굴→목→가슴으로 연결 — 세트 명도 앵커",
            "안경: 가는 원형 메탈 (동그란 눈과 이중 원 구조). 뿔테 금지",
            "금지: 켈프/해초, 몸통에 케이블 감기, 활짝 웃음, 만화적 패닉",
        ],
    },
    "bob": {
        "props": [
            "유자 1개 — 머리 위 고정. 앰버 #FFB957 액센트 담당",
            "낡은 클램셸 노트북 — 웜그레이 #B8B2A4 (검정 금지), 모서리 마모",
            "노트북 화면 = 검은 터미널 + 시안 프롬프트 라인 1줄 #22D3EE (유일 시안)",
            "변수 슬롯: 유자 자리 = 글 주제 따라 교체 (수건 / 소형 드론 등)",
        ],
        "points": [
            "종 식별: 벽돌형 두상 — 정수리~콧등 일직선(로만 노즈), 각진 주둥이, 무꼬리",
            "명도 역할: 세트 최고 명도 갈색 #A97B4F — 어두워지면 rae와 충돌",
            "표정: 반쯤 감긴 점눈 + 입꼬리 미소 — 세트 유일 디폴트 미소",
            "금지: 곰상(돔 이마·둥근 큰 귀), 검정 노트북, 다이나믹 포즈",
        ],
    },
    "chan": {
        "props": [
            "책 더미 3~5권 — 앉는 자리. 앰버 책등 정확히 1권 #FFB957",
            "앰버 포스트잇 2~3장 — 책과 날개 끝",
            "시안 책갈피 리본 1가닥 — 펼친 책 #22D3EE (유일 시안)",
            "변수 슬롯: 펼친 책 자리 = 돋보기 / 회로도 / 화이트보드",
        ],
        "points": [
            "종 식별: 귀깃(ear tufts) 필수, 머리 비중 큰 달걀형 — 세트 유일 조류",
            "눈: 앰버 홍채 #F59E0B — 세트 유일 홍채 ('유일한 학자' 이질감)",
            "크림 안면판 #E8DCC4 → 가슴 연결 필수. 하프림 사각 안경 (원형 금지)",
            "포즈: 고개 15° 갸웃 + 날개 끝을 부리께 (생각 제스처). 노려봄 금지",
        ],
    },
    "josh": {
        "props": [
            "탁상형 3D 프린터 — 웜그레이 #B8B2A4 (검정 금지). 노즐 LED 1점만 시안 #22D3EE",
            "앰버 필라멘트 스풀 #FFB957 + 단풍잎 핀 #F59E0B (가슴)",
            "양손 동시 소지: 납땜인두 + 출력물 (룩/rook 모티프) — 산만한 에너지의 정적 번역",
            "변수 슬롯: 출력물 = 글 주제 따라 교체 (소형 로봇 팔 / 미니어처 간판)",
        ],
        "points": [
            "종 식별: 주걱 꼬리(격자 톤온톤) 필수, 앞니 2개 노출, 세트 최소 체구",
            "명도 역할: 세트 최저 명도 갈색 #5F4732 (검정 금지), 배 #C9AE8C",
            "표정: 크게 뜬 점눈 + 살짝 벌린 입 — 말하다 만 얼굴",
            "금지: 쥐꼬리, 캐나다 국기, 인두 불꽃, 과대 머리",
        ],
    },
}

_FONT_DIR = Path.home() / ".local/share/fonts"


def font(size, bold=False):
    name = "NotoSansCJKkr-Bold.otf" if bold else "NotoSansCJKkr-Regular.otf"
    try:
        return ImageFont.truetype(str(_FONT_DIR / name), size)
    except OSError:
        try:
            return ImageFont.truetype(
                f"/usr/share/fonts/truetype/dejavu/DejaVuSans{'-Bold' if bold else ''}.ttf", size)
        except OSError:
            return ImageFont.load_default()


def fit(img: Image.Image, height: int) -> Image.Image:
    return img.resize((round(img.width * height / img.height), height))


def hex2rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def wrap(draw, text, fnt, max_w):
    """공백 기준 그리디 줄바꿈."""
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        cand = f"{cur} {w}".strip()
        if draw.textlength(cand, font=fnt) <= max_w:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def bullet_block(draw, items, x, y, col_w, fnt, line_h):
    """불릿 목록을 그리고 끝 y를 반환."""
    for item in items:
        draw.text((x, y), "·", font=fnt, fill=ACCENT)
        for i, line in enumerate(wrap(draw, item, fnt, col_w - 22)):
            draw.text((x + 20, y), line, font=fnt, fill=FG)
            y += line_h
        y += 6
    return y


def measure_bullets(draw, items, col_w, fnt, line_h):
    y = 0
    for item in items:
        y += line_h * len(wrap(draw, item, fnt, col_w - 22)) + 6
    return y


def assemble(slug: str, out: Path | None) -> Path:
    d = ROOT / slug
    parts = {
        "turnaround": d / "canonical-front-side.png",
        "back": d / "turn-back-01.png",
        "expressions": d / "expressions-01.png",
        "clean": d / "clean-body-01.png",
    }
    if not parts["turnaround"].is_file():
        raise SystemExit(f"정본 없음: {parts['turnaround']}")

    pad, label_h = 24, 30
    row1_h, row2_h, sw_h = 500, 400, 96

    row1 = [("TURNAROUND  front / side", Image.open(parts["turnaround"]).convert("RGB"))]
    if parts["back"].is_file():
        row1.append(("back", Image.open(parts["back"]).convert("RGB")))
    row2 = []
    if parts["expressions"].is_file():
        row2.append(("EXPRESSIONS  default / surprised / signature",
                     Image.open(parts["expressions"]).convert("RGB")))
    if parts["clean"].is_file():
        row2.append(("CLEAN BODY", Image.open(parts["clean"]).convert("RGB")))

    row1_imgs = [(t, fit(im, row1_h)) for t, im in row1]
    row2_imgs = [(t, fit(im, row2_h)) for t, im in row2]
    row_w = lambda imgs: sum(im.width for _, im in imgs) + pad * (len(imgs) + 1)
    palette = PALETTES.get(slug, [])
    design = DESIGN.get(slug)
    sw_w = pad * 2 + len(palette) * 150
    W = max(row_w(row1_imgs), row_w(row2_imgs) if row2_imgs else 0, sw_w, 1100)

    # 디자인 패널 높이 사전 계산
    body_f, head_f = font(19), font(21, bold=True)
    line_h = 27
    col_w = (W - pad * 3) // 2
    _probe = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    panel_h = 0
    if design:
        rows_h = max(
            measure_bullets(_probe, design["props"], col_w, body_f, line_h),
            measure_bullets(_probe, design["points"], col_w, body_f, line_h),
        )
        panel_h = 40 + rows_h + pad  # 컬럼 제목 + 본문

    header_h = 92
    H = (header_h + row1_h + label_h + (row2_h + label_h if row2_imgs else 0)
         + panel_h + (sw_h + label_h if palette else 0) + pad * 5)

    sheet = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(sheet)

    # 헤더
    draw.text((pad, pad), slug.upper(), font=font(44, bold=True), fill=FG)
    title_w = draw.textlength(slug.upper(), font=font(44, bold=True))
    draw.text((pad + title_w + 18, pad + 22),
              f"— {SPECIES.get(slug, '')}  ·  character reference sheet",
              font=font(20), fill=DIM)
    stamp = time.strftime("%Y-%m-%d")
    draw.text((W - pad - draw.textlength(stamp, font=font(18)), pad + 24), stamp,
              font=font(18), fill=DIM)

    def place_row(imgs, y):
        x = pad
        for title, im in imgs:
            sheet.paste(im, (x, y))
            draw.text((x + 2, y + im.height + 6), title, font=font(16), fill=DIM)
            x += im.width + pad
        return y + (imgs[0][1].height if imgs else 0) + label_h + pad

    y = header_h + pad
    y = place_row(row1_imgs, y)
    if row2_imgs:
        y = place_row(row2_imgs, y)

    # 소품 규칙 / 디자인 포인트 패널
    if design:
        draw.text((pad, y), "소품 규칙 (PROPS)", font=head_f, fill=ACCENT)
        draw.text((pad * 2 + col_w, y), "디자인 포인트 (IDENTITY)", font=head_f, fill=ACCENT)
        y_body = y + 40
        yl = bullet_block(draw, design["props"], pad, y_body, col_w, body_f, line_h)
        yr = bullet_block(draw, design["points"], pad * 2 + col_w, y_body, col_w, body_f, line_h)
        y = max(yl, yr) + pad

    # 팔레트 스와치
    if palette:
        x = pad
        for hexcode, role in palette:
            draw.rectangle([x, y, x + 132, y + sw_h], fill=hex2rgb(hexcode))
            draw.text((x + 2, y + sw_h + 4), hexcode, font=font(15, bold=True), fill=FG)
            draw.text((x + 2, y + sw_h + 22), role, font=font(14), fill=DIM)
            x += 150

    out = out or d / f"SHEET-{slug}.png"
    sheet.save(out)
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="레퍼런스 캐릭터 시트 조립기")
    ap.add_argument("slug", choices=sorted(PALETTES))
    ap.add_argument("-o", "--out", type=Path)
    args = ap.parse_args()
    print(assemble(args.slug, args.out))
