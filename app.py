from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

from database.game_database import GameDatabase
from hardware.detector import HardwareDetector
from predictor.engine import RuleBasedPredictionEngine
from utils.display import (
    render_hardware_summary,
    render_prediction,
    render_search_results,
    show_banner,
    show_loading,
)
from utils.paths import resource_path


console = Console()


def choose_target(database: GameDatabase) -> dict:
    """Let the user search and select a game or creative application."""
    while True:
        query = Prompt.ask("\n[bold cyan]Search game/software[/bold cyan]").strip()
        matches = database.search(query)

        if not matches:
            console.print("[yellow]No matches found. Try GTA, Valorant, Blender, OBS, etc.[/yellow]")
            continue

        render_search_results(matches)
        choice = Prompt.ask(
            "[bold green]Choose an item number[/bold green]",
            choices=[str(index + 1) for index in range(len(matches))],
        )
        return matches[int(choice) - 1]


def main() -> None:
    show_banner()
    console.print(
        Panel.fit(
            "RunWise AI checks your laptop hardware and estimates how smoothly it can run popular games and apps.",
            title="[bold green]Text-Based Performance Advisor[/bold green]",
            border_style="green",
        )
    )

    database = GameDatabase(resource_path("data/games.json"))
    detector = HardwareDetector(console)
    engine = RuleBasedPredictionEngine()

    show_loading("Detecting laptop hardware")
    hardware = detector.detect()
    render_hardware_summary(hardware)

    while True:
        target = choose_target(database)
        show_loading(f"Analyzing {target['name']}")
        prediction = engine.predict(hardware, target)
        render_prediction(target, prediction)

        again = Prompt.ask("\n[bold cyan]Analyze another title?[/bold cyan]", choices=["y", "n"], default="y")
        if again.lower() != "y":
            console.print("\n[bold green]Thanks for using RunWise AI. Game smart.[/bold green]")
            break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[yellow]RunWise AI closed by user.[/yellow]")
    except Exception as exc:
        console.print(f"\n[bold red]Unexpected error:[/bold red] {exc}")
        console.print("[dim]Tip: install requirements and run again with Python 3.10+.[/dim]")
