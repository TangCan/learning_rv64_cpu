Set `development_status[{story_key}]` to `{target_status}` in `{{.implementation_artifacts}}/sprint-status.yaml`.
For Epic N with N > 1, before changing a story from `backlog` or `ready-for-dev` to `in-progress`, run `uv run --no-cache .agents/skills/bmad-sprint-planning/scripts/sprint_plan.py gate --status-file {{.implementation_artifacts}}/sprint-status.yaml --story-key {story_key}`. If it exits non-zero, stop without changing either the story or epic status; report that the previous Epic retrospective must be `done` first.
If `{story_key}` is missing, warn once and stop.
If the story is already at `{target_status}` or later, stop.
When `{target_status}` is `in-progress`, set parent epic (e.g. `3-2-foo` → `epic-3`) from `backlog` to `in-progress` if present.
Update `last_updated`. Preserve comments and structure.
