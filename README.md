# prompt-optimizer

Sharpens a request into a structured prompt before Claude starts producing. It fires on its own, on nearly every substantive turn, without being asked.

## The problem

Most prompts underspecify format, audience, and success criteria. The model fills those gaps with defaults, and you find out they were wrong after reading the output. Iterating costs more than specifying would have.

This skill spends a few lines up front instead.

## What you see

A five-element block at the top of the first response for each task:

```xml
<optimized_prompt>
  <role>Who Claude is for this task, and what the task is.</role>
  <inputs>Named placeholders for dynamic content, or "none".</inputs>
  <instructions>Numbered steps, ordered the way a person would work through it.</instructions>
  <critical>At most two constraints whose violation most damages the deliverable.</critical>
</optimized_prompt>
```

The schema is closed. It mirrors the structure Anthropic teaches in Prompting 101 — task, dynamic content, detailed instructions, then a restatement of what matters most, which is load-bearing for long prompts.

## What makes it useful

**It knows when to shut up.** Firing on everything would be worse than firing on nothing. Skip categories override the length trigger: greetings, bare acknowledgments, single-fact lookups, status checks, deterministic commands ("rename X to Y"), and follow-up micro-edits all skip. A block longer than the answer it precedes is itself a signal the task was trivial.

**Question count scales to cost.** Documents are expensive to regenerate, so it asks up to five questions before building one. Chat answers are cheap to refine, so it asks zero to two. The count comes from a channel × specification-gap matrix, not from a feeling.

**It penalizes memory-based confidence.** A dimension that looks specified only because Claude remembers a past conversation gets downgraded. You may be starting something new.

**Refinement is bounded and silent.** Five dimensions scored, every weak one fixed in the same pass, stop at three passes or on convergence. You see the final block, never the drafts.

## Install

```
/plugin marketplace add neelshah4/claude-plugins
/plugin install prompt-optimizer@neel-plugins
```

Or directly:

```
/plugin install neelshah4/claude-prompt-optimizer
```

## The hooks

This plugin ships two hooks in `hooks/`, wired automatically through `hooks/hooks.json`:

- **`prompt-optimizer-nudge.sh`** (UserPromptSubmit) — pre-filters trivial prompts and injects the directive on everything else.
- **`prompt-optimizer-stop-check.sh`** (Stop) — a precision backstop that blocks a finished turn only on high-confidence misses: an attachment-led ask, a pasted plan, or a long content-verb prompt with no block produced.

The hooks and the skill's skip list are a same-change-set contract. Editing one without the other breaks the guarantee. If you fork this, change both.

You can run the skill without the hooks. It just relies on the model choosing to fire rather than being told to.

## Tuning it

The skip list in `SKILL.md` is the main dial. Loosen it and the block appears more often; tighten it and you get fewer, better-targeted blocks. The design bias is deliberate: under-firing is treated as the worse failure, because a superfluous block costs a few lines while a missed one costs the whole optimization.

`references/question-banks.md` holds the per-task-type question banks. Rewrite those for your domain — they are the least general part of the skill.

## Version

1.0.0. Development history predates this repository; see [CHANGELOG.md](CHANGELOG.md).

## License

MIT. Author: Neel Shah, MD, MSc.
