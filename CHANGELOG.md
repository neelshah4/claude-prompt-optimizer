# Changelog

All notable changes to this plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning is calendar-based (`YYYY.M.D`), matching the skill's own dated version
string rather than imposing a semantic version it does not have.

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
