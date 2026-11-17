# buzz-off

A machine, not a fork. It builds **BuzzOff.app**: upstream [block/buzz-app](https://github.com/block/buzz-app) `main`,
with a slimmer agent base prompt.

```bash
./build.sh             # fetch upstream, apply spec, build -> dist/BuzzOff.app
./build.sh --no-build  # just apply the spec and show the diff
```

## Spec (`strip_prompt.py`)
Applied to `src/features/agent-harness/base_prompt.md`:
- remove `## Engineering Discipline`
- remove `### General`
- remove the "Your commits use the git identity…/Co-authored-by" bullet

Rules match by heading/text, not line numbers. If upstream renames something, the build fails with
`rule matched nothing: …` — update the rule.

## App identity (`tauri.buzzoff.conf.json`)
Name `BuzzOff`, identifier `com.michaelneale.buzzoff` (separate data from Buzz), no updater artifacts.
Unsigned local build.

Needs: git, python3, node + pnpm, Rust toolchain.
