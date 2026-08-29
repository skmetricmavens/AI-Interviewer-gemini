"""Tests that verify project scaffolding for task-1 exists correctly."""

from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class TestPyprojectToml:
    """Verify pyproject.toml exists and contains key dependencies."""

    def test_pyproject_toml_exists(self) -> None:
        assert (PROJECT_ROOT / "pyproject.toml").is_file()

    @pytest.mark.parametrize(
        "dependency",
        [
            "pipecat-ai",
            "google-genai",
            "anthropic",
            "elevenlabs",
            "typer",
            "rich",
            "python-dotenv",
            "aiosqlite",
        ],
    )
    def test_pyproject_contains_dependency(self, dependency: str) -> None:
        content = (PROJECT_ROOT / "pyproject.toml").read_text()
        assert dependency in content, f"Missing dependency: {dependency}"


class TestDirectoryStructure:
    """Verify required directories exist."""

    @pytest.mark.parametrize(
        "directory",
        [
            "src",
            "src/interview",
            "src/writing",
            "src/storage",
            "src/persona",
            "persona/samples",
            "tests",
        ],
    )
    def test_directory_exists(self, directory: str) -> None:
        assert (PROJECT_ROOT / directory).is_dir(), f"Missing directory: {directory}"


class TestInitFiles:
    """Verify __init__.py files exist in required packages."""

    @pytest.mark.parametrize(
        "package",
        [
            "src",
            "src/interview",
            "src/writing",
            "src/storage",
            "src/persona",
        ],
    )
    def test_init_file_exists(self, package: str) -> None:
        init_path = PROJECT_ROOT / package / "__init__.py"
        assert init_path.is_file(), f"Missing __init__.py in {package}"


class TestConftest:
    """Verify tests/conftest.py exists."""

    def test_conftest_exists(self) -> None:
        assert (PROJECT_ROOT / "tests" / "conftest.py").is_file()
