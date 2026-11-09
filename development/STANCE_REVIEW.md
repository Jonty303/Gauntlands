# Moving stance and return to wide idle

9 November 2026. Baseline 7bbeff5. User explicitly requested inward landings while
moving and a return to wide idle, including the affected transition animation.
R3 lead, R2 runtime integration and R6 validation by the same agent.

## Bounded contract, before implementation

Use the accepted v0.3 rig and clips. Add a model-specific runtime leg adjustment:
20 mm inward per moving foot (nominal ankle tracks 250 -> 210 mm apart), retaining
toe rotation and authored forward travel/roll. Change the added lateral placement
only while swinging. Idle remains the exact wide baseline. The trailing foot
widens during its existing stop recovery (0.12–0.64 s); the leading foot then takes
a small outward settling step (0.64–0.96 s, initially 18 mm lift). The original stop
only lifts the trailing foot, so simply blending narrow Run into wide Idle cannot
satisfy the contact requirement. Run-up timing, steering and braking are retained.
Restart must interrupt settling without a lateral jump or blocking input.

Implement in a separate runtime stance adapter, after AnimationTree sampling and
before actual sole clearance. Two-bone leg solve retains source knee bend plane,
bone lengths and global foot orientation. Accepted Blender sources/GLBs/generators
stay frozen; this runtime pose contract is specific to this rig, not a new source
animation version or a generic retargeting system.

Acceptance: moving steady feet each 20 mm inward within 0.5 mm; idle offsets return
to <0.1 mm within 1.0 s of release; no lateral adjustment on support intervals;
no discontinuous offset >2 mm per 60 Hz tick; no knee-direction flip, stretched
bones or non-finite poses; full-body sampled floor >= -3 mm. Check both stop leads,
eight release phases, cancelled starts/restarts, 30/60/120 Hz and prior motion/run-up
regression. Inspect rendered gait and settling in isometric, 3/4 and top-down.
Document geometry checks and any unverified clothing/physical-controller quality.

## Evidence

Implemented [foot_stance.gd](../prototype/motion/foot_stance.gd) and integrated it
into [motion_animation.gd](../prototype/motion/motion_animation.gd). Each foot
retains its current lateral offset through support, interpolates during swing,
and keeps the reached placement at touchdown. A 0.115 m/s lateral speed bound
prevents a late interrupted swing from snapping to its target; any remaining
adjustment finishes on the next swing. The leading stop foot gets an 18 mm lift
while stepping outward after the trailing foot lands. The HUD reports Settling
stance until the placement is complete; input can interrupt throughout.

The old Stop clip time remains capped at 0.8 s; the adapter's stop clock extends
to 1.0 s so the extra settling step can finish at 0.96 s. Movement braking and
the accepted run-up controller are unchanged. Toe orientation and the source
knee bend plane are retained by an analytic two-bone solve. This adds runtime IK
for stance width; the earlier demo's “no IK” description is historical.

## Commands and results — 9 November 2026

From the Gauntlands repository, using installed Godot 4.5.2 stable and Blender
5.2.3 LTS (substitute their installed paths for godot/blender):

```powershell
godot --headless --editor --path prototype --quit
godot --headless --path prototype --script res://tests/test_stance.gd
godot --headless --path prototype --script res://tests/test_run_up.gd
godot --headless --path prototype --script res://tests/test_motion_demo.gd
godot --headless --path prototype --script res://tests/test_stance.gd -- --stance-geometry
blender --background --factory-startup --python-exit-code 1 --python tools/motion_v04/stance/check_geometry.py
godot --path prototype --script res://tests/test_stance.gd -- --stance-capture
python tools/motion_v04/stance/package_previews.py
```

Godot installation: `C:/Users/jonat/AppData/Local/Temp/gauntlands-godot-4.5.2/`.
Blender installation: `C:/Program Files/Blender Foundation/Blender 5.2/`.
Preview packaging uses the existing Pillow PYTHONPATH at
`$env:TEMP/gauntlands-preview-libs`. No dependency installation or live Blender
file mutation. Historical motion/run-up reports were restored byte-for-byte;
new regression results are stored in this pass's folder.

[Stance suite](../tools/motion_v04/stance/validation.json): pass at 30/60/120 Hz,
16 phase-stop cases (both gaits and leads) and five interrupted-restart cases.

| Check | Measured result |
| --- | --- |
| Steady moving placement | Both feet 20 mm inward, within 0.5 mm |
| Return to wide idle | Within 1.0 s; residual <0.0005 mm |
| Added lateral offset drift during support | 0 m |
| Largest lateral change per 60 Hz tick | 1.917 mm, below 2 mm guard |
| Largest lateral change when sole is <=1 mm above floor | 0.00345 mm, below 0.2 mm guard |
| Leg-length discrepancy | 0.000268 mm |
| Minimum knee bend-plane alignment | 0.99999976 (no flip) |
| Largest knee rotation step per 60 Hz tick | 6.080 degrees, below 9-degree runtime guard |
| Lowest sampled full-body skin height | -0.000000151 m (float noise) |
| Travel over test | 6.8267765 m, identical across all three rates |

These contact metrics describe this adapter's added correction, not proof of
world-space contact locking during every turn. The pre-existing movement/turn
sliding limitations still apply.

[Motion regression](../tools/motion_v04/stance/motion_validation.json): pass,
including 24 direction/camera cases, input/pause/disconnect behavior and the prior
16 phase-stop cases. Largest runtime ground-lift correction 28.01 mm in the full
rehearsal. [Run-up regression](../tools/motion_v04/stance/run_up_validation.json):
pass; first walking step still 1.30 s and full run speed 1.85–1.867 s.

[Geometry comparison](../tools/motion_v04/stance/geometry_validation.json): sixteen
paired actual Godot-skinned body/garment poses spanning start, walk, run, stop,
settle and idle. Baseline and adjusted samples both have zero body/garment
triangle overlaps and zero garment vertices inside the body beyond 0.1 mm.
This is sampled clearance, not a continuous collision or cloth-self-contact guarantee.

The first test compile failed because a local ease helper collided with Godot's
built-in ease function. Renaming it placement_ease fixed compilation. The first
placement planner forced its target at the end of a sampled swing; review removed
that behavior proactively and added a speed bound plus per-tick restart checks,
so late interruptions retain the reached placement instead of jumping.

## Visual evidence and handoff

[Isometric](../tools/motion_v04/stance/isometric.gif) ·
[3/4](../tools/motion_v04/stance/three_quarter.gif) ·
[top-down](../tools/motion_v04/stance/top_down.gif).
Pose sheets: [isometric](../tools/motion_v04/stance/isometric_poses.png),
[3/4](../tools/motion_v04/stance/three_quarter_poses.png),
[top-down](../tools/motion_v04/stance/top_down_poses.png).

180 rendered frames per view, 30 Hz; previews 90 frames / 6 s each, timing verified.
Agent inspected moving and settling poses from all three angles. Physical joypad
feel and normal-speed owner sign-off remain pending. The change is deliberately
modest at 2 cm per foot; further narrowing is a tuning decision after review.

R3 -> R2/R6 same-agent handoff: rig-specific adapter, same 137-bone hierarchy,
metres/Y-up/+Z-forward and source clips. Automated gates pass; renderer samples
reviewed. Accepted source/GLB/generator manifests remain unchanged. No new source
animation version, release tag, merge or push. Next owner: user for feel review.

The adapter is intentionally scoped to this human. Future armour, different body
proportions, aiming/strafe clips and dedicated turns require their own leg/cloth
checks. Current compensation does not add full world-space foot locking.
