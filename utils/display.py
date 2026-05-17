from __future__ import annotations

from time import sleep

from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn
from rich.table import Table

from hardware.models import HardwareProfile
from predictor.models import PredictionResult


console = Console()


def show_banner() -> None:
    console.print(
        Panel(
            "[bold green]RunWise AI[/bold green]\n[white]Laptop Game & Software Performance Predictor[/white]",
            border_style="bright_green",
            box=box.DOUBLE,
        )
    )


def show_loading(message: str) -> None:
    with Progress(
        SpinnerColumn(style="green"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=28, complete_style="green"),
        TimeElapsedColumn(),
        transient=True,
        console=console,
    ) as progress:
        task = progress.add_task(message, total=100)
        for _ in range(10):
            sleep(0.08)
            progress.advance(task, 10)


def render_hardware_summary(hardware: HardwareProfile) -> None:
    table = Table(title="System Summary", box=box.ROUNDED, border_style="cyan")
    table.add_column("Component", style="bold cyan")
    table.add_column("Detected Value", style="white")
    table.add_column("Score", justify="right", style="green")

    scores = {
        "CPU": hardware.cpu_score,
        "RAM": hardware.ram_score,
        "GPU": hardware.gpu_score,
        "Storage": hardware.storage_score,
    }

    for component, value in hardware.as_dict().items():
        table.add_row(component, value, str(scores.get(component, "-")))

    console.print(table)


def render_search_results(matches: list[dict]) -> None:
    table = Table(title="Search Results", box=box.SIMPLE_HEAVY, border_style="green")
    table.add_column("#", justify="right", style="bold green")
    table.add_column("Name", style="bold white")
    table.add_column("Type", style="cyan")
    table.add_column("Demand", style="yellow")

    for index, item in enumerate(matches, start=1):
        table.add_row(str(index), item["name"], item["type"], item["performance_class"].title())

    console.print(table)


def render_prediction(target: dict, prediction: PredictionResult) -> None:
    table = Table(title=f"RunWise Prediction: {target['name']}", box=box.ROUNDED, border_style="magenta")
    table.add_column("Metric", style="bold cyan")
    table.add_column("Result", style="white")

    table.add_row("Compatibility Score", f"{prediction.compatibility_score}/100")
    table.add_row("Estimated FPS / Smoothness", str(prediction.estimated_fps))
    table.add_row("Lag Chance", _category_style(prediction.lag_chance))
    table.add_row("Battery Drain", _category_style(prediction.battery_drain))
    table.add_row("Thermal Stress", _category_style(prediction.thermal_stress))
    table.add_row("Recommended Settings", prediction.recommended_settings)

    console.print(table)

    notes = "\n".join(f"- {note}" for note in prediction.notes)
    console.print(Panel(notes, title="Notes", border_style="yellow"))


def _category_style(value: str) -> str:
    colors = {
        "Low": "green",
        "Mild": "green",
        "Cool": "green",
        "Medium": "yellow",
        "Moderate": "yellow",
        "Warm": "yellow",
        "High": "red",
        "Heavy": "red",
        "Hot": "red",
    }
    return f"[{colors.get(value, 'white')}]{value}[/{colors.get(value, 'white')}]"
