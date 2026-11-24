# For coding agents

- `README.md` covers the demo app; `bench/README.md` covers the measurements.
- Measuring current uses two tools of this workspace. Read their procedures before any capture:
  - `../zephyr-ppk2/.claude/skills/ppk2-profile/SKILL.md` (markers, `west ppk2`, reading a report);
  - the `ppk2` skill of [ppk2-lib](https://github.com/rdagher/ppk2-lib/blob/main/.claude/skills/ppk2/SKILL.md)
    (modes, powering the DUT for a flash, debug mode after a flash, lost samples).
- Flashing and capturing use the hardware on the bench. Do not do either unless asked.
- Never capture in the same powered session as a flash: the chip stays in debug mode and reads high.
