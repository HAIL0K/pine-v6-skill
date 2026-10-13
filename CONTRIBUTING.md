# Contributing

## Layout

```
skills/pine-v6-indicators/
  SKILL.md                         what users ask for, defaults, hand-over format
  references/                      loaded by Claude only when a job needs them
    pine-v6-gotchas.md             v5→v6 breaking changes + observed compiler traps
    correctness.md                 execution model, repainting, other timeframes, alerts, deeper checks
    limits-and-performance.md      platform limits, Pine Profiler, optimisation
    visuals-cookbook.md            plots, markers, lines/boxes/labels, tables, colours
    tradingview-mcp.md             compiling on the chart via the MCP, and its known hazards
examples/                          complete scripts
  broken/v5-traps.pine             known-bad canary: must FAIL to compile
scripts/
  check_skill.py                   structure lint (runs in CI)
  compile_examples.py              opt-in compile check via TradingView's guest compiler
  build_zip.py                     builds dist/pine-v6-indicators.zip for claude.ai
docs/upstream/                     draft issues for the MCP authors (not filed)
```

## Rules for edits

- Keep `SKILL.md` short and aimed at users. Detail goes in `references/`, and each reference must be mentioned in `SKILL.md`.
- Each reference names the docs pages it is based on and the date they were checked. In `pine-v6-gotchas.md`, mark every rule *documented* (with a link) or *observed* (seen in real compiles, not in the docs). When the live docs disagree with this repo, the docs win.
- No personal names, local paths or client-specific tool names.

## Releasing

Push a tag such as `v1.0.0`. The release workflow runs the lint, builds `dist/pine-v6-indicators.zip` and attaches it to the GitHub release. Check that the zip is attached before sharing the link. To build it locally, run `python scripts/build_zip.py`.

## Checks

```
python scripts/check_skill.py                # structure, links, leaked paths, v5 syntax in snippets
python scripts/compile_examples.py --yes     # sends ONLY examples/*.pine to TradingView's guest compiler
```

`check_skill.py` also reads an untracked, git-ignored `.local-denylist` (one regex per line) or `PINE_SKILL_DENYLIST`, for names you never want published. CI has neither, so that check runs only on your machine.

`compile_examples.py` fails closed:
- A reply without a compile result counts as a failure.
- The known-bad canary must fail before any pass is trusted.
- Warnings fail an example.

It uses an undocumented TradingView endpoint, the same one the MCP's `pine_check` uses, so it is opt-in and not run in CI.
