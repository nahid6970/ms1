# Features Roadmap

This file tracks the next modular features to add to the button generator.

## Planned

- Add more action types per control.
- Add more trigger types per control.
- Support hotkey-based triggers, not only mouse events.
- Add folder/file utilities like open, copy, paste, and launch.
- Add per-control enable/disable switches.
- Add import/export for individual profiles.
- Add duplicate row/button actions.
- Add presets/templates for common workflows.
- Add better preview text in the Python GUI showing what each control does.
- Add validation for unsupported paths, shortcuts, and empty actions.

## Notes

- The current implementation is moving toward a data-driven model.
- Each control should store its own action and trigger metadata in JSON.
- The AHK generator should stay a pure renderer from that JSON model.
- UI changes should stay backward compatible with older profile JSON files when possible.
