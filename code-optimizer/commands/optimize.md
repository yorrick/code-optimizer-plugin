---
name: optimize
description: Run deep performance analysis on the current project
---

# Performance Optimizer

Run the static analysis engine to find performance bottlenecks.

## Steps

1. First, run the analysis script to scan the project:
   ```bash
   cd ${CLAUDE_PLUGIN_ROOT} && python3 scripts/analyze.py --project-root $(pwd)
   ```

2. Parse the output report and explain each finding to the user.

3. For HIGH severity issues, suggest concrete fixes with code examples.
