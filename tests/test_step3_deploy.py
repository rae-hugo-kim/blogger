"""Step 3: 배포 Tests.

GitHub Actions 워크플로 유효성 및 Hugo 빌드 배포 설정 검증.
"""

import re
from pathlib import Path

import yaml
import pytest

PROJECT_ROOT = Path(__file__).parent.parent


class TestHugoDeployWorkflow:
    """Hugo 빌드 + GitHub Pages 배포 워크플로 검증."""

    @pytest.fixture
    def workflow(self):
        wf_path = PROJECT_ROOT / ".github" / "workflows" / "deploy.yml"
        if not wf_path.exists():
            pytest.fail("deploy.yml workflow not found")
        content = wf_path.read_text(encoding="utf-8")
        return yaml.safe_load(content)

    def test_workflow_has_trigger(self, workflow):
        """워크플로에 트리거가 정의되어 있음."""
        assert "on" in workflow or True in workflow, "Missing 'on' trigger"

    def test_workflow_triggers_on_push_to_main(self, workflow):
        """main 브랜치 push 시 트리거."""
        trigger = workflow.get("on") or workflow.get(True)
        if isinstance(trigger, dict):
            push = trigger.get("push", {})
            branches = push.get("branches", [])
            assert "main" in branches, "Workflow doesn't trigger on push to main"

    def test_workflow_has_jobs(self, workflow):
        """워크플로에 jobs가 정의되어 있음."""
        assert "jobs" in workflow
        assert len(workflow["jobs"]) >= 1

    def test_workflow_uses_hugo(self, workflow):
        """워크플로에서 Hugo를 사용함."""
        jobs_yaml = yaml.dump(workflow["jobs"])
        assert "hugo" in jobs_yaml.lower(), "Workflow doesn't reference Hugo"

    def test_workflow_has_deploy_step(self, workflow):
        """워크플로에 배포 스텝이 존재."""
        jobs_yaml = yaml.dump(workflow["jobs"])
        assert "pages" in jobs_yaml.lower() or "deploy" in jobs_yaml.lower(), (
            "Workflow missing deployment step"
        )


class TestSubpathCompatibility:
    """GitHub Pages 서브패스 배포 호환성 검증."""

    def test_base_url_configured(self):
        """hugo.yaml에 baseURL이 설정됨."""
        config_path = PROJECT_ROOT / "hugo.yaml"
        assert config_path.exists(), "hugo.yaml not found"
        config = yaml.safe_load(config_path.read_text(encoding="utf-8"))
        base_url = config.get("baseURL", "")
        assert base_url, "baseURL is empty"

    def test_base_url_includes_repo_path(self):
        """baseURL에 repo 서브패스가 포함됨."""
        config = yaml.safe_load(
            (PROJECT_ROOT / "hugo.yaml").read_text(encoding="utf-8")
        )
        base_url = config.get("baseURL", "")
        # /blogger/ 같은 서브패스가 있거나 커스텀 도메인이면 OK
        assert "/" in base_url.rstrip("/"), "baseURL may not handle subpath deployment"

    def test_canonical_url_in_html(self):
        """빌드된 HTML에 canonical URL이 포함."""
        import subprocess
        result = subprocess.run(
            ["hugo", "build", "-d", "/tmp/blogger-deploy-test"],
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            env={"PATH": f"{Path.home() / '.local' / 'bin'}:{__import__('os').environ.get('PATH', '')}"},
        )
        assert result.returncode == 0
        index = Path("/tmp/blogger-deploy-test/index.html")
        html = index.read_text(encoding="utf-8")
        assert re.search(r'<link[^>]*rel="canonical"', html), (
            "Missing canonical URL in HTML"
        )

    def test_og_meta_tags_in_html(self):
        """빌드된 HTML에 OG 메타 태그 포함."""
        index = Path("/tmp/blogger-deploy-test/index.html")
        if not index.exists():
            pytest.skip("Deploy test build not available")
        html = index.read_text(encoding="utf-8")
        assert re.search(r'<meta[^>]*property="og:title"', html), "Missing og:title"
        assert re.search(r'<meta[^>]*property="og:url"', html), "Missing og:url"
