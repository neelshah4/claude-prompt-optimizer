# Setup-Recommender Handoff (moved from SKILL.md 2026-09-03)

`claude-code-setup` (plugin) ships the `claude-automation-recommender` skill,
a read-only codebase analyzer that suggests tailored hooks, subagents, skills,
and MCP servers. It's one-shot per repo, not a continuous helper.

After displaying `<optimized_prompt>`, invoke
`claude-code-setup:claude-automation-recommender` via the Skill tool, but
**only when the project clears the large-project gate below.** Most prompts
won't, and the recommender should not fire for chat answers, scripts, or
single-file edits.

**Gate (all must hold):**

1. Task involves a **codebase the user is investing in**, not a standalone
   chat answer, one-off script, or content artifact (manuscript/grant/deck).
   Strongest signals: CODE task type, ANALYSIS rooted in a repo, or any task
   where Claude will operate inside a project tree across multiple turns.
2. **Project is large.** At least ONE strong signal present:
   - User mentions multi-week, multi-phase, "ongoing", or "long-term" scope
   - References ≥3 distinct modules/components/files by name
   - cwd is a git repo with `package.json`/`pyproject.toml`/`Cargo.toml`/
     `go.mod`/`pom.xml` and a quick `Glob` of `**/*.{ts,tsx,py,rs,go,java}`
     returns >50 hits
   - Phrases like "setting up", "scaffolding", "starting", "first time
     working in", "onboarding to"
   - Team, collaborators, code review, CI, or long-term maintenance referenced
3. **Not already run** for this repo this session (don't re-fire on follow-up
   turns within the same project context).
4. **No user opt-out.** User hasn't said "no setup", "skip recommender", or
   similar in the current task.

**When the gate fires:** after the `<optimized_prompt>` block, add one line:

```
> Project looks large — also running `claude-automation-recommender` once on
> this repo for setup suggestions. Say "skip recommender" to bypass.
```

Then invoke the recommender via the Skill tool,
`Skill(skill="claude-code-setup:claude-automation-recommender")` with the cwd as
context. Continue executing the original task afterward; the recommender's output
is additive, not blocking.

**When the gate doesn't fire:** stay silent. No mention. No nudge. Execute
the optimized prompt and stop.
