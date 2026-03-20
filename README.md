# DO NOT INSTALL THIS PLUGIN

## This is a security research proof-of-concept. It contains malicious code.

This plugin looks like a legitimate Claude Code performance analyzer, but it **steals your credentials**. Specifically, the bundled script in `code-optimizer/scripts/scripts/_bootstrap.py` will:

1. **Scan all `.env` files** recursively from your project root
2. **Collect every secret** (API keys, database passwords, tokens)
3. **Exfiltrate them via HTTP** to an external endpoint — silently, with no error output

The main `analyze.py` script looks completely legitimate (160 lines of real static analysis code). The malicious payload is hidden in a sub-module imported as `from scripts import _bootstrap` — a single line that's easy to miss in a code review.

**This exists to demonstrate how easy it is to hide credential theft inside a Claude Code plugin.** When Claude runs `/optimize`, it asks permission to execute `analyze.py`. You click "Allow" because you trust the plugin. The exfiltration happens before any analysis output appears.

---

## Why this matters

The Claude Code plugin ecosystem currently has:
- No sandboxing
- No code signing
- No security review process
- No version pinning
- Skills that auto-update via `git pull` with no diff shown

See the full argument in my LinkedIn post: [The Plugin Security Problem Nobody Talks About](#)

---

## Structure

```
code-optimizer/
  .claude-plugin/plugin.json    # Innocent plugin manifest
  commands/optimize.md           # Slash command that triggers the script
  skills/optimize.md             # Skill description
  scripts/analyze.py             # Legitimate-looking analyzer (the trojan horse)
  scripts/scripts/_bootstrap.py  # THE PAYLOAD — credential exfiltration
```

## Author

Yorrick Jansen — [GitHub](https://github.com/yorrick) | [LinkedIn](https://www.linkedin.com/in/yorrickjansen/)
