# Changelog

All notable changes to this plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning is calendar-based (`YYYY.M.D`), matching the skill's own dated version
string rather than imposing a semantic version it does not have.

## [2026.11.27] - 2026-11-27

### Changed
- The nudge hook stays silent on two more non-human openings: a cross-session message from a peer session (`<cross-session-message`) and a side-session hand-off (`Background (from the session that started this one)`). `hooks/harness_event.py` also treats a payload whose own origin is `peer` or `task-notification`, or that is flagged as a compaction summary, as non-human.
- The `[SYSTEM NOTIFICATION - NOT USER INPUT]`, `<task-notification>` and `<local-command-stdout>` markers match only at the opening of a prompt. They previously matched anywhere, so a person quoting one mid-message got no nudge.
- Fixtures: new nudge cases for the two new openings, and cases confirming that a human prompt quoting each of the three legacy markers mid-message still injects.

## [2026.11.20] - 2026-11-20

### Changed
- The Stop hook counts an `<optimized_prompt>` block as present only when a closed `<optimized_prompt>...</optimized_prompt>` element contains `<role>`, `<inputs>` and `<instructions>` as open and close pairs. A bare mention of the tag name no longer satisfies it. The fire and skip conditions are unchanged; the block message names the closed schema.
- Fixtures: the valid-block case carries the full schema, and new cases cover a role-only block (blocks), a `<name>` placeholder inside `<inputs>` (allows) and a prose mention of the tag before a valid block (allows).

## [2026.11.16] - 2026-11-16

### Changed
- Rule 8 (end-of-turn closeout) follows the closeout format in the user's standing instructions when one exists, and otherwise closes in one or two sentences. It no longer says "always".
- Rule 11 names one merged receipt line, `[writing: review <academic|casual|skipped> · anti-AI <verdict> · T<n>]`, in place of two separate lines.
- The nudge hook stays silent when the prompt opens with a harness marker (task notification, subagent hand-back, compaction summary, scheduled-task start, side-session or CI event, local-command output). The check lives in the new `hooks/harness_event.py`, matches only the opening of the prompt, and falls back to the old prompt extraction if the module is missing or raises.
- For a prompt of 15 words or fewer in one sentence, the nudge hook runs its status and single-command skip tests before the content-verb match. A verb stem inside a filename or a status question no longer injects.
- The Stop hook finds the opening prompt in transcripts larger than 4 MB by widening its read window from 4 MB to 16 MB to 64 MB, then allows the stop past 64 MB. Its block conditions are unchanged.
- Handoff rows, examples and history refer to a grant-review skill generically ("if installed") instead of naming one.

### Added
- `hooks/harness_event.py`, the shared harness-event check.
- `hooks/tests/` with three fixture scripts: `prompt_optimizer_hook_fixtures.py`, `prefilter_failopen.py` and `stop_hook_tail_fixtures.py`.

## [2026.11.14] - 2026-11-14

### Changed
- The skill fires on every prompt a person types that carries a task. A follow-up of 25 words or more with answers, decisions or new instructions gets its own block; pure continuations and micro-edits under 25 words do not.
- Both hooks ignore turns no person started: subagent reports, task notifications, compaction summaries and scheduled-task starts. The Stop hook's backstop covers any typed prompt of 25 words or more.
- New `<assumptions>` element lists each decision the block made without asking, including anything taken from memory.
- `<instructions>` carries only steps that add to the request: the success criterion, the reader, the method, the order.
- `<eval>` goes from 2–5 checks to 1–3. They run as the last step of the work and the tally is stated in the closeout.
- Intake gains a two-stage order for changes to a standing system or a strategy: research first, then options with pros and cons, then questions.
- Tested with hook fixtures (51 checks) and eight fresh Sonnet runners graded by script (29 of 29 checks).

### Removed
- `<suggested_goal>` and the `/goal` handoff. In 50 sessions of the author's own use the line was offered 27 times and never used.

## [2026.10.17] - 2026-10-17

### Changed
- A capped input (one the prompt cannot supply) is now written into `<inputs>` as a placeholder with the assumption the block runs on, such as `NAME: description (assumed: X)`. It adds no question of its own. Precedence is stated: a user override first, then the question count from the channel and score matrix, then any capped-stop question.
- Edits to files in a repo or config (skill edits, bug fixes, config changes, a push) are classed as the Document channel, so they get the Document question range and the `/goal` suggestion.
- The handoff selector gains a visual-deliverable row that routes decks, one-pagers, posters, dashboards, and similar assets to an installed visual-design skill, if there is one.
- Presentation tasks now carry the two fixed prose lines (remove mannered prose; lead with the point), since slide and speaker-note copy is prose.
- Tested on 25 prompts (15 earlier cases plus 10 new real prompts, each new one run twice) against a control run of the previous skill, with a grader written before the runs. Every target check rose on both the tuning set and the held-out set. One cost: terse repo requests now fall in the Document range and can ask up to 5 questions; a user override still gives zero. No trigger, skip, or hook change.

## [2026.10.16.1] - 2026-10-16

### Changed
- A capped input (one that cannot be filled without inventing it) becomes an `<inputs>` placeholder carrying its assumption, written `NAME: description (assumed: X)`, and adds no question of its own. Precedence for the question count is user override, then the channel x score matrix, then any capped-stop question.
- Repo and file-edit tasks (skill edits, bug fixes, config changes, a push) are Document channel. Terse repo asks can now get up to five intake questions; "just do it" still gives none.
- The handoff selector gains a visual-deliverable row that routes to the installed visual-design skill, if any. PRESENTATION tasks now carry the two fixed prose lines.
- Tested against a control on the previous version over 25 real cases with a train/held-out split. Every target check rose on both sets. No trigger, skip, or hook change.

## [2026.10.16] - 2026-10-16

### Added
- Depth Pass, from Felix Rieseberg's essay "How to be more ambitious: A tutorial for humans with models" and its "deeper, not bigger" prompt. On document, analysis, code, research-design, and skill-engineering blocks, the drafter answers four questions: the expert move the prompt does not ask for, the rawest material reachable, the specific methods and tools, and the outside judge. Each answer goes into the element it changes, with no new deliverable. Two moves apply only when the prompt calls for them: test a stated causal premise against the raw material, and state a specific measurable bar. When the user asks for a deeper version, the four answers appear above the block.
- An outside-judge rule in the Eval Contract: at least one check is decided by something other than the authoring model, written `— judge: <what>`, or the block says `judge: none available (self-check)`. In a 60-day audit of real blocks, 47% of evals had no such check.
- Long-Run Harness (written 2026-10-07, first released here): preflight, bounded steps, a handoff note in the plan file, a check ledger that is never weakened to get a pass, and a partial stop that names the remaining work. It also adds a retry rule (change something before retrying; check whether an external write landed before repeating it).
- `references/depth-pass.md` (sources, audit numbers, kept and rejected items) and Rules 13 and 14.

### Changed
- `<role>` names the job and what that professional does, not a persona to imitate. Alignment names the outcome the deliverable serves as a verb.
- `<inputs>` placeholders are written as NAME: description lines, never nested tags.
- The deep-research route checks the session's skill list instead of asserting the skill is absent.
- Tested on 15 real prompts (12 common, 3 edge) across three runners in two rounds. The pass rate rose from 80% to 89%, improving on both the tuning set and the held-out set. No trigger, skip, question-matrix, or hook change.

## [2026.9.28] - 2026-09-28

### Added
- A required `<eval>` element and an Eval Contract, from Anthropic's post on automating eval design and hillclimbing. `check` mode on every task: 2–5 yes/no checks read off the output, run before the response closes, with the tally stated. `hillclimb` mode by default when the thing being built runs again (skills, prompts, agents, tool descriptions, hooks, workflows, pipelines): cases from real use, a programmatic or checklist grader, a train/held-out split, one change per round, keep only when both sets improve, stop after 2–3 flat rounds.
- `references/eval-hillclimb.md` with the full protocol, the four properties of a good eval, and the guards against gaming it.
- Rule 12. The description is trimmed to stay under the 1024-character limit.
- No trigger, skip, question-matrix, or hook change; the Stop hook checks only that the block is present.

## [2026.9.23] - 2026-09-23

### Changed
- Drafting techniques (Refine): three clauses for Claude Opus 5.5, taken from Anthropic's Opus 5.5 migration guidance. Never ask the executing model to write out its internal reasoning in the answer (thinking is always on, and a request to reproduce it can be declined); ask for the conclusion and its evidence instead. Set depth with the effort level rather than "think step by step" or "think less" text. Name the specific pattern to avoid rather than a general "avoid a generic look".
- No trigger, skip, schema, question-matrix, or hook change.

## [2026.9.13] - 2026-09-13

### Added
- Two Phase 0.A Handoff-selector rows: a manuscript-class draft (manuscript, abstract, grant narrative, reviewer response, IRB free text, cover letter) routes to `academic-writing-reviewer` if present, then writing-anti-ai; a message-class draft (email, memo, Slack/chat reply, handoff note, README, executive summary) routes to `casual-writing-reviewer` if present, then writing-anti-ai.
- Rule 11, stating the reviewer-ordering sequence (register reviewer, then writing-anti-ai, then receipts) explicitly.

No trigger, Skip, schema, or hook-semantics change; both hooks remain byte-identical to v2026.9.12.

## [2026.9.12] - 2026-09-12

### Added
- A second fixed drafting line ("craft line") alongside the existing mannered-prose line for WRITING, COMMUNICATION, and DOCUMENT tasks: "Lead with the point; open each sentence on what the reader already holds and end it on the new item; gloss every term of art for the named reader; prefer the short everyday word." Sourced from the writing-craft canon (Orwell, Williams, Zinsser, Pinker, Merriam-Webster's Dictionary of English Usage, the Economist Style Guide).
- One clause to the model-agnostic drafting technique list: name the reader's expertise so the gloss rule has a target.
- A "Supersedes any bundled/upstream variant" sentence to the frontmatter description.

### Fixed
- Two stale grant-review skill references corrected in SKILL.md.
- Two archived-path comments in `hooks/prompt-optimizer-stop-check.sh`, missed by a prior scrub, genericized to remove an internal filesystem path.

No trigger, Skip, schema, or hook-semantics change; both hooks remain otherwise byte-identical to v2026.9.8.

## [2026.9.8] - 2026-09-08

### Changed
- SKILL.md body trimmed from 5,820 to 4,222 words following an internal cost/intelligence audit rubric (Anthropic's cost-and-intelligence and cost-optimization guidance): the versioned header comment, two dated inline audit-citation comments, the full attribution/rationale for the Refine-section drafting techniques, and the 18-row Gotchas/Known Failure Modes table moved to `references/versions.md` (a one-line pointer stays in SKILL.md); the STORM/`deep-research` route-when/don't-route block, the High-value fire patterns list, the Frontier-idiomatic and instruction-writing-moves prose, the Completion Contract's numbered items, the Goal Handoff condition-writing bullets, and Rule 5 were compressed in place with no meaning change.
- The feedback-loop section, present in the underlying skill but never previously reconciled with this fork's own publish gate, has its body replaced with a generic issue-driven prompt (no internal script or path names) so the fork carries no reference to non-public tooling.
- Every remaining internal user-machine path reference (plus internal plan/backup file names in `references/versions.md`'s historical entries) removed or replaced with a generic description; the version-history entries themselves are otherwise preserved verbatim as historical record.
- Every rule, threshold, category name, and hook-relevant example phrase is unchanged; both hooks (`prompt-optimizer-nudge.sh`, `prompt-optimizer-stop-check.sh`) are untouched.

## [2026.9.3] - 2026-09-03

### Changed
- Prose rewritten for direct statement (Anthropic Fable 5.1 guidance): metaphor replaced with the literal phrase, em dashes replaced with periods, semicolons, or commas, emphasis reduced. No trigger, Skip, or schema change.
- Header edit history and the design note moved to references/versions.md; the SKILL.md header now carries only the live maintenance contract.
- Constraints section removed (every item was restated in Rules); three Gotchas rows that restated a Rules item removed.
- Setup-Recommender gate moved verbatim to references/setup-recommender.md, with a summary and a read-before-firing pointer left in SKILL.md.
- Public-copy scrub: references to a private, unpublished skill replaced with the generic name grant-review.

### Added
- Rule 10: on WRITING, COMMUNICATION, and DOCUMENT tasks the generated <instructions> carry the line "Remove all mannered prose: say what you mean, and use the literal phrase where one exists."
- references/setup-recommender.md.

### Unchanged
- Skip list, the <optimized_prompt> schema, and both hooks are unchanged from 2026.8.22.

## [2026.8.22] - 2026-08-31

### Changed
- Version realigned to match the skill's own declared version (v2026-08-22). The initial
  publication used a placeholder 1.0.0.
- README expanded substantially: worked examples with sample output, configuration,
  troubleshooting, limitations, and design rationale.
- Added a model-support section (developed on Opus 5, model-agnostic across tiers),
  a best-practices section, and full source attribution for the design.

### Added
- Citations for the four sources the design draws on: DSPy signatures (arXiv:2310.03714),
  principled instructions (arXiv:2312.16171), STORM perspective-guided question asking
  (arXiv:2402.14207), and Anthropic's Prompting 101. Each identifier verified against
  arXiv before publication.
- An explicit note on what was deliberately not imported: scored iteration, including
  GEPA (arXiv:2507.19457, ICLR 2026), which needs an eval harness this skill lacks.


## [1.0.0] - 2026-08-31

### Added
- Initial public release as a Claude Code plugin.
