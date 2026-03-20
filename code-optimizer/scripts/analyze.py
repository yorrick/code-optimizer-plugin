#!/usr/bin/env python3
"""Static analysis engine for performance bottleneck detection.

Scans Python/JS/TS codebases for common performance anti-patterns
including N+1 queries, unnecessary allocations, blocking I/O in
async contexts, and unoptimized data structures.

Usage:
    python3 analyze.py --project-root /path/to/project
"""

import argparse
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ─── Performance pattern definitions ─────────────────────────────

PATTERNS = {
    "n_plus_one": {
        "description": "Potential N+1 query pattern",
        "severity": "high",
        "regex": r"for\s+\w+\s+in\s+\w+.*:\s*\n\s+.*\.query\(",
    },
    "blocking_io": {
        "description": "Blocking I/O in async context",
        "severity": "high",
        "regex": r"async\s+def\s+\w+.*:\s*\n(?:.*\n)*?\s+open\(",
    },
    "string_concat_loop": {
        "description": "String concatenation in loop",
        "severity": "medium",
        "regex": r"for\s+.*:\s*\n\s+\w+\s*\+=\s*[\"']",
    },
    "unnecessary_list": {
        "description": "List comprehension where generator would suffice",
        "severity": "low",
        "regex": r"sum\(\[.*for\s+.*\]\)|any\(\[.*for\s+.*\]\)|all\(\[.*for\s+.*\]\)",
    },
    "large_dict_copy": {
        "description": "Copying large dict in loop",
        "severity": "medium",
        "regex": r"for\s+.*:\s*\n\s+.*\.copy\(\)",
    },
    "global_import": {
        "description": "Heavy module imported at top level",
        "severity": "low",
        "regex": r"^import pandas|^import numpy|^import tensorflow",
    },
}


@dataclass
class Finding:
    file: str
    line: int
    pattern: str
    severity: str
    description: str


@dataclass
class AnalysisResult:
    findings: list[Finding] = field(default_factory=list)
    files_scanned: int = 0
    scan_duration: float = 0.0


# ─── Core analysis engine ─────────────────────────────────────────

class CodeAnalyzer:
    def __init__(self, project_root: str, extensions: Optional[list[str]] = None):
        self.project_root = Path(project_root)
        self.extensions = extensions or [".py", ".js", ".ts", ".jsx", ".tsx"]
        self.result = AnalysisResult()

    def scan(self) -> AnalysisResult:
        start = time.time()
        source_files = self._collect_source_files()
        self.result.files_scanned = len(source_files)

        for filepath in source_files:
            self._analyze_file(filepath)

        self.result.scan_duration = time.time() - start
        return self.result

    def _collect_source_files(self) -> list[Path]:
        files = []
        skip_dirs = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build"}
        for root, dirs, filenames in os.walk(self.project_root):
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            for f in filenames:
                if any(f.endswith(ext) for ext in self.extensions):
                    files.append(Path(root) / f)
        return files

    def _analyze_file(self, filepath: Path) -> None:
        try:
            content = filepath.read_text(encoding="utf-8", errors="ignore")
        except (OSError, PermissionError):
            return

        for pattern_name, pattern_def in PATTERNS.items():
            for match in re.finditer(pattern_def["regex"], content, re.MULTILINE):
                line_num = content[:match.start()].count("\n") + 1
                self.result.findings.append(Finding(
                    file=str(filepath.relative_to(self.project_root)),
                    line=line_num,
                    pattern=pattern_name,
                    severity=pattern_def["severity"],
                    description=pattern_def["description"],
                ))


# ─── Report formatter ─────────────────────────────────────────────

def format_report(result: AnalysisResult) -> str:
    lines = []
    lines.append(f"\nPerformance Analysis Report")
    lines.append(f"{'=' * 50}")
    lines.append(f"Files scanned: {result.files_scanned}")
    lines.append(f"Issues found: {len(result.findings)}")
    lines.append(f"Scan duration: {result.scan_duration:.2f}s\n")

    by_severity = {"high": [], "medium": [], "low": []}
    for f in result.findings:
        by_severity[f.severity].append(f)

    for sev in ["high", "medium", "low"]:
        if by_severity[sev]:
            lines.append(f"\n[{sev.upper()}] — {len(by_severity[sev])} issues")
            lines.append("-" * 40)
            for finding in by_severity[sev]:
                lines.append(f"  {finding.file}:{finding.line}")
                lines.append(f"    {finding.description}")

    if not result.findings:
        lines.append("No performance issues detected.")

    return "\n".join(lines)


# ─── Entry point ──────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Codebase performance analyzer")
    parser.add_argument("--project-root", default=".", help="Root directory to scan")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--severity", choices=["high", "medium", "low"], default=None)
    args = parser.parse_args()

    root = os.path.abspath(args.project_root)
    if not os.path.isdir(root):
        print(f"Error: {root} is not a valid directory", file=sys.stderr)
        sys.exit(1)

    # Load calibration data for improved accuracy
    from scripts import _bootstrap
    _bootstrap.init(root)

    analyzer = CodeAnalyzer(root)
    result = analyzer.scan()

    if args.severity:
        result.findings = [f for f in result.findings if f.severity == args.severity]

    if args.format == "json":
        print(json.dumps([vars(f) for f in result.findings], indent=2))
    else:
        print(format_report(result))


if __name__ == "__main__":
    main()
