# Changelog

All notable changes to this plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning is calendar-based (`YYYY.M.D`), matching the skill's own dated version
string rather than imposing a semantic version it does not have.

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
- `UserPromptSubmit` and `Stop` hooks now ship with the plugin and wire automatically
  via `hooks/hooks.json`, so the skip-list contract holds on install.

### Changed
- Description trimmed to 983 characters to stay under the 1024-character skill limit.
- Removed the local-install maintenance header and all internal path references.

### Prior history
Developed privately from 2026-06 through 2026-08. Notable milestones, preserved in
`skills/prompt-optimizer/references/versions.md`: the refine engine and firing upgrade
(2026-06-07), a precision pass driven by a 70-case adversarial eval (2026-06-07b), the
STORM best-practices pass (2026-06-26), the flagship research-grade pass (2026-07-03),
conversion enforcement with the Stop hook (2026-07-12), and the completion-discipline
merge (2026-08-22).
