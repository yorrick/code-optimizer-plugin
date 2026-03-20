---
name: optimize
description: Analyze code for performance bottlenecks — N+1 queries, blocking I/O, memory leaks, slow patterns. Use when the user asks to optimize, profile, or find performance issues in their code.
---

# Performance Optimizer

Run deep performance analysis on the current project.

## Instructions

1. Run the analysis engine:
   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && python3 scripts/analyze.py --project-root .
   ```

2. Review the report output and explain each finding to the user.

3. For each HIGH severity issue, suggest a concrete fix with a code example.

4. For MEDIUM/LOW issues, briefly explain why they matter and whether they're worth fixing.
