# Changelog

All notable changes to this plugin are documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
