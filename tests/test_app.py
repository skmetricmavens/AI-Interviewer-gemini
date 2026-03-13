"""Tests for app.py — Typer CLI entrypoint.

Verifies that CLI commands are registered, help text works,
and basic argument validation behaves correctly.
Does NOT invoke actual interviews or API calls.
"""

import typer
import typer.testing
import pytest

from app import app


@pytest.fixture()
def runner() -> typer.testing.CliRunner:
    """Create a Typer CliRunner for invoking commands."""
    return typer.testing.CliRunner()


class TestAppInstance:
    """Verify the app object is a proper Typer instance."""

    def test_app_is_typer_instance(self) -> None:
        assert isinstance(app, typer.Typer)


class TestNoCommandShowsHelp:
    """Invoking the CLI with no command should show help."""

    def test_no_args_exits_zero(self, runner: typer.testing.CliRunner) -> None:
        result = runner.invoke(app, [])
        assert result.exit_code == 0


class TestInterviewCommand:
    """Tests for the 'interview' command."""

    def test_interview_help_exits_zero(self, runner: typer.testing.CliRunner) -> None:
        result = runner.invoke(app, ["interview", "--help"])
        assert result.exit_code == 0

    def test_interview_help_shows_topic_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["interview", "--help"])
        assert "--topic" in result.output

    def test_interview_help_shows_language_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["interview", "--help"])
        assert "--language" in result.output

    def test_interview_help_shows_context_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["interview", "--help"])
        assert "--context" in result.output

    def test_interview_without_topic_fails(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """topic is required; omitting it should cause a non-zero exit."""
        result = runner.invoke(app, ["interview"])
        assert result.exit_code != 0


class TestWriteCommand:
    """Tests for the 'write' command."""

    def test_write_help_exits_zero(self, runner: typer.testing.CliRunner) -> None:
        result = runner.invoke(app, ["write", "--help"])
        assert result.exit_code == 0

    def test_write_help_shows_session_id_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["write", "--help"])
        assert "--session-id" in result.output

    def test_write_help_shows_format_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["write", "--help"])
        assert "--format" in result.output

    def test_write_help_shows_language_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["write", "--help"])
        assert "--language" in result.output


class TestPersonaAnalyzeCommand:
    """Tests for the 'persona-analyze' command."""

    def test_persona_analyze_help_exits_zero(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["persona-analyze", "--help"])
        assert result.exit_code == 0

    def test_persona_analyze_help_shows_samples_dir_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["persona-analyze", "--help"])
        assert "--samples-dir" in result.output

    def test_persona_analyze_help_shows_output_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["persona-analyze", "--help"])
        assert "--output" in result.output


class TestSessionsListCommand:
    """Tests for the sessions list command."""

    def test_sessions_list_help_exits_zero(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """Try both possible command names for listing sessions."""
        result = runner.invoke(app, ["sessions-list", "--help"])
        if result.exit_code != 0:
            # Might be registered as just 'sessions'
            result = runner.invoke(app, ["sessions", "--help"])
        assert result.exit_code == 0


class TestCommandRegistration:
    """Verify all expected commands are registered on the app."""

    def test_has_interview_command(self, runner: typer.testing.CliRunner) -> None:
        result = runner.invoke(app, ["--help"])
        assert "interview" in result.output

    def test_has_write_command(self, runner: typer.testing.CliRunner) -> None:
        result = runner.invoke(app, ["--help"])
        assert "write" in result.output

    def test_has_persona_analyze_command(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["--help"])
        # Typer converts underscores to hyphens in command names
        assert "persona-analyze" in result.output

    def test_has_sessions_command(self, runner: typer.testing.CliRunner) -> None:
        result = runner.invoke(app, ["--help"])
        # Could be 'sessions-list' or 'sessions'
        assert "sessions" in result.output
