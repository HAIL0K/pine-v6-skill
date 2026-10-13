"""Structure lint for the pine-v6-indicators skill. Runs in CI; needs only the stdlib.

Fails closed: if it finds no skill, no references or no Pine code blocks to scan,
that is a FAIL, not a pass.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "pine-v6-indicators"

# Strings that must never ship in a public skill: personal names, local paths,
# and tool names that exist only in one client.
FORBIDDEN = [r"\bhailok\b", r"C:\\Users", r"\bkevwe\b", r"\bcreate_file\b", r"\bstr_replace\b"]

# Pine v5-and-older syntax that is a compile error or a silent bug in v6.
V5_ISMS = {
    r"\btransp\s*=": "transp= was removed in v6; use color.new()",
    r"(?<![\w.])study\s*\(": "study() is v4; use indicator()",
    r"(?<![\w.])security\s*\(": "bare security() is v4; use request.security()",
    r"//@version=[1-5]\b": "script declares a pre-v6 version",
    r"\bwhen\s*=": "when= was removed from strategy.*() in v6",
}

errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        return {}
    out = {}
    for line in m.group(1).splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def main() -> int:
    skill_md = SKILL_DIR / "SKILL.md"
    if not skill_md.is_file():
        print(f"FAIL: {skill_md} not found")
        return 1
    text = skill_md.read_text(encoding="utf-8")

    fm = frontmatter(text)
    name, desc = fm.get("name", ""), fm.get("description", "")
    if name != SKILL_DIR.name:
        fail(f"frontmatter name {name!r} != folder {SKILL_DIR.name!r}")
    if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
        fail("name must be lowercase letters, digits and hyphens, at most 64 chars")
    if not 1 <= len(desc) <= 1024:
        fail(f"description length {len(desc)} outside 1..1024")
    if re.search(r"<[^>]+>", desc):
        fail("description must not contain XML tags")
    body_lines = text.count("\n")
    if body_lines > 500:
        fail(f"SKILL.md is {body_lines} lines; keep it under 500 and move detail to references/")

    # Every referenced file exists, and every reference file is referenced.
    refs = sorted((SKILL_DIR / "references").glob("*.md"))
    if not refs:
        fail("no reference files found")
    linked = set(re.findall(r"references/([\w.-]+\.md)", text))
    for ref in refs:
        if ref.name not in linked:
            fail(f"references/{ref.name} is never mentioned in SKILL.md (orphan)")
    for name_ in linked:
        if not (SKILL_DIR / "references" / name_).is_file():
            fail(f"SKILL.md mentions references/{name_}, which does not exist")

    # Scan every shipped text file.
    scanned = 0
    pine_blocks = 0
    files = [p for p in ROOT.rglob("*") if p.is_file() and p.suffix in {".md", ".pine", ".json"}
             and ".git" not in p.parts]
    for path in files:
        rel = path.relative_to(ROOT)
        content = path.read_text(encoding="utf-8")
        scanned += 1
        for pat in FORBIDDEN:
            if re.search(pat, content, re.I):
                fail(f"{rel}: forbidden string matching {pat}")
        if path.suffix == ".pine":
            blocks = [content]
            if "examples/broken" in rel.as_posix():
                continue  # deliberately broken fixture for compile_examples.py
            if not content.startswith("//@version=6"):
                fail(f"{rel}: first line must be //@version=6")
        else:
            blocks = re.findall(r"```pine\n(.*?)```", content, re.S)
        for block in blocks:
            pine_blocks += 1
            for pat, why in V5_ISMS.items():
                for line in block.splitlines():
                    code = line.split("//", 1)[0] if not line.lstrip().startswith("//@") else line
                    if re.search(pat, code):
                        fail(f"{rel}: {why}: {line.strip()}")

    for manifest in (ROOT / ".claude-plugin").glob("*.json"):
        try:
            json.loads(manifest.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            fail(f"{manifest.relative_to(ROOT)}: invalid JSON: {e}")

    # Fail closed on an empty scan.
    if scanned == 0:
        fail("scanned 0 files")
    if pine_blocks == 0:
        fail("found 0 Pine code blocks; the v5-syntax scan checked nothing")

    print(f"scanned {scanned} files, {pine_blocks} Pine blocks, {len(refs)} reference files")
    if errors:
        for e in errors:
            print("FAIL:", e)
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
