"""Step 2: 콘텐츠 정제 파이프라인 Tests.

RED phase: 정제 스크립트의 핵심 기능을 검증한다.
파이프라인은 scripts/refine.py 모듈로 구현될 예정.
"""

import subprocess
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def refine_module():
    """Import the refine module, skip if not yet created."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "refine", PROJECT_ROOT / "scripts" / "refine.py"
    )
    if spec is None:
        pytest.skip("scripts/refine.py not found")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def sample_md_no_frontmatter(tmp_path):
    """프론트매터 없는 순수 마크다운 파일."""
    md = tmp_path / "raw.md"
    md.write_text(textwrap.dedent("""\
        # Docker 컨테이너 네트워킹 가이드

        Docker 컨테이너 간 네트워킹은 마이크로서비스 아키텍처에서 핵심적인 부분입니다.

        ## 브릿지 네트워크

        기본적으로 Docker는 브릿지 네트워크를 사용합니다.

        ```bash
        docker network create my-network
        docker run --network my-network --name web nginx
        ```

        ## 결론

        Docker 네트워킹을 이해하면 컨테이너 기반 서비스를 더 효과적으로 구성할 수 있습니다.
    """), encoding="utf-8")
    return md


@pytest.fixture
def sample_md_with_frontmatter(tmp_path):
    """이미 프론트매터가 있는 마크다운 파일."""
    md = tmp_path / "existing.md"
    md.write_text(textwrap.dedent("""\
        ---
        title: "기존 제목"
        date: 2026-03-15
        tags: ["docker"]
        draft: true
        ---

        # Docker 컨테이너 네트워킹

        이미 프론트매터가 있는 문서입니다.

        ```python
        import docker
        client = docker.from_env()
        ```
    """), encoding="utf-8")
    return md


@pytest.fixture
def sample_md_short(tmp_path):
    """매우 짧은 메모 수준의 파일."""
    md = tmp_path / "short.md"
    md.write_text("Docker는 좋다.\n", encoding="utf-8")
    return md


@pytest.fixture
def sample_md_code_heavy(tmp_path):
    """코드 블록만 있는 파일."""
    md = tmp_path / "code_only.md"
    md.write_text(textwrap.dedent("""\
        ```python
        def hello():
            print("hello world")
        ```

        ```bash
        echo "test"
        ```
    """), encoding="utf-8")
    return md


@pytest.fixture
def sample_md_special_chars(tmp_path):
    """프론트매터를 깨뜨릴 수 있는 특수문자가 포함된 파일."""
    md = tmp_path / "special.md"
    md.write_text(textwrap.dedent("""\
        # YAML 특수문자 테스트: "따옴표"와 '작은따옴표'

        이 문서에는 콜론: 이 있고, 줄바꿈도
        여러 줄에 걸쳐 있습니다.

        제목에 특수문자가 많아서 프론트매터 생성 시 주의가 필요합니다.
    """), encoding="utf-8")
    return md


class TestFrontmatterGeneration:
    """프론트매터 생성 검증."""

    def test_generates_frontmatter_for_raw_md(self, refine_module, sample_md_no_frontmatter):
        """프론트매터 없는 md에 title, description, tags, date를 생성."""
        result = refine_module.refine(sample_md_no_frontmatter)
        assert "title" in result.frontmatter
        assert "description" in result.frontmatter
        assert "tags" in result.frontmatter
        assert "date" in result.frontmatter

    def test_preserves_existing_frontmatter(self, refine_module, sample_md_with_frontmatter):
        """기존 프론트매터 값을 유지하고, 빈 필드만 채움."""
        result = refine_module.refine(sample_md_with_frontmatter)
        assert result.frontmatter["title"] == "기존 제목"
        assert str(result.frontmatter["date"]) == "2026-03-15"
        assert result.frontmatter["tags"] == ["docker"]

    def test_preserves_draft_flag(self, refine_module, sample_md_with_frontmatter):
        """정제 파이프라인이 draft 값을 덮어쓰지 않음."""
        result = refine_module.refine(sample_md_with_frontmatter)
        assert result.frontmatter["draft"] is True

    def test_fills_missing_description(self, refine_module, sample_md_with_frontmatter):
        """기존 프론트매터에 description이 없으면 자동 생성."""
        result = refine_module.refine(sample_md_with_frontmatter)
        assert "description" in result.frontmatter
        assert len(result.frontmatter["description"]) > 0


class TestFrontmatterValidity:
    """생성된 프론트매터가 Hugo와 호환되는지 검증."""

    def test_date_is_iso_format(self, refine_module, sample_md_no_frontmatter):
        """date 필드가 Hugo 파싱 가능한 형식."""
        result = refine_module.refine(sample_md_no_frontmatter)
        date_str = str(result.frontmatter["date"])
        # YYYY-MM-DD 또는 ISO 8601
        assert len(date_str) >= 10, f"Date too short: {date_str}"

    def test_tags_is_list(self, refine_module, sample_md_no_frontmatter):
        """tags가 리스트 타입."""
        result = refine_module.refine(sample_md_no_frontmatter)
        assert isinstance(result.frontmatter["tags"], list)
        assert len(result.frontmatter["tags"]) >= 1

    def test_description_length(self, refine_module, sample_md_no_frontmatter):
        """SEO description이 적절한 길이."""
        result = refine_module.refine(sample_md_no_frontmatter)
        desc = result.frontmatter["description"]
        assert 10 <= len(desc) <= 200, f"Description length {len(desc)} out of range"

    def test_hugo_build_with_refined_content(self, refine_module, sample_md_no_frontmatter):
        """정제된 콘텐츠로 Hugo 빌드가 실제로 통과."""
        result = refine_module.refine(sample_md_no_frontmatter)
        # 정제된 파일을 content/posts/에 임시 배치 후 빌드
        target = PROJECT_ROOT / "content" / "posts" / "_test-refined" / "index.md"
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            target.write_text(result.to_markdown(), encoding="utf-8")
            build = subprocess.run(
                ["hugo", "build"],
                cwd=PROJECT_ROOT,
                capture_output=True,
                text=True,
                env={"PATH": f"{Path.home() / '.local' / 'bin'}:{subprocess.os.environ.get('PATH', '')}"},
            )
            assert build.returncode == 0, f"Hugo build failed with refined content:\n{build.stderr}"
        finally:
            # 테스트 후 정리
            if target.exists():
                target.unlink()
            if target.parent.exists():
                target.parent.rmdir()


class TestYAMLSafety:
    """YAML 특수문자 처리 검증."""

    def test_special_chars_in_title(self, refine_module, sample_md_special_chars):
        """제목에 :, ", ' 등이 있어도 프론트매터가 깨지지 않음."""
        result = refine_module.refine(sample_md_special_chars)
        md_text = result.to_markdown()
        # 결과가 유효한 YAML 프론트매터를 포함하는지 확인
        assert md_text.startswith("---\n"), "Output doesn't start with frontmatter"
        end = md_text.index("---\n", 4)
        assert end > 4, "Frontmatter not properly closed"

        # YAML 파싱 가능한지 확인
        import yaml
        fm_text = md_text[4:end]
        parsed = yaml.safe_load(fm_text)
        assert "title" in parsed


class TestContentPreservation:
    """콘텐츠 보존 검증."""

    def test_code_blocks_unchanged(self, refine_module, sample_md_no_frontmatter):
        """코드 블록 내용이 변경되지 않음."""
        result = refine_module.refine(sample_md_no_frontmatter)
        body = result.body
        assert "docker network create my-network" in body
        assert "docker run --network my-network --name web nginx" in body

    def test_links_preserved(self, refine_module, tmp_path):
        """내부/외부 링크와 이미지 경로가 유지됨."""
        md = tmp_path / "links.md"
        md.write_text(textwrap.dedent("""\
            # 링크 테스트

            [외부 링크](https://example.com)와 [내부 링크](/posts/hello-world/)가 있습니다.

            ![이미지](./images/test.png)

            이 문서에는 다양한 링크가 포함되어 있어서 정제 후에도 모두 유지되어야 합니다.
        """), encoding="utf-8")
        result = refine_module.refine(md)
        body = result.body
        assert "https://example.com" in body
        assert "/posts/hello-world/" in body
        assert "./images/test.png" in body


class TestIdempotency:
    """정제 파이프라인 멱등성 검증."""

    def test_double_refine_produces_same_result(self, refine_module, sample_md_no_frontmatter, monkeypatch):
        """같은 파일을 두 번 정제해도 결과가 동일 (AI 비결정성 제외)."""
        monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
        result1 = refine_module.refine(sample_md_no_frontmatter)
        # 첫 번째 결과를 파일로 저장 후 다시 정제
        refined_path = sample_md_no_frontmatter.parent / "refined.md"
        refined_path.write_text(result1.to_markdown(), encoding="utf-8")
        result2 = refine_module.refine(refined_path)
        assert result1.frontmatter == result2.frontmatter
        assert result1.body == result2.body


class TestEdgeCases:
    """엣지 케이스 검증."""

    def test_empty_file_handled(self, refine_module, tmp_path):
        """빈 파일은 에러 메시지 또는 스킵."""
        md = tmp_path / "empty.md"
        md.write_text("", encoding="utf-8")
        with pytest.raises((ValueError, refine_module.RefineError)):
            refine_module.refine(md)

    def test_short_memo_warns(self, refine_module, sample_md_short):
        """짧은 메모는 경고를 포함하여 처리."""
        result = refine_module.refine(sample_md_short)
        assert result.warnings, "Short content should produce warnings"

    def test_code_only_file_handled(self, refine_module, sample_md_code_heavy):
        """코드 블록만 있는 파일도 처리 가능."""
        result = refine_module.refine(sample_md_code_heavy)
        assert "title" in result.frontmatter


class TestIntegration:
    """통합 테스트: drafts/ → content/posts/ 파이프라인."""

    def test_drafts_to_content_pipeline(self, refine_module, sample_md_no_frontmatter, tmp_path):
        """drafts/ 폴더의 md가 content/posts/에 초안으로 생성됨."""
        drafts_dir = tmp_path / "drafts"
        output_dir = tmp_path / "posts"

        # page bundle 구조로 테스트 파일 배치
        bundle = drafts_dir / "test-pipeline"
        bundle.mkdir(parents=True)
        src = bundle / "index.md"
        src.write_text(sample_md_no_frontmatter.read_text(encoding="utf-8"), encoding="utf-8")

        result = refine_module.process_drafts(drafts_dir, output_dir)
        assert len(result.processed) >= 1, "No files processed"

        # 생성된 파일 확인
        out_bundle = output_dir / "test-pipeline"
        assert out_bundle.exists(), "Output directory not created"
        assert (out_bundle / "index.md").exists(), "index.md not created"

    def test_github_actions_yaml_valid(self):
        """GitHub Actions 워크플로 YAML이 유효한 구문."""
        import yaml
        wf = PROJECT_ROOT / ".github" / "workflows" / "refine.yml"
        if not wf.exists():
            pytest.skip("Workflow file not yet created")
        content = wf.read_text(encoding="utf-8")
        parsed = yaml.safe_load(content)
        assert "on" in parsed or True in parsed, "Workflow missing 'on' trigger"
        assert "jobs" in parsed, "Workflow missing 'jobs'"
