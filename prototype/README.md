# Animated rig/export proof

Open `project.godot` in **Godot 4.5.2 stable** and press **F5**.
The eight-second diagnostic plays automatically. Use Play/pause, the timeline,
and Front/Side/Back/Three-quarter buttons to inspect it.

This scene demonstrates the existing 1.80 m character, skin, eyes, briefs and
137-bone rig in Godot. It is a diagnostic animation viewer, not the walking
milestone. No movement controller, idle/walk cycle or gamepad actions yet.

The clip lifts and bends the left leg, then right leg, swings the arms, and
turns the head both ways. Neutral poses separate the tests. Foot planting,
weight shifts and believable locomotion are deliberately not implied by this clip.

[Build, validation, limitations and handoff](../development/ANIMATION_PROOF_REVIEW.md)

## Checks

After importing the project, from the repository root (replace `godot` with
its full executable path if it is not on PATH):

```powershell
godot --headless --editor --path prototype --quit
godot --headless --path prototype --script res://tests/test_import.gd
```

`godot --path prototype -- --capture` writes seven actual GPU-rendered review
frames to `tools/blender/animation_previews/` and exits. It requires a display
and renderer; headless import checks are not visual evidence.

Keep the committed `.glb.import` settings: unit import scale, 30 fps, animation
optimisation disabled, mesh compression disabled, LOD generation disabled.
The GLB includes its textures; Godot extracts the two PNGs alongside it.
Do not manually overwrite the GLB with a default-settings export.
