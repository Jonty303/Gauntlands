# Human male prototype — motion demo

F5 opens the **v0.4 joypad motion demo**, ready for feel review. Left stick tilt
controls walking/running. WASD/arrows walk; Shift runs on keyboard. 1/2/3 change
review view, P pauses, R resets. **Replay test** repeats the same motion scenario;
**Close view** restores the model-inspection framing.

The latest [run-up polish](../development/RUN_UP_REVIEW.md) completes one clear
walking step before building running speed from rest. Replay test demonstrates it.

The [stance pass](../development/STANCE_REVIEW.md) brings moving landings inward
and uses two sequential placements to return to wide idle. Release the stick after
running to review the settling step; movement can interrupt it.

See [implementation, evidence and limitations](../development/MOTION_DEMO_V04.md).
The v0.3 source/export remain frozen. Physical joypad feel and sharp-turn foot
pivoting still need owner review.

## Accepted run review

The approved walk is frozen at `human_male_prototype_v0.1` (`f4579d0`).
The accepted Idle/WalkStart/Walk/WalkStop set is checkpointed locally at
`human_male_prototype_v0.2` (`12b2b0b`).

Open `locomotion_v03.tscn` in **Godot 4.5.2 stable** and press **F6** for the accepted run review.
**Idle / Walk / Run** request the authored sequence. Gait changes enter at the
next matching foot contact; requests made during a transition are retained.
Running from Idle goes through WalkStart and WalkToRun. Stopping from Run goes
through RunToWalk and the existing stop. This is an animation review, not a
responsive gameplay-controller contract or a direct sprint-start animation.

The single-clip selector, pause and timeline allow pose inspection. Isometric,
raised three-quarter, top-down and eight facings remain the review views.
See [running review and reproduction](../development/RUN_REVIEW.md).

For the v0.2 checkpoint, open `locomotion_v02.tscn` and press **F6**.
Its current start is 0.7 seconds. See [the chest-entry correction](../development/WALK_START_CHEST_REVIEW.md)
and [the v0.2 record](../development/HUMAN_MALE_PROTOTYPE_V02.md).

## Approved v0.1 review

Open `locomotion.tscn` in **Godot 4.5.2 stable** and press **F6**.

- **Idle**: relaxed four-second standing loop with subtle body movement.
- **Walk**: in-place 1.2-second loop, intended for travel at **0.9 m/s**.
- **Idle / Walk buttons**: start walking from a planted passing pose; stopping
  finishes the step before a short blend to idle.
- **Ground reference**: moving marks help reveal foot sliding at the nominal speed.
- **Play/pause and timeline**: inspect the animation at a chosen phase.
- **Isometric / Raised 3/4 / Top-down**: the required model review views; isometric is the default.
- **Facing selector**: inspect eight facings without changing the animation.

This older scene is animation review. The new motion demo supplies gamepad
movement and steering; dedicated turn clips remain future work. The relaxed unarmed walk is approved as
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

## Human Prototype 02 — dummy walk

F5 launches dummy_walk.tscn: Kevin Iglesias male dummy, one forward walk,
left-stick/WASD movement and three cameras. 1/2/3: views; Space: auto-walk;
P: pause; R: reset. Release holds pose. Transitions/retargeting are not in test 01.
[Local asset rebuild and tests](../tools/kevin_walk/README.md).
Licensed assets are local and gitignored; rebuild them on a fresh checkout.
