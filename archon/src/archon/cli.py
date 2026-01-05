from __future__ import annotations
import asyncio
import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from archon.core.config import ArchonConfig
from archon.core.engine import ConsensusEngine
from archon.core.models import AnalysisResult, Stance


console = Console()


def print_analysis(result: AnalysisResult) -> None:
    stance_colors = {
        Stance.BULLISH: "green",
        Stance.BEARISH: "red",
        Stance.NEUTRAL: "yellow",
    }

    consensus = result.consensus
    color = stance_colors[consensus.overall_stance]

    header = Panel(
        f"[bold {color}]{consensus.overall_stance.value.upper()}[/] "
        f"({consensus.overall_confidence:.0f}% confidence)",
        title=f"[bold]ARCHON Analysis: {result.symbol}[/]",
        border_style=color,
    )
    console.print(header)

    table = Table(title="Agent Thoughts", show_header=True, header_style="bold")
    table.add_column("Agent", style="cyan")
    table.add_column("Stance")
    table.add_column("Confidence")
    table.add_column("Key Insight")

    for thought in consensus.agent_thoughts:
        stance_color = stance_colors[thought.stance]
        table.add_row(
            thought.agent_type.value.upper(),
            f"[{stance_color}]{thought.stance.value}[/]",
            f"{thought.confidence:.0f}%",
            thought.key_factors[0] if thought.key_factors else "-",
        )

    console.print(table)

    risk = consensus.risk_assessment
    risk_text = (
        f"Approved: {'Yes' if risk.approved else f'NO - {risk.veto_reason}'}\n"
        f"Risk Level: {risk.risk_level.value}\n"
        f"Position Size: {risk.position_size_pct:.1f}%"
    )
    if risk.stop_loss_pct:
        risk_text += f"\nStop Loss: {risk.stop_loss_pct:.1f}%"

    risk_panel = Panel(risk_text, title="Risk Assessment (SENTINEL)", border_style="blue")
    console.print(risk_panel)

    action_panel = Panel(
        f"[bold]{consensus.suggested_action}[/]",
        title="Suggested Action",
        border_style=color,
    )
    console.print(action_panel)

    if consensus.dissenting_opinions:
        console.print(f"\n[dim]Dissenting views: {', '.join(consensus.dissenting_opinions)}[/]")

    console.print(f"\n[dim]Analysis completed in {result.execution_time_seconds}s[/]")
    console.print(f"[dim]Data sources: {', '.join(result.providers_used)}[/]")


async def analyze_symbol(symbol: str) -> None:
    console.print(f"\n[bold]Analyzing {symbol}...[/]")
    console.print("[dim]Gathering data and running agent analysis...[/]\n")

    try:
        config = ArchonConfig()
        engine = ConsensusEngine(config)
        result = await engine.analyze(symbol)
        print_analysis(result)
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        raise


def serve(host: str = "0.0.0.0", port: int = 8000) -> None:
    import uvicorn
    from archon.api.app import app

    console.print(f"\n[bold green]Starting Archon API server...[/]")
    console.print(f"[dim]Docs: http://{host}:{port}/docs[/]")
    console.print(f"[dim]WebSocket: ws://{host}:{port}/api/v1/ws/analyze/SYMBOL[/]\n")

    uvicorn.run(app, host=host, port=port)


def main() -> None:
    if len(sys.argv) < 2:
        console.print("[bold]Archon - Glass-Box Trading Intelligence[/]\n")
        console.print("[yellow]Usage:[/]")
        console.print("  archon <SYMBOL>          Analyze a symbol")
        console.print("  archon serve [--port N]  Start API server")
        console.print("\n[dim]Examples:[/]")
        console.print("  archon NVDA")
        console.print("  archon serve --port 8080")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "serve":
        port = 8000
        if "--port" in sys.argv:
            idx = sys.argv.index("--port")
            if idx + 1 < len(sys.argv):
                port = int(sys.argv[idx + 1])
        serve(port=port)
    else:
        symbol = sys.argv[1].upper()
        asyncio.run(analyze_symbol(symbol))


if __name__ == "__main__":
    main()
