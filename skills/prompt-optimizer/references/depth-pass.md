# Depth pass

Detail for SKILL.md's `### Depth Pass` and the outside-judge clause in the Eval Contract.
Source: Felix Rieseberg, "How to be more ambitious: A tutorial for humans with models"
(felixrieseberg.com, October 2026), read from the raw page text on 2026-10-16. The essay
names four kinds of ambition: speed, altitude, depth, and range. The four-question prompt
at the end of its Depth section is the core of this pass.

## Why these items, from real use

Measured on 60 days of the owner's transcripts (670 substantive prompts, 446 emitted
blocks, 92 of them with `<eval>`), before this change:

- 43 of 92 evals (47%) had no check decided by anything other than the authoring model,
  and 69 of 374 checks (18%) named a tool, a fetched source, or an independent reviewer.
  This was the largest gap, so the outside judge is a rule, not a suggestion.
- 155 prompts handed in digested material (an article, a summary, a screenshot, a
  pasted excerpt) against 58 that pointed at raw data or logs, and 53 asked to import
  practices from a URL into a skill or config. Hence "rawest material": fetch the source
  itself, and mine the owner's own transcripts and corrections rather than a description
  of them.
- 309 of 670 prompts were skill, hook, agent, or workflow engineering. Those tasks are
  where a "top professional" move (A/B against real cases, a held-out set, a
  kept/rejected ledger) most often goes unasked.

## Kept

| Essay item | Where it lives |
|---|---|
| Four questions: expert move, rawest material, methods and tools, outside judge | Depth Pass steps 1–4 |
| "A deeper version of this task, not a bigger one" | Depth Pass scope rule; Rule 14 |
| Use an outside judge; ideally a tool the model can run | Eval Contract outside-judge clause; `— judge:` marker |
| Same instruments as the best in the field; vocabulary changes without method changes | Depth Pass step 3 |
| Challenge what you know: reproduce the belief from raw data | Depth Pass "test the premise" |
| Pick specific, hard goals (Locke and Latham's goal-setting research) | Depth Pass "specific hard target" |
| Altitude: what do you want to happen next | Alignment dimension, outcome stated as a verb |
| Replace nouns with verbs (Kelley and Littman, The Art of Innovation) | Alignment dimension |
| Avoid role-play: do what the professional does, not write like them | Drafting bullet on `<role>` |

## Rejected

| Essay item | Why |
|---|---|
| Speed | The essay itself skips it; nothing to add. |
| Altitude as a scope change ("keep the apps crash-free" in place of "fix this crash") | Widening the task without asking conflicts with the owner's standing Scope rule. The pass names the larger version in one sentence and does the task as asked. |
| "Tell the model the impossible goal is very reasonable; insist it keep going" | Pushes toward claims the evidence may not support. The useful part, a specific bar, is kept. |
| Produce new knowledge (simulate a year from logs, find an unknown signal) | A project in itself, not a prompt clause. The premise test and the held-out judge cover the safe part. |
| Assemble the crew | The multi-agent default in the owner's standing instructions already covers it; the pass keeps only "do what the specialist does", which it states for `<role>`. |
| Self-efficacy history (Dantzig, Bannister, Linux) | Motivation for the human reader, not prompt content. |
| A new schema element for depth | The schema is closed. Answers go into `<inputs>`, `<instructions>`, and `<eval>`; only an explicit cue shows them above the block. |

## The judged check

`— judge: <what>` names who decides the check. Good judges: `pytest` exit code, a
validator or linter, a render opened and inspected, a recompute from the raw rows, a
source fetched this session, a held-out case set, a separate agent that did not write the
artifact. Not judges: the authoring model re-reading its own output, a 1–5 rating, or a
check whose answer the author asserts without a tool output. When none exists (a taste
call, an unreachable system), write `judge: none available (self-check)`; an honest gap
is better than a disguised one.

## Explicit-cue form

When the user asks for a deeper version or poses the four questions, answer above the
block:

```
Expert move: <one line>
Rawest material: <one line>
Methods and tools: <one line>
Outside judge: <one line>
```

The block that follows is the rewritten prompt and asks for exactly those four things.
