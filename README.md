# Pine v6 skill for Claude

A [Claude skill](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/overview) for writing, fixing, porting and optimising **TradingView Pine Script v6 indicators**, and for *proving they work* before handing them over.

Most AI-written Pine fails in one of three ways: it uses v5 syntax that no longer compiles, it repaints, or it compiles but computes the wrong number. This skill makes Claude run a loop with explicit stop criteria instead of trusting its memory:

1. Spec: inputs, outputs, timeframes, and whether repainting is allowed.
2. Write, with built-in `debugMode` invariant checks.
3. Static check against the v6 traps and the platform budgets.
4. Compile: 0 errors, every warning justified.
5. Runtime: no runtime errors on 2 symbols × 2 timeframes.
6. Values: at least 5 spot bars match an independent recompute.
7. Repainting audit.
8. Visual check against the spec.
9. Hand-off with the verification stated as numbers, plus a *Not verified* line.

Steps 4 to 8 run automatically when a TradingView Desktop MCP server is connected (see below). Without one, Claude asks you to paste the compiler output and Pine Logs, and never claims a check it didn't see.

## What's inside

```
skills/pine-v6-indicators/
  SKILL.md                         the loop, defaults, pre-hand-off checklist
  references/
    pine-v6-gotchas.md             v5→v6 breaking changes + observed compiler traps
    correctness.md                 execution model, repainting, request.security, alerts, log.*, value check
    limits-and-performance.md      platform limits, Pine Profiler, optimisation order
    visuals-cookbook.md            plots, markers, lines/boxes/labels, tables, colours
    tradingview-mcp.md             compile/verify loop through the MCP + known hazards
examples/                          complete scripts, compile-checked
  broken/v5-traps.pine             known-bad canary: must FAIL to compile
scripts/
  check_skill.py                   structure lint (runs in CI)
  compile_examples.py              opt-in compile check via TradingView's guest compiler
  build_zip.py                     builds the zip for claude.ai upload
```

Every rule in the references is marked *documented* (with a link to the official [Pine Script v6 docs](https://www.tradingview.com/pine-script-docs/)) or *observed* (seen in real compiles, not in the docs). They were checked against the docs on 2026-10-13. Where this repo and the live docs disagree, the docs win; please open an issue.

## Install

**Claude Code (plugin):**

```
/plugin marketplace add HAIL0K/pine-v6-skill
/plugin install pine-v6@pine-v6-skill
```

**Claude Code (manual):** copy `skills/pine-v6-indicators/` into `~/.claude/skills/` (for all projects) or into `<project>/.claude/skills/` (for one project).

**claude.ai / Claude Desktop:** run `python scripts/build_zip.py`, then upload `dist/pine-v6-indicators.zip` under *Settings → Capabilities → Skills*.

The skill triggers on its own when you ask for a Pine indicator, paste Pine code, or quote a Pine error.

## Optional: compile on your own chart with an MCP server

The skill is written to work with **[tradingview-mcp-jackson](https://github.com/LewisWJackson/tradingview-mcp-jackson)** by Lewis Jackson, a fork of the original **[tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp)** by [@tradesdontlie](https://github.com/tradesdontlie). It lets Claude inject code into your TradingView Desktop's Pine Editor, compile it, read errors and logs, read plotted values, and take screenshots. Install it by following that repo's README; it needs TradingView Desktop and your own TradingView subscription.

Read `references/tradingview-mcp.md` before you let an agent save scripts. In our use, `pine_new` and `pine_open` can leave a *different* script open in the editor, so a following save overwrites it. The skill tells Claude to check the editor title before every save.

## Checks

```
python scripts/check_skill.py                # structure, links, leaked personal data, v5 syntax in snippets
python scripts/compile_examples.py --yes     # sends ONLY examples/*.pine to TradingView's guest compiler
```

`compile_examples.py` fails closed. A reply without a compile result counts as a failure, and the known-bad canary must fail before any pass is trusted. It uses an undocumented TradingView endpoint (the same one the MCP's `pine_check` uses), so it is opt-in and not run in CI.

## Credits

- **[tradesdontlie/tradingview-mcp](https://github.com/tradesdontlie/tradingview-mcp)**, the original TradingView Desktop MCP server (MIT).
- **[LewisWJackson/tradingview-mcp-jackson](https://github.com/LewisWJackson/tradingview-mcp-jackson)**, the fork this skill was used with. This repo contains none of its code, and we did not modify it.
- **[TradingView Pine Script v6 documentation](https://www.tradingview.com/pine-script-docs/)**. Rules are paraphrased and linked, not copied.
- Skill structure follows Anthropic's [skill authoring best practices](https://docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices).

## Disclaimer

Not affiliated with TradingView Inc. or Anthropic. TradingView and Pine Script are trademarks of TradingView, Inc. Indicators are tools, not trading advice; verify everything on your own data before you rely on it.

## License

MIT. See [LICENSE](LICENSE).
