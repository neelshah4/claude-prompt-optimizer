---
name: prompt-optimizer
description: >-
  Use when sharpening a user's request before producing content — fires on
  nearly every substantive turn that carries a task, even when unasked.
  Trigger on: a prompt past one sentence with a task; any content-production
  ask (writing, analysis, code, slides, grants, manuscripts, emails,
  reasoning); an attachment-led ask (file plus instruction); a pasted plan
  or persona to execute or critique; a skill/hook/agent-engineering ask; a
  short but substantive ask; or a cue (optimize my prompt, help me
  draft/analyze/build/review). When ambiguous, fire. Skip categories
  OVERRIDE the trigger: greetings; bare acks/continuations; single-fact
  lookups with no synthesis; bare yes/no; bare definitions;
  status/verification checks; deterministic file/tool commands; in-prompt
  continuations or edits (resume, continue, check it, make the Nth shorter),
  though a continuation adding new work fires; or a block longer than the
  answer. Emits a 5-element prompt block on the first response per task.
lastReviewed: 2026-09-03
---

# Prompt Optimizer

<!-- prompt-optimizer v2026-09-03 (LANGUAGE PASS + mannered-prose line; prior v2026-08-22).
     Canonical in public fork.
     Propagation: Code reads canonical natively; Cowork, the .claude-science org store, and
     chat are re-synced snapshots (not live symlinks; verify with shasum after edits).
     MAINTENANCE: the Skip categories below are mirrored in the UserPromptSubmit hook
     ~/.claude/hooks/prompt-optimizer-nudge.sh. If a Skip category changes, update the hook's
     additionalContext in the SAME change set. The same-change-set contract is now THREE-WAY:
     this SKILL.md Skip list, the UserPromptSubmit nudge hook prompt-optimizer-nudge.sh, and the
     new Stop hook prompt-optimizer-stop-check.sh must move together whenever the Skip/fire
     semantics change.
     Pre-filter gate (2026-07-09): the hook ALSO pre-filters before printing. It silently
     suppresses injection only on high-confidence trivial prompts (pure greetings, bare acks,
     bare yes/no, tightly-anchored status/verification checks, and single deterministic
     commands), and injects on everything else. This pre-filter is a strict, conservative
     SUBSET of the Skip categories above; it does not implement single-fact lookups, bare
     definitions, in-prompt continuations, or block-would-exceed-answer, which stay enforced
     by this skill in-context, not the hook. If the pre-filter regex changes, keep it a subset
     and update this note. False negatives (failing to inject on a real task) are worse than
     false positives.
     Edit history and design rationale: references/versions.md. -->


Sharpen the user's request through structured refinement before execution.

## Output Rule

Display the optimized prompt at the top of the **first substantive response**
for each new task. Skip on follow-up edits, clarifications, and continuations
within the same task.

The output is a 5-element XML block that mirrors Anthropic's Prompting 101
structure (task description → dynamic content → detailed instructions →
optional examples → reminder of critical points):

```
<optimized_prompt>
  <role>One sentence: who Claude is for this task and what the task is.</role>
  <inputs>Named placeholders for dynamic content, or "none".</inputs>
  <instructions>
    Numbered steps, ordered to mirror how a human would naturally work
    through the task. Include format/length/tone constraints inline with
    the step they govern.
  </instructions>
  <examples>Include only if a worked example sharpens the spec; otherwise omit.</examples>
  <critical>Restate AT MOST 2 of the hardest constraints — the two whose
  violation most damages the deliverable (length cap, audience,
  refuse-if-uncertain, format). Everything else lives in <instructions>.
  Repetition at the end is load-bearing for long prompts.</critical>
  <suggested_goal>Include only when the Goal-handoff gate fires (see
  below). A copy-pasteable `/goal <condition>` line derived from
  <critical> + success criteria. Omit entirely when gate is not met.</suggested_goal>
</optimized_prompt>
```

**FIRST-RESPONSE GATE.** The `<optimized_prompt>` block goes at the very top of the
first substantive response for a task, above every other line. If no skip category
applies, the response does not ship without it. Enforcement is external and
deterministic, via the `Stop` hook `prompt-optimizer-stop-check.sh`, not a self-check.

**The schema is closed.** Use exactly `<role>`, `<inputs>`, `<instructions>`,
and `<critical>` as element names, plus `<examples>` /
`<suggested_goal>` only when their gates fire. Never substitute `<task>`,
`<context>`, `<constraints>`, or any other tag; never drop `<inputs>` (use
literal "none") or `<instructions>`. Keep `<instructions>` terse on trivial Chat
asks. If the whole block would run longer than the answer itself, that's a
signal the prompt was trivial: skip the block (and likely the skill) rather than
bloating a short reply.

## Trigger Rules

### Trigger
<!-- >1-sentence threshold (user override 2026-05-29). Fires aggressively on anything past a single sentence. -->

These conditions are independent; fire if any one holds, but only when the
prompt carries a **task to optimize** (production, reasoning, or synthesis). The
length trigger is necessary, not sufficient: a multi-clause prompt with no such
task does not fire (see Skip → status checks, deterministic commands).

- User message is longer than one sentence and carries a task to optimize
- Substantive content-production request: writing, analysis, code,
  presentations, research design, grants, manuscripts, emails, multi-step
  reasoning, comparisons, recommendations. Fires regardless of length;
  even a one-sentence content-production request still fires.
- Explicit cue: "optimize my prompt," "prompt engineer this," "help me
  draft/write/analyze/design/plan/build/compare/review/summarize/explain/
  evaluate/create"

#### High-value fire patterns (these FIRE)

Five measured miss clusters that look skippable but carry a task:

1. **Attachment-led** (`@file …`). The attachment is `<inputs>`; the surrounding
   ask is the task. A bare attachment with a single clause is still a task.
2. **Pasted-plan / persona** ("# Plan — …", "you are a senior engineer…"). The
   plan or persona is context; the task is to execute or critique it. These are the
   highest-value fires.
3. **Meta / skill-and-agent-engineering.** This covers editing skills, hooks,
   agents, workflows, or CLAUDE.md. Content production about the system is still
   content production.
4. **Dense clinical consults.** Fire via the icu-clinical-consult handoff;
   synthesize the block from the specialist's intake even when the specialist runs
   first. A missed block here usually means the specialist was missed too.
5. **Short-but-substantive** ("give me a 1-sentence hypothesis and where to put it
   in the aims"). Length is necessary-not-sufficient in BOTH directions; short does
   not mean skip when the ask produces content.

> These patterns resolve the "looks skippable but isn't" cases toward FIRING. Skip precedence is unchanged: if a Skip category matches, it still wins. A bare deterministic command or a status check on an attached file still skips (an attachment is not a task by itself); a one-word continuation still skips. High-value patterns resolve ambiguous cases as firing; they do not override the Skip list.

### Skip

**Precedence: skip categories OVERRIDE the length trigger.** If a prompt matches any
category below, do not fire, regardless of sentence count; each category names a
prompt with no task to sharpen, so a block there costs a turn and buys nothing. The
fire-when-uncertain tiebreaker applies only after no skip category matches. Each
category is otherwise narrow; borderline-substantive prompts fire.

- Pure greetings ("hi," "hello," "good morning")
- Bare acknowledgments and continuations ("thanks," "ok," "got it,"
  "continue," "go on"), with no new task attached
- A single-fact lookup answerable in one sentence **with no synthesis**.
  Multi-fact requiring synthesis or comparison fires; a flat enumeration or
  bounded list (N named items, one line each) with no synthesis SKIPS.
- A **bare** yes/no with no downstream task ("should I do X, and if so how"
  fires; it carries a task)
- A bare definition with no application
- A **status / system-state / verification check** with no content to produce,
  such as "what's still running," "did X finish," "is Y installed," "check my
  changes," even across multiple clauses or sentences
- A **single deterministic action / file or tool command** with no content to
  produce, such as rename / move / delete / open / run / install X. If bundled
  with a content-production clause, fire on that clause only.
- A **background-task event with no human instruction in it**, such as a
  `<task-notification>`, a `[SYSTEM NOTIFICATION - NOT USER INPUT]` payload, a
  Monitor event, or a returning agent's result. These arrive on the user channel
  but nobody spoke, so there is no request to optimize and the next turn is a
  continuation of work already scoped. This is a **SACRED hard skip**: it survives
  the fire-when-uncertain tiebreaker, because the tiebreaker compares the cost of
  a superfluous block to the cost of a missed optimization, and here there is no
  prompt to miss. Both hooks pre-filter it on the harness-emitted markers (never
  on text shape, so a human quoting one still fires). If the *user* then replies
  with new work, that reply fires normally.
- A **follow-up edit or continuation**, detected by IN-PROMPT signal, anaphora
  or an edit-verb referencing prior work without restating the task: resume,
  continue, also do, now make it, "the [artifact] you built," update the files,
  "still slide X," "check it," "make the Nth shorter." Skips even if >1 sentence.
  (Keyed on observable words, not on session state the skill cannot verify.)
  **Carve-out: a continuation that introduces NEW substantive work FIRES**,
  "update the files with the following [new scope/content]…", "resume — and now
  also draft the discussion" get a fresh block for the new work; pure micro-edits
  ("make the third bullet shorter") still skip.
- **Block-would-exceed-answer.** If the optimized block would run longer than the
  answer itself, the ask is trivial; skip the block (and usually the skill). This
  is the trivial-Chat guard: a one-line reply does not need a five-element frame.

**Tiebreaker** (applies only after no skip matches): when a prompt could plausibly
be either substantive or trivial, treat it as substantive and FIRE. This is the
user's explicit standing preference. A superfluous block costs a few lines; a
missed block costs the whole optimization. Only the SACRED hard skips survive
ambiguity: pure greeting, bare ack, bare yes/no, pure status check, single
deterministic command, background-task event, and pure continuation. The soft categories (single-fact
lookup, bare definition, block-would-exceed-answer) still exist but lose every
tie. The measured register below governs behavior once it fires.

## Core Workflow

```
User prompt arrives
    → Trigger check (skip categories OVERRIDE the length trigger)
        → Phase 0: Classify type + channel + score gaps + ask questions
        → Refine: bounded multi-dimension loop — fix ALL weak dimensions each
          pass; ≤3 passes; stop on all-3 / convergence / capped (silent)
        → Display block + execute
        → Uncertainty loop: if >20% uncertainty remains, follow up
```

### Phase 0: Adaptive Intake

#### A. Classify Task Type

| Type | Signals |
|------|---------|
| WRITING | Emails, manuscripts, abstracts, reports, letters, blogs, grants |
| ANALYSIS | Data analysis, statistics, code for analysis, literature synthesis |
| CODE | Software, scripts, tools, pipelines (not analysis code) |
| CLINICAL | Patient scenarios, physiology; *defer to icu-clinical-consult* |
| PRESENTATION | Slide decks, posters, visual deliverables |
| COMMUNICATION | Outreach, networking, committee messages |
| DOCUMENT | Spreadsheets, templates, checklists |
| RESEARCH-DESIGN | Study design, protocols, grant aims; *defer to grant-review for R01/K* |
| GENERAL | Recommendations, comparisons, explanations, multi-step reasoning |

WRITING, COMMUNICATION, and DOCUMENT tasks carry the mannered-prose line in
`<instructions>` (see Refine).

**Handoff protocol**: If the task activates another skill with its own intake or
required pre-step, that skill runs first; prompt-optimizer then displays a
synthesized `<optimized_prompt>` block from the collected inputs. No
double-intake. Route by this selector:

| Signal | Hand off to (before intake) |
|--------|------------------------------|
| Grant / specific aims / RFA / payoff aim | grant-review |
| Manuscript / abstract / reviewer response | manuscript-reviewer |
| Manuscript-class stats on a **new dataset** | biostat-kickoff (then stats-plan-reviewer) |
| Live patient scenario / physiology / drug-vent-hemodynamics | icu-clinical-consult |
| Buy/hold/sell or position-sizing on a security | personalization-gate |
| Any deliverable that will name citations | clinical-citation-audit / citation-verification |
| Broad grounded multi-source synthesis from scratch, such as "comprehensive/grounded report, survey, landscape, state-of-the-field on topic X," explore-an-unfamiliar-topic, cited long-form built from web sources | `deep-research` **if installed**, else run the sweep inline (see below) |

When "review" is ambiguous (grant vs manuscript), pick by the artifact named:
aims page → grant-review; abstract/results/figures → manuscript-reviewer.

**STORM-shaped task → `deep-research` (route-when / don't-route).** `deep-research`
is the bundled research harness (fan-out web search → fetch → adversarially verify →
cited report); it is the local analog of Stanford's STORM, which is best suited to
*pre-writing a grounded survey of a topic from scratch*, not finishing the user's own
content.
- **Route when all hold:** the deliverable is a broad report/survey on a *topic* (not
  the user's own draft/data); it needs grounding across *many external sources discovered
  from scratch*; the required breadth exceeds the content the user supplied; multi-source
  synthesis is the point.
- **Do not route when ANY holds:** the user supplies the content/data/draft (their
  manuscript, their dataset, their numbers); a single-source or single-fact lookup;
  opinion / taste / recommendation with no source-synthesis; the task is already owned by
  a specialist above (grant-review, manuscript-reviewer, icu-clinical-consult); a short
  answer; or the user explicitly wants Claude's own reasoning, not a web survey.
- **No double-intake:** `deep-research` runs its own 2–3 clarifying questions when the
  topic is underspecified, so prompt-optimizer defers intake to it and synthesizes the
  block from the refined question, the same pattern as grant-review / manuscript-reviewer.
- **CHECK IT EXISTS BEFORE ROUTING.** As of 2026-07-26 no `deep-research` skill is
  installed on this surface. The only copy on disk is an uninstalled legal-plugin skill,
  so this branch pointed at nothing and a STORM-shaped ask silently fell through it.
  Confirm the skill is in the available-skills list first. If it is not, do the work
  inline instead of naming a skill that will not load: run the fan-out yourself (parallel
  web searches across distinct angles → fetch the primary sources → verify each claim
  against what you actually fetched → cite only fetched sources), ask the 2–3 scoping
  questions yourself, and hold the same no-fabrication bar. Never tell the user a skill
  is handling it when no skill exists.

#### B. Classify Output Channel

This drives question count. Documents are expensive to regenerate, so pay
intake cost up front. Chat answers are cheap to refine, so don't stall.

| Channel | Signals | Min Q | Max Q |
|---------|---------|-------|-------|
| **Document / Artifact** | Creates .docx, .pdf, .pptx, .xlsx, .html deliverable; manuscript, abstract, grant aims, slide deck, poster, report | **1** | **5** |
| **Chat** | Explanation, quick analysis, recommendation, code snippet, short answer that stays in conversation | **0** | **2** |

Presentation and Research-Design tasks are always Document channel.

**Channel tiebreaker** (channel is the dominant question-count driver, so resolve
it explicitly): share / send / post / file / deck / poster / one-pager /
outline-that-seeds-a-manuscript / runnable-script language → **Document**; a bare
explain / compare / tell-me / recommend with no artifact noun → **Chat**; when
still ambiguous, prefer **Chat** (cheaper to refine) and let the uncertainty loop
catch any under-asking.

#### C. Score Specification Gaps (1–3 each)

| Dimension | 1 = Gap | 2 = Partial | 3 = Clear |
|-----------|---------|-------------|-----------|
| Goal | No explicit objective | Implied | Stated |
| Format | No format specified | Partial | Exact format/length/structure |
| Audience | Unknown | Inferable | Explicit |
| Constraints | None set | Some | Word count, tone, scope defined |
| Context | Missing background | Partial | Fully specified |

**Score** = sum (5–15). **Uncertainty** = (15 − score) / 10.
- Score 15 → 0% uncertainty
- Score 13 → 20% uncertainty (threshold)
- Score 10 → 50% uncertainty
- Score 5 → 100% uncertainty

**Memory inference penalty**: If a dimension scored 2 or 3 relies on memory
of past chats rather than on the current prompt, downgrade it (3→2, 2→1).
Rationale: the user may be starting something new, and memory-based
assumptions risk over-confident intake. Only information explicit in the
current prompt counts at full value.

<!-- Memory penalty kept strict per 2026-05-19 audit (Q9). Do not relax even when the user appears to be continuing prior work; let the user signal continuation explicitly. -->


#### D. Determine Question Count

Apply the **channel × score** matrix:

| Channel | Score 13–15 (uncertainty <20%) | Score 10–12 (20–50%) | Score 5–9 (>50%) |
|---------|--------------------------------|----------------------|------------------|
| **Chat** | **0 Q** | **1 Q** | **2 Q** |
| **Document / Artifact** | **1 Q** (content-extending) | **4 Q** | **5 Q** |

> **Matrix note:** the Document/Artifact 13–15 band is a distinct cell, not a
> rounding of "0 Q." It asks exactly **1 content-extending** question (emphasis /
> framing / reviewer lens, per Phase 0.E), never a dimensional-gap question. Only
> the Chat 13–15 cell goes to 0 Q.

The prompt is already specified, so the question sharpens output direction
rather than re-asking what the user already supplied.

**Uncertainty override loop**: After the initial batch, recompute the score
using the answers. If uncertainty remains >20% (score <13), ask a follow-up
batch in the next turn before proceeding. Continue until uncertainty drops
below 20% or the user signals override. For document-producing work, it's
cheaper to ask now than to regenerate later.

**User override (always wins)**: "just do it," "just give me," "just
list/show," "stop asking," "you decide," "proceed," "go ahead," "autonomously,"
"keep going," or similar end the intake loop. A user-specified question count
overrides the matrix in BOTH directions. "Ask me 5–10," "quiz me" RAISE the cap;
"just"-class LOWER it to 0 Q. Note: a "just give me X" caps questions at 0 but
does **not** by itself suppress firing; the skill still fires and shows the
block; it just proceeds without a clarifying question.

#### E. Question Banks by Task Type

**When the count from Phase 0.D is above 0, read `references/question-banks.md`
before asking.** It holds the per-task-type option banks, the perspective-guided
(STORM) framing technique, and the rule for reading the banks against the Phase 0.C
dimensions. Nothing there changes the count set by the matrix above.

#### F. Incorporate Answers

Phase 0 answers become hard constraints. If they contradict memory, current
answers win.

### Refine

With Phase 0 complete:

1. **Objective**, confirmed or inferred.
2. **Success criteria**, what separates excellent from mediocre output.
3. **Constraints**, from Phase 0 + user preferences.
4. **Gaps**, state assumptions internally if any remain.

Draft the optimized prompt, then run a **bounded multi-dimension refinement
loop**. Score all five dimensions 1–3 each pass; fix every weak one at once;
stop when it converges.

The five dimensions:

- **Specificity.** Are the instructions concrete and unambiguous?
- **Completeness.** Are all constraints, formats, and criteria captured?
- **Economy.** Is every instruction necessary, or is anything redundant?
- **Alignment.** Does it match what the user actually needs, not what's easy?
- **Order.** Do steps unfold in the order a human would naturally work
  through this? Information needed first should appear first; downstream
  steps should reference upstream context, not the reverse.

**Frontier-idiomatic output (applies when drafting the block's `<instructions>` and
`<role>`):** these are model-agnostic and hold on every current Claude model.
- **Give the reason, not only the request.** When it sharpens direction, name who the
  deliverable is for and what it enables, then state the task. Claude connects the work
  to the right context instead of inferring it.
- **Lead with the outcome.** Order instructions so the most important constraint and the
  end state come first; supporting detail follows.
- **Enumerate sparingly.** A strong single instruction beats a long "don't do X, don't
  do Y" list; keep only the constraints that each add something distinct (this is the
  Economy dimension applied to the generated prompt, not just to this skill's prose).
- **Let thinking carry the reasoning.** Do not instruct the target to "explain your
  reasoning in the response"; it bloats output and can trip a refusal.
- **Decompose at natural joints.** A step that hides two deliverables is under-split;
  steps smaller than a real unit of work mean the split went one layer too deep. Depth
  follows the task's joints; it is never adjusted to signal more effort.
- **Prefer the cheap reversible action to a prediction about it.** When the target could
  run the check, open the file, or read the value, write the step as that action and its
  observation, not as reasoning about what the result would probably be.
- **Remove all mannered prose.** On WRITING, COMMUNICATION, and DOCUMENT tasks, the
  generated `<instructions>` carry one line: "Remove all mannered prose: say what you
  mean, and use the literal phrase where one exists." Source: Anthropic's Fable 5.1
  prompting guidance, which places this instruction in the user message. It is one
  line, added once, and is exempt from the Economy pass.

**Instruction-writing moves** (the transferable core of the prompt-engineering
literature, Bsharat et al. "Principled Instructions," arXiv 2312.16171, applied
one-shot, not as a search): name the audience and its expertise; decompose a
complex ask into ordered steps; state directives affirmatively (do X, not "don't
do Y"); assign a role in `<role>`; leave an `<inputs>` slot for any exemplar the
user should supply rather than inventing one. These sharpen `<role>`/`<instructions>`;
they never expand the block past what the task needs.

**Each pass:**

1. **Score** all five dimensions 1–3 (1 = weak, 3 = strong; same rubric as the
   Phase 0.C gap scale).
2. **Revise every dimension scoring below 3 in the SAME pass**, not just the
   single weakest. Fixing weak dimensions together avoids the trade-off where
   improving one quietly degrades another (e.g., adding Specificity bloats
   Economy).
3. **Resolve trade-offs in favor of Alignment.** If strengthening one
   dimension forces a cost on another, choose the resolution that best serves
   what the user actually needs; note the tension internally. **Never drop
   Economy from the same-pass fix.** When expanding Specificity/Completeness
   depresses Economy, re-tighten Economy in that same pass (fold lists into
   referenced clauses) instead of deferring it.
4. **Stop** when ANY holds: (a) all five dimensions score 3; (b) a pass yields
   no material improvement over the prior version (convergence); (c) 3 passes
   completed; or (d) **CAPPED, not converged**, a dimension cannot reach 3
   because the required input is absent from the prompt and inventing it would
   fabricate. A capped stop is not the same as convergence: it must (1) name the
   missing input as an explicit `<inputs>` placeholder and (2) raise it as a
   clarifying question (or fold it into the Document question batch) rather than
   emit a thin block. Scope this to genuinely-missing input; do not re-ask about
   content the prompt already answered. Gains plateau fast; a 3rd pass is
   rarely needed.

The loop runs on every triggered turn (Chat and Document alike). Because it
stops on convergence, an already-strong prompt resolves in a single pass, so
"run it everywhere" self-limits. **Refinement is silent.** Show only the
final `<optimized_prompt>` block, never the intermediate passes. Commit.

### Completion Contract

**Content gate, not a trigger.** This decides what goes *inside* an already-fired block.
It never decides whether prompt-optimizer fires, never suppresses it, and can never
override a skip-listed prompt. Skip precedence is absolute, and a count word inside a
status check or a micro-edit changes nothing.

**Fires when BOTH hold.** (1) **Enumerable.** The ask names or implies a set the
deliverable must cover completely (an explicit N; *all / every / each / the whole*; a
sweep, audit, or inventory), or the deliverable will state a count, tally, or percentage
Claude must **derive** rather than quote. (2) **Silent under-coverage is possible.**
Multi-file or multi-artifact output, a long autonomous run, or an explicit thoroughness
cue. **Excluded:** the whole set fits in one short answer; the number bounds the OUTPUT
rather than the work, a length cap ("500 words") or a quantity to produce ("3 options"),
as opposed to defining a coverage set the work must sweep ("all 47 files"); or a
specialist owns coverage via handoff. That distinction is the whole test: an explicit N
fires only when it names what must be covered, never when it caps what is produced. A thoroughness cue
raises strictness only. "Resume, and don't be lazy this time" is still a pure
continuation and still skips.

**What it changes.** One sharpened line, then silence.

1. **The done-condition is the final step.** The last numbered `<instructions>` step
   IS the countable done-condition, replacing the generic verify step that would
   otherwise be written: "all 47 files opened, count stated in the closeout," never
   "verify the output." Add no step where one already exists. It may be promoted into a
   `<critical>` slot when under-coverage IS the dominant failure mode. This is a
   permission, never a mandate.
2. **Report audit, behavioural, zero output.** Any count, tally, or percentage stated in
   the deliverable or the closeout is re-measured at report time from the artifact or the
   tool output, or labeled unverified. Its evidence is stated in the closeout sentence
   CLAUDE.md already requires. Scope: numbers Claude derived this session; claimed
   external specifics stay with `fabrication-audit`.
3. **Deviation disclosure, behavioural, zero output on the happy path.** Full coverage
   adds nothing. Partial coverage must state what was covered and what was not. Sampling
   is legitimate; silent sampling is not.

**Economy.** The contract adds no standalone boilerplate, only the final step's countable
wording, which the refine loop must not compress away, and which does not count toward the
block-would-exceed-answer guard.

Read `references/completion-discipline.md` when the run is long, multi-artifact, or
orchestrated.

### Display and Execute

1. Display the `<optimized_prompt>` block at the top of the response.
2. Execute the task guided by the prompt. Deliver output below.
3. If Document channel and post-answer uncertainty still >20%: ask
   follow-up batch in the next turn before executing the deliverable.

### Goal Handoff (default-on suggestion)

`/goal` is a built-in Claude Code command (≥ 2.1.139) that sets a
session-scoped completion condition: after every turn, a small/fast model
checks whether the condition is met from the transcript. If not, Claude
takes another turn. prompt-optimizer and `/goal` compose; prompt-optimizer
specifies *what to do*, `/goal` specifies *when to stop*.

> **`/goal` in one line (for readers new to it):** the user types
> `/goal <measurable end state> — or stop after N turns` and Claude keeps
> working until a fast evaluator reads that state as met. Example:
> `/goal every section drafted and under its word cap, or stop after 15 turns`.

**Suggest only.** Setting a goal immediately starts a loop, so
prompt-optimizer only ever surfaces a pre-filled, copy-pasteable line, in the
`<suggested_goal>` element, and lets the user opt in
explicitly. Never run `/goal` on the user's behalf.

**Gate (Document-only, 2026-08-08):** include `<suggested_goal>`
on **Document / Artifact tasks only**, single-pass included (a one-figure or
abstract task still gets a pasteable line; the user may still want it verified).

**Chat tasks never get `<suggested_goal>`**, regardless of autonomy signal or
multi-turn shape. The user knows `/goal` exists; the suggestion was unnecessary.
(Pre-2026-08-08 this gate also fired on autonomy-signal Chat tasks. The duplicate CTA
line rendered under the block was removed 2026-08-22. The element carries the
pasteable line once, and once is enough.)

**Condition-writing rules, always pre-filled and countable:**
- One measurable end state, filled in concretely (never the literal template token).
- The `/goal` evaluator is a **small/fast model that CANNOT call tools or read
  files.** It judges only what Claude has already surfaced in the transcript. So
  phrase the condition to be transcript-provable: artifact written at a stated
  path, N sections shown drafted, each section under its word cap, every cited item
  shown resolving.
- When "done" is naturally subjective (taste, tone, persuasiveness), substitute
  transcript-provable proxies rather than dropping the suggestion.
- Always include a natural-language turn bound inside the condition, "or stop
  after N turns." There is no `--max-turns` flag; the bound is prose.
- ≤ 4,000 chars total.
- When the Completion Contract fired, the condition inherits its countable
  done-condition, the same N-of-N, naming the evidence the transcript must show.

**Format inside `<suggested_goal>`:**

```
/goal <condition phrased so the evaluator can read the answer from the
transcript> — or stop after N turns
```

Nothing is rendered under the block. The pre-filled line lives in `<suggested_goal>`
and nowhere else; if the gate doesn't fire (any Chat-channel task), omit the element
rather than leaving it empty.

### Setup-Recommender Handoff (large projects only)

Fires only on a CODE or repo-rooted ANALYSIS task in a large, ongoing codebase (git repo with a manifest and more than 50 source files, or multi-week / team / onboarding signals), once per repo per session, and never when the user has opted out. Read `references/setup-recommender.md` for the full four-condition gate and the exact announcement line before firing; then invoke `claude-code-setup:claude-automation-recommender` via the Skill tool after the `<optimized_prompt>` block and continue the original task. When the gate does not fire, say nothing.

## Self-improvement
Lessons leave this file. When a run of this skill produces a correction, a
missed edge case, or a wrong-shaped output, append one observation via
`~/.claude/scripts/skill-observation-add.sh --target prompt-optimizer` and keep working;
the monthly drain folds it back through skill-eval. Never edit this skill mid-run.

## Examples

Five worked examples, grant aims via handoff, a Chat email showing the memory penalty,
a score-15 Document with the content-extending question, a long-request auto-trigger, and
the uncertainty override loop, live in `references/examples.md`. Read them when a case is
genuinely borderline; the trigger rules, skip list, schema, matrix, and handoff selector
above are authoritative on their own.

## Rules

1. The `<optimized_prompt>` block appears at the top of the first substantive
   response per task, structured as the closed 5-element template (see Output Rule
   for the canonical schema).
2. Question count is channel × score: Chat 0–2; Document 1–5 (1 only at
   score ≥ 13, content-extending).
3. Uncertainty override loop: if >20% uncertainty remains after the initial
   questions on a Document task, ask a follow-up batch next turn (see Phase 0.D
   for the recompute logic).
4. Memory inference penalty applies (3→2, 2→1) for memory-based dimensions; full
   credit only for what's explicit in the current prompt (canonical rule: Phase 0.C).
5. Defer to specialist skills/pre-steps for their intake, then synthesize their
   output into the `<optimized_prompt>` block: grant-review, manuscript-reviewer,
   icu-clinical-consult, biostat-kickoff (new-dataset stats), personalization-gate
   (securities sizing), clinical-citation-audit / citation-verification
   (citation-bearing deliverables), deep-research (broad grounded multi-source
   synthesis of a topic from scratch, STORM-shaped; not the user's own
   content/data). See the Handoff selector for the route-when / don't-route test.
6. User override beats every rule above:
   (a) "just do it" / "just give me" / "stop asking" / "you decide" / "proceed" /
   "autonomously" → skip the intake questions, proceed with assumptions stated
   explicitly. The block STILL fires (unless skip-listed).
   (b) A user-named count ("ask me 5–10," "quiz me") → RAISES the question cap.
   (c) "Just"-class defaults → LOWER the count to 0 (but still fires).
7. Goal handoff (Document-only, 2026-08-08): include `<suggested_goal>` on
   Document / Artifact tasks only (single-pass included). Chat tasks never get it,
   regardless of autonomy signal. Suggest the `/goal` line; never auto-fire on the
   user's behalf. The duplicate CTA line under the block was removed 2026-08-22.
8. End-of-turn summary length: 1–2 sentences, always (2026-08-08, the former
   3–5-sentence band for non-trivial turns is deleted). This governs the prose
   after the deliverable, not the deliverable itself.
9. Completion Contract (2026-08-22) is a CONTENT gate, never a trigger: it shapes what
   goes inside an already-fired block and can never change whether the skill fires. When
   it fires, the final `<instructions>` step is the countable done-condition; derived
   numbers are re-measured at report time or labeled unverified; partial coverage is
   declared. Canonical home: the Completion Contract section.
10. Mannered-prose line (2026-09-03): WRITING, COMMUNICATION, and DOCUMENT blocks
    carry the one-line instruction "Remove all mannered prose: say what you mean, and
    use the literal phrase where one exists." It never affects firing.

## Gotchas / Known Failure Modes

| Thought | Reality |
|---|---|
| "Show the optimized block every turn." | It belongs at the top of the FIRST substantive response per task only. Re-displaying it on follow-up edits, clarifications, and continuations within the same task is the most common over-fire. |
| "Both this skill and grant-review/manuscript-reviewer/icu-clinical-consult should run their intake." | No double-intake. The specialist skill runs its intake first; prompt-optimizer then synthesizes one `<optimized_prompt>` from the collected inputs (Handoff protocol). |
| "Audience/Constraints are clear because I remember them from past chats." | Apply the memory inference penalty (3→2, 2→1). Only what's explicit in the current prompt earns full credit; the user may be starting something new. |
| "Score 14, so skip questions." | For Document/Artifact channel even score 13+ asks 1 *content-extending* question (emphasis/framing/reviewer lens), not zero. Only Chat channel goes to 0 Q. |
| "User said 'just do it' but I have one more question." | User override wins immediately. End the intake loop and proceed with assumptions made explicit. |
| "Keep refining until the prompt is perfect." | The refine loop is bounded: fix all weak dimensions each pass, stop at ≤3 passes or on convergence. Gains plateau fast; a 3rd pass is rarely needed. Never show the intermediate passes; only the final block. |
| "Revise only the single weakest dimension." | Old behavior. Fix EVERY dimension scoring below 3 in the same pass; one-at-a-time lets fixing one quietly degrade another. Resolve trade-offs toward Alignment. |
| "It's >1 sentence, so fire." | Length is necessary, not sufficient, and skip categories OVERRIDE it. A multi-clause status check ("what's still running, did it work?"), a deterministic command ("rename X to Y"), or an in-prompt continuation ("resume…", "check it") SKIPS regardless of sentence count. |
| "This continuation is a follow-up, so skip." | Only PURE micro-edits skip ("make the third bullet shorter"). A continuation that introduces NEW substantive work FIRES, "update the files with the following [new scope]…", "resume — and now also draft the discussion" get a fresh block for the new work. |
| "Attachment-led / pasted-plan / one-line ask, looks skippable." | These are the highest-value FIRES. An `@file` attachment is `<inputs>` and the surrounding ask is the task; a pasted plan or persona is context to execute or critique; a short-but-substantive ask still produces content. But skip precedence is unchanged. If a Skip category matches (a bare command, a status check on an attached file, a one-word continuation), it still wins. |
| "The loop stopped, call it converged." | A stop with a dimension still <3 because the input is missing is CAPPED, not converged. Name the missing input as an `<inputs>` placeholder and raise it as a question; don't emit a thin block that hides the gap. |
| "I'm finished, so I'll write the summary." | A report is a set of claims backed by a measurement, never a feeling of completion. Re-measure every derived count at report time or label it unverified, and declare any coverage you did not achieve; a silently narrowed sweep reads exactly like a complete one. |
| "Broad 'write me a report on X', just optimize and answer it inline." | If it needs grounding across many sources discovered from scratch (a survey / landscape / state-of-the-field on a topic), route to `deep-research` and defer intake to it (no double-intake). But do not route the inverse: the user's own draft/data, single-fact lookups, opinion/taste, specialist-owned tasks, or short answers. Those stay inline. See the STORM-shaped route-when / don't-route test. |
| "The block is already long; drop the mannered-prose line to save space." | It is one line, scoped to prose-producing task types, and exempt from the Economy pass. Keep it. |

## Versions

Full version history: `references/versions.md` (historical records, not current
instructions).
