#!/usr/bin/env python3
"""Apply the buzz-off spec to Buzz's base_prompt.md.
Removes sections by heading and bullets by text, so it survives upstream edits.
Fails loudly if a rule matches nothing (upstream changed -> update the rule)."""
import re, sys

# Headings to drop, with everything under them up to the next heading of same or higher level.
DROP_SECTIONS = [
    "## Engineering Discipline",
    "### General",
]
# Bullets (lines starting "- ") to drop, matched by a substring.
DROP_BULLETS = [
    "Your commits use the git identity of the person running you",
]

def drop_section(text, heading, strict=True):
    level = len(heading.split()[0])
    pat = re.compile(rf"(?ms)^{re.escape(heading)}\s*\n.*?(?=^#{{1,{level}}} |\Z)")
    new, n = pat.subn("", text)
    if not n and strict: sys.exit(f"rule matched nothing: section {heading!r}")
    return new

def drop_bullet(text, needle, strict=True):
    pat = re.compile(rf"(?m)^- [^\n]*{re.escape(needle)}[^\n]*\n?")
    new, n = pat.subn("", text)
    if not n and strict: sys.exit(f"rule matched nothing: bullet {needle!r}")
    return new

def strip(text, strict=True):
    out = text
    for h in DROP_SECTIONS: out = drop_section(out, h, strict)
    for b in DROP_BULLETS:  out = drop_bullet(out, b, strict)
    return re.sub(r"\n{3,}", "\n\n", out)

if __name__ == "__main__":
    path = sys.argv[1]
    src = open(path).read()
    out = strip(src).rstrip() + "\n"
    open(path, "w").write(out)
    print(f"base_prompt.md: {len(src.splitlines())} -> {len(out.splitlines())} lines, "
          f"{len(src)} -> {len(out)} bytes", file=sys.stderr)
