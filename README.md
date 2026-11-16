# prompt-optimizer

Sharpens a request into a structured prompt before Claude starts producing. It fires on its own, on nearly every substantive turn, without being asked.

---

## Contents

- [The problem](#the-problem)
- [What you see](#what-you-see)
- [Worked examples](#worked-examples)
- [Install](#install)
- [Model support](#model-support)
- [How it decides to fire](#how-it-decides-to-fire)
- [How many questions it asks](#how-many-questions-it-asks)
- [The refinement loop](#the-refinement-loop)
- [The hooks](#the-hooks)
- [Best practices](#best-practices)
- [Tuning it for your work](#tuning-it-for-your-work)
- [Troubleshooting](#troubleshooting)
- [Where the design comes from](#where-the-design-comes-from)
- [What it deliberately does not do](#what-it-deliberately-does-not-do)

---

## The problem

Most prompts underspecify format, audience, and success criteria. The model fills those gaps with defaults, and you find out they were wrong after reading the output. Iterating costs more than specifying would have.

This skill spends a few lines up front instead. The cost is bounded and visible; the cost of a wrong default is neither.

---

## What you see

A block at the top of the response to each prompt you type that carries a task, with its own pass/fail eval built in:

```xml
<optimized_prompt>
  <role>Who Claude is for this task, and what the task is.</role>
  <inputs>Named placeholders for dynamic content, as NAME: description lines, or "none".</inputs>
  <instructions>Numbered steps that add to your words: the success criterion, the reader, the method, the order.</instructions>
  <assumptions>Each decision made without asking, one line each, or "none".</assumptions>
  <eval>check or hillclimb, plus 1–3 pass/fail checks; at least one names its outside judge.</eval>
  <critical>At most two constraints whose violation most damages the deliverable.</critical>
</optimized_prompt>
```

One element is conditional: `<examples>` appears only when a worked example sharpens the spec. `<assumptions>` lists what the block decided without asking, including anything taken from memory, so a wrong default is visible and one reply corrects it.

**Every block carries an eval.** `<eval>` lists 1–3 yes/no checks that can be read off the output or a tool result ("script exits 0 on the sample", "≤ 300 words"), never a 1–5 quality scale, and the checks run as the last step of the work, with the tally stated in the closeout. At least one check names an outside judge, written `— judge: <what>`: something other than the model that made the output, such as a test run, a recompute from the raw data, a source fetched in the session, or a reviewer that did not write it. When no such judge exists, the block says so. When the thing being built runs again (a skill, prompt, agent, workflow, or pipeline), the mode is `hillclimb`: build cases from real use, split them into train and held-out test sets, change one thing per round, keep a change only when both sets improve, and stop after 2–3 flat rounds. The method follows Anthropic's post on automating eval design and hillclimbing; the full protocol is in `skills/prompt-optimizer/references/eval-hillclimb.md`.

**Deeper, not bigger.** On document, analysis, code, research-design, and skill-engineering tasks, the block answers four questions while it is drafted: what a top professional would do that the prompt does not ask for, the rawest material they would start from, the specific methods and tools they would use, and what besides the model or the user would show the result is right. Each answer replaces a vague step or sharpens `<inputs>` and `<eval>`; none adds a deliverable. Ask for "a deeper version" and the four answers appear above the block. The questions come from Felix Rieseberg's essay "How to be more ambitious: A tutorial for humans with models" (October 2026); `skills/prompt-optimizer/references/depth-pass.md` lists what was kept and what was left out.

**The schema is closed.** Only these element names, ever. Invented tags and dropped `<inputs>` are bugs, not stylistic variation. The closure is what makes the block skimmable — you learn where to look once.

---

## Worked examples

### A chat question that fires

> **You:** Compare albumin and crystalloid for early septic shock resuscitation in kids

```xml
<optimized_prompt>
  <role>You are a pediatric intensivist comparing volume-expansion strategies
  for early septic shock, for a colleague who will act on the answer.</role>
  <inputs>none</inputs>
  <instructions>
    1. State the current guideline position and its GRADE strength before
       any mechanistic argument.
    2. Compare albumin and crystalloid on the outcomes that change practice:
       mortality, fluid balance, AKI, time to shock reversal.
    3. Name where pediatric evidence is extrapolated from adults and say so
       explicitly rather than smoothing it over.
    4. Close with the specific patient phenotype, if any, where the choice
       actually differs.
  </instructions>
  <assumptions>The reader is a pediatric intensivist. No patient data was supplied,
  so this is an evidence summary, not a bedside recommendation.</assumptions>
  <eval>check: guideline and GRADE strength stated before mechanism; every
  adult-derived claim labeled adult; each cited recommendation matches the
  guideline text — judge: the guideline fetched this session.</eval>
  <critical>Do not promote an association to a causal claim. Pediatric-first
  evidence hierarchy — adult data is labeled as adult data.</critical>
</optimized_prompt>
```

Zero questions asked. Chat channel, high specification score.

### A document task that asks first

> **You:** Draft the cover letter for the ECMO manuscript

The specification score is low — no journal, no editor, no emphasis. It asks four questions, then produces the block and the letter. Documents are expensive to regenerate, so the intake is worth it.

### Three that skip

> **You:** thanks, that's great

Bare acknowledgment. No block.

> **You:** what's the max dose of dexmedetomidine

Single-fact lookup, no synthesis. No block.

> **You:** make the third bullet shorter

In-prompt micro-edit. No block. But `resume — and now also draft the discussion` **does** fire, because it introduces new work.

---

## Install

```
/plugin marketplace add neelshah4/claude-plugins
/plugin install prompt-optimizer@neel-plugins
```

Or directly:

```
/plugin install neelshah4/claude-prompt-optimizer
```

---

## Model support

**Developed on Claude Opus 5 and retuned for Claude Opus 5.5.** The 2026.9.23 release fitted the drafting rules to Opus 5.5 (thinking is always on, `medium` is the default effort, and requests to reproduce reasoning are declined). The earlier Opus 5 migration added a progressive-disclosure split that moved the question banks, worked examples, and version history into `references/` so the always-loaded body stays small.

**The design is model-agnostic and holds on every current Claude model** — Opus, Sonnet, Haiku, and Fable. Nothing in the skill pins a model ID, and the instruction-writing guidance is written as model-agnostic principle rather than as a workaround for one model's quirks. Pinning model IDs was an explicit anti-pattern during the migration: the previous approach left two dozen dead identifiers behind.

Practical notes by tier:

| Tier | Behavior |
|---|---|
| **Opus** | Full behavior. The refinement loop converges in one or two passes; the skip-list judgment calls land correctly. |
| **Sonnet** | Works well. Slightly more likely to fire on a borderline skip, which is the intended failure direction. |
| **Haiku** | Usable for the block itself. The channel × score matrix is mechanical enough to hold; nuanced skip calls degrade first. |

**On reasoning effort.** The skill's refinement loop is bounded at three passes and stops on convergence, so it does not need high effort to behave. Effort controls thinking volume, not the block's length. Holding effort constant within a session matters more than raising it, because changing it mid-session invalidates the prompt cache.

**On other harnesses.** The skill body is portable. The two hooks are Claude Code specific — they use the `UserPromptSubmit` and `Stop` hook events and `${CLAUDE_PLUGIN_ROOT}` expansion. On a harness without hooks, the skill still works; it just relies on the model choosing to fire rather than being told to.

---

## How it decides to fire

**Fire conditions are OR'd.** Any one is enough:

- The message runs past one sentence **and** carries a task
- Any content-production request, regardless of length
- An explicit cue: "optimize my prompt", "help me draft/analyze/build/review"

Length alone is necessary, not sufficient. A four-sentence status check does not fire.

**Five patterns that look skippable and are not.** These were the measured miss clusters:

1. **Attachment-led** — `@file.docx` plus a short ask. The attachment is `<inputs>`; the surrounding sentence is the task.
2. **Pasted plan or persona** — "you are a senior engineer…" or a pasted plan to execute. Highest-value fires.
3. **Meta work** — editing skills, hooks, agents, or config. Content production about the system is still content production.
4. **Dense clinical consults** — fires through the specialist handoff.
5. **Short but substantive** — "give me a one-sentence hypothesis and where to put it in the aims."

**Skip categories override everything.** Greetings; bare acknowledgments; single-fact lookups with no synthesis; bare yes/no; bare definitions; status and verification checks; single deterministic commands; background-task notifications and other turns no person started (agent reports, compaction summaries, scheduled-task starts); pure continuations and micro-edits under 25 words; and any case where the block would run longer than the answer. A follow-up of 25 words or more that carries answers, decisions or new instructions gets its own block, which compiles them into the working spec.

**When genuinely ambiguous, it fires.** A superfluous block costs a few lines. A missed one costs the whole optimization. Only the hard skips survive ambiguity.

---

## How many questions it asks

Question count comes from a channel × specification-gap matrix, not from a feeling.

**Channel.** Documents and artifacts are expensive to regenerate, so intake is worth paying for. Chat answers are cheap to refine, so it should not stall you.

**Specification gap.** Five dimensions scored 1–3: Goal, Format, Audience, Constraints, Context. Uncertainty is `(15 − score) / 10`.

| Channel | Score 13–15 | Score 10–12 | Score 5–9 |
|---|---|---|---|
| **Chat** | 0 questions | 1 | 2 |
| **Document** | **1** (content-extending) | 4 | 5 |

The document 13–15 cell asks exactly one question, and it is not a gap question — it sharpens emphasis, framing, or reviewer lens. The prompt is already specified; the question improves direction.

**The memory penalty.** A dimension that scores well only because Claude remembers a past conversation is downgraded (3→2, 2→1). You may be starting something new, and memory-based confidence is the kind that produces a fluent answer to last week's question.

**Overrides always win.** "Just do it", "you decide", "proceed" drop the count to zero — but the block still appears. "Ask me 5–10" raises the cap.

---

## The refinement loop

Five dimensions, scored 1–3 each pass: Specificity, Completeness, Economy, Alignment, Order.

Every dimension scoring below 3 is fixed **in the same pass**. Fixing one at a time lets an improvement in Specificity quietly bloat Economy. Trade-offs resolve toward Alignment — what you actually need, not what is easy to write.

It stops when all five score 3, when a pass yields no material gain, at three passes, or when **capped**: a dimension cannot reach 3 because the required input is absent and inventing it would fabricate. A capped stop is not convergence. It names the missing input as an `<inputs>` placeholder and asks, rather than shipping a thin block that hides the gap.

You never see the intermediate passes. Only the final block.

---

## The hooks

Two hooks ship in `hooks/`, wired automatically through `hooks/hooks.json`, with one shared module they import:

**`prompt-optimizer-nudge.sh`** — `UserPromptSubmit`. Pre-filters high-confidence trivial prompts and injects the directive on everything else. The pre-filter is deliberately a strict subset of the skill's skip list: it implements only greetings, bare acknowledgments, bare yes/no, tightly anchored status checks, and single deterministic commands. Soft skips stay with the model, because a regex that guesses wrong on those fails silently.

Two behaviors matter for non-human events and short prompts. First, the hook stays silent when the prompt opens with a marker the harness writes onto the user channel (a task notification, a subagent hand-back, a compaction summary, a scheduled-task start, a side-session or CI event, local-command output). Markers are matched only against the opening of the prompt, so a person who quotes one mid-message still gets the normal behavior. The matching lives in `hooks/harness_event.py`; if that file is missing or raises, the hook falls back to its own prompt extraction and behaves as before. Second, for a prompt of 15 words or fewer in one sentence, the status and single-command tests run before the content-verb match, so a filename that contains a verb stem ("rename draft_v2.docx to final.docx") or a status question that contains one ("is the model running") no longer injects. A stem anywhere outside a path-like token still injects.

**`prompt-optimizer-stop-check.sh`** — `Stop`. A precision backstop that blocks a finished turn only on high-confidence misses: an attachment-led ask, a pasted plan, or a long content-verb prompt with no block produced. It cannot reproduce the soft skips and does not try. On a long session the opening prompt may lie before the last 4 MB of the transcript, so the hook widens its read window (4 MB, then 16 MB, then 64 MB) until it finds the prompt that started the turn; past 64 MB, or on any error, it allows the stop. A transcript of 4 MB or less is read whole.

**Closeout and receipt.** The skill's closeout rule defers to the standing instructions of the person using it: when they define a closeout format, the turn ends in that format; otherwise it ends in one or two sentences. When a setup runs a register reviewer and a writing pass after the drafted prose, the skill expects one receipt line under the block rather than two.

**Tests.** `hooks/tests/` holds fixtures for both hooks. Run them from the repository root:

```
python3 hooks/tests/prompt_optimizer_hook_fixtures.py
python3 hooks/tests/prefilter_failopen.py
python3 hooks/tests/stop_hook_tail_fixtures.py
```

**The three-way contract.** The skill's skip list, the nudge hook's pre-filter, and the Stop hook's block conditions must move together. Change one without the others and the guarantee breaks. If you fork this, honor that or delete the hooks.

You can run the skill without them. Enforcement just becomes advisory.

---

## Best practices

These are the instruction-writing moves the skill applies when it drafts a block, and they work equally well when you write prompts by hand.

**Give the reason, not only the request.** Naming who the output is for and what it enables lets the model connect the work to the right context instead of inferring it.

**Lead with the outcome.** Put the most important constraint and the end state first. Supporting detail after.

**Do not over-enumerate.** One strong instruction beats a long list of prohibitions. Keep only constraints that each add something distinct.

**State directives affirmatively.** "Do X" outperforms "don't do Y" — a finding from the principled-instructions work cited below, and one that holds across model families.

**Never ask for reasoning narration.** "Explain your reasoning in the response" bloats output and can trip refusals. Let thinking do that work.

**Decompose at natural joints.** A step hiding two deliverables is under-split. Steps smaller than a real unit of work went one layer too deep. Depth follows the task's structure; it is not a dial for effort.

**Prefer the cheap reversible action to a prediction about it.** If the model could run the check, open the file, or read the value, write the step as that action and its observation — not as reasoning about what the result would probably be.

**Restate what matters at the end.** Repetition at the close of a long prompt is load-bearing, which is why `<critical>` exists and why it is capped at two items. Three or more and none of them are critical.

---

## Tuning it for your work

**The skip list is the main dial.** It lives in `skills/prompt-optimizer/SKILL.md`. Loosen it and the block appears more often; tighten it and you get fewer, better-targeted blocks. The shipped bias treats under-firing as the worse failure — invert that if the block becomes noise for you.

**The question banks are the least general part.** `references/question-banks.md` holds per-task-type banks written for academic and clinical work: manuscripts, grants, presentations, clinical consults. If you work in another domain, rewrite these first. Everything else transfers unchanged.

**The handoff table assumes companion skills.** The skill defers intake to specialists — grant review, manuscript review, clinical consult, citation verification. If you do not have those installed, the handoff rows are inert and the skill runs its own intake. Nothing breaks; it just does the work itself.

---

## Troubleshooting

**It fires on everything and I hate it.** Tighten the skip list, or remove the nudge hook and let the model decide. The default is deliberately aggressive.

**It never fires.** Check the hooks installed. `/plugin list` should show the plugin; the nudge hook and `harness_event.py` need to be reachable at `${CLAUDE_PLUGIN_ROOT}/hooks/`.

**The block is longer than the answer.** That is the trivial-Chat guard failing. It should have skipped. Worth an issue with the prompt that caused it.

**It asked five questions and I just wanted a quick answer.** Say "just do it". The count drops to zero immediately and it proceeds with assumptions stated.

**It shows a block on my follow-ups.** Since 2026.11.14 that is intended for a follow-up of 25 words or more that carries answers, decisions or new instructions. Pure continuations and micro-edits under 25 words get none; a block on one of those is an over-fire, so report it.

**A skill I don't have is named in a handoff.** Harmless — the row is inert. Tell it to proceed inline.

---

## Where the design comes from

The block is a typed input → output contract — a DSPy-style *signature* applied one-shot, not compiled.

- **DSPy signatures.** Khattab et al., *DSPy: Compiling Declarative Language Model Calls into Self-Improving Pipelines*, [arXiv:2310.03714](https://arxiv.org/abs/2310.03714) (2023). The closed schema borrows the typed-signature idea and nothing else.
- **Principled instructions.** Bsharat, Myrzakhan, and Shen, *Principled Instructions Are All You Need for Questioning LLaMA-1/2, GPT-3.5/4*, [arXiv:2312.16171](https://arxiv.org/abs/2312.16171) (2023). Source of the transferable instruction-writing moves: name the audience, decompose into ordered steps, state directives affirmatively, assign a role, leave a slot for a user-supplied exemplar.
- **Perspective-guided question asking.** Shao et al., *Assisting in Writing Wikipedia-like Articles From Scratch with Large Language Models* (STORM), [arXiv:2402.14207](https://arxiv.org/abs/2402.14207), NAACL 2024. Shapes the question banks: asking from a named perspective produces better questions than asking generically.
- **Anthropic's Prompting 101.** The block's ordering — task description, dynamic content, detailed instructions, then a closing restatement of what matters — mirrors that structure directly.

**Deliberately not imported: scored iteration.** The 2026 state of the art in prompt optimization is GEPA (Agrawal et al., *GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning*, [arXiv:2507.19457](https://arxiv.org/abs/2507.19457), ICLR 2026), which beats reinforcement learning with far fewer rollouts. It still needs numeric rollouts against a metric. This skill has no eval harness and no metric, so importing evolutionary or auto-demo machinery would be cargo cult. The single bounded critique-then-revise loop is the honest version of that idea; **you are the outer loop.**

If you want real scored optimization, use DSPy or GEPA directly. This is a human-in-the-loop rewriter and does not pretend otherwise.

---

## What it deliberately does not do

- **No scored iteration.** See above.
- **No auto-generated few-shot examples.** `<examples>` appears only when a worked example genuinely sharpens the spec.
- **It does not override your instructions.** It shapes the request, and yours wins on every conflict.
- **It does not evaluate output quality.** It specifies the task. Whether the result is good is a separate question, and one this skill has no opinion about.

---

## Version

`2026.10.16.1`, a same-day patch on the skill's `lastReviewed: 2026-10-16`. This project uses calendar versioning because the skill itself is date-versioned. See [CHANGELOG.md](CHANGELOG.md).

## Contributing

Issues and pull requests welcome. If you change the skip list, change both hooks in the same commit — the three-way contract is the only thing keeping firing behavior coherent.

## License

MIT. Author: Neel Shah, MD, MSc.
