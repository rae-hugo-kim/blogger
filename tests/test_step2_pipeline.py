"""Step 2: 게시 정규화 파이프라인 Tests.

scripts/normalize.py — 기계적(non-AI) publish normalizer를 검증한다:
프론트매터 생성/보존(휴리스틱), 선두 h1 제거, 페이지 번들/에셋 조립.
산문 퇴고는 파이프라인 밖(사람/에이전트)의 일이므로 여기서 다루지 않는다.
"""

import subprocess
import textwrap
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).parent.parent


@pytest.fixture
def normalize_module():
    """Import the normalize module, skip if not yet created."""
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "normalize", PROJECT_ROOT / "scripts" / "normalize.py"
    )
    if spec is None:
        pytest.skip("scripts/normalize.py not found")
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


@pytest.fixture
def sample_md_essay(tmp_path):
    """에세이(서술체) 드래프트: categories 프론트매터 보존 검증용."""
    md = tmp_path / "essay.md"
    md.write_text(textwrap.dedent("""\
        ---
        categories: ["에세이"]
        ---

        아마도 아직 바람이 차갑던 겨울의 어느 점심 자리였던 것으로 기억한다.

        우리는 보쌈정식을 시켜놓고 이런 저런 이야기를 나누었다.

        "한 번 들어봐요." Bob은 QR코드 아이디어를 이야기했다.
    """), encoding="utf-8")
    return md


class TestFrontmatterGeneration:
    """프론트매터 생성 검증."""

    def test_generates_frontmatter_for_raw_md(self, normalize_module, sample_md_no_frontmatter):
        """프론트매터 없는 md에 title, description, tags, date를 생성."""
        result = normalize_module.normalize(sample_md_no_frontmatter)
        assert "title" in result.frontmatter
        assert "description" in result.frontmatter
        assert "tags" in result.frontmatter
        assert "date" in result.frontmatter

    def test_preserves_existing_frontmatter(self, normalize_module, sample_md_with_frontmatter):
        """기존 프론트매터 값을 유지하고, 빈 필드만 채움."""
        result = normalize_module.normalize(sample_md_with_frontmatter)
        assert result.frontmatter["title"] == "기존 제목"
        assert str(result.frontmatter["date"]) == "2026-03-15"
        assert result.frontmatter["tags"] == ["docker"]

    def test_preserves_draft_flag(self, normalize_module, sample_md_with_frontmatter):
        """정규화가 draft 값을 덮어쓰지 않음."""
        result = normalize_module.normalize(sample_md_with_frontmatter)
        assert result.frontmatter["draft"] is True

    def test_fills_missing_description(self, normalize_module, sample_md_with_frontmatter):
        """기존 프론트매터에 description이 없으면 자동 생성."""
        result = normalize_module.normalize(sample_md_with_frontmatter)
        assert "description" in result.frontmatter
        assert len(result.frontmatter["description"]) > 0


class TestFrontmatterValidity:
    """생성된 프론트매터가 Hugo와 호환되는지 검증."""

    def test_date_is_iso_format(self, normalize_module, sample_md_no_frontmatter):
        """date 필드가 Hugo 파싱 가능한 형식."""
        result = normalize_module.normalize(sample_md_no_frontmatter)
        date_str = str(result.frontmatter["date"])
        # YYYY-MM-DD 또는 ISO 8601
        assert len(date_str) >= 10, f"Date too short: {date_str}"

    def test_tags_is_list(self, normalize_module, sample_md_no_frontmatter):
        """tags가 리스트 타입."""
        result = normalize_module.normalize(sample_md_no_frontmatter)
        assert isinstance(result.frontmatter["tags"], list)
        assert len(result.frontmatter["tags"]) >= 1

    def test_description_length(self, normalize_module, sample_md_no_frontmatter):
        """SEO description이 적절한 길이."""
        result = normalize_module.normalize(sample_md_no_frontmatter)
        desc = result.frontmatter["description"]
        assert 10 <= len(desc) <= 200, f"Description length {len(desc)} out of range"

    def test_hugo_build_with_normalized_content(self, normalize_module, sample_md_no_frontmatter):
        """정규화된 콘텐츠로 Hugo 빌드가 실제로 통과."""
        result = normalize_module.normalize(sample_md_no_frontmatter)
        # 정규화된 파일을 content/posts/에 임시 배치 후 빌드
        target = PROJECT_ROOT / "content" / "posts" / "_test-normalized" / "index.md"
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
            assert build.returncode == 0, f"Hugo build failed with normalized content:\n{build.stderr}"
        finally:
            # 테스트 후 정리
            if target.exists():
                target.unlink()
            if target.parent.exists():
                target.parent.rmdir()


class TestYAMLSafety:
    """YAML 특수문자 처리 검증."""

    def test_special_chars_in_title(self, normalize_module, sample_md_special_chars):
        """제목에 :, ", ' 등이 있어도 프론트매터가 깨지지 않음."""
        result = normalize_module.normalize(sample_md_special_chars)
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


class TestBodyPreservation:
    """본문 보존 검증 — 선두 h1 제거 외에는 바이트 단위 불변."""

    def test_body_preserved_except_leading_h1(self, normalize_module, sample_md_essay):
        """본문은 선두 h1 제거(기계적) 외 바이트 불변."""
        _, src_body = normalize_module._parse_frontmatter(
            sample_md_essay.read_text(encoding="utf-8")
        )
        result = normalize_module.normalize(sample_md_essay)
        # sample_md_essay에는 h1이 없으므로 본문이 그대로여야 함
        assert result.body == src_body, "body must not be altered beyond leading h1"

    def test_leading_h1_stripped(self, normalize_module, sample_md_no_frontmatter):
        """선두 h1은 제거되고 (title이 대신함) 나머지는 보존."""
        _, src_body = normalize_module._parse_frontmatter(
            sample_md_no_frontmatter.read_text(encoding="utf-8")
        )
        result = normalize_module.normalize(sample_md_no_frontmatter)
        expected = src_body.replace("# Docker 컨테이너 네트워킹 가이드\n\n", "", 1)
        assert result.body == expected

    def test_body_without_h1_is_byte_identical(self, normalize_module, tmp_path):
        """h1이 없으면 본문이 바이트 단위로 동일."""
        md = tmp_path / "no-h1.md"
        md.write_text("---\ntitle: 제목\n---\n\n다듬은 문장 하나.\n\n다듬은 문장 둘.\n", encoding="utf-8")
        result = normalize_module.normalize(md)
        assert result.body == "\n다듬은 문장 하나.\n\n다듬은 문장 둘.\n"

    def test_code_blocks_unchanged(self, normalize_module, sample_md_no_frontmatter):
        """코드 블록 내용이 변경되지 않음."""
        result = normalize_module.normalize(sample_md_no_frontmatter)
        body = result.body
        assert "docker network create my-network" in body
        assert "docker run --network my-network --name web nginx" in body

    def test_links_preserved(self, normalize_module, tmp_path):
        """내부/외부 링크와 이미지 경로가 유지됨."""
        md = tmp_path / "links.md"
        md.write_text(textwrap.dedent("""\
            # 링크 테스트

            [외부 링크](https://example.com)와 [내부 링크](/posts/hello-world/)가 있습니다.

            ![이미지](./images/test.png)

            이 문서에는 다양한 링크가 포함되어 있어서 정규화 후에도 모두 유지되어야 합니다.
        """), encoding="utf-8")
        result = normalize_module.normalize(md)
        body = result.body
        assert "https://example.com" in body
        assert "/posts/hello-world/" in body
        assert "./images/test.png" in body


class TestIdempotency:
    """정규화 멱등성 검증."""

    def test_double_normalize_produces_same_result(self, normalize_module, sample_md_no_frontmatter):
        """같은 파일을 두 번 정규화해도 결과가 동일."""
        result1 = normalize_module.normalize(sample_md_no_frontmatter)
        # 첫 번째 결과를 파일로 저장 후 다시 정규화
        normalized_path = sample_md_no_frontmatter.parent / "normalized.md"
        normalized_path.write_text(result1.to_markdown(), encoding="utf-8")
        result2 = normalize_module.normalize(normalized_path)
        assert result1.frontmatter == result2.frontmatter
        assert result1.body == result2.body


class TestEdgeCases:
    """엣지 케이스 검증."""

    def test_empty_file_handled(self, normalize_module, tmp_path):
        """빈 파일은 에러 메시지 또는 스킵."""
        md = tmp_path / "empty.md"
        md.write_text("", encoding="utf-8")
        with pytest.raises((ValueError, normalize_module.NormalizeError)):
            normalize_module.normalize(md)

    def test_short_memo_warns(self, normalize_module, sample_md_short):
        """짧은 메모는 경고를 포함하여 처리."""
        result = normalize_module.normalize(sample_md_short)
        assert result.warnings, "Short content should produce warnings"

    def test_code_only_file_handled(self, normalize_module, sample_md_code_heavy):
        """코드 블록만 있는 파일도 처리 가능."""
        result = normalize_module.normalize(sample_md_code_heavy)
        assert "title" in result.frontmatter


class TestToneGuides:
    """톤 가이드 문서 무결성 + 카테고리 보존 (퇴고는 에이전트/사람 몫)."""

    def test_tone_guide_files_exist(self):
        """공통 + 톤별 가이드 문서가 모두 존재 (퇴고 시 컨텍스트로 로드됨)."""
        docs = PROJECT_ROOT / "docs"
        for name in ("tone-guide.md", "tone-tech.md", "tone-essay.md", "tone-note.md"):
            assert (docs / name).exists(), f"docs/{name} missing"

    def test_essay_category_preserved_through_normalize(self, normalize_module, sample_md_essay):
        """에세이 카테고리가 정규화 후 유지되고 기본값으로 덮어쓰이지 않음."""
        result = normalize_module.normalize(sample_md_essay)
        assert result.frontmatter["categories"] == ["에세이"]

    def test_default_category_is_worknote(self, normalize_module, sample_md_no_frontmatter):
        """카테고리 미지정 시 기본값은 '작업노트' — 권위 프레임('기술') 대신 경험 프레임."""
        result = normalize_module.normalize(sample_md_no_frontmatter)
        assert result.frontmatter["categories"] == ["작업노트"]


class TestIntegration:
    """통합 테스트: drafts/ → content/posts/ 파이프라인."""

    def test_drafts_to_content_pipeline(self, normalize_module, sample_md_no_frontmatter, tmp_path):
        """drafts/ 폴더의 md가 content/posts/에 초안으로 생성됨."""
        drafts_dir = tmp_path / "drafts"
        output_dir = tmp_path / "posts"

        # page bundle 구조로 테스트 파일 배치
        bundle = drafts_dir / "test-pipeline"
        bundle.mkdir(parents=True)
        src = bundle / "index.md"
        src.write_text(sample_md_no_frontmatter.read_text(encoding="utf-8"), encoding="utf-8")

        result = normalize_module.process_drafts(drafts_dir, output_dir)
        assert len(result.processed) >= 1, "No files processed"

        # 생성된 파일 확인
        out_bundle = output_dir / "test-pipeline"
        assert out_bundle.exists(), "Output directory not created"
        assert (out_bundle / "index.md").exists(), "index.md not created"


class TestSkipExisting:
    """리뷰 보호: 이미 정규화된 slug는 재조립으로 덮어쓰지 않음."""

    @pytest.fixture
    def pipeline_dirs(self, sample_md_no_frontmatter, tmp_path):
        """draft 1개 + 이미 사람이 교정 중인 출력물이 있는 파이프라인 구조."""
        drafts_dir = tmp_path / "drafts"
        output_dir = tmp_path / "posts"
        bundle = drafts_dir / "reviewed-post"
        bundle.mkdir(parents=True)
        (bundle / "index.md").write_text(
            sample_md_no_frontmatter.read_text(encoding="utf-8"), encoding="utf-8"
        )
        out_bundle = output_dir / "reviewed-post"
        out_bundle.mkdir(parents=True)
        (out_bundle / "index.md").write_text("사람이 교정한 문장", encoding="utf-8")
        return drafts_dir, output_dir

    def test_existing_output_not_overwritten(self, normalize_module, pipeline_dirs):
        """출력물이 존재하면 (draft:true 리뷰 중이라도) 스킵하고 교정본을 보존."""
        drafts_dir, output_dir = pipeline_dirs
        result = normalize_module.process_drafts(drafts_dir, output_dir)
        assert [e["slug"] for e in result.skipped] == ["reviewed-post"]
        assert result.processed == []
        preserved = (output_dir / "reviewed-post" / "index.md").read_text(encoding="utf-8")
        assert preserved == "사람이 교정한 문장"

    def test_force_renormalizes_slug(self, normalize_module, pipeline_dirs):
        """--force로 지정한 slug만 명시적으로 재조립."""
        drafts_dir, output_dir = pipeline_dirs
        result = normalize_module.process_drafts(drafts_dir, output_dir, force={"reviewed-post"})
        assert [e["slug"] for e in result.processed] == ["reviewed-post"]
        assert result.skipped == []
        rewritten = (output_dir / "reviewed-post" / "index.md").read_text(encoding="utf-8")
        assert rewritten.startswith("---"), "Forced re-normalize should regenerate frontmatter"

    def test_new_slug_processed_next_to_skipped(self, normalize_module, pipeline_dirs, sample_md_no_frontmatter):
        """기존 출력이 있어도 신규 slug는 정상 처리 (부분 스킵)."""
        drafts_dir, output_dir = pipeline_dirs
        new_bundle = drafts_dir / "new-post"
        new_bundle.mkdir()
        (new_bundle / "index.md").write_text(
            sample_md_no_frontmatter.read_text(encoding="utf-8"), encoding="utf-8"
        )
        result = normalize_module.process_drafts(drafts_dir, output_dir)
        assert [e["slug"] for e in result.processed] == ["new-post"]
        assert [e["slug"] for e in result.skipped] == ["reviewed-post"]
        assert (output_dir / "new-post" / "index.md").exists()

    def test_skip_reports_asset_drift(self, normalize_module, pipeline_dirs, caplog):
        """스킵된 slug의 드래프트에 새 에셋이 있으면 조용히 무시하지 않고 표면화."""
        drafts_dir, output_dir = pipeline_dirs
        (drafts_dir / "reviewed-post" / "diagram.png").write_bytes(b"png")
        with caplog.at_level("WARNING"):
            result = normalize_module.process_drafts(drafts_dir, output_dir)
        assert result.skipped[0]["asset_drift"] == ["diagram.png"]
        assert any("asset drift" in r.message for r in caplog.records)

    def test_force_preserves_output_only_assets(self, normalize_module, pipeline_dirs, caplog):
        """force 재조립이 사람이 리뷰 중 추가한(출력에만 있는) 에셋을 지우지 않음."""
        drafts_dir, output_dir = pipeline_dirs
        (drafts_dir / "reviewed-post" / "from-draft.png").write_bytes(b"a")
        (output_dir / "reviewed-post" / "human-added.png").write_bytes(b"b")
        with caplog.at_level("WARNING"):
            normalize_module.process_drafts(drafts_dir, output_dir, force={"reviewed-post"})
        out = output_dir / "reviewed-post"
        assert (out / "human-added.png").exists(), "human-added asset must survive --force"
        assert (out / "from-draft.png").exists(), "draft asset must be (re)copied on --force"
        assert any("output-only assets preserved" in r.message for r in caplog.records)

    def test_partial_bundle_without_index_is_reprocessed(self, normalize_module, pipeline_dirs):
        """index.md 없는 부분상태 번들(에셋만 존재)은 완료로 취급하지 않고 재처리."""
        drafts_dir, output_dir = pipeline_dirs
        (output_dir / "reviewed-post" / "index.md").unlink()
        (output_dir / "reviewed-post" / "stray.png").write_bytes(b"c")
        result = normalize_module.process_drafts(drafts_dir, output_dir)
        assert [e["slug"] for e in result.processed] == ["reviewed-post"]
        assert (output_dir / "reviewed-post" / "index.md").exists()

    def test_dry_run_cli_respects_skip(self, pipeline_dirs):
        """--dry-run 프리뷰가 실제 실행과 동일하게 skip 판정을 적용 (비대칭 금지)."""
        drafts_dir, output_dir = pipeline_dirs
        proc = subprocess.run(
            [
                "python3", str(PROJECT_ROOT / "scripts" / "normalize.py"),
                "--dry-run",
                "--drafts-dir", str(drafts_dir),
                "--output-dir", str(output_dir),
            ],
            capture_output=True, text=True,
        )
        assert proc.returncode == 0, proc.stderr
        assert "skip (already normalized): reviewed-post" in proc.stdout
        assert "===" not in proc.stdout, "skipped slug must not be rendered in dry-run"


class TestMetadataPlaceholders:
    """자동 채움 필드는 침묵 확정이 아니라 warning으로 표면화 (placeholder 계약)."""

    def test_auto_filled_fields_warn(self, normalize_module, sample_md_no_frontmatter):
        """휴리스틱이 채운 SEO 필드마다 auto-filled warning이 남음."""
        result = normalize_module.normalize(sample_md_no_frontmatter)
        joined = "\n".join(result.warnings)
        for field in ("title", "description", "tags", "categories"):
            assert f"auto-filled: {field}" in joined, f"{field} fill must surface a warning"

    def test_complete_frontmatter_no_placeholder_warnings(self, normalize_module, tmp_path):
        """모든 필드가 확정된 문서는 placeholder warning 없음."""
        md = tmp_path / "complete.md"
        md.write_text(textwrap.dedent("""\
            ---
            title: "완성 제목"
            description: "충분히 긴 설명 문안이 이미 확정되어 있는 문서입니다."
            tags: ["docker", "network"]
            categories: ["작업노트"]
            date: 2026-07-01
            draft: false
            ---

            첫 문단입니다.

            둘째 문단입니다.

            셋째 문단입니다.
        """), encoding="utf-8")
        result = normalize_module.normalize(md)
        assert not any(w.startswith("auto-filled") for w in result.warnings)


class TestAssetHygiene:
    """dot-엔트리(.omc 등 런타임·에디터 상태)가 공개 posts로 복사되지 않음."""

    def test_dot_entries_not_copied(self, normalize_module, sample_md_no_frontmatter, tmp_path):
        """.omc 상태 디렉토리와 .DS_Store는 번들 조립에서 제외."""
        drafts_dir = tmp_path / "drafts"
        output_dir = tmp_path / "posts"
        bundle = drafts_dir / "with-state"
        bundle.mkdir(parents=True)
        (bundle / "index.md").write_text(
            sample_md_no_frontmatter.read_text(encoding="utf-8"), encoding="utf-8"
        )
        state = bundle / ".omc" / "state"
        state.mkdir(parents=True)
        (state / "agent-replay.jsonl").write_text("{}", encoding="utf-8")
        (bundle / ".DS_Store").write_bytes(b"junk")
        (bundle / "image.png").write_bytes(b"png")
        # 중첩 dot-엔트리: 일반 디렉토리 복사에 딸려가면 안 됨
        nested = bundle / "images" / ".cache"
        nested.mkdir(parents=True)
        (nested / "token").write_text("secret", encoding="utf-8")
        (bundle / "images" / "photo.jpg").write_bytes(b"jpg")

        normalize_module.process_drafts(drafts_dir, output_dir)
        out = output_dir / "with-state"
        assert (out / "image.png").exists(), "real asset must be copied"
        assert (out / "images" / "photo.jpg").exists(), "nested real asset must be copied"
        assert not (out / ".omc").exists(), "runtime state must never reach posts"
        assert not (out / ".DS_Store").exists()
        assert not (out / "images" / ".cache").exists(), "nested dot-entries must be excluded recursively"

    def test_drift_check_ignores_dot_entries(self, normalize_module, sample_md_no_frontmatter, tmp_path):
        """스킵 slug의 drift 검사도 dot-엔트리를 에셋으로 세지 않음."""
        drafts_dir = tmp_path / "drafts"
        output_dir = tmp_path / "posts"
        bundle = drafts_dir / "reviewed"
        bundle.mkdir(parents=True)
        (bundle / "index.md").write_text(
            sample_md_no_frontmatter.read_text(encoding="utf-8"), encoding="utf-8"
        )
        out_bundle = output_dir / "reviewed"
        out_bundle.mkdir(parents=True)
        (out_bundle / "index.md").write_text("교정본", encoding="utf-8")
        (bundle / ".omc").mkdir()

        result = normalize_module.process_drafts(drafts_dir, output_dir)
        assert result.skipped[0]["asset_drift"] == [], "dot-entries must not count as drift"

    def test_symlinks_not_dereferenced(self, normalize_module, sample_md_no_frontmatter, tmp_path):
        """symlink는 어느 깊이에서도 역참조 복사하지 않음 — 링크 대상(시크릿 등) 게시 차단."""
        secret_dir = tmp_path / "outside"
        secret_dir.mkdir()
        (secret_dir / "token").write_text("secret", encoding="utf-8")

        drafts_dir = tmp_path / "drafts"
        output_dir = tmp_path / "posts"
        bundle = drafts_dir / "with-links"
        bundle.mkdir(parents=True)
        (bundle / "index.md").write_text(
            sample_md_no_frontmatter.read_text(encoding="utf-8"), encoding="utf-8"
        )
        (bundle / "image.png").write_bytes(b"png")
        # top-level symlink (디렉토리 대상)
        (bundle / "linked-dir").symlink_to(secret_dir)
        # 중첩 symlink (파일 대상)
        sub = bundle / "images"
        sub.mkdir()
        (sub / "photo.jpg").write_bytes(b"jpg")
        (sub / "linked-file").symlink_to(secret_dir / "token")

        normalize_module.process_drafts(drafts_dir, output_dir)
        out = output_dir / "with-links"
        assert (out / "image.png").exists()
        assert (out / "images" / "photo.jpg").exists()
        assert not (out / "linked-dir").exists(), "top-level symlink must not be dereferenced"
        assert not (out / "images" / "linked-file").exists(), "nested symlink must not be dereferenced"
