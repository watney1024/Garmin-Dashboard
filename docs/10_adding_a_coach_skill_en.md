# 10 · Adding a new coach skill (for agents & maintainers)

Coach packages let plan generation **plug different coaching philosophies in and out**.
Anyone (usually an agent collaborating with the runner) can add one by following this
file. **Adding a package requires no code changes.**

## Workflow

1. Confirm the source methodology has a **citable public origin** (book/article/person).
   The body of the package must be **your own summary & application guide**, not copied
   text — every package carries a copyright notice in section 1.
2. Copy `coaches/_TEMPLATE_en.md` (and `_zh.md`) → `coaches/<new_id>/README_en.md` /
   `_zh.md`. The `id` is lowercase snake_case; it becomes the profile's `coach` value.
3. Fill the 8 fixed sections. Watch out:
   - The **pace source** must resolve to real data (VDOT table / HR zones / feel) — do not
     invent an uncredited pace table.
   - **Red lines & cautions** may only be stricter than the generic safety layer; the
     generic layer cannot be overridden (docs/03, docs/06).
   - **Weekly-skeleton rules** must be consumable with the
     `runs_per_week / long_run_day / quality_days` parameters.
4. Add one row to the index in `coaches/README_en.md` and `_zh.md`.
5. If the philosophy changes the content of an HTML-plan chapter, give template/example
   snippets inside the package; never change the document structure.
6. Optionally add an `examples/` subdirectory with a sketch.

## Quality gate (agent self-check)

- [ ] An agent reading only this package can build a compliant weekly skeleton & schedule.
- [ ] Every section has content ("not applicable" stated explicitly where relevant).
- [ ] No conflict with the generic safety layer, or the stricter rule is chosen & noted.
- [ ] Copyright notice in section 1; body is paraphrase, not quotation.
- [ ] Clear "good for / not for" profile to avoid misuse.

## Integration with docs/05

`docs/05` describes the generic flow: read profile → load the selected package → generate
the HTML plan. Each package supplies the "methodology parameters" for that flow; if you
find every package needs a new parameter (e.g. a threshold for some intensity definition),
promote it to a shared section of `_TEMPLATE` instead of writing it in one package only.

## Testing

- Run the docs/05 flow once with `examples/runner_profile.example.yaml` + your package and
  have a human/agent check the weekly skeleton is self-consistent (session count,
  long-run day, quality days match the profile).
- Check paces land in a plausible range (within ~10–20 s/km of public references).
