# Contributing

Thank you for considering contributing to **VDL Parkings**.

Bug reports, documentation improvements, compatibility fixes and feature proposals are welcome.

## Before opening a pull request

1. Search existing issues and pull requests to avoid duplicate work.
2. For larger changes, open an issue first to discuss the proposed approach.
3. Keep changes compatible with the minimum Home Assistant version declared in `custom_components/vdl_parkings/manifest.json`.
4. Update the README or relevant documentation when behaviour, configuration or entities change.
5. Update `CHANGELOG.md` under **Unreleased** for user-visible changes.

## Development guidelines

- Follow the existing Python style and Home Assistant integration conventions.
- Keep network access asynchronous.
- Do not add credentials, API tokens, personal data or local Home Assistant configuration to the repository.
- Preserve existing entity unique IDs unless a migration is intentionally implemented.
- Handle missing or malformed upstream data defensively.
- Log actionable errors without exposing sensitive information.
- Avoid creating duplicate Home Assistant zones.

## Local checks

Before submitting a change, perform the checks that apply:

- Compile the integration Python files:

  ```bash
  python -m compileall custom_components/vdl_parkings
  ```

- Validate JSON files such as `manifest.json` and translation files.
- Run the integration in a Home Assistant test instance where possible.
- Check the Home Assistant logs during setup, refresh, reload and unload.
- Verify that selected parking entities update and zone creation/removal behaves as expected.

Do not claim that a check passed unless you have actually run it.

## Pull requests

A useful pull request description includes:

- What changed and why.
- The Home Assistant version used for testing.
- Relevant logs or screenshots, with private information removed.
- The checks performed and their results.
- Any user-facing changes or migration considerations.

Keep pull requests focused. Avoid bundling unrelated refactoring with a bug fix.

## Reporting bugs

Use the [GitHub issue tracker](https://github.com/janreimen/HA-VDL-Parkings/issues).

Include the integration version, Home Assistant Core version, reproduction steps and relevant log entries.
