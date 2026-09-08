# Changelog

All notable changes to this plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning is calendar-based (`YYYY.M.D`), matching the skill's own dated version
string rather than imposing a semantic version it does not have.

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
