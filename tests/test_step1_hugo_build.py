"""Step 1: Hugo 블로그 기본 구조 — Build & Structure Tests.

RED phase: these tests should FAIL until Hugo project is initialized.
"""

from pathlib import Path


class TestHugoBuild:
    """hugo build가 성공하고 기본 파일이 생성되는지 검증."""

    def test_build_succeeds(self, hugo_build):
        assert hugo_build["returncode"] == 0, (
            f"hugo build failed:\n{hugo_build['stderr']}"
        )

    def test_index_html_exists(self, hugo_build):
        assert hugo_build["returncode"] == 0
        index = hugo_build["public_dir"] / "index.html"
        assert index.exists(), "public/index.html not generated"

    def test_sample_post_html_exists(self, hugo_build):
        assert hugo_build["returncode"] == 0
        posts_dir = hugo_build["public_dir"] / "posts"
        assert posts_dir.exists(), "public/posts/ directory not generated"
        html_files = list(posts_dir.rglob("index.html"))
        assert len(html_files) >= 1, "No post HTML files generated under public/posts/"


class TestSEOFiles:
    """SEO 관련 파일 생성 검증."""

    def test_sitemap_exists(self, hugo_build):
        assert hugo_build["returncode"] == 0
        assert (hugo_build["public_dir"] / "sitemap.xml").exists()

    def test_robots_txt_exists(self, hugo_build):
        assert hugo_build["returncode"] == 0
        assert (hugo_build["public_dir"] / "robots.txt").exists()

    def test_rss_feed_exists(self, hugo_build):
        assert hugo_build["returncode"] == 0
        assert (hugo_build["public_dir"] / "index.xml").exists()


class TestDraftState:
    """Hugo 게시 상태 검증."""

    def test_draft_post_not_in_production_build(self, hugo_build):
        """draft: true 포스트가 프로덕션 빌드에 노출되지 않음."""
        assert hugo_build["returncode"] == 0
        public = hugo_build["public_dir"]
        # draft 포스트의 slug가 public에 없어야 함
        draft_marker = public / "posts" / "draft-test-post"
        assert not draft_marker.exists(), "Draft post exposed in production build"
