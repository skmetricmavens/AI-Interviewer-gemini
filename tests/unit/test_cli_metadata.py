"""Tests for interview CLI metadata options (--interviewee, --pillar, etc.)."""

import typer
import typer.testing
import pytest

from app import app


@pytest.fixture()
def runner() -> typer.testing.CliRunner:
    """Create a Typer CliRunner for invoking commands."""
    return typer.testing.CliRunner()


class TestInterviewMetadataOptions:
    """Verify interview command exposes new metadata options in help."""

    def test_help_shows_interviewee_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["interview", "--help"])
        assert "--interviewee" in result.output

    def test_help_shows_pillar_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["interview", "--help"])
        assert "--pillar" in result.output

    def test_help_shows_architecture_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["interview", "--help"])
        assert "--architecture" in result.output

    def test_help_shows_audience_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["interview", "--help"])
        assert "--audience" in result.output

    def test_all_options_are_optional(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """Interview should still only require --topic (metadata is optional)."""
        result = runner.invoke(app, ["interview", "--help"])
        # topic is required, metadata options are not
        assert result.exit_code == 0
