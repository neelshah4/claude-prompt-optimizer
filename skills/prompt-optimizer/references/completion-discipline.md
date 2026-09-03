# Completion Discipline

Long-form detail for the `### Completion Contract` section of SKILL.md. Read this when a
run is long, multi-artifact, or orchestrated. The gate, the three rules, and the
exclusions in SKILL.md are authoritative on their own; this file holds the worked cases
and the reasoning.

Merged from `unlazy` (github.com/Leonxlnx/unlazy, MIT) on 2026-08-22. Provenance and the
rejected list are at the bottom.

## The gate, worked

Two conjuncts. A disjunction on "names a quantity" catches every prompt containing a
number, which is why the first draft of this gate was wrong.

**Conjunct 1, enumerable.** The ask names or implies a set the deliverable must cover
completely, or the deliverable will state a count, tally, or percentage that Claude must
**derive** rather than quote.

**Conjunct 2, silent under-coverage is possible.** The set is large enough, or the run
long enough, that a partial answer would still read as complete.

### Fires

| Ask | Why |
|---|---|
| "Go through all 47 skills and tell me which name a missing reference file." | Explicit N, multi-file, a partial sweep looks identical to a complete one. |
| "Which of my hooks lack the loop guard? Check every hook, not just the ones you remember." | Enumerable set; the "not just the ones you remember" is the user pre-empting exactly this failure. |
| "How many cases had Table-1 overrides applied?" | No sweep keyword, but the answer is a derived count. Fires on the second limb of conjunct 1. |
| "Audit every row for missing cannulation timestamps and give me the count." | Sweep plus derived count plus an attachment large enough to hide a gap. |

### Does not fire

| Ask | Why not |
|---|---|
| "Give me 3 options for framing the discussion." | The 3 is a number the user handed you, not one the work discovers. Highest-volume false positive; the exclusion exists for it. |
| "Write a 500-word abstract." | 500 is a length cap. Same exclusion. |
| "Compare all three cannulation strategies." | Enumerable, but the whole set fits in one visible answer; conjunct 2 fails. |
| "Review the whole manuscript." | `manuscript-reviewer` owns coverage via handoff. Never layer a second coverage contract on a specialist's own. |
| "check it — did all 20 slides render?" | A status check. The block already skipped, so the gate never runs. Skip precedence is absolute and a count word cannot override it. |

## Rule 1, the done-condition is the final step

When the gate fires, the block's last numbered `<instructions>` step **is** the countable
done-condition. It replaces the generic verify step that would otherwise be written, so
the typical cost is zero added lines.

Phrase it so a reader of the transcript alone can judge it.

| Weak | Countable |
|---|---|
| "Verify the output is complete." | "All 47 files opened; state the count in the closeout." |
| "Check the references." | "Every reference resolved to a PMID or marked [CITATION NEEDED]; state the resolved/total." |
| "Make sure nothing was missed." | "Each of the 6 organ groups scored; name any group with no source data." |
| "Review thoroughly." | "Every hook read end to end; list each hook and whether the guard is present." |

A done-condition that cannot be counted is a mood, not a condition. If the work genuinely
has no countable end state, the gate should not have fired.

## Rule 2, report audit

Any count, tally, or percentage stated in the deliverable or the closeout is re-measured
at report time from the artifact or the tool output, or labeled unverified. Not recalled
from earlier in the run, and not carried forward from a plan written before the work.

The evidence is stated in the closeout sentence that CLAUDE.md already requires, so this
costs nothing in output. "3 surfaces × 5 files identical" is a measured claim; "everything
is in sync" is not.

**Boundary, do not double-fire.** This rule covers numbers Claude *derived from work done
this session*. Claimed external specifics, doses, prevalence, guideline years, fees,
belong to `fabrication-audit` and the CLAUDE.md citation Hard Rule. A numeric deliverable
should trip one of the two, not both.

## Rule 3, deviation disclosure

Full coverage produces no extra output. Partial coverage must be declared: what was
covered, what was not, and why. Sampling is legitimate; silent sampling is not.

This is the observable half of unlazy's "ignore resource anxiety"; the internal-state
directive is dropped, the consequence is kept. It also replaces its `ABANDON: G<n>` syntax,
which presupposes a gates file and an ID space this skill does not import.

The disclosure appears exactly when the user needs it, which is the point: the discipline
runs in the background and surfaces only on deviation.

## Token economy

Discipline is not maximalism.

- A check is a shell command, not a re-read of everything already written.
- Evidence is the deciding lines, never a full log.
- The contract adds one sharpened step and no standalone boilerplate. If it would push the
  block past the answer it precedes, the ask was trivial and the gate should not have
  fired.
- The sharpened final step does not count toward the block-would-exceed-answer guard,
  which is evaluated against the base block.

## Provenance

`unlazy` v2 (github.com/Leonxlnx/unlazy, MIT), fetched 2026-08-22. Its thesis is that
prose cannot enforce prose, and that enforcement belongs in files and hooks.

Its controlled test ran two build tasks across three conditions each. Findings, with the
unfavourable half kept:

- Baselines already shipped zero placeholders and zero console errors, so v1's
  "no TODOs, no stubs" constraints are obsolete against current models.
- Depth arithmetic is fiction: "tree 6" cost 1.0–1.5x "tree 3", never the promised 8x.
  Models treat decomposition depth as a proxy for thoroughness and ignore the multiplier.
- Every *skill* run's final report carried 1–3 wrong numbers; the *baselines* carried
  none. Read straight, that suggests the skill induced the defect through long
  ledger-keeping runs rather than curing a pre-existing one.

Those numbers are single-source and n=6, and are **UNVERIFIED beyond one fetch**. The
report-audit rule here is justified from this surface's own record instead: TITRE batch-3
scored six cases with Table-1 overrides silently unapplied; the monthly drain emailed
itself a success it had not achieved; the Gmail probe returned a confident negative from a
probe that never ran.

## Rejected from the import

| Rejected | Why |
|---|---|
| `GATES.md` artifacts, `gate-check.mjs` | This surface already has a nudge hook, an ARMED Stop hook, a hook harness, a fail-closed lint, and skill-eval. A second unowned enforcement path with no harness is the shape that produced four undetected defects on 2026-08-01. |
| unlazy's Stop hook | Hazardous, not merely redundant. A third Stop hook would contend with the two existing ones for the same turn-ending decision, and the documented runaway (issue 55754) is a loop between exactly these. |
| The Depth Tree as a tree | Planning machinery. SKILL.md's own design-boundary note rejects search and iteration machinery for a one-shot rewriter, and `superpowers:writing-plans` owns decomposition. Only the natural-joints heuristic survives, as one Refine bullet. |
| Solo vs orchestrated mode, the 30-minute subagent threshold | CLAUDE.md owns delegation and is stricter. A softer threshold inside a skill that fires on nearly every turn competes with a Hard Rule. |
| Fresh context per leaf | Harness behaviour a prompt rewriter cannot specify. |
| `ABANDON: G<n>` syntax | Keep the idea, drop the syntax. No ID space without a gates file. |
| "Ignore resource anxiety" | A directive about internal state; SKILL.md already bans that family. Only the observable consequence is kept, as Rule 3. |
| unlazy's numbers inside SKILL.md | Single-source, n=6, and the strongest finding argues against part of the import. Provenance belongs in a provenance log, with both halves. |
| Three visible lines per fire | This merge's own first carrier design, rejected once the governing constraint became minimal added output. |
