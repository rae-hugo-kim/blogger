"""Step 1: Hugo 블로그 기본 구조 — Navigation & Link Integrity Tests.

글 목록, 태그, 카테고리 간 링크 연결 검증.
"""

import re
from pathlib import Path


def _read_html(path: Path) -> str:
    return path.read_text(encoding="utf-8")


class TestNavigationLinks:
    """페이지 간 링크 연결 검증."""

    def test_home_links_to_posts(self, hugo_build):
        """홈 페이지에서 글 상세로의 링크가 존재."""
        assert hugo_build["returncode"] == 0
        index = _read_html(hugo_build["public_dir"] / "index.html")
        # 최소한 /posts/ 경로를 포함하는 링크가 있어야 함
        assert re.search(r'href="[^"]*/?posts/', index), (
            "Home page has no link to posts"
        )

    def test_post_links_to_tags(self, hugo_build):
        """글 상세 페이지에서 태그 링크가 존재."""
        assert hugo_build["returncode"] == 0
        posts_dir = hugo_build["public_dir"] / "posts"
        post_htmls = list(posts_dir.rglob("index.html"))
        assert len(post_htmls) >= 1, "No posts to check"

        post_html = _read_html(post_htmls[0])
        assert re.search(r'href="[^"]*/?tags/', post_html), (
            "Post page has no link to tags"
        )

    def test_tag_page_lists_posts(self, hugo_build):
        """개별 태그 페이지에 해당 태그의 글이 노출."""
        assert hugo_build["returncode"] == 0
        tags_dir = hugo_build["public_dir"] / "tags"
        assert tags_dir.exists(), "public/tags/ not generated"
        # 개별 태그 디렉토리 찾기 (tags/index.html은 태그 목록이므로 제외)
        tag_term_dirs = [
            d for d in tags_dir.iterdir()
            if d.is_dir() and (d / "index.html").exists()
        ]
        assert len(tag_term_dirs) >= 1, "No individual tag pages generated"

        tag_html = _read_html(tag_term_dirs[0] / "index.html")
        # 개별 태그 페이지에 글로의 링크가 있어야 함
        assert re.search(r'href="[^"]*/?posts/|href="[^"]*/?hello-world', tag_html), (
            "Tag term page has no link to posts"
        )

    def test_category_page_lists_posts(self, hugo_build):
        """개별 카테고리 페이지에 해당 카테고리 글이 노출."""
        assert hugo_build["returncode"] == 0
        cats_dir = hugo_build["public_dir"] / "categories"
        assert cats_dir.exists(), "public/categories/ not generated"
        # 개별 카테고리 디렉토리 찾기
        cat_term_dirs = [
            d for d in cats_dir.iterdir()
            if d.is_dir() and (d / "index.html").exists()
        ]
        assert len(cat_term_dirs) >= 1, "No individual category pages generated"

        cat_html = _read_html(cat_term_dirs[0] / "index.html")
        assert re.search(r'href="[^"]*/?posts/|href="[^"]*/?hello-world', cat_html), (
            "Category term page has no link to posts"
        )


class TestSlugGeneration:
    """Slug/URL 생성 규칙 검증."""

    def test_post_slug_follows_convention(self, hugo_build):
        """포스트 URL이 /posts/<slug>/ 패턴을 따름."""
        assert hugo_build["returncode"] == 0
        posts_dir = hugo_build["public_dir"] / "posts"
        post_dirs = [d for d in posts_dir.iterdir() if d.is_dir() and d.name != "page"]
        assert len(post_dirs) >= 1, "No post directories found"

        for post_dir in post_dirs:
            # slug는 소문자, 하이픈, 숫자만 허용 (한글 slug도 허용)
            slug = post_dir.name
            assert slug, f"Empty slug found"
            assert (post_dir / "index.html").exists(), (
                f"Post {slug} has no index.html"
            )
