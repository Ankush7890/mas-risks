# mas-risks

This project builds small open-weight agents whose susceptibility to influence is controlled, then runs them in multi-agent risk scenarios. Julian and Ankush work on it.

This project uses the [Epistemic Memory](https://github.com/FlorianDietz/EpistemicMemory) conventions: all project memory lives in LOG/SUMMARY file pairs under `convos/`, governed by [CLAUDE.md](CLAUDE.md). Human guide: [docs/HOW_TO_USE.md](docs/HOW_TO_USE.md). Open ideas and deferred items: [FUTURE_WORK.md](FUTURE_WORK.md). Workflow problems and lessons: [FEEDBACK.md](FEEDBACK.md).

## Team

- Julian Bitterlich — `convos/julian/` (git user.name: `Julian Bitterlich`)
- Ankush — `convos/ankush/` (git user.name: not yet recorded; add it here on Ankush's first session)

**Identifying the current user:** match `git config user.name` against this list. If it doesn't match anyone or the match is ambiguous, ask before proceeding.

## Current status and goals

Project setup completed 26-11-21. No research topics started yet.

## Maintenance

Recurring tasks:

| Task | Last run | Due when | Notes |
|------|----------|----------|-------|
| Sync (LOG/SUMMARY drift) | — | After many LOG changes, or ~monthly | `!sync`; procedure: `docs/procedures/sync.md` |
| LLM-ism checklist refresh | — | ~Monthly while you publish regularly; otherwise before any high-stakes submission | Update the checklist and Known-screening sections of `docs/procedures/outward_text.md` from full primary sources (see the file's refresh rule); bump its refresh date |

## Conversation Index

All discussions live in `convos/{user}/`. **When starting a new topic, add a row here.** Read the SUMMARY first; open the LOG only if the SUMMARY is insufficient. Status cells describe current state only — rewrite them on update, don't append.

| Date | User | Topic | Status | SUMMARY | LOG |
|------|------|-------|--------|---------|-----|
| 26-11-21 | julian | Project setup (template configuration) | Done | [SUMMARY](convos/julian/26-11-21_project_setup_SUMMARY.md) | [LOG](convos/julian/26-11-21_project_setup_LOG.md) |
