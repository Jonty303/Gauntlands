# Idle and walk — first locomotion clips

Open `project.godot` in **Godot 4.5.2 stable** and press **F5**.

- **Idle**: relaxed four-second standing loop with subtle body movement.
- **Walk**: in-place 1.2-second loop, intended for travel at **0.9 m/s**.
- **Idle / Walk buttons**: start walking from a planted passing pose; stopping
  finishes the step before a short blend to idle.
- **Ground reference**: moving marks help reveal foot sliding at the nominal speed.
- **Play/pause and timeline**: inspect the animation at a chosen phase.
- **Isometric / Raised 3/4 / Top-down**: the required model review views; isometric is the default.
- **Facing selector**: inspect eight facings without changing the animation.

This is animation review, not a controllable character. Gamepad movement and
turning are the next implementation stage. The relaxed unarmed walk is approved as
[human_male_prototype_v0.1](../development/HUMAN_MALE_PROTOTYPE_V01.md). The original diagnostic is still available by
opening `proof.tscn` and pressing **F6**.

[Animated walk preview](../tools/blender/locomotion_previews/walk.gif) ·
[Validation and reproduction](../development/LOCOMOTION_REVIEW.md) ·
[Earlier diagnostic report](../development/ANIMATION_PROOF_REVIEW.md).

From the repository root, substitute the installed executable path for `godot`:

```powershell
godot --headless --editor --path prototype --quit
godot --headless --path prototype --script res://tests/test_locomotion.gd
godot --headless --path prototype --script res://tests/test_locomotion_viewer.gd
```

The [model review contract](../development/HUMAN_MODEL_REVIEW.md) defines the
three required sign-off views. `godot --path prototype -- --record --review`
captures those loops and eight-facing pose sheets; run
`python tools/blender/encode_review_views.py` to encode them.

`godot --path prototype -- --capture` records six actual engine views.
`godot --path prototype -- --record` records 36 walk frames; optional
`tools/blender/encode_walk_preview.py` packages these into a GIF using Pillow.

Keep the committed GLB import settings: metres, 60 fps for locomotion, disabled
animation optimisation, disabled mesh compression and disabled LOD generation.
The diagnostic retains its separate 30 fps import settings.
