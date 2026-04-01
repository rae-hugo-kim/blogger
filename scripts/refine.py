"""Step 2: Content refinement pipeline for Hugo blog.

Processes raw markdown files from drafts/ and generates refined drafts
with proper Hugo frontmatter.
"""

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml


class RefineError(Exception):
    """Raised for invalid input during refinement."""


@dataclass
class RefineResult:
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
    """Extract title from first # heading or fallback to filename."""
    m = _HEADING_RE.search(body)
    if m:
        return m.group(1).strip()
    return filepath.stem.replace("-", " ").replace("_", " ").title()


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


def refine(path: Path) -> RefineResult:
    """Refine a markdown file, generating/preserving Hugo frontmatter."""
    text = path.read_text(encoding="utf-8")

    if not text.strip():
        raise RefineError(f"Empty file: {path}")

    existing_fm, body = _parse_frontmatter(text)
    warnings = []

    # Check for short content
    non_code_lines = _count_non_code_lines(body)
    if non_code_lines < 3:
        warnings.append("Short content: fewer than 3 lines of non-code text")

    # Build frontmatter, preserving existing values
    fm = dict(existing_fm)

    if "title" not in fm:
        fm["title"] = _extract_title(body, path)

    if "description" not in fm:
        desc = _extract_description(body)
        if desc:
            fm["description"] = desc
        else:
            fm["description"] = fm.get("title", path.stem)

    if "tags" not in fm:
        fm["tags"] = _extract_tags(body)

    if "date" not in fm:
        fm["date"] = date.today().isoformat()

    if "categories" not in fm:
        fm["categories"] = ["\uae30\uc220"]

    if "draft" not in fm:
        fm["draft"] = True

    return RefineResult(frontmatter=fm, body=body, warnings=warnings)


def _ai_refine(body: str) -> str:
    """AI refinement hook (no-op for now)."""
    return body


def process_drafts(drafts_dir: Path, output_dir: Path) -> ProcessResult:
    """Process all .md files from drafts_dir into Hugo page bundles in output_dir."""
    result = ProcessResult()
    output_dir.mkdir(parents=True, exist_ok=True)

    for md_file in sorted(drafts_dir.glob("*.md")):
        refined = refine(md_file)
        slug = md_file.stem
        bundle_dir = output_dir / slug
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "index.md").write_text(
            refined.to_markdown(), encoding="utf-8"
        )
        result.processed.append(
            {"source": str(md_file), "slug": slug, "output": str(bundle_dir / "index.md")}
        )

    return result
