# Loose fists and gait refinement - 8 November 2026

Historical pass: superseded by the [walk fluidity pass](WALK_FLUIDITY_REVIEW.md). Shared reports and walk previews now describe that later pass.

## Scope and handoff

User requested loose fists, more roll over the ball of the foot, and slightly
more hip movement. Existing `human-prototype-01`, Jonty303/Gauntlands only.
R3 lead; R2 integration and R6 checks performed sequentially by one agent.
No independent sign-off, commits, pushes, branches or merges. Human visual
acceptance remains pending.

R3 -> R2/R6 deliverables: [generator](../tools/blender/build_locomotion.py),
[validation](../tools/blender/test_locomotion.py),
[Blender derivative](../assets/Blender%20Models/Human-Male-Locomotion.blend),
[GLB](../prototype/assets/human_locomotion.glb), regenerated bounds, reports
and GPU previews. Original source model hash preserved. Pre-edit scripts,
source/export and previews backed up to
`%TEMP%/gauntlands-fists-before-20261108-222819`.

## Changes and preserved interfaces

Loose fists apply consistently to Idle and Walk: finger joints 2-5 curl
25/40/20 degrees; thumb bends 5 degrees at each distal joint and turns 15%
towards the index-base direction at its base. Space remains inside the curl;
this is a relaxed pose, not a tight clenched fist. Axes now consistently use
armature-space rest head/tail coordinates before conversion to bone-local space.
The prior mixed-space calculation became visibly wrong at stronger curl angles.

Foot push-off rises from 22 to 28 degrees around the existing ball/toe joint,
with the toes kept level during stance. Stance phases, heel contact, swing timing
and cadence are unchanged; ankle compensation adapts to the increased roll.

Hip root sway amplitude rises from 24 to 28 mm; yaw from 3 to 4 degrees and tilt
from 1.5 to 2 degrees. Vertical amplitude stays 12 mm. Existing spine/head
counter-motion follows the revised pelvis; shoulders/arms retain their authored
phase offsets and elbow/wrist motion.

Preserved: 137 bones, nine source shape keys, clothing, materials/provenance,
metres, Blender Z-up/-Y-forward, Godot Y-up/+Z-facing, 60 Hz bake, 4-second Idle,
1.2-second Walk, 0.9 m/s reference speed, 60% stance, half-cycle leg offset,
8-influence GLB export and viewer transition rules. Idle hands intentionally
change. No controller, gameplay, modelling or rig-framework additions.

## Validation

Blender 5.2.3 LTS and Godot 4.5.2 stable. Early fist candidates failed sampled
hand self-intersection checks and were revised. Live hand-pose trials isolated
coordinate-space and thumb-overlap issues. Temporary inspection geometry was
removed and the reproducibly built derivative reloaded; live experiments were
not saved over the source.

Final build and full `test_locomotion.py` exited 0, with `quick: false` and all
241 Idle plus 73 Walk frames. Godot headless editor import, `test_locomotion.gd`,
`test_locomotion_viewer.gd`, GPU `--capture` and `--record`, and the existing
Pillow GIF encoder all exited 0. Python syntax, documentation links and
`git diff --check` passed. Diagnostic regression was not rerun because its
assets and shared engine code were unchanged. No physical controller test.

| Check | Final observed result |
| --- | --- |
| Original model / save-reopen | Pass: hash preserved, nine shape keys and packed textures |
| Hand-region self intersections | Zero across both clips |
| Body-cloth / cloth self intersections / inside vertices | Zero |
| Loop seam | Zero endpoint vertex difference |
| Walk floor minimum | 1.067 mm above plane |
| Contact anchor / sampled sole step error | 0.000655 / 0.188290 mm maximum |
| Tested hand-thigh clearance | Minimum 14.079 mm; zero intersections |
| Pelvis lateral range | 56.756 mm, previously 48.487 mm |
| Pelvis vertical range | 23.996 mm, effectively unchanged |
| Head lateral / vertical range | 27.922 / 23.854 mm |
| Knee flex / maximum change | 21.122-64.755 degrees / 4.962 degrees per 60 Hz frame |
| Godot pose agreement | Maximum bounds error 0.048637 mm |
| Cross-fade / actual viewer floor minima | -1.683 / -1.084 mm; within existing -3 mm limit |
| Visual inspection | Close hand trials, built side-view pose strip and Godot contact pose inspected |
| Artistic acceptance | Pending human review |

Hand testing now includes non-adjacent surface intersections in both clips,
excluding shared vertices and coincident export seams. The bind-space hand
region was expanded to abs(X)>0.455 m, Z<1.25 m to cover more of the thumb/root.
Other task-local limits remain: >5 mm hand-thigh clearance, <6-degree elbow/knee
step change, and existing foot/cloth limits. This is region-based checking, not
an exhaustive whole-body collision certificate. Tests sample authored 60 Hz
frames, not every subframe or terrain. Naturalness remains an artistic judgement.
Existing exporter warnings about reducing weights above eight and using the
first texture sampler remain; the actual export was tested. Existing CC0 MPFB
material provenance continues; motion is project-authored.

## Review

- [Before/after loop](../tools/blender/locomotion_previews/fists_gait_before_after.gif)
- [Updated walk](../tools/blender/locomotion_previews/walk.gif)
- [Before/after poses](../tools/blender/locomotion_previews/fists_gait_contact_sheet.png)
- [Metrics](../tools/blender/locomotion_previews/fists_gait_metrics.json)
- [Full Blender report](../tools/blender/locomotion_previews/validation.json)
- [Godot pose/blend report](../tools/blender/locomotion_previews/godot_validation.json)
- [Viewer report](../tools/blender/locomotion_previews/viewer_validation.json)

R2/R6 receiving result: technically accepted for visual review. Built source is
loaded in connected Blender with Walk selected, frames 1-73. Next owner is the
human for gait/hand judgement; no first-character milestone sign-off inferred.
