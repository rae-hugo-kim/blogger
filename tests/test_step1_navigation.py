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


class TestHeaderMenu:
    """헤더 메뉴 링크 검증 — GitHub Pages 서브패스(/blogger/) 회귀 방지.

    hugo.yaml 메뉴를 `url:`로 정의하면 root-relative로 출력되어 서브패스가
    누락된다(실제 발생 회귀). `pageRef:`만 baseURL을 관통한다.
    """

    MENU_ITEMS = ["글", "이세계표류기", "에세이", "태그"]

    def test_menu_hrefs_include_base_subpath(self, hugo_build):
        """홈 헤더의 메뉴 4종 href가 모두 /blogger/ 프리픽스를 포함."""
        assert hugo_build["returncode"] == 0
        html = _read_html(hugo_build["public_dir"] / "index.html")
        anchors = re.findall(r"<a\b[^>]*>", html)
        for label in self.MENU_ITEMS:
            # 속성 순서 독립: 같은 <a> 태그 안에서 aria-label과 href를 따로 추출
            tag = next(
                (a for a in anchors
                 if re.search(r'aria-label="?' + re.escape(label) + r'"?[\s>]', a)),
                None,
            )
            assert tag, f"Menu item '{label}' not rendered in header"
            href = re.search(r'href="?([^"\s>]+)"?', tag)
            assert href and href.group(1).startswith("/blogger/"), (
                f"Menu '{label}' href '{href.group(1) if href else None}' misses /blogger/ subpath — "
                "use pageRef (not url) in hugo.yaml menus"
            )

    def test_series_term_page_lists_opener(self, hugo_build):
        """시리즈 페이지(/series/이세계표류기/)가 존재하고 서장을 나열."""
        assert hugo_build["returncode"] == 0
        term = hugo_build["public_dir"] / "series" / "이세계표류기" / "index.html"
        assert term.exists(), "series term page not generated"
        assert "이세계 표류기: 서장" in _read_html(term), (
            "series page does not list the opener post"
        )
