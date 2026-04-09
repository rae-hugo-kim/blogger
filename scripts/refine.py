"""Step 2: Content refinement pipeline for Hugo blog.

Processes raw markdown files from drafts/ and generates refined drafts
with proper Hugo frontmatter.
"""

import logging
import os
import re
import shutil
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


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

    # AI refinement: generates frontmatter fields + refined body
    ai_result = _ai_refine(body)
    refined_body = ai_result.get("body", body)
    if refined_body != body:
        warnings.append("AI refinement applied")

    # Build frontmatter: existing values > AI values > heuristic fallback
    fm = dict(existing_fm)

    if not fm.get("title") or fm["title"].startswith("Draft "):
        fm["title"] = ai_result.get("title") or _extract_title(body, path)

    if not fm.get("description"):
        fm["description"] = ai_result.get("description") or _extract_description(body) or fm.get("title", path.stem)

    if not fm.get("tags"):
        fm["tags"] = ai_result.get("tags") or _extract_tags(body)

    if "date" not in fm:
        fm["date"] = ai_result.get("date") or date.today().isoformat()

    if not fm.get("categories"):
        fm["categories"] = ["\uae30\uc220"]

    if "draft" not in fm:
        fm["draft"] = True

    return RefineResult(frontmatter=fm, body=refined_body, warnings=warnings)


def _ai_refine(body: str) -> dict:
    """Refine body and generate frontmatter using Claude API. Returns dict with keys: title, description, tags, date, body."""
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return {"body": body}

    tone_guide_path = Path(__file__).parent.parent / "docs" / "tone-guide.md"
    if not tone_guide_path.exists():
        return {"body": body}

    try:
        import json
        from anthropic import Anthropic  # lazy import: optional dependency

        tone_guide = tone_guide_path.read_text(encoding="utf-8")
        system_prompt = (
            tone_guide
            + "\n\n아래 마크다운 본문을 위 톤 가이드에 맞게 정제하고, "
            "프론트매터 필드도 함께 생성해주세요.\n\n"
            "반드시 아래 JSON 형식으로만 응답하세요 (```json 없이 순수 JSON만):\n"
            '{"title": "블로그 포스트 제목 (60자 이내, SEO 친화적)", '
            '"description": "글 요약 (150-160자, 구체적 내용)", '
            '"tags": ["태그1", "태그2", "태그3"], '
            '"date": "본문에서 추출한 날짜 (YYYY-MM-DD 형식, 없으면 null)", '
            '"body": "정제된 마크다운 본문"}\n\n'
            "규칙:\n"
            "- title: 본문 내용을 대표하는 매력적인 제목. '개발일기' 같은 일반적 제목 지양\n"
            "- description: '이 글에서는~' 패턴 금지, 핵심 가치를 구체적으로\n"
            "- tags: 3-7개, 구체적 기술명 우선, 소문자\n"
            "- date: 본문 상단에 날짜가 있으면 추출 (YYYY-MM-DD), 없으면 null\n"
            "- body: 톤 가이드에 맞게 정제. 코드 블록, 링크, 이미지 경로는 절대 변경 금지\n"
        )
        model = os.environ.get("REFINE_MODEL", "claude-sonnet-4-5-20250929")
        client = Anthropic(api_key=api_key, timeout=60.0)
        message = client.messages.create(
            model=model,
            max_tokens=8192,
            system=system_prompt,
            messages=[{"role": "user", "content": body}],
        )
        raw = message.content[0].text
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = re.sub(r"^```(?:json)?\s*\n?", "", raw)
            raw = re.sub(r"\n?```\s*$", "", raw)
        result = json.loads(raw)
        if not isinstance(result.get("body"), str) or not result["body"]:
            raise ValueError("AI response missing or empty 'body' field")
        if "tags" in result and not isinstance(result["tags"], list):
            result.pop("tags")
        if "title" in result and not isinstance(result["title"], str):
            result.pop("title")
        return result
    except json.JSONDecodeError as exc:
        logging.warning("AI response was not valid JSON: %s", exc)
        return {"body": body}
    except ValueError as exc:
        logging.warning("AI response validation failed: %s", exc)
        return {"body": body}
    except Exception as exc:  # noqa: BLE001
        logging.error("AI refinement unexpected error: %s", exc)
        return {"body": body}


def process_drafts(drafts_dir: Path, output_dir: Path) -> ProcessResult:
    """Process all .md files from drafts_dir into Hugo page bundles in output_dir."""
    result = ProcessResult()
    output_dir.mkdir(parents=True, exist_ok=True)

    for md_file in sorted(drafts_dir.glob("*/index.md")):
        refined = refine(md_file)
        slug = md_file.parent.name
        bundle_dir = output_dir / slug
        bundle_dir.mkdir(parents=True, exist_ok=True)
        (bundle_dir / "index.md").write_text(
            refined.to_markdown(), encoding="utf-8"
        )
        # Copy non-md assets (images, etc.) from the draft bundle
        for asset in md_file.parent.iterdir():
            if asset.name != "index.md":
                shutil.copy2(asset, bundle_dir / asset.name)
        result.processed.append(
            {"source": str(md_file), "slug": slug, "output": str(bundle_dir / "index.md")}
        )

    return result


if __name__ == "__main__":
    import argparse
    import sys

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    parser = argparse.ArgumentParser(description="Refine markdown drafts for Hugo blog.")
    parser.add_argument("--drafts-dir", default="drafts", type=Path, metavar="DIR")
    parser.add_argument("--output-dir", default="content/posts", type=Path, metavar="DIR")
    parser.add_argument("--dry-run", action="store_true", help="Print results to stdout without writing files.")
    parser.add_argument("--single", type=Path, metavar="FILE", help="Refine a single file instead of the whole drafts dir.")
    parser.add_argument("--no-ai", action="store_true", help="Disable AI refinement by clearing ANTHROPIC_API_KEY.")
    args = parser.parse_args()

    if args.no_ai:
        os.environ["ANTHROPIC_API_KEY"] = ""

    try:
        if args.single:
            result = refine(args.single)
            if result.warnings:
                for w in result.warnings:
                    print(f"warning: {w}", file=sys.stderr)
            print(result.to_markdown())
        elif args.dry_run:
            for md_file in sorted(args.drafts_dir.glob("*/index.md")):
                result = refine(md_file)
                print(f"=== {md_file} ===")
                if result.warnings:
                    for w in result.warnings:
                        print(f"warning: {w}")
                print(result.to_markdown())
                print()
        else:
            process_result = process_drafts(args.drafts_dir, args.output_dir)
            for entry in process_result.processed:
                print(f"{entry['source']} -> {entry['slug']}")
    except RefineError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
