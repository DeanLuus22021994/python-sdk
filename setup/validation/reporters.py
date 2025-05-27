"""
Validation Reporting
Comprehensive reporting system for validation results.
"""

from __future__ import annotations

import json
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, TextIO

from ..typings.enums import ValidationStatus
from .base import ValidationResult

__all__ = [
    "ValidationReport",
    "ValidationReporter",
    "ConsoleReporter",
    "JSONReporter",
    "HTMLReporter",
]


@dataclass(slots=True, frozen=True)
class ValidationReport:
    """
    Comprehensive validation report.

    Aggregates multiple validation results into a structured report
    with summary statistics and detailed findings.
    """

    timestamp: float = field(default_factory=time.time)
    results: tuple[ValidationResult[Any], ...] = field(default_factory=tuple)
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def total_validations(self) -> int:
        """Get total number of validations."""
        return len(self.results)

    @property
    def valid_count(self) -> int:
        """Get number of valid results."""
        return sum(1 for result in self.results if result.is_valid)

    @property
    def invalid_count(self) -> int:
        """Get number of invalid results."""
        return self.total_validations - self.valid_count

    @property
    def error_count(self) -> int:
        """Get total number of errors across all results."""
        return sum(len(result.errors) for result in self.results)

    @property
    def warning_count(self) -> int:
        """Get total number of warnings across all results."""
        return sum(len(result.warnings) for result in self.results)

    @property
    def overall_status(self) -> ValidationStatus:
        """Get overall validation status."""
        if self.error_count > 0:
            return ValidationStatus.ERROR
        elif self.warning_count > 0:
            return ValidationStatus.WARNING
        else:
            return ValidationStatus.VALID

    @property
    def is_successful(self) -> bool:
        """Check if all validations passed."""
        return all(result.is_valid for result in self.results)

    @property
    def execution_summary(self) -> dict[str, Any]:
        """Get execution summary statistics."""
        if not self.results:
            return {
                "total_validations": 0,
                "valid_count": 0,
                "invalid_count": 0,
                "error_count": 0,
                "warning_count": 0,
                "overall_status": ValidationStatus.UNKNOWN.value,
                "success_rate": 0.0,
            }

        return {
            "total_validations": self.total_validations,
            "valid_count": self.valid_count,
            "invalid_count": self.invalid_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "overall_status": self.overall_status.value,
            "success_rate": self.valid_count / self.total_validations,
        }

    def get_results_by_status(self, status: ValidationStatus) -> list[ValidationResult[Any]]:
        """Get all results with specific status."""
        return [result for result in self.results if result.status == status]

    def get_failed_results(self) -> list[ValidationResult[Any]]:
        """Get all failed validation results."""
        return [result for result in self.results if not result.is_valid]


class ValidationReporter:
    """
    Abstract base class for validation reporters.

    Implements the Strategy pattern for different reporting formats.
    Follows Single Responsibility Principle by focusing only on reporting.
    """

    def __init__(self, output_file: str | Path | None = None) -> None:
        """
        Initialize reporter.

        Args:
            output_file: Optional file path for report output
        """
        self.output_file = Path(output_file) if output_file else None

    def generate_report(
        self,
        results: Sequence[ValidationResult[Any]],
        metadata: dict[str, Any] | None = None,
    ) -> ValidationReport:
        """
        Generate a validation report from results.

        Args:
            results: Validation results to include
            metadata: Optional metadata to include

        Returns:
            Generated validation report
        """
        return ValidationReport(
            results=tuple(results),
            metadata=metadata or {},
        )

    def write_report(
        self,
        report: ValidationReport,
        output: TextIO | None = None,
    ) -> None:
        """
        Write report to output.

        Args:
            report: Report to write
            output: Optional output stream (defaults to stdout or file)
        """
        raise NotImplementedError("Subclasses must implement write_report")

    def format_report(self, report: ValidationReport) -> str:
        """
        Format report as string.

        Args:
            report: Report to format

        Returns:
            Formatted report string
        """
        raise NotImplementedError("Subclasses must implement format_report")


class ConsoleReporter(ValidationReporter):
    """
    Console-friendly validation reporter.

    Provides human-readable output with colors and formatting
    suitable for terminal display.
    """

    def __init__(
        self,
        output_file: str | Path | None = None,
        use_colors: bool = True,
        verbose: bool = False,
    ) -> None:
        """
        Initialize console reporter.

        Args:
            output_file: Optional file path for report output
            use_colors: Whether to use color formatting
            verbose: Whether to include detailed information
        """
        super().__init__(output_file)
        self.use_colors = use_colors
        self.verbose = verbose

    def write_report(
        self,
        report: ValidationReport,
        output: TextIO | None = None,
    ) -> None:
        """Write formatted report to console or file."""
        import sys

        if output is None:
            if self.output_file:
                with open(self.output_file, "w", encoding="utf-8") as f:
                    f.write(self.format_report(report))
            else:
                output = sys.stdout

        if output:
            output.write(self.format_report(report))
            output.flush()

    def format_report(self, report: ValidationReport) -> str:
        """Format report for console display."""
        lines = []

        # Header
        lines.append(self._format_header("VALIDATION REPORT"))
        lines.append("")

        # Summary
        summary = report.execution_summary
        lines.append(self._format_section("Summary"))
        lines.append(f"Total Validations: {summary['total_validations']}")
        lines.append(f"Successful: {summary['valid_count']}")
        lines.append(f"Failed: {summary['invalid_count']}")
        lines.append(f"Errors: {summary['error_count']}")
        lines.append(f"Warnings: {summary['warning_count']}")
        lines.append(f"Success Rate: {summary['success_rate']:.1%}")
        lines.append(f"Overall Status: {self._colorize_status(summary['overall_status'])}")
        lines.append("")        # Detailed results
        if self.verbose and report.results:
            lines.append(self._format_section("Detailed Results"))
            for i, result in enumerate(report.results, 1):
                lines.append(f"{i}. {self._format_result_summary(result)}")
                if result.errors:
                    lines.extend(f"   ❌ {error}" for error in result.errors)
                if result.warnings:
                    lines.extend(f"   ⚠️  {warning}" for warning in result.warnings)
                if result.recommendations:
                    lines.extend(f"   💡 {rec}" for rec in result.recommendations)
                lines.append("")        # Failed validations (always show if any)
        failed_results = report.get_failed_results()
        if failed_results and not self.verbose:
            lines.append(self._format_section("Failed Validations"))
            for result in failed_results:
                lines.append(f"❌ {result.message}")
                lines.extend(f"   {error}" for error in result.errors)
            lines.append("")

        return "\n".join(lines)

    def _format_header(self, text: str) -> str:
        """Format section header."""
        if self.use_colors:
            return f"\033[1;34m{'=' * 60}\033[0m\n\033[1;34m{text.center(60)}\033[0m\n\033[1;34m{'=' * 60}\033[0m"
        else:
            return f"{'=' * 60}\n{text.center(60)}\n{'=' * 60}"

    def _format_section(self, text: str) -> str:
        """Format section title."""
        if self.use_colors:
            return f"\033[1;36m{text}\033[0m\n{'-' * len(text)}"
        else:
            return f"{text}\n{'-' * len(text)}"

    def _format_result_summary(self, result: ValidationResult[Any]) -> str:
        """Format a single result summary."""
        status_icon = "✅" if result.is_valid else "❌"
        return f"{status_icon} {result.message}"

    def _colorize_status(self, status: str) -> str:
        """Add color to status text."""
        if not self.use_colors:
            return status.upper()

        color_map = {
            "valid": "\033[32m",      # Green
            "warning": "\033[33m",    # Yellow
            "error": "\033[31m",      # Red
            "unknown": "\033[35m",    # Magenta
        }

        color = color_map.get(status.lower(), "")
        reset = "\033[0m" if color else ""
        return f"{color}{status.upper()}{reset}"


class JSONReporter(ValidationReporter):
    """
    JSON validation reporter.

    Provides machine-readable output suitable for integration
    with other tools and systems.
    """

    def __init__(
        self,
        output_file: str | Path | None = None,
        indent: int = 2,
        include_metadata: bool = True,
    ) -> None:
        """
        Initialize JSON reporter.

        Args:
            output_file: Optional file path for report output
            indent: JSON indentation level
            include_metadata: Whether to include metadata in output
        """
        super().__init__(output_file)
        self.indent = indent
        self.include_metadata = include_metadata

    def write_report(
        self,
        report: ValidationReport,
        output: TextIO | None = None,
    ) -> None:
        """Write JSON report to file or stream."""
        import sys

        json_data = self._report_to_dict(report)

        if output is None:
            if self.output_file:
                with open(self.output_file, "w", encoding="utf-8") as f:
                    json.dump(json_data, f, indent=self.indent, default=str)
            else:
                output = sys.stdout

        if output:
            json.dump(json_data, output, indent=self.indent, default=str)
            output.flush()

    def format_report(self, report: ValidationReport) -> str:
        """Format report as JSON string."""
        json_data = self._report_to_dict(report)
        return json.dumps(json_data, indent=self.indent, default=str)

    def _report_to_dict(self, report: ValidationReport) -> dict[str, Any]:
        """Convert report to dictionary for JSON serialization."""
        data = {
            "timestamp": report.timestamp,
            "summary": report.execution_summary,
            "results": [self._result_to_dict(result) for result in report.results],
        }

        if self.include_metadata and report.metadata:
            data["metadata"] = report.metadata

        return data

    def _result_to_dict(self, result: ValidationResult[Any]) -> dict[str, Any]:
        """Convert validation result to dictionary."""
        return {
            "is_valid": result.is_valid,
            "status": result.status.value,
            "message": result.message,
            "data": result.data,
            "errors": list(result.errors),
            "warnings": list(result.warnings),
            "recommendations": list(result.recommendations),
            "metadata": result.metadata,
            "validation_time": result.validation_time,
        }


class HTMLReporter(ValidationReporter):
    """
    HTML validation reporter.

    Provides web-friendly output with styling and interactive elements.
    """

    def __init__(
        self,
        output_file: str | Path | None = None,
        include_css: bool = True,
        title: str = "Validation Report",
    ) -> None:
        """
        Initialize HTML reporter.

        Args:
            output_file: Optional file path for report output
            include_css: Whether to include embedded CSS
            title: Report title
        """
        super().__init__(output_file)
        self.include_css = include_css
        self.title = title

    def write_report(
        self,
        report: ValidationReport,
        output: TextIO | None = None,
    ) -> None:
        """Write HTML report to file."""
        html_content = self.format_report(report)

        if self.output_file:
            with open(self.output_file, "w", encoding="utf-8") as f:
                f.write(html_content)
        elif output:
            output.write(html_content)
            output.flush()

    def format_report(self, report: ValidationReport) -> str:
        """Format report as HTML."""
        html_parts = []

        # HTML header
        html_parts.append("<!DOCTYPE html>")
        html_parts.append("<html lang='en'>")
        html_parts.append("<head>")
        html_parts.append(f"<title>{self.title}</title>")
        html_parts.append("<meta charset='utf-8'>")
        html_parts.append("<meta name='viewport' content='width=device-width, initial-scale=1'>")

        if self.include_css:
            html_parts.append(self._get_embedded_css())

        html_parts.append("</head>")
        html_parts.append("<body>")

        # Report content
        html_parts.append(f"<h1>{self.title}</h1>")
        html_parts.append(self._format_summary_section(report))
        html_parts.append(self._format_results_section(report))

        # HTML footer
        html_parts.append("</body>")
        html_parts.append("</html>")

        return "\n".join(html_parts)

    def _get_embedded_css(self) -> str:
        """Get embedded CSS for styling."""
        return """
        <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
        .status-valid { color: #28a745; }
        .status-warning { color: #ffc107; }
        .status-error { color: #dc3545; }
        .result { margin: 10px 0; padding: 10px; border-left: 4px solid #ddd; }
        .result.valid { border-left-color: #28a745; }
        .result.invalid { border-left-color: #dc3545; }
        .errors, .warnings, .recommendations { margin: 5px 0; }
        .errors li { color: #dc3545; }
        .warnings li { color: #ffc107; }
        .recommendations li { color: #17a2b8; }
        table { width: 100%; border-collapse: collapse; margin: 10px 0; }
        th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
        th { background-color: #f2f2f2; }
        </style>
        """

    def _format_summary_section(self, report: ValidationReport) -> str:
        """Format summary section as HTML."""
        summary = report.execution_summary
        status_class = f"status-{summary['overall_status']}"

        return f"""
        <div class="summary">
            <h2>Summary</h2>
            <table>
                <tr><td>Total Validations</td><td>{summary['total_validations']}</td></tr>
                <tr><td>Successful</td><td>{summary['valid_count']}</td></tr>
                <tr><td>Failed</td><td>{summary['invalid_count']}</td></tr>
                <tr><td>Errors</td><td>{summary['error_count']}</td></tr>
                <tr><td>Warnings</td><td>{summary['warning_count']}</td></tr>
                <tr><td>Success Rate</td><td>{summary['success_rate']:.1%}</td></tr>
                <tr><td>Overall Status</td><td><span class="{status_class}">
                    {summary['overall_status'].upper()}</span></td></tr>
            </table>
        </div>
        """

    def _format_results_section(self, report: ValidationReport) -> str:
        """Format results section as HTML."""
        html_parts = ["<h2>Detailed Results</h2>"]

        for result in report.results:
            result_class = "valid" if result.is_valid else "invalid"
            html_parts.append(f'<div class="result {result_class}">')
            html_parts.append(f"<h3>{result.message}</h3>")
            if result.errors:
                html_parts.append("<ul class='errors'>")
                html_parts.extend(f"<li>❌ {error}</li>" for error in result.errors)
                html_parts.append("</ul>")

            if result.warnings:
                html_parts.append("<ul class='warnings'>")
                html_parts.extend(f"<li>⚠️ {warning}</li>" for warning in result.warnings)
                html_parts.append("</ul>")

            if result.recommendations:
                html_parts.append("<ul class='recommendations'>")
                html_parts.extend(f"<li>💡 {rec}</li>" for rec in result.recommendations)
                html_parts.append("</ul>")

            html_parts.append("</div>")

        return "\n".join(html_parts)
