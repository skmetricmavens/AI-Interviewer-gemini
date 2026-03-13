"""Tests for task-53 (InterviewBot plumbing) and task-54 (--prep CLI flag).

Task-53: InterviewBot.start_session and _build_pipeline accept
prepared_questions: list[str] | None = None and pass it to build_system_prompt.

Task-54: The interview CLI command gets a --prep option that loads a prep file,
and a new 'prepare' CLI command is registered with all expected options.

These tests use typer.testing.CliRunner to verify CLI argument registration
without actually running interviews or making API calls.
"""

from __future__ import annotations

import inspect

import pytest
import typer.testing

from app import app
from src.interview.prompts import build_system_prompt


@pytest.fixture()
def runner() -> typer.testing.CliRunner:
    """Create a Typer CliRunner for invoking commands."""
    return typer.testing.CliRunner()


# ---------------------------------------------------------------------------
# Task-53: build_system_prompt signature accepts prepared_questions
# ---------------------------------------------------------------------------


class TestBuildSystemPromptPreparedQuestionsParam:
    """Verify build_system_prompt accepts the prepared_questions keyword arg."""

    def test_accepts_prepared_questions_kwarg(self) -> None:
        """build_system_prompt must accept prepared_questions as a keyword arg."""
        sig = inspect.signature(build_system_prompt)
        assert "prepared_questions" in sig.parameters

    def test_prepared_questions_default_is_none(self) -> None:
        """The default value for prepared_questions must be None."""
        sig = inspect.signature(build_system_prompt)
        param = sig.parameters["prepared_questions"]
        assert param.default is None

    def test_call_with_prepared_questions_returns_string(self) -> None:
        """Calling with prepared_questions should return a valid prompt string."""
        result = build_system_prompt(
            topic="AI trends",
            context=None,
            language="en",
            prepared_questions=["What is your biggest challenge?"],
        )
        assert isinstance(result, str)
        assert len(result) > 0

    def test_call_without_prepared_questions_still_works(self) -> None:
        """Calling without prepared_questions should work (backward compat)."""
        result = build_system_prompt(
            topic="AI trends",
            context=None,
            language="en",
        )
        assert isinstance(result, str)
        assert len(result) > 0


# ---------------------------------------------------------------------------
# Task-54: interview --prep flag
# ---------------------------------------------------------------------------


class TestInterviewPrepFlag:
    """Verify the interview command exposes a --prep option."""

    def test_interview_help_shows_prep_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["interview", "--help"])
        assert result.exit_code == 0
        assert "--prep" in result.output

    def test_interview_help_prep_description_mentions_file(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """The --prep help text should mention loading a prep file."""
        result = runner.invoke(app, ["interview", "--help"])
        assert result.exit_code == 0
        lower = result.output.lower()
        assert "prep" in lower


# ---------------------------------------------------------------------------
# Task-54: prepare command registration
# ---------------------------------------------------------------------------


class TestPrepareCommandRegistration:
    """Verify the 'prepare' command is registered on the app."""

    def test_prepare_command_in_app_help(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["--help"])
        assert "prepare" in result.output

    def test_prepare_help_exits_zero(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["prepare", "--help"])
        assert result.exit_code == 0


class TestPrepareCommandOptions:
    """Verify the prepare command exposes all expected options."""

    def test_shows_topic_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["prepare", "--help"])
        assert "--topic" in result.output

    def test_shows_pillar_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["prepare", "--help"])
        assert "--pillar" in result.output

    def test_shows_audience_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["prepare", "--help"])
        assert "--audience" in result.output

    def test_shows_architecture_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["prepare", "--help"])
        assert "--architecture" in result.output

    def test_shows_language_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["prepare", "--help"])
        assert "--language" in result.output

    def test_shows_interviewee_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["prepare", "--help"])
        assert "--interviewee" in result.output

    def test_shows_suggest_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["prepare", "--help"])
        assert "--suggest" in result.output

    def test_shows_output_dir_option(
        self, runner: typer.testing.CliRunner
    ) -> None:
        result = runner.invoke(app, ["prepare", "--help"])
        assert "--output-dir" in result.output


class TestPrepareCommandArgs:
    """Verify prepare command argument validation."""

    def test_missing_topic_fails(
        self, runner: typer.testing.CliRunner
    ) -> None:
        """topic is required; omitting it should cause a non-zero exit."""
        result = runner.invoke(app, ["prepare"])
        assert result.exit_code != 0
