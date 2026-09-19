# Prompt · Collect the runner profile `collect_profile`

> Purpose: on first contact with a runner, build `runner_profile.yaml` through **one structured
> Q&A round** (schema: docs/08). Send the whole block (replace `<...>` with actual paths).

```
[collect_profile] Please interview me and build my runner profile (target <workspace/runner_profile.yaml>).

1. **Get the question list first**: run `python scripts/profile_wizard.py --questions --lang en` —
   that is the one authoritative list (derived from `FIELDS` in `scripts/profile_wizard.py`).
   **Never write your own list of questions**; it will drift away from the schema.
2. **Ask in order, one group at a time**: identity → races → weekly → pr → coach → strength →
   constraints → metric_baselines → devices. Use the list's "Q:" wording; "help:" explains why you
   are asking; "example:" only when I am stuck. **Do not dump all 29 questions on me at once** —
   finish a group, let me answer, then move on.
3. **Look it up before asking**: with MCP tools available, read the resting-HR baseline / weight /
   sleep baseline / existing VO2max straight from Garmin (`scripts/garmin_wellness.py`,
   `get_user_profile`) and **show me the number to confirm** — don't make me answer from memory.
   Ask only for what you cannot read. Write "待补" for what is still missing, and **never invent a
   value on my behalf**.
4. **Required and mutually exclusive**: **at most one race may carry `role: A`**; every race must be
   tagged with a role (`A` / `attempt` / `training`, mutually exclusive). At least **one of the four
   PRs is required** — it is the only source of the VDOT (docs/09).
5. **Pin down the accessories**: HR strap / running pod / power meter or none, **from which date it
   first appears** (`since` IS the data break point, docs/02 §6.10), and which sessions it was left
   off. Leave the whole block out if there is none.
6. **Write the profile** per the docs/08 schema into <workspace/runner_profile.yaml>. **Block-style
   YAML only** — no flow mappings (`{...}`), no block scalars (`|` / `>`), no tab indentation.
   `profile_wizard.py` rejects those outright: the parser only accepts this subset, so it is a hard
   requirement rather than a style preference.
7. **Self-check**: run `python scripts/profile_wizard.py --check <workspace/runner_profile.yaml>` —
   it **must report 0 errors** (warnings are allowed, but explain each one and whether it matters).
   Fix and re-run until it is clean.
8. Reply in ≤400 characters: the 1-2 things in my profile I should confirm, what is still missing
   (the "待补" list), and whether you can generate the plan next.
```

Alternative entry point (when the runner fills it in themselves): `examples/runner_profile.questionnaire.yaml`
is a **blank questionnaire** over the same fields — the runner fills it in, then the agent runs the
`--check` from step 7. The interactive wizard `python scripts/profile_wizard.py` asks the same questions
and **preserves** any out-of-schema extension blocks (such as the private `measured:` anchors) verbatim.
