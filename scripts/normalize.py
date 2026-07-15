"""Publish normalizer for the Hugo blog.

drafts/의 마크다운을 content/posts/ 페이지 번들로 조립하는 기계적(non-AI)
게시 단계: 빈 프론트매터 필드 휴리스틱 채움, 선두 h1 제거, 에셋 복사.
산문 퇴고는 파이프라인 밖의 일이다(사람 또는 에이전트가 docs/tone-guide.md를
기준으로 수행) — 본문은 선두 h1 제거 외에 바이트 단위로 보존된다.
"""

import logging
import re
import shutil
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml


class NormalizeError(Exception):
    """Raised for invalid input during normalization."""


@dataclass
class NormalizeResult:
    frontmatter: dict
    body: str
    warnings: list = field(default_factory=list)

    def to_markdown(self) -> str:
        fm_text = yaml.dump(
            self.frontmatter,
            default_flow_style=False,
            allow_unicode=True,
            sort_keys=False,
        )
        return f"---\n{fm_text}---\n{self.body}"


@dataclass
class ProcessResult:
    processed: list = field(default_factory=list)
    skipped: list = field(default_factory=list)


_FRONTMATTER_RE = re.compile(r"\A---\n(.*?\n)---\n", re.DOTALL)
_CODE_BLOCK_RE = re.compile(r"```.*?```", re.DOTALL)
_HEADING_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_SUB_HEADING_RE = re.compile(r"^#{2,}\s+(.+)$", re.MULTILINE)


def _parse_frontmatter(text: str) -> tuple[dict, str]:
    """Parse existing frontmatter from markdown text. Returns (fm_dict, body)."""
    m = _FRONTMATTER_RE.match(text)
    if m:
        fm = yaml.safe_load(m.group(1)) or {}
        body = text[m.end():]
        return fm, body
    return {}, text


def _extract_title(body: str, filepath: Path) -> str:
    """Extract title from first # heading or fallback to parent folder name."""
    m = _HEADING_RE.search(body)
    if m:
        return m.group(1).strip()
    # For page bundles (index.md), use parent folder name
    name = filepath.parent.name if filepath.stem == "index" else filepath.stem
    return name.replace("-", " ").replace("_", " ").title()


def _extract_description(body: str) -> str:
    """Extract description from first non-heading paragraph."""
    # Remove code blocks for analysis
    clean = _CODE_BLOCK_RE.sub("", body)
    paragraphs = []
    current = []
    for line in clean.split("\n"):
        stripped = line.strip()
        if not stripped:
            if current:
                paragraphs.append(" ".join(current))
                current = []
        elif not stripped.startswith("#"):
            current.append(stripped)
    if current:
        paragraphs.append(" ".join(current))

    for p in paragraphs:
        if len(p) >= 10:
            if len(p) > 200:
                return p[:197] + "..."
            return p
    # Fallback: use whatever text is available
    for p in paragraphs:
        if p:
            return p
    return ""


def _extract_tags(body: str) -> list:
    """Extract tags from headings as simple keyword heuristic."""
    headings = _SUB_HEADING_RE.findall(body)
    main_heading = _HEADING_RE.search(body)
    if main_heading:
        headings = [main_heading.group(1)] + headings

    # Extract meaningful words from headings
    tags = set()
    for h in headings:
        words = re.findall(r"[A-Za-z\uac00-\ud7a3]+", h)
        for w in words:
            if len(w) >= 2:
                tags.add(w.lower() if w.isascii() else w)

    if not tags:
        return ["general"]
    return sorted(tags)[:5]


def _count_non_code_lines(body: str) -> int:
    """Count lines of non-code, non-empty text."""
    clean = _CODE_BLOCK_RE.sub("", body)
    return sum(1 for line in clean.strip().split("\n") if line.strip())


def _strip_leading_h1(body: str) -> str:
    """본문 맨 앞의 h1(#) 제목 라인을 기계적으로 제거 (프론트매터 title이 대신함).

    h1 앞의 선행 공백/개행은 보존한다 — 프론트매터 뒤 빈 줄 관례 유지.
    """
    return re.sub(r"\A(\s*)#\s+[^\n]*\n+", r"\1", body, count=1)


def normalize(path: Path) -> NormalizeResult:
    """Normalize a markdown file for publishing.

    본문은 선두 h1 제거(구조 규칙 — 제목은 프론트매터 title이 대신함) 외에
    변경하지 않는다. 프론트매터는 기존 값을 보존하고, 비어 있는 필드만
    휴리스틱으로 채운다.
    """
    text = path.read_text(encoding="utf-8")

    if not text.strip():
        raise NormalizeError(f"Empty file: {path}")

    existing_fm, body = _parse_frontmatter(text)
    warnings = []

    # Check for short content
    non_code_lines = _count_non_code_lines(body)
    if non_code_lines < 3:
        warnings.append("Short content: fewer than 3 lines of non-code text")

    refined_body = _strip_leading_h1(body)

    # Build frontmatter: existing values > heuristic fallback
    fm = dict(existing_fm)

    if not fm.get("title") or str(fm["title"]).startswith("Draft "):
        fm["title"] = _extract_title(body, path)
        warnings.append("auto-filled: title (heuristic placeholder — 퇴고에서 확정)")

    if not fm.get("description"):
        fm["description"] = _extract_description(body) or fm.get("title", path.stem)
        warnings.append("auto-filled: description (heuristic placeholder — SEO 문안은 퇴고에서 확정)")

    if not fm.get("tags"):
        fm["tags"] = _extract_tags(body)
        warnings.append("auto-filled: tags (heuristic placeholder — 퇴고에서 확정)")

    if "date" not in fm:
        fm["date"] = date.today().isoformat()

    if not fm.get("categories"):
        fm["categories"] = ["작업노트"]
        warnings.append("auto-filled: categories=작업노트 (기본값 — 톤 라우팅에 영향)")

    if "draft" not in fm:
        fm["draft"] = True

    return NormalizeResult(frontmatter=fm, body=refined_body, warnings=warnings)


def _is_asset(p: Path) -> bool:
    """게시 가능한 에셋 판정 — index.md, dot-엔트리(.omc/.obsidian/.DS_Store 등
    런타임·에디터 상태), symlink를 제외한다. 상태 파일 복사와 symlink 역참조
    게시를 차단한다. 범위 명시: hardlink는 감지하지 않는다 — 동일 FS에서 고의로
    생성해야 하는 형태라 우발 유출 위협모델(dot-엔트리/symlink) 밖으로 수용."""
    return p.name != "index.md" and not p.name.startswith(".") and not p.is_symlink()


def _assets_only_in(left: Path, right: Path) -> list:
    """left 번들에는 있지만 right 번들에는 없는 에셋 이름 목록."""
    left_assets = {p.name for p in left.iterdir() if _is_asset(p)}
    right_assets = {p.name for p in right.iterdir() if _is_asset(p)}
    return sorted(left_assets - right_assets)


def _ignore_hidden_and_symlinks(dirpath, names):
    """copytree ignore 콜백 — 전 깊이에서 dot-엔트리와 symlink를 제외."""
    return {
        name for name in names
        if name.startswith(".") or (Path(dirpath) / name).is_symlink()
    }


def _copy_assets(draft_bundle: Path, out_bundle: Path) -> None:
    """Copy publishable assets (images, dirs, etc.) from the draft bundle.

    dot-엔트리와 symlink는 재귀 전 깊이에서 제외한다 — 중첩된 `.cache`/`.omc` 같은
    상태 파일이나 링크 역참조 데이터가 디렉토리 복사에 딸려 게시되는 것을 차단.
    """
    for asset in draft_bundle.iterdir():
        if not _is_asset(asset):
            continue
        if asset.is_dir():
            shutil.copytree(
                asset, out_bundle / asset.name, dirs_exist_ok=True,
                ignore=_ignore_hidden_and_symlinks,
            )
        else:
            shutil.copy2(asset, out_bundle / asset.name)


def should_skip(md_file: Path, output_dir: Path, force: set) -> bool:
    """스킵 판정: 출력 index.md가 존재하고 force 대상이 아니면 스킵.

    index.md는 마지막에 쓰이는 '완료 마커'다 — 에셋만 남은 부분상태는
    스킵되지 않고 재처리된다.
    """
    slug = md_file.parent.name
    return (output_dir / slug / "index.md").exists() and slug not in force


def process_drafts(drafts_dir: Path, output_dir: Path, force: set | None = None) -> ProcessResult:
    """Process .md files from drafts_dir into Hugo page bundles in output_dir.

    이미 출력물이 존재하는 slug는 스킵한다 — content/posts/는 사람이 리뷰·교정하는
    작업물이므로 재조립으로 덮어쓰지 않는다. 재조립은 명시적으로 `force`에 slug를
    담아 요청할 때만 수행하며, index.md와 드래프트 에셋을 다시 쓴다. 드래프트에
    없는 출력 전용 에셋(사람이 리뷰 중 추가했을 수 있음)은 삭제하지 않고 경고만
    남긴다 — provenance를 모르는 파일의 삭제는 복구 불가 손실이다.
    """
    force = force or set()
    result = ProcessResult()
    output_dir.mkdir(parents=True, exist_ok=True)

    for md_file in sorted(drafts_dir.glob("*/index.md")):
        slug = md_file.parent.name
        bundle_dir = output_dir / slug
        if should_skip(md_file, output_dir, force):
            drift = _assets_only_in(md_file.parent, bundle_dir)
            if drift:
                logging.warning(
                    "asset drift in skipped slug '%s' (missing: %s) — re-normalize with --force %s",
                    slug, ", ".join(drift), slug,
                )
            result.skipped.append({"source": str(md_file), "slug": slug, "asset_drift": drift})
            continue
        normalized = normalize(md_file)
        for w in normalized.warnings:
            logging.warning("%s: %s", slug, w)
        if slug in force and bundle_dir.exists():
            extra = _assets_only_in(bundle_dir, md_file.parent)  # 출력에만 있는 에셋
            if extra:
                logging.warning(
                    "force '%s': output-only assets preserved (%s) — delete manually if stale",
                    slug, ", ".join(extra),
                )
        bundle_dir.mkdir(parents=True, exist_ok=True)
        # 에셋을 먼저, index.md를 마지막에 — index.md 존재가 완료 마커이므로
        # 부분 실패 시 다음 실행이 해당 slug를 영구 스킵하지 않는다.
        _copy_assets(md_file.parent, bundle_dir)
        (bundle_dir / "index.md").write_text(
            normalized.to_markdown(), encoding="utf-8"
        )
        result.processed.append(
            {"source": str(md_file), "slug": slug, "output": str(bundle_dir / "index.md")}
        )

    return result


if __name__ == "__main__":
    import argparse
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Normalize markdown drafts into Hugo page bundles.")
    parser.add_argument("--drafts-dir", default="drafts", type=Path, metavar="DIR")
    parser.add_argument("--output-dir", default="content/posts", type=Path, metavar="DIR")
    parser.add_argument("--dry-run", action="store_true", help="Print results to stdout without writing files.")
    parser.add_argument("--single", type=Path, metavar="FILE", help="Normalize a single file instead of the whole drafts dir.")
    parser.add_argument(
        "--force", action="append", default=[], metavar="SLUG",
        help="Re-normalize this slug even if content/posts/<slug>/ already exists. Repeatable.",
    )
    args = parser.parse_args()

    try:
        if args.single:
            result = normalize(args.single)
            if result.warnings:
                for w in result.warnings:
                    print(f"warning: {w}", file=sys.stderr)
            print(result.to_markdown())
        elif args.dry_run:
            force_set = set(args.force)
            for md_file in sorted(args.drafts_dir.glob("*/index.md")):
                if should_skip(md_file, args.output_dir, force_set):
                    print(f"skip (already normalized): {md_file.parent.name}")
                    continue
                result = normalize(md_file)
                print(f"=== {md_file} ===")
                if result.warnings:
                    for w in result.warnings:
                        print(f"warning: {w}")
                print(result.to_markdown())
                print()
        else:
            process_result = process_drafts(args.drafts_dir, args.output_dir, force=set(args.force))
            for entry in process_result.processed:
                print(f"{entry['source']} -> {entry['slug']}")
            for entry in process_result.skipped:
                print(f"skip (already normalized): {entry['slug']}")
    except NormalizeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
