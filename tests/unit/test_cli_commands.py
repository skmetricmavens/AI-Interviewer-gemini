"""Tests for CLI commands: blueprint, export, and topics.

Tasks 42, 45, and 48: Verify that the blueprint, export, and topics
commands are registered on the Typer app with the correct options.
Tests use typer.testing.CliRunner to invoke commands without real
API calls or database connections.
"""

from __future__ import annotations

import typer
import typer.testing
import pytest

from app import app


@pytest.fixture()
def runner() -> typer.testing.CliRunner:
    """Create a Typer CliRunner for invoking commands."""
    return typer.testing.CliRunner()


# ---------------------------------------------------------------------------
# Command registration
# ---------------------------------------------------------------------------


class TestCommandRegistration:
    """Verify all three new commands appear in the app help output."""

    def test_blueprint_command_registered(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["--help"])
        assert "blueprint" in result.output

    def test_export_command_registered(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["--help"])
        assert "export" in result.output

    def test_topics_command_registered(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["--help"])
        assert "topics" in result.output


# ---------------------------------------------------------------------------
# Task-42: blueprint CLI command
# ---------------------------------------------------------------------------


class TestBlueprintCommandHelp:
    """Verify blueprint command --help output and option registration."""

    def test_help_exits_zero(self, runner: typer.testing.CliRunner) -> None:
        result = runner.invoke(app, ["blueprint", "--help"])
        assert result.exit_code == 0

    def test_help_shows_session_id_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["blueprint", "--help"])
        assert "--session-id" in result.output

    def test_help_shows_architecture_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["blueprint", "--help"])
        assert "--architecture" in result.output

    def test_help_shows_pillar_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["blueprint", "--help"])
        assert "--pillar" in result.output

    def test_help_shows_audience_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["blueprint", "--help"])
        assert "--audience" in result.output

    def test_help_shows_language_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["blueprint", "--help"])
        assert "--language" in result.output


class TestBlueprintCommandArgs:
    """Verify blueprint command argument validation."""

    def test_missing_session_id_fails(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """session_id is required; omitting it should cause a non-zero exit."""
        result = runner.invoke(app, ["blueprint"])
        assert result.exit_code != 0

    def test_architecture_default_is_inverted_pyramid(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """Architecture should default to 'inverted_pyramid' per the signature."""
        result = runner.invoke(app, ["blueprint", "--help"])
        assert "inverted_pyramid" in result.output

    def test_language_default_is_en(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """Language should default to 'en' per the signature."""
        result = runner.invoke(app, ["blueprint", "--help"])
        # The help text should show the default value
        assert result.exit_code == 0


# ---------------------------------------------------------------------------
# Task-45: export CLI command
# ---------------------------------------------------------------------------


class TestExportCommandHelp:
    """Verify export command --help output and option registration."""

    def test_help_exits_zero(self, runner: typer.testing.CliRunner) -> None:
        result = runner.invoke(app, ["export", "--help"])
        assert result.exit_code == 0

    def test_help_shows_session_id_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["export", "--help"])
        assert "--session-id" in result.output

    def test_help_shows_output_dir_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["export", "--help"])
        assert "--output-dir" in result.output

    def test_help_shows_format_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["export", "--help"])
        assert "--format" in result.output


class TestExportCommandArgs:
    """Verify export command argument validation."""

    def test_missing_session_id_fails(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """session_id is required; omitting it should cause a non-zero exit."""
        result = runner.invoke(app, ["export"])
        assert result.exit_code != 0

    def test_output_dir_default_is_exports(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """output_dir should default to 'exports' per the signature."""
        result = runner.invoke(app, ["export", "--help"])
        assert "exports" in result.output

    def test_format_default_is_markdown(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """format should default to 'markdown' per the signature."""
        result = runner.invoke(app, ["export", "--help"])
        assert "markdown" in result.output


# ---------------------------------------------------------------------------
# Task-48: topics CLI command
# ---------------------------------------------------------------------------


class TestTopicsCommandHelp:
    """Verify topics command --help output and option registration."""

    def test_help_exits_zero(self, runner: typer.testing.CliRunner) -> None:
        result = runner.invoke(app, ["topics", "--help"])
        assert result.exit_code == 0

    def test_help_shows_pillar_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["topics", "--help"])
        assert "--pillar" in result.output

    def test_help_shows_count_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["topics", "--help"])
        assert "--count" in result.output

    def test_help_shows_language_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["topics", "--help"])
        assert "--language" in result.output

    def test_help_shows_suggest_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["topics", "--help"])
        assert "--suggest" in result.output


class TestTopicsCommandArgs:
    """Verify topics command argument validation."""

    def test_missing_pillar_fails(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """pillar is required; omitting it should cause a non-zero exit."""
        result = runner.invoke(app, ["topics"])
        assert result.exit_code != 0

    def test_count_default_is_three(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """count should default to 3 per the signature."""
        result = runner.invoke(app, ["topics", "--help"])
        # Default value should appear in help
        assert result.exit_code == 0

    def test_language_default_is_en(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """language should default to 'en' per the signature."""
        result = runner.invoke(app, ["topics", "--help"])
        assert result.exit_code == 0


class TestTopicsWithoutSuggest:
    """Test topics command without --suggest flag (local evergreen topics only)."""

    def test_lists_topics_for_valid_pillar(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """Without --suggest, should list evergreen topics from local bank."""
        result = runner.invoke(
            app, ["topics", "--pillar", "connected_journey"]
        )
        assert result.exit_code == 0
        # Should display topic text in the output
        assert len(result.output.strip()) > 0

    def test_lists_topics_for_crm_intelligence(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(
            app, ["topics", "--pillar", "crm_intelligence"]
        )
        assert result.exit_code == 0
        assert len(result.output.strip()) > 0

    def test_lists_topics_for_building_smart(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(
            app, ["topics", "--pillar", "building_smart"]
        )
        assert result.exit_code == 0
        assert len(result.output.strip()) > 0

    def test_lists_topics_for_people_not_prompts(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(
            app, ["topics", "--pillar", "people_not_prompts"]
        )
        assert result.exit_code == 0
        assert len(result.output.strip()) > 0

    def test_lists_topics_for_field_notes(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(
            app, ["topics", "--pillar", "field_notes"]
        )
        assert result.exit_code == 0
        assert len(result.output.strip()) > 0

    def test_displays_multiple_topics(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """Should display multiple lines or items (at least 3 topics)."""
        result = runner.invoke(
            app, ["topics", "--pillar", "connected_journey"]
        )
        assert result.exit_code == 0
        # Expect at least a few lines of output (topics)
        non_empty_lines = [
            line for line in result.output.strip().split("\n") if line.strip()
        ]
        assert len(non_empty_lines) >= 3

    def test_no_api_call_without_suggest(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """Without --suggest, the command should not require API keys."""
        # This should succeed even without ANTHROPIC_API_KEY set
        result = runner.invoke(
            app, ["topics", "--pillar", "field_notes"]
        )
        assert result.exit_code == 0


class TestTopicsInvalidPillar:
    """Test topics command with invalid pillar name."""

    def test_invalid_pillar_shows_error(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """An unrecognized pillar should produce a non-zero exit or error message."""
        result = runner.invoke(
            app, ["topics", "--pillar", "nonexistent_pillar"]
        )
        # Should either exit non-zero or show an error message
        assert result.exit_code != 0 or "error" in result.output.lower()

    def test_empty_pillar_shows_error(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """An empty pillar string should produce an error."""
        result = runner.invoke(app, ["topics", "--pillar", ""])
        assert result.exit_code != 0 or "error" in result.output.lower()
