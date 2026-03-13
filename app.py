"""AI Content Interviewer — Typer CLI entrypoint."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from src.config import load_settings
from src.persona.analyzer import PersonaAnalyzer
from src.storage.db import SessionStore
from src.storage.exporter import TranscriptExporter
from src.topics.evergreen import get_topics
from src.writing.blueprint import BlueprintGenerator
from src.writing.humanizer import ContentHumanizer
from src.writing.templates import format_instructions

app = typer.Typer(
    name="ai-interviewer",
    help="Voice-first CLI tool for conducting interviews and generating content.",
    invoke_without_command=True,
)
console = Console()


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context) -> None:
    """AI Content Interviewer — voice-first interview & content generation."""
    if ctx.invoked_subcommand is None:
        console.print(ctx.get_help())


@app.command()
def interview(
    topic: str = typer.Option(..., help="Interview topic"),
    context: Optional[str] = typer.Option(None, help="Path to context file"),
    language: str = typer.Option("auto", help="Language: en, nl, or auto"),
    interviewee: Optional[str] = typer.Option(None, help="Interviewee name (e.g. Sandy, Julian)"),
    pillar: Optional[str] = typer.Option(
        None,
        help="Content pillar: connected_journey, crm_intelligence, "
        "building_smart, people_not_prompts, field_notes",
    ),
    architecture: Optional[str] = typer.Option(
        None,
        help="Article architecture: inverted_pyramid, narrative_arc, pillar_cluster",
    ),
    audience: Optional[str] = typer.Option(
        None,
        help="Target audience: crm_managers, performance_marketers, marketing_leaders, c_suite",
    ),
    prep: Optional[str] = typer.Option(
        None,
        help="Path to a prep file with prepared interview questions",
    ),
) -> None:
    """Start a voice interview session."""
    settings = load_settings()
    settings.validate()

    context_text: str | None = None
    if context:
        context_path = Path(context)
        if not context_path.exists():
            console.print(f"[red]Context file not found: {context}[/red]")
            raise typer.Exit(1)
        context_text = context_path.read_text()

    # Load prepared questions from prep file
    prepared_questions: list[str] | None = None
    if prep:
        from src.interview.prep import parse_prep_file

        prep_path = Path(prep)
        if not prep_path.exists():
            console.print(f"[red]Prep file not found: {prep}[/red]")
            raise typer.Exit(1)
        prep_data = parse_prep_file(str(prep_path))
        if prep_data.questions:
            prepared_questions = prep_data.questions
            console.print(
                f"[cyan]Loaded {len(prepared_questions)} prepared questions from {prep}[/cyan]"
            )

    async def _run() -> None:
        from src.interview.pipecat_bot import InterviewBot

        store = SessionStore(settings.db_path)
        await store.connect()

        bot = InterviewBot(settings=settings, store=store)
        session_id = await bot.start_session(
            topic=topic,
            context_text=context_text,
            language=language,
            interviewee_name=interviewee,
            content_pillar=pillar,
            target_architecture=architecture,
            target_audience=audience,
            prepared_questions=prepared_questions,
        )

        info_lines = [f"Topic: {topic}", f"Language: {language}"]
        if interviewee:
            info_lines.append(f"Interviewee: {interviewee}")
        if pillar:
            info_lines.append(f"Pillar: {pillar}")
        if architecture:
            info_lines.append(f"Architecture: {architecture}")
        if audience:
            info_lines.append(f"Audience: {audience}")
        if prepared_questions:
            info_lines.append(f"Prepared questions: {len(prepared_questions)}")
        info_lines.append(f"Session: {session_id}")
        console.print(Panel("\n".join(info_lines), title="Interview Started"))

        try:
            await bot.run()
        finally:
            await bot.stop_session()
            await store.close()
            console.print("[green]Interview session ended.[/green]")

    asyncio.run(_run())


@app.command()
def write(
    session_id: str = typer.Option(..., help="Session ID to generate content from"),
    format: str = typer.Option(
        "linkedin",
        help="Output format: linkedin, blog, inverted_pyramid, narrative_arc, or pillar_cluster",
    ),
    language: str = typer.Option("en", help="Output language: en or nl"),
) -> None:
    """Generate content from a past interview session."""
    settings = load_settings()
    settings.validate()

    async def _run() -> str:
        store = SessionStore(settings.db_path)
        await store.connect()

        transcript = await store.get_session_transcript(session_id)
        await store.close()

        if not transcript:
            console.print(f"[red]No transcript found for session: {session_id}[/red]")
            raise typer.Exit(1)

        fingerprint_path = Path("persona/fingerprint.json")
        if not fingerprint_path.exists():
            console.print("[red]No fingerprint found. Run 'persona-analyze' first.[/red]")
            raise typer.Exit(1)

        analyzer = PersonaAnalyzer(anthropic_api_key=settings.anthropic_api_key)
        fingerprint = analyzer.load_fingerprint(str(fingerprint_path))

        format_instructions(format)  # validates format_type
        humanizer = ContentHumanizer(
            anthropic_api_key=settings.anthropic_api_key,
            model=settings.claude_model,
        )

        content = humanizer.generate(
            transcript=transcript,
            fingerprint=fingerprint,
            format_type=format,
            language=language,
        )
        return content

    content = asyncio.run(_run())
    console.print(Panel(content, title=f"{format.title()} Post"))


@app.command()
def persona_analyze(
    samples_dir: str = typer.Option("persona/samples", help="Directory with writing samples"),
    output: str = typer.Option("persona/fingerprint.json", help="Output path for fingerprint"),
) -> None:
    """Analyze writing samples and generate a style fingerprint."""
    settings = load_settings()
    settings.validate()

    samples_path = Path(samples_dir)
    if not samples_path.exists():
        console.print(f"[red]Samples directory not found: {samples_dir}[/red]")
        raise typer.Exit(1)

    analyzer = PersonaAnalyzer(anthropic_api_key=settings.anthropic_api_key)

    with console.status("Analyzing writing samples..."):
        fingerprint = analyzer.analyze_samples(samples_dir)

    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    analyzer.save_fingerprint(fingerprint, str(output_path))

    console.print(f"[green]Fingerprint saved to {output}[/green]")
    console.print(Panel(str(fingerprint), title="Linguistic Fingerprint"))


@app.command()
def sessions_list() -> None:
    """List past interview sessions."""
    settings = load_settings()

    async def _run() -> list[dict]:
        store = SessionStore(settings.db_path)
        await store.connect()
        sessions = await store.list_sessions()
        await store.close()
        return sessions  # type: ignore[return-value]

    sessions = asyncio.run(_run())

    if not sessions:
        console.print("[yellow]No sessions found.[/yellow]")
        return

    table = Table(title="Interview Sessions")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Topic", style="green")
    table.add_column("Language")
    table.add_column("Started")
    table.add_column("Ended")

    for s in sessions:
        table.add_row(
            str(s["id"])[:8] + "...",
            str(s["topic"]),
            str(s["language"]),
            str(s["started_at"])[:19],
            str(s["ended_at"])[:19] if s["ended_at"] else "In progress",
        )

    console.print(table)


@app.command()
def blueprint(
    session_id: str = typer.Option(..., help="Session ID"),
    architecture: str = typer.Option("inverted_pyramid", help="Architecture type"),
    pillar: Optional[str] = typer.Option(None, help="Content pillar"),
    audience: Optional[str] = typer.Option(None, help="Target audience"),
    language: str = typer.Option("en", help="Language: en or nl"),
) -> None:
    """Generate an article blueprint from a past interview session."""
    settings = load_settings()
    settings.validate()

    async def _run() -> str:
        store = SessionStore(settings.db_path)
        await store.connect()

        transcript = await store.get_session_transcript(session_id)
        await store.close()

        if not transcript:
            console.print(f"[red]No transcript found for session: {session_id}[/red]")
            raise typer.Exit(1)

        gen = BlueprintGenerator(
            anthropic_api_key=settings.anthropic_api_key,
            model=settings.claude_model,
        )

        bp = gen.generate(
            transcript=transcript,
            architecture=architecture,
            content_pillar=pillar or "",
            target_audience=audience or "",
            language=language,
        )
        return bp.to_markdown()

    md = asyncio.run(_run())
    console.print(Panel(md, title="Article Blueprint"))


@app.command()
def export(
    session_id: str = typer.Option(..., help="Session ID"),
    output_dir: str = typer.Option("exports", help="Output directory"),
    format: str = typer.Option("markdown", help="Export format: markdown, plain_text, or json"),
) -> None:
    """Export a session transcript to a file."""
    settings = load_settings()

    async def _run() -> str:
        store = SessionStore(settings.db_path)
        await store.connect()

        transcript = await store.get_session_transcript(session_id)
        metadata = await store.get_session_metadata(session_id)
        await store.close()

        if not transcript:
            console.print(f"[red]No transcript found for session: {session_id}[/red]")
            raise typer.Exit(1)

        exporter = TranscriptExporter()
        file_path = exporter.save(
            transcript=transcript,
            output_dir=output_dir,
            session_id=session_id,
            format=format,
            session_metadata=metadata,
        )
        return file_path

    path = asyncio.run(_run())
    console.print(f"[green]Exported to {path}[/green]")


@app.command()
def topics(
    pillar: str = typer.Option(..., help="Content pillar"),
    count: int = typer.Option(3, help="Number of topics to suggest"),
    language: str = typer.Option("en", help="Language: en or nl"),
    suggest: bool = typer.Option(False, help="Use AI to suggest new topics"),
) -> None:
    """List or suggest interview topics for a content pillar."""
    if not suggest:
        try:
            topic_list = get_topics(pillar)
        except ValueError as e:
            console.print(f"[red]{e}[/red]")
            raise typer.Exit(1) from e

        console.print(f"[bold]Evergreen topics for '{pillar}':[/bold]\n")
        for t in topic_list:
            console.print(f"  - {t}")
        return

    settings = load_settings()
    settings.validate()

    from src.topics.generator import TopicGenerator

    gen = TopicGenerator(
        anthropic_api_key=settings.anthropic_api_key,
        model=settings.claude_model,
    )
    suggested = gen.suggest(pillar=pillar, count=count, language=language)

    console.print(f"[bold]Suggested topics for '{pillar}':[/bold]\n")
    for t in suggested:
        console.print(f"  - {t}")


@app.command()
def prepare(
    topic: str = typer.Option(..., help="Interview topic"),
    pillar: Optional[str] = typer.Option(
        None,
        help="Content pillar: connected_journey, crm_intelligence, "
        "building_smart, people_not_prompts, field_notes",
    ),
    audience: Optional[str] = typer.Option(None, help="Target audience"),
    architecture: Optional[str] = typer.Option(
        None,
        help="Article architecture: inverted_pyramid, narrative_arc, pillar_cluster",
    ),
    language: str = typer.Option("en", help="Language: en or nl"),
    interviewee: Optional[str] = typer.Option(None, help="Interviewee name"),
    suggest: bool = typer.Option(
        False,
        help="Use AI to suggest interview questions",
    ),
    output_dir: str = typer.Option("interviews", help="Output directory for prep files"),
) -> None:
    """Create an interview preparation file with questions."""
    from src.interview.prep import InterviewPrep, QuestionGenerator, write_prep_file

    questions: list[str] = []

    if suggest:
        settings = load_settings()
        settings.validate()

        gen = QuestionGenerator(
            anthropic_api_key=settings.anthropic_api_key,
            model=settings.claude_model,
        )
        with console.status("Generating interview questions..."):
            questions = gen.generate(
                topic=topic,
                pillar=pillar or "",
                audience=audience or "",
                language=language,
            )
        console.print(f"[green]Generated {len(questions)} questions[/green]")

    prep = InterviewPrep(
        topic=topic,
        pillar=pillar or "",
        audience=audience or "",
        architecture=architecture or "",
        language=language,
        interviewee=interviewee or "",
        questions=questions,
    )

    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    safe_topic = topic.lower().replace(" ", "_")[:40]
    file_path = out_path / f"prep_{safe_topic}.md"

    write_prep_file(prep, str(file_path))
    console.print(f"[green]Prep file created: {file_path}[/green]")
    console.print(
        "[cyan]Edit the file to add/modify questions, then run:[/cyan]\n"
        f"  [bold]ai-interviewer interview --topic '{topic}' --prep {file_path}[/bold]"
    )


if __name__ == "__main__":
    app()
