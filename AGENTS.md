# For coding agents

- `README.md` covers the demo app. `bench/README.md` covers the measurements.
- Measuring current uses zephyr-ppk2 and ppk2-lib. Read their two procedures before any capture.
- `../zephyr-ppk2/.claude/skills/ppk2-profile/SKILL.md`: markers, `west ppk2`, reading a report.
- The [`ppk2` skill](https://github.com/rdagher/ppk2-lib/blob/main/.claude/skills/ppk2/SKILL.md)
  of ppk2-lib: modes, powering the DUT for a flash, debug mode after a flash, lost samples.
- Flashing and capturing use the hardware on the bench. Do not do either unless asked.
- Never capture in the same powered session as a flash. The chip stays in debug mode and reads high.
