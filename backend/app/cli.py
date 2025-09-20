#!/usr/bin/env python3
"""
CQIA CLI - Code Quality Intelligence Agent Command Line Interface
Usage: python cli.py analyze <path-to-code>
"""

import click
import asyncio
import os
import sys
import json
from pathlib import Path
from typing import Optional, List
import requests
import time
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

console = Console()

class CQIAClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    def analyze_local_path(self, path: str) -> dict:
        """Analyze local file or directory"""
        path_obj = Path(path)

        if not path_obj.exists():
            raise click.ClickException(f"Path does not exist: {path}")

        # Collect files to analyze
        files_to_analyze = []

        if path_obj.is_file():
            files_to_analyze.append(path_obj)
        else:
            # Recursively find code files
            extensions = {'.py', '.js', '.jsx', '.ts', '.tsx', '.java', '.go', '.rs', '.cs'}
            for ext in extensions:
                files_to_analyze.extend(path_obj.rglob(f"*{ext}"))

        # Read file contents
        file_contents = {}
        total_lines = 0

        for file_path in files_to_analyze[:50]:  # Limit to 50 files for demo
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    file_contents[str(file_path.relative_to(path_obj))] = content
                    total_lines += len(content.splitlines())
            except Exception as e:
                console.print(f"[yellow]Warning: Could not read {file_path}: {e}[/yellow]")

        return {
            "files": file_contents,
            "total_files": len(file_contents),
            "total_lines": total_lines,
            "languages": self._detect_languages(files_to_analyze)
        }

    def _detect_languages(self, files: List[Path]) -> List[str]:
        """Detect programming languages from file extensions"""
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'JavaScript',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript',
            '.java': 'Java',
            '.go': 'Go',
            '.rs': 'Rust',
            '.cs': 'C#'
        }

        languages = set()
        for file_path in files:
            if file_path.suffix in lang_map:
                languages.add(lang_map[file_path.suffix])

        return list(languages)

    def start_analysis(self, data: dict) -> str:
        """Start analysis via API"""
        try:
            response = requests.post(
                f"{self.base_url}/api/v1/analyze",
                json={"input": "local_files", "data": data},
                timeout=30
            )
            response.raise_for_status()
            return response.json()["report_id"]
        except requests.exceptions.ConnectionError:
            # Fallback to local analysis if API is not available
            return self._local_analysis(data)

    def _local_analysis(self, data: dict) -> str:
        """Perform local analysis when API is not available"""
        console.print("[yellow]API not available, performing local analysis...[/yellow]")

        # Simulate analysis with actual code inspection
        issues = []
        quality_score = 85

        for filename, content in data["files"].items():
            # Basic issue detection
            lines = content.splitlines()

            # Security issues
            if any(keyword in content.lower() for keyword in ['password', 'secret', 'api_key', 'token']):
                issues.append({
                    "file": filename,
                    "type": "Security",
                    "severity": "High",
                    "line": 1,
                    "message": "Potential hardcoded credentials detected",
                    "suggestion": "Move sensitive data to environment variables"
                })

            # Performance issues
            if 'for' in content and 'in' in content and len(lines) > 100:
                issues.append({
                    "file": filename,
                    "type": "Performance",
                    "severity": "Medium",
                    "line": 1,
                    "message": "Large file with loops - potential performance impact",
                    "suggestion": "Consider breaking into smaller modules"
                })

            # Code quality issues
            if len(lines) > 200:
                issues.append({
                    "file": filename,
                    "type": "Code Quality",
                    "severity": "Low",
                    "line": 1,
                    "message": "File is too large",
                    "suggestion": "Split into smaller, focused modules"
                })

        # Calculate quality score based on issues
        high_issues = len([i for i in issues if i["severity"] == "High"])
        medium_issues = len([i for i in issues if i["severity"] == "Medium"])
        low_issues = len([i for i in issues if i["severity"] == "Low"])

        quality_score = max(0, 100 - (high_issues * 20) - (medium_issues * 10) - (low_issues * 5))

        return {
            "report_id": "local_analysis",
            "status": "completed",
            "summary": {
                "total_files": data["total_files"],
                "total_lines": data["total_lines"],
                "languages": data["languages"],
                "quality_score": quality_score
            },
            "issues": issues,
            "recommendations": [
                "Focus on high-severity security issues first",
                "Consider refactoring large files",
                "Add unit tests for critical functions"
            ]
        }

    def get_analysis_status(self, report_id: str) -> dict:
        """Get analysis status"""
        if report_id == "local_analysis":
            return self._local_analysis({})

        try:
            response = requests.get(f"{self.base_url}/api/v1/analyze/{report_id}/status")
            response.raise_for_status()
            return response.json()
        except:
            return {"status": "error", "message": "Could not fetch status"}

@click.group()
def cli():
    """CQIA - Code Quality Intelligence Agent"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--format', default='table', help='Output format: table, json, markdown')
@click.option('--output', '-o', help='Output file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def analyze(path: str, format: str, output: Optional[str], verbose: bool):
    """Analyze code repository for quality issues"""

    console.print(Panel.fit(
        "[bold blue]CQIA - Code Quality Intelligence Agent[/bold blue]\n"
        f"Analyzing: {path}",
        border_style="blue"
    ))

    client = CQIAClient()

    try:
        # Step 1: Collect and analyze files
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Scanning files...", total=None)
            data = client.analyze_local_path(path)
            progress.update(task, description=f"Found {data['total_files']} files")

            # Step 2: Start analysis
            progress.update(task, description="Starting analysis...")
            result = client.start_analysis(data)

            if isinstance(result, str):
                # API mode - wait for completion
                report_id = result
                progress.update(task, description="Analyzing code...")

                while True:
                    status = client.get_analysis_status(report_id)
                    if status.get("status") == "completed":
                        result = status
                        break
                    elif status.get("status") == "error":
                        raise click.ClickException(f"Analysis failed: {status.get('message')}")
                    time.sleep(2)

            progress.update(task, description="Analysis complete!")

        # Step 3: Display results
        display_results(result, format, output, verbose)

    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)

def display_results(result: dict, format: str, output: Optional[str], verbose: bool):
    """Display analysis results in specified format"""

    if format == 'json':
        output_text = json.dumps(result, indent=2)
    elif format == 'markdown':
        output_text = generate_markdown_report(result)
    else:
        display_table_report(result, verbose)
        return

    if output:
        with open(output, 'w') as f:
            f.write(output_text)
        console.print(f"[green]Report saved to {output}[/green]")
    else:
        console.print(output_text)

def display_table_report(result: dict, verbose: bool):
    """Display results in table format"""

    summary = result.get("summary", {})
    issues = result.get("issues", [])

    # Summary table
    summary_table = Table(title="📊 Analysis Summary", show_header=True, header_style="bold magenta")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="green")

    summary_table.add_row("Total Files", str(summary.get("total_files", 0)))
    summary_table.add_row("Lines of Code", f"{summary.get('total_lines', 0):,}")
    summary_table.add_row("Languages", ", ".join(summary.get("languages", [])))

    quality_score = summary.get("quality_score", 0)
    score_color = "green" if quality_score >= 80 else "yellow" if quality_score >= 60 else "red"
    summary_table.add_row("Quality Score", f"[{score_color}]{quality_score}/100[/{score_color}]")

    console.print(summary_table)
    console.print()

    # Issues table
    if issues:
        issues_table = Table(title="🔍 Detected Issues", show_header=True, header_style="bold red")
        issues_table.add_column("File", style="cyan", max_width=30)
        issues_table.add_column("Type", style="blue")
        issues_table.add_column("Severity", style="red")
        issues_table.add_column("Message", style="white", max_width=50)

        if verbose:
            issues_table.add_column("Suggestion", style="green", max_width=40)

        for issue in issues[:20]:  # Limit display
            severity_color = {
                "High": "red",
                "Medium": "yellow",
                "Low": "blue"
            }.get(issue.get("severity", "Low"), "white")

            row = [
                issue.get("file", ""),
                issue.get("type", ""),
                f"[{severity_color}]{issue.get('severity', '')}[/{severity_color}]",
                issue.get("message", "")
            ]

            if verbose:
                row.append(issue.get("suggestion", ""))

            issues_table.add_row(*row)

        console.print(issues_table)

        if len(issues) > 20:
            console.print(f"[yellow]... and {len(issues) - 20} more issues[/yellow]")
    else:
        console.print("[green]🎉 No issues detected![/green]")

    # Recommendations
    recommendations = result.get("recommendations", [])
    if recommendations:
        console.print()
        console.print(Panel(
            "\n".join(f"• {rec}" for rec in recommendations),
            title="💡 Recommendations",
            border_style="green"
        ))

def generate_markdown_report(result: dict) -> str:
    """Generate markdown report"""
    summary = result.get("summary", {})
    issues = result.get("issues", [])

    md = f"""# Code Quality Analysis Report

## Summary
- **Total Files**: {summary.get('total_files', 0)}
- **Lines of Code**: {summary.get('total_lines', 0):,}
- **Languages**: {', '.join(summary.get('languages', []))}
- **Quality Score**: {summary.get('quality_score', 0)}/100

## Issues Detected ({len(issues)})

"""

    for issue in issues:
        md += f"""### {issue.get('type', '')} - {issue.get('severity', '')}
**File**: `{issue.get('file', '')}`
**Message**: {issue.get('message', '')}
**Suggestion**: {issue.get('suggestion', '')}

"""

    recommendations = result.get("recommendations", [])
    if recommendations:
        md += "## Recommendations\n\n"
        for rec in recommendations:
            md += f"- {rec}\n"

    return md

@cli.command()
def interactive():
    """Start interactive Q&A session"""
    console.print(Panel.fit(
        "[bold blue]CQIA Interactive Mode[/bold blue]\n"
        "Ask questions about your code analysis",
        border_style="blue"
    ))

    console.print("[green]Type 'exit' to quit[/green]")

    while True:
        try:
            question = console.input("\n[bold cyan]❓ Your question: [/bold cyan]")
            if question.lower() in ['exit', 'quit', 'q']:
                break

            # Simple Q&A responses
            responses = {
                "security": "Focus on the high-severity security issues first. Look for hardcoded credentials, SQL injection risks, and input validation gaps.",
                "performance": "The main performance issues are in large files with complex loops. Consider breaking them into smaller modules.",
                "quality": "Your code quality can be improved by reducing file sizes, adding documentation, and following consistent naming conventions.",
                "test": "Add unit tests for critical functions, especially those handling user input or business logic."
            }

            response = "I can help you understand your code analysis results. Try asking about security, performance, quality, or testing issues."

            for keyword, answer in responses.items():
                if keyword in question.lower():
                    response = answer
                    break

            console.print(f"[green]🤖 {response}[/green]")

        except KeyboardInterrupt:
            break

    console.print("\n[blue]Thanks for using CQIA![/blue]")

if __name__ == '__main__':
    cli()
