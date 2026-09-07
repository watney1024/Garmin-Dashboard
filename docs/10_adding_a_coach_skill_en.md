# 10 · Adding a new coach skill (for agents & maintainers)

Coach skills let plan generation **plug different coaching philosophies in and out**.
Anyone (usually an agent collaborating with the runner) can add one by following this
file. **Adding a skill requires no code changes.**

## Location & naming (Agent Skills standard)

```
.agents/skills/
  README.md                                   # index: add a row
  coach-<new_id>/                             # dir name = "coach-" + id (id `_` -> `-`)
    SKILL.md                                  # frontmatter name/description + load steps
    references/
      coach-<new_id>_zh.md                    # full method body (9 fixed sections)
      coach-<new_id>_en.md
```

The profile's `coach: <id>` (e.g. `daniels_vdot`) maps to `coach-daniels-vdot`. When
generating a plan the agent reads `SKILL.md` first, then the language-matching reference
in full (docs/05 §2).

## Workflow

1. Confirm the source methodology has a **citable public origin** (book/article/person).
   The body must be **your own summary & application guide**, not copied text — every
   reference file carries a copyright notice in section 1.
2. Create `coach-<new_id>/SKILL.md` with frontmatter like:

   ```yaml
   ---
   name: coach-<new_id>
   description: >-
     <methodology name> 教练方法论包。仅当跑者档案 coach 字段为 <new_id>、且需要生成或更新
     训练计划时加载；随后按档案 language 读取 references/coach-<new_id>_zh.md（或 _en.md）
     全文并遵守。 <one-line English trigger, same semantics>...
   ---
   ```

   The SKILL.md body states the load steps and three rules: read the full reference in the
   profile language; never invent paces (look up `data/vdot/` or use the HR/feel
   doctrine); where the generic safety layer conflicts, take the stricter rule.
3. Put `coach-<new_id>_{zh,en}.md` under `references/`, filling the 9 fixed sections of the
   body template below.
4. Add one row to the index in `.agents/skills/README.md` (coach id + trigger condition).
5. If the philosophy changes the content of an HTML-plan chapter, give template/example
   snippets inside the references; never change the document structure.

## Body template (9 fixed sections of references/coach-<id>_<lang>.md)

Every section must have content; write "（本流派不涉及 / not part of this methodology)"
where not applicable:

```
# <Coach name> <new_id>
## 1. Origin & fit       ← mandatory copyright notice; source; good for / not for
## 2. Intensity system & pace source  ← zones; paces resolve to VDOT table / HR / feel
## 3. Weekly skeleton construction    ← parameterised by runs_per_week/long_run_day/quality_days
## 4. Periodization & volume ramp     ← phases, increase caps, recovery weeks, taper
## 5. Tests & gates       ← non-A races, key gates of this school
## 6. Red lines & cautions            ← may only be stricter than docs/03/06
## 7. Strength / auxiliary advice
## 8. Worked example (optional)
## 9. Mandatory checks (post-generation self-check)
```

### Section 9 "Mandatory checks" convention (required for every coach)

Section 9 answers **four fixed items**, each written in this school's own terms; the four
items are mandatory and keep their order:

1. **Intensity composition**: the weekly share/caps per intensity band (E vs quality), and
   what gets cut first when the cap is exceeded.
2. **Fatigue quantification & management**: how this school quantifies fatigue (load /
   time / pace drift / HR etc.) and when to cut back.
3. **Micro/macro cycles**: the weekly shape and the phase structure, where recovery weeks go.
4. **Easy-run doctrine**: E/low-intensity sessions are judged by **HR and time**, not pace
   or distance (table paces are a reference end only).

## Quality gate (agent self-check)

- [ ] An agent reading only this skill (SKILL.md + the language reference) can build a
      compliant weekly skeleton & schedule.
- [ ] Every section has content ("not applicable" stated explicitly where relevant).
- [ ] No conflict with the generic safety layer, or the stricter rule is chosen & noted.
- [ ] Copyright notice in section 1; body is paraphrase, not quotation.
- [ ] Clear "good for / not for" profile to avoid misuse.
- [ ] `.agents/skills/README.md` index updated.

## Integration with docs/05

`docs/05` describes the generic flow: read profile → load the selected skill (SKILL.md +
references) → generate the HTML plan. Each skill supplies the "methodology parameters"
for that flow; if every skill needs a new parameter, promote it to a shared convention
here instead of writing it in one skill only.

## Testing

- Run the docs/05 flow once with `examples/runner_profile.example.yaml` + the new skill
  and have a human/agent check the weekly skeleton is self-consistent (session count,
  long-run day, quality days match the profile).
- Check paces land in a plausible range (within ~10–20 s/km of public references).
