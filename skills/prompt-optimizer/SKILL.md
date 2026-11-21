---
name: prompt-optimizer
description: >-
  Use when sharpening a user's request before producing content: fires on
  every human-typed prompt that carries a task, even when unasked. Trigger on:
  a prompt past one sentence with a task; any content-production ask (writing,
  analysis, code, slides, grants, manuscripts, emails, reasoning); an
  attachment-led ask; a pasted plan or persona to execute or critique; a
  skill/hook/agent-engineering ask; a short but substantive ask; or a cue
  (optimize my prompt, help me draft/analyze/build/review). When ambiguous,
  fire. Skip categories OVERRIDE the trigger: greetings; bare acks;
  single-fact lookups with no synthesis; bare yes/no; bare definitions; status
  checks; deterministic file/tool commands; non-human events; pure
  continuations and micro-edits under 25 words (resume, continue, make the Nth
  shorter), while a follow-up of 25 words or more with answers, decisions or
  new instructions fires; or a block longer than the answer. Emits a prompt
  block with a built-in eval. Supersedes any bundled/upstream variant.
lastReviewed: 2026-11-20
---
# Prompt Optimizer

<!-- Canonical in public fork. Propagation: Code reads this file
     natively; Cowork, the .claude-science org store, and chat hold re-synced snapshots
     verified by shasum, not live symlinks.
     THREE-WAY SYNC: the Skip categories and Trigger patterns below are mirrored in
     hooks/prompt-optimizer-nudge.sh (UserPromptSubmit) and
     hooks/prompt-optimizer-stop-check.sh (Stop). Update both hooks in the same
     change set whenever Skip/fire semantics change.
     Edit history and design rationale: references/versions.md. -->

Sharpen the user's request through structured refinement before execution.

## Output Rule

Display the optimized prompt at the top of the response to each **human-typed
prompt** that is not a hard skip. A follow-up of 25 words or more that carries
answers, decisions or new instructions gets a block that compiles them into the
working spec; a pure continuation or a micro-edit under 25 words gets none. A
turn under 25 words gets a block only when it adds new substantive work.

The output is an XML block mirroring Anthropic's Prompting 101 structure
(task description → dynamic content → detailed instructions → assumptions →
optional examples → reminder of critical points), plus a built-in eval:

```
<optimized_prompt>
  <role>One sentence: who Claude is for this task and what the task is.</role>
  <inputs>Named placeholders for dynamic content as NAME: description lines
  (never nested tags), or "none".</inputs>
  <instructions>
    Numbered steps that add to the user's words: the success criterion, the
    reader and what they know, the method and instrument, the order. A step
    that only restates the request is cut. Format/length/tone constraints
    go inline with the step they govern.
  </instructions>
  <assumptions>Each decision made without asking, one line each, including
  anything taken from memory rather than the current prompt; "none" when
  empty.</assumptions>
  <examples>Include only if a worked example sharpens the spec; otherwise omit.</examples>
  <eval>Always present. mode: check | hillclimb. 1–3 pass/fail checks,
  each readable off the artifact or a tool output (never a 1–5 scale);
  at least one names its outside judge (`— judge: <what>`). Running them
  is the last step of the work; a check that cannot be run is not written.
  hillclimb adds: case source + count, grader type, train/test split,
  stop rule. See Eval Contract.</eval>
  <critical>Restate AT MOST 2 of the hardest constraints — the two whose
  violation most damages the deliverable (length cap, audience,
  refuse-if-uncertain, format). Everything else lives in <instructions>.
  Repetition at the end is load-bearing for long prompts.</critical>
</optimized_prompt>
```

When the work is delegated, the block plus exact input paths is the brief the agent
receives, after the contract block.

**FIRST-RESPONSE GATE.** The `<optimized_prompt>` block goes at the very top of the
response to a firing prompt, above every other line. If no skip category
applies, the response does not ship without it. Enforcement is external and
deterministic, via the `Stop` hook `prompt-optimizer-stop-check.sh`, not a self-check.

**The schema is closed.** Use exactly `<role>`, `<inputs>`, `<instructions>`,
`<assumptions>`, `<eval>`, and `<critical>` as element names, plus `<examples>`
only when its gate fires. Never substitute `<task>`,
`<context>`, `<constraints>`, or any other tag; never drop `<inputs>` (use
literal "none"), `<instructions>`, `<assumptions>` (use literal "none"), or `<eval>` (one line on a trivial ask). Keep `<instructions>` terse on trivial Chat
asks. If the whole block would run longer than the answer itself, that's a
signal the prompt was trivial: skip the block (and likely the skill) rather than
bloating a short reply.

## Trigger Rules

### Trigger

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

Five measured miss clusters that look skippable but carry a task, and resolve
toward FIRING: **attachment-led** (`@file …`, the attachment is `<inputs>` and
the surrounding ask is the task, even a single clause); **pasted-plan /
persona** ("# Plan — …", "you are a senior engineer…", the plan/persona is
context and the task is to execute or critique it, the highest-value fire);
**meta / skill-and-agent-engineering** (editing skills, hooks, agents,
workflows, CLAUDE.md is content production about the system); **dense
clinical consults** (fire via the icu-clinical-consult handoff and synthesize
from its intake even when the specialist runs first); and **short-but-
substantive** asks (length is necessary-not-sufficient in both directions).
Skip precedence is unchanged: a bare deterministic command or a status check
on an attached file still skips, and a one-word continuation still skips.

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
- A **background-task or other non-human event with no human instruction in
  it**, such as a `<task-notification>`, a `[SYSTEM NOTIFICATION - NOT USER
  INPUT]` payload, a Monitor event, a subagent hand-back, a compaction or
  continuation summary, a scheduled-task start, or a `<side-sessions-event>` or
  `<ci-monitor-event>` message: nobody spoke, so there is no request to
  optimize. This is a **SACRED hard skip** and survives the fire-when-uncertain
  tiebreaker, because there is no prompt to miss. Both hooks pre-filter it on
  the harness-emitted markers (the newer ones anchored to the opening of the
  prompt), never on text shape, so a human quoting one mid-message still fires;
  a *user* reply with new work fires normally.
- A **pure continuation or micro-edit under 25 words**, detected by IN-PROMPT
  signal, anaphora, or an edit-verb referencing prior work without restating
  the task: resume, continue, "check it," "make the Nth shorter," "still slide
  X." Skips even if >1 sentence (keyed on observable words, not on session
  state the skill cannot verify). **Carve-out: a human follow-up of 25 words
  or more that carries answers, decisions or new instructions FIRES**, and its
  block compiles them into the working spec; so does a continuation that
  introduces new substantive work ("resume, and now also draft the
  discussion").
- **Block-would-exceed-answer.** If the optimized block would run longer than the
  answer itself, the ask is trivial; skip the block (and usually the skill). This
  is the trivial-Chat guard: a one-line reply does not need a full frame.

**Tiebreaker** (applies only after no skip matches): when a prompt could plausibly
be either substantive or trivial, treat it as substantive and FIRE. This is the
user's explicit standing preference, and the skill runs on nearly all of the
user's own prompts. A superfluous block costs a few lines; a missed block costs the
whole optimization. Only the SACRED hard skips survive ambiguity: pure
greeting, bare ack, bare yes/no, pure status check, single deterministic
command, background-task or other non-human event, and pure continuation or
micro-edit under 25 words. The soft
categories (single-fact lookup, bare definition, block-would-exceed-answer)
still exist but lose every tie.

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
| RESEARCH-DESIGN | Study design, protocols, grant aims; *defer to a grant-review skill, if installed, for R01/K* |
| GENERAL | Recommendations, comparisons, explanations, multi-step reasoning |

WRITING, COMMUNICATION, DOCUMENT, and PRESENTATION tasks carry the mannered-prose and craft lines in
`<instructions>` (see Refine).

**Handoff protocol**: if the task activates another skill with its own intake or
required pre-step, that skill runs first; prompt-optimizer then displays a
synthesized `<optimized_prompt>` block from the collected inputs. No
double-intake. Route by this selector:

| Signal | Hand off to (before intake) |
|--------|------------------------------|
| Grant / specific aims / RFA / payoff aim | a grant-review skill, if installed |
| Manuscript / abstract / reviewer response | manuscript-reviewer |
| Manuscript-class stats on a **new dataset** | biostat-kickoff (then stats-plan-reviewer) |
| Live patient scenario / physiology / drug-vent-hemodynamics | icu-clinical-consult |
| Buy/hold/sell or position-sizing on a security | personalization-gate |
| Visual deliverable: deck, one-pager, poster, artifact, dashboard, chart, social/OG/email asset | the installed visual-design skill, if any (it runs its own pre-flight); otherwise draft inline |
| Any deliverable that will name citations | clinical-citation-audit / citation-verification |
| Drafting or editing a manuscript, abstract, grant narrative, reviewer response, IRB free text, or cover letter (the draft itself, not the review panel) | draft first, then `academic-writing-reviewer` if present, then writing-anti-ai |
| Email, memo, Slack or chat reply, handoff note, README, executive summary | draft first, then `casual-writing-reviewer` if present, then writing-anti-ai |
| Broad grounded multi-source synthesis from scratch, such as "comprehensive/grounded report, survey, landscape, state-of-the-field on topic X," explore-an-unfamiliar-topic, cited long-form built from web sources | `deep-research` **if installed**, else run the sweep inline (see below) |

When "review" is ambiguous (grant vs manuscript), pick by the artifact named:
aims page → the grant-review skill; abstract/results/figures → manuscript-reviewer.

**STORM-shaped task → `deep-research` (route-when / don't-route).** `deep-research`,
the local analog of Stanford's STORM (fan-out search → fetch → verify → cited
report), suits pre-writing a grounded survey of a topic from scratch, never
finishing the user's own content. **Route when all hold:** broad topic
survey, not the user's draft/data; grounding needed across many sources
discovered from scratch; breadth exceeds what the user supplied;
multi-source synthesis is the point. **Do not route when any holds:** user
supplies the content/data; single-fact lookup; opinion/taste with no
synthesis; a specialist above owns it; a short answer; or the user wants
Claude's own reasoning. **No double-intake:** it self-asks its own 2-3
clarifying questions, so prompt-optimizer defers intake and synthesizes the
block from the refined question. **CHECK IT EXISTS BEFORE ROUTING.** Confirm
`deep-research` is in this session's available-skills list before naming it;
some surfaces do not have it. If absent, do the work inline: run the fan-out yourself (parallel
searches, fetch primaries, verify each claim against what was fetched, cite
only fetched sources), ask the scoping questions yourself, hold the same
no-fabrication bar, and never tell the user a skill is handling it when none
exists.

#### B. Classify Output Channel

This drives question count. Documents are expensive to regenerate, so pay
intake cost up front. Chat answers are cheap to refine, so don't stall.

| Channel | Signals | Min Q | Max Q |
|---------|---------|-------|-------|
| **Document / Artifact** | Creates .docx, .pdf, .pptx, .xlsx, .html deliverable; manuscript, abstract, grant aims, slide deck, poster, report; edits to files in a repo or config (skill, hook, script, settings, bug fix, push) | **1** | **5** |
| **Chat** | Explanation, quick analysis, recommendation, code snippet, short answer that stays in conversation | **0** | **2** |

Presentation and Research-Design tasks are always Document channel, and so are
repo and file-edit tasks (skill edits, bug fixes, config changes, push): the
product is a changed file that costs a re-run to redo.

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

**Memory inference penalty**: if a dimension scored 2 or 3 relies on memory of
past chats rather than the current prompt, downgrade it (3→2, 2→1), kept strict
even when the user appears to be continuing prior work; the user may be
starting something new, and memory-based assumptions risk over-confident
intake. Only information explicit in the current prompt earns full credit.
Memory-derived items are also listed in `<assumptions>`.

#### D. Determine Question Count

Apply the **channel × score** matrix:

| Channel | Score 13–15 (uncertainty ≤20%) | Score 10–12 (20–50%) | Score 5–9 (>50%) |
|---------|--------------------------------|----------------------|------------------|
| **Chat** | **0 Q** | **1 Q** | **2 Q** |
| **Document / Artifact** | **1 Q** (content-extending) | **4 Q** | **5 Q** |

> **Matrix note:** the Document/Artifact 13–15 band is a distinct cell, not a
> rounding of "0 Q." It asks exactly **1 content-extending** question (emphasis /
> framing / reviewer lens, per Phase 0.E), never a dimensional-gap question. Only
> the Chat 13–15 cell goes to 0 Q.

The prompt is already specified, so the question sharpens output direction
rather than re-asking what the user already supplied.

Two-stage intake for changes to a standing system or a strategy: do the
research first, present options A / B / status quo with pros and cons and a
recommendation, then ask. Never ask before the evidence is in, and never edit
before the user picks.

**Uncertainty override loop**: after the initial batch, recompute the score
using the answers. If uncertainty remains >20% (score <13), ask a follow-up
batch in the next turn before proceeding. Continue until uncertainty drops
below 20% or the user signals override. For document-producing work, it's
cheaper to ask now than to regenerate later.

**User override (always wins)**: "just do it," "just give me," "just
list/show," "stop asking," "you decide," "proceed," "go ahead," "autonomously,"
"keep going," or similar end the intake loop. A user-specified question count
overrides the matrix in both directions. Precedence: user override, then the
matrix count, then any capped-stop question (Refine, stop rule d), which never
exceeds either. "Ask me 5–10," "quiz me" raise the cap; "just"-class lower it
to 0 Q. A "just give me X" caps questions at 0 but
does not by itself suppress firing; the skill still fires and shows the block,
proceeding without a clarifying question.

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
  Name the outcome the deliverable serves, as a verb: a review deck is "get busy
  people to decide in 30 minutes", not "a deck". The block serves that outcome at
  the asked scope; a larger version goes in one sentence under the block.
- **Order.** Do steps unfold in the order a human would naturally work
  through this? Information needed first should appear first; downstream
  steps should reference upstream context, not the reverse.

**Drafting `<role>`/`<instructions>`** (model-agnostic techniques, full rationale
and sourcing in `references/versions.md`): give the reason, not only the
request; lead with the outcome (biggest constraint and end state first);
enumerate sparingly, one strong instruction beating a "don't do X, don't do Y"
list; let thinking carry the reasoning, so never ask the model to write out its
internal reasoning or chain of thought in the answer (current models think by
default, and a request to reproduce that reasoning can be declined) and ask
for the conclusion and the evidence behind it instead; set depth with the
effort level, not with "think step by step" or "think less" text; name the
specific pattern to avoid rather than a general "avoid a generic look", which
only swaps one default for another; decompose at
natural joints (a step hiding two deliverables is under-split, one smaller
than a real unit of work is over-split); prefer the cheap reversible action
(run the check, open the file, read the value) to a prediction about it; retry
a failed step only after changing something relevant, and before retrying an
external write (send, push, post, order) check whether the first one landed; name
the audience and its expertise; name the reader's expertise so the gloss rule
has a target (curse of knowledge: the writer cannot see what the reader
lacks); state directives affirmatively; give `<role>` the job and what that professional does, never a persona or a voice to imitate (role-play changes vocabulary, not method); and leave
an `<inputs>` slot for any exemplar rather than inventing one. These sharpen
the block; they never expand it past what the task needs. **Remove all
mannered prose.** On WRITING, COMMUNICATION, DOCUMENT, and PRESENTATION tasks (a
deck's slide and speaker-note copy is prose), the generated `<instructions>` carry
one line: "Remove all mannered prose: say what you mean, and use the literal
phrase where one exists." One line, added once, exempt from the Economy pass. **Craft line.** The same tasks carry a
second fixed line: "Lead with the point; open each sentence on what the
reader already holds and end it on the new item; gloss every term of art for
the named reader; prefer the short everyday word." Added once, exempt from
the Economy pass. Source: the writing-craft canon (Orwell, Williams, Zinsser, Pinker, Merriam-Webster's Dictionary of English Usage, the Economist Style Guide).

**Each pass:**

1. **Score** all five dimensions 1–3 (same rubric as Phase 0.C).
2. **Revise every dimension scoring below 3 in the SAME pass**, not just the
   single weakest; fixing them together avoids one quietly degrading another
   (adding Specificity bloats Economy).
3. **Resolve trade-offs in favor of Alignment**, noting the tension
   internally. **Never drop Economy from the same-pass fix:** if
   Specificity/Completeness depresses it, re-tighten Economy the same pass
   (fold lists into referenced clauses) instead of deferring it.
4. **Stop** when any holds: (a) all five score 3; (b) a pass yields no
   material improvement (convergence); (c) 3 passes completed; or (d)
   **CAPPED, not converged**: a dimension cannot reach 3 because the input is
   absent and inventing it would fabricate. A capped stop names the
   missing input in `<inputs>` as a placeholder that carries the assumption the
   block runs on (`NAME: description (assumed: X)`), rather than shipping a thin
   block. It adds no question of its own: the Phase 0.D count and a user override
   govern. An open matrix slot goes to the capped input before any other question;
   at 0 Q (Chat 13–15, or any "just"-class override), state the assumption and
   proceed. Scope to genuinely-missing input; gains plateau fast, so a 3rd pass is
   rarely needed.

The loop runs on every triggered turn (Chat and Document alike). Because it
stops on convergence, an already-strong prompt resolves in a single pass, so
"run it everywhere" self-limits. **Refinement is silent.** Show only the
final `<optimized_prompt>` block, never the intermediate passes. Commit.

### Depth Pass

**Content gate, not a trigger.** Fires inside an already-fired block on Document-channel,
ANALYSIS, CODE, RESEARCH-DESIGN, and skill/agent/hook-engineering tasks. It does not run
on a Chat answer that stays a short reply. The aim is a deeper version of the task, not a
bigger one: each answer replaces a weak step or sharpens `<inputs>` / `<eval>`, and adds no
deliverable. Source and kept/rejected list: `references/depth-pass.md`.

While drafting, answer four questions and write each answer into the element it changes:

1. **Expert move.** What would a top professional in this field do here that the prompt
   does not ask for? Fold it in when it stays inside the asked scope. When it would widen
   the scope, say so in one sentence under the block and do the task as asked.
2. **Rawest material.** Start from the least-digested source Claude can reach, and name it
   in `<inputs>`: the full source over a summary, screenshot, or fetch digest; the rows over
   the summary table; the logs, transcripts, and logged corrections over a description of
   them. When only a digest is reachable, say so.
3. **Methods and instruments.** Name the method and the tool the expert would use (a
   mixed-effects model in statsmodels, a pytest suite, a blind pairwise judge, a
   pharmacokinetic calculation), never an adjective such as rigorous, comprehensive, or
   expert. New vocabulary without a new method is the failure this step exists to catch.
4. **Outside judge.** Name what, other than the model that made the artifact or the user,
   shows the result is right. It becomes the judged check in `<eval>` (Eval Contract).

Two further moves, only when the prompt calls for them. **Test the premise:** when the
task builds on a stated belief about cause ("churn is an onboarding problem"), add a step
that tries to reproduce the belief from the raw material before building on it.
**Specific hard target:** where the work has a measurable bar, state the bar ("p95 load
under 200 ms") rather than "improve" or "do your best".

**Size.** The pass edits; it does not add. Each answer replaces a vague clause or folds
into a step that already exists, and the judge is a short tail on an existing check
(`— judge: pytest exit code`), not a new sentence. Target at most 6 `<instructions>` steps
on a Document block and 4 on Chat, one or two sentences each, unless the ask itself names
more parts; `<eval>` stays at 1–3 one-line checks. A block that came out longer than the
task needed fails Economy, so re-tighten it in the same pass.

**Explicit cue.** When the user asks for a deeper version of a task or poses these four
questions, the pass runs on any channel, and the four answers go directly above the block,
one or two lines each. The block is then the rewritten prompt the user asked for, so the
block-would-exceed-answer guard does not apply. Without the cue the pass is silent and
only its results show.

### Completion Contract

**Content gate, not a trigger.** This decides what goes *inside* an already-fired
block. It never decides whether prompt-optimizer fires, never suppresses it, and
can never override a skip-listed prompt. Skip precedence is absolute.

**Fires when both hold.** (1) **Enumerable:** the ask names or implies a set the
deliverable must cover completely (an explicit N; *all / every / each / the whole*;
a sweep, audit, or inventory), or the deliverable states a count, tally, or
percentage Claude must **derive** rather than quote. (2) **Silent under-coverage is
possible:** multi-file/multi-artifact output, a long autonomous run, or a
thoroughness cue. **Excluded:** the whole set fits in one short answer; the number
bounds the OUTPUT, not the work (a length cap or a quantity to produce, versus a
coverage set to sweep, "all 47 files"); or a specialist owns coverage via handoff.
An explicit N fires only when it names what must be covered, never what is
produced. A thoroughness cue raises strictness only; "resume, don't be lazy" is
still a pure continuation.

**What it changes.** One sharpened line, then silence.

1. **The done-condition is the final step.** The last numbered `<instructions>`
   step IS the countable done-condition, replacing the generic verify step:
   "all 47 files opened, count stated in the closeout," never "verify the
   output." Add no step where one already exists; may be promoted into
   `<critical>` when under-coverage is the dominant failure mode, a
   permission, never a mandate.
2. **Report audit, behavioural, zero output.** Any count, tally, or
   percentage stated in the deliverable or closeout is re-measured at report
   time from the artifact or tool output, or labeled unverified, evidenced in
   the closeout sentence CLAUDE.md already requires. Scope: numbers derived
   this session; external specifics stay with `fabrication-audit`.
3. **Deviation disclosure, behavioural, zero output on the happy path.**
   Partial coverage must state what was covered and what was not; sampling is
   legitimate, silent sampling is not.

**Economy.** The contract adds no standalone boilerplate, only the final step's
countable wording, which the refine loop must not compress away and which does not
count toward the block-would-exceed-answer guard.

Read `references/completion-discipline.md` when the run is long, multi-artifact, or
orchestrated.

### Long-Run Harness

**Content gate, not a trigger.** Fires inside an already-fired block when the run may
outlive one context window or one session: a multi-stage build, an autonomous or
Workflow run, a sweep the Completion Contract caught, or a "keep going until done" ask.
Adapted from Karpathy's autoresearch by way of a seven-layer harness prompt; what was
kept and rejected is in `references/completion-discipline.md` (Long-run harness).

When it fires, `<instructions>` carry these steps, folded into existing steps where
they overlap:

1. **Preflight.** Confirm one known source or tool is readable before the long run
   starts. A missing tool is named as the blocker, and the work that does not need it
   still ships.
2. **Bounded steps.** Each step changes one thing within scope, runs the checks that
   change touches, keeps useful work, and undoes only its own failed change. A failed
   approach is not repeated without a new reason.
3. **Handoff note.** After each meaningful stage, the plan file (the run's live checklist) records outputs at exact paths, finished stages with observed check
   results, decisions with their evidence, open issues, and one concrete next action.
   On resume, open the referenced files before trusting the recorded status.
4. **Partial stop.** At a blocker or the run limit, return the partial status with the
   exact remaining work rather than a summary that reads as done.

The `<eval>` checks run as the ledger described in the Eval Contract. The harness adds
no schema element; on a short run it adds nothing.

### Eval Contract (default-on)

**Content gate, not a trigger.** Every fired block carries `<eval>`; it never decides
whether the skill fires. Full protocol: `references/eval-hillclimb.md`.

- **`check` mode (every task).** 1–3 pass/fail checks derived from the success
  criteria, each answerable from the artifact or a tool output: "script exits 0 on the
  sample", "≤ 300 words", "every row cites a source". No 1–5 scales. Running them is
  the last step of the work; the tally goes in the closeout's Proof line ("3/3 checks
  passed", or which failed). A check that cannot be run is not written. When the
  Completion Contract fires, its countable done-condition is one of the checks.
  On a long or multi-artifact run, keep the checks as a ledger (requirement | pass /
  fail / unresolved | evidence | correction): evidence is a path, a source link, or
  the check's output; missing evidence stays visible; a fix re-runs only the checks
  it touches. Never weaken a check to get a pass.
- **Outside judge (every non-trivial task).** At least one check is decided by something
  other than the model that made the artifact: a tool it runs (test, linter, validator,
  render, a recompute from the raw data), a source fetched this session, a held-out case
  set, or a reviewer that did not write it. Write it as `— judge: <what>`. When no outside
  judge exists, write `judge: none available (self-check)` rather than passing a self-read
  check off as external. A trivial Chat one-liner may omit it.
- **`hillclimb` mode (default for repeatable surfaces).** Fires when the thing built
  runs again (skill, prompt, agent, tool description, hook, workflow script, pipeline,
  template, extraction step), on any Workflow run, and on any optimize / iterate /
  improve / make-cheaper ask. Build cases from real use: past outputs, logged
  corrections, bug reports, 5–10 hand-written. Pick hard cases by human judgment, not
  by today's model's failures, and grade programmatically where the output is
  constrained. Confirm headroom first (baseline well under ~95%), then split train from
  test and change one thing per round. Keep the change only when both sets improve;
  revert when only train does. Stop after 2–3 flat rounds. At the stall, sort
  leftovers into real defects and broken cases or graders.
- **Guards.** Never paste failure or case text into the surface being tuned; the system
  under test never sees reference answers; no harness hack that only satisfies the eval.
- **Economy.** On a trivial Chat ask `<eval>` is one line ("check: answer names the
  dose and its source"). It is exempt from the Economy pass and does not count toward the
  block-would-exceed-answer guard.

### Display and Execute

1. Display the `<optimized_prompt>` block at the top of the response.
2. Execute the task guided by the prompt. Deliver output below.
3. If Document channel and post-answer uncertainty still >20%: ask
   follow-up batch in the next turn before executing the deliverable.

### Setup-Recommender Handoff (large projects only)

Fires only on a CODE or repo-rooted ANALYSIS task in a large, ongoing codebase
(git repo with a manifest and >50 source files, or multi-week/team/onboarding
signals), once per repo per session, never when opted out. Read
`references/setup-recommender.md` for the full four-condition gate and
announcement line before firing, then invoke
`claude-code-setup:claude-automation-recommender` via the Skill tool after the
block and continue the original task. Say nothing when the gate does not fire.

## Feedback loop
Found a missed edge case, a wrong-shaped output, or a rule that misfires?
Open an issue on this plugin's repository with the input and the output you
expected. Do not edit this skill mid-run.

## Examples

Five worked examples, grant aims via handoff, a Chat email showing the memory penalty,
a score-15 Document with the content-extending question, a long-request auto-trigger, and
the uncertainty override loop, live in `references/examples.md`. Read them when a case is
genuinely borderline; the trigger rules, skip list, schema, matrix, and handoff selector
above are authoritative on their own.

## Rules

1. The `<optimized_prompt>` block appears at the top of the response to every human-typed
   prompt that is not a hard skip, structured as the closed template with its `<assumptions>`
   and `<eval>` elements (Output Rule). Follow-ups of 25 words or more fire; pure
   continuations and micro-edits under 25 words do not.
2. Question count is channel × score: Chat 0–2; Document 1–5 (1 only at
   score ≥ 13, content-extending).
3. Uncertainty override loop: if >20% uncertainty remains after the initial
   questions on a Document task, ask a follow-up batch next turn (Phase 0.D).
4. Memory inference penalty applies (3→2, 2→1) for memory-based dimensions; full
   credit only for what's explicit in the current prompt (Phase 0.C).
5. Defer to a specialist skill's own intake, then synthesize its output into the
   `<optimized_prompt>` block (no double-intake). Full routing table and the
   deep-research route-when / don't-route test: Phase 0.A Handoff selector.
6. User override beats every rule above:
   (a) "just do it" / "just give me" / "stop asking" / "you decide" / "proceed" /
   "autonomously" → skip the intake questions, proceed with assumptions stated
   explicitly. The block STILL fires (unless skip-listed).
   (b) A user-named count ("ask me 5–10," "quiz me") → raises the question cap.
   (c) "Just"-class defaults → lowers the count to 0 (but still fires).
7. (Retired 2026-11-14: goal handoff removed.)
8. End-of-turn closeout: when the user's standing instructions define a closeout
   format (for example three labelled lines, Result, Proof and Open, on a turn that
   changed a file or reports something done), use that format; otherwise close in
   1–2 sentences. Governs the prose after the deliverable, not the deliverable itself.
9. Completion Contract is a CONTENT gate, never a trigger: it shapes what goes
   inside an already-fired block and can never change whether the skill fires.
   When it fires, the final `<instructions>` step is the countable
   done-condition; derived numbers are re-measured at report time or labeled
   unverified; partial coverage is declared. Canonical home: Completion Contract.
10. Mannered-prose and craft lines: WRITING, COMMUNICATION, DOCUMENT, and PRESENTATION blocks
    carry two fixed lines — "Remove all mannered prose: say what you mean, and
    use the literal phrase where one exists," and "Lead with the point; open
    each sentence on what the reader already holds and end it on the new item;
    gloss every term of art for the named reader; prefer the short everyday
    word." Neither affects firing.
11. Reviewer ordering on WRITING, COMMUNICATION, and DOCUMENT tasks: register
    reviewer (academic or casual) → writing-anti-ai → one receipt line,
    `[writing: review <academic|casual|skipped> · anti-AI <verdict> · T<n>]`, under the block in the
    response that carries the drafted prose (not above a draft that does not exist yet).
    Neither affects firing.
12. Eval Contract: every block carries `<eval>`. `check` mode (1–3 pass/fail checks,
    at least one with a named outside judge, run as the last step, tally in the closeout's
    Proof line) on every task; `hillclimb` mode (train/test split, one
    change per round, keep only when both sets improve, stop after 2–3 flat rounds) by
    default on repeatable surfaces and Workflow runs. Content gate; never affects firing.
13. Long-Run Harness: a run that may outlive one context or session gets preflight,
    bounded steps, a handoff note in the plan file, a check ledger, and a partial stop
    with the exact remaining work. Never weaken a check to get a pass; never retry an
    external write without checking whether the first landed. Content gate; never
    affects firing.
14. Depth Pass: on Document, ANALYSIS, CODE, RESEARCH-DESIGN, and system-engineering
    blocks, answer expert move, rawest material, methods and instruments, and outside
    judge, and write each answer into the element it changes. Deeper, not bigger: no new
    deliverable, and a scope-widening move is one sentence under the block. Shown above
    the block only on an explicit cue. Content gate; never affects firing.

## Gotchas / Known Failure Modes

Eighteen recurring misreadings of these rules, with the correction, are logged in
`references/versions.md` ("Gotchas / Known Failure Modes, moved from SKILL.md").
Read it when behavior seems off; the Rules list above is the authoritative statement.

## Versions

Full version history: `references/versions.md` (historical records, not current
instructions).
