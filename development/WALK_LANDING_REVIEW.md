# Landing and supported-rise pass - 8 November 2026

Historical pass: followed by the [leg-extension pass](WALK_EXTENSION_REVIEW.md).
Numbers below describe the landing pass; shared current reports/media may now
represent its successor.

## Scope and handoff

User authorised the next iteration on landing, knee softness and pelvis timing.
R3 leads; R2/R6 integration and validation performed sequentially by the same
agent. Existing `human-prototype-01`, Jonty303/Gauntlands only. No commits, pushes,
branches or merges. The improved shoulder pass is the comparison baseline;
artistic acceptance of this new pass remains pending.

Target: knee yields during loading, then straightens more as the body passes over
the supporting foot. Keep the current foot paths, cadence and upper-body rotations.
Compare normal-speed side and three-quarter loops and actual forward travel.
Backup: `%TEMP%/gauntlands-landing-before-20261108-233702`.

## Change

The [generator](../tools/blender/build_locomotion.py) replaces the previous
sinusoidal vertical pelvis motion with a small set of Hermite height poses.
Coordinates are root offsets relative to the source rig, not floor heights.
The sequence repeats every half-cycle for alternate foot contacts.

| Full-cycle phase within a step | Root offset | Slope, metres/cycle |
| --- | --- | --- |
| 0%, heel contact | -52 mm | -0.10 |
| 8%, loaded settling pose | -58 mm | 0 |
| 27%, supported rise | -22 mm | 0 |
| 42%, descending towards next contact | -48 mm | -0.10 |
| 50%, opposite heel contact | -52 mm | -0.10 |

Matching endpoint values/slopes keep the loop continuous. The existing leg solver
turns the revised pelvis height into knee flexion while preserving the prescribed
foot poses. Explicit height keys and their period are stored in
[build.json](../tools/blender/locomotion_previews/build.json), replacing the obsolete
single bob-amplitude field. A preliminary curve without the 42% descent pose
predicted excessive late-swing knee speed (6.08 degrees/sample); it was revised
before building. The existing <6-degree guard was not relaxed.

This increases measured pelvis vertical range from 23.996 to 35.859 mm. That is
an intentional trade-off: clearer settling and supported rise, with more vertical
body/head travel to judge in playback. No additional head stabilisation was added.

R3 -> R2/R6 artifacts: generator, [editable derivative](../assets/Blender%20Models/Human-Male-Locomotion.blend),
[GLB](../prototype/assets/human_locomotion.glb), refreshed pose bounds, reports
and review media. Validator and viewer code are unchanged.

Preserved interfaces: metres; Blender Z-up/-Y-forward and Godot Y-up/+Z-facing;
137 bones, nine source shape keys, packed textures, clothing and loose fists;
60 Hz bake, 4-second Idle, 1.2-second Walk, 0.9 m/s, 60% stance and opposite-leg
half-cycle offset; 8-influence GLB export and prior transition rules. No gameplay,
controller or modelling additions. Sprite dimensions/facing order are not applicable.

## Evidence

Blender 5.2.3 LTS; Godot 4.5.2 stable. Build and full Blender validator exited 0:
241 Idle frames, 73 Walk frames and 72 intermediate floor samples. No tolerances
changed. A separate source comparison sampled both feet/toes and the root/chest/
clavicle/upper-arm/head rotations at all 73 Walk frames.

| Check | Result |
| --- | --- |
| Original source / save-reopen / shape keys | Pass; source preserved, nine keys |
| Sampled foot pose matrix element difference | <=3.58e-7 versus baseline |
| Sampled upper-body rotation matrix element difference | Zero |
| Left knee at contact / 0.15 s loading / 0.30 s support | 21.635 / 33.359 / 27.357 degrees; previously 23.703 / 32.463 / 32.722 |
| Knee full range / maximum 60 Hz change | 13.429-64.347 degrees / 5.279 degrees; pass |
| Pelvis vertical / head vertical range | 35.859 / 35.738 mm |
| Loop endpoint vertex difference | Zero |
| Hand self / body-cloth / cloth self / inside-vertex checks | Zero across authored frames |
| Hand-thigh clearance / intersections | 15.755 mm minimum / zero |
| Walk floor, authored / intermediate | +1.954 / +1.961 mm |
| Contact anchor / sampled skin step error | 0.000626 / 0.188544 mm maximum |
| Godot pose bounds error | 0.049114 mm maximum; pass |
| Godot cross-fade / viewer floor minima | -2.289 / -0.985 mm; within existing -3 mm limit |
| Visual inspection | Blender side strip and matched Godot landing/support poses inspected |
| Feel / naturalness | Pending human normal-speed review, especially added vertical travel |

Godot headless editor import, `test_locomotion.gd`, `test_locomotion_viewer.gd`,
GPU `--capture`, `--record`, `--record --side-view`, `--record --travel`, and
`encode_walk_preview.py --baseline <saved-preview-folder> --comparison-name landing`
all exited 0. Numerical curve value/slope continuity, Python syntax, source/export
hashes, local documentation links and `git diff --check` were checked. Installed
executable paths and reproduction commands remain those in the
[push-off review](WALK_PUSHOFF_REVIEW.md).

[landing_metrics.json](../tools/blender/locomotion_previews/landing_metrics.json)
contains source before/after heights, knee angles and preservation checks, produced
by `%TEMP%/gauntlands-compare-landing.py`. Idle bounds and authored foot targets
also match the baseline reports exactly.

Limits: region-based sampled collision tests are not exhaustive; intermediate
samples check floor clearance only. No physical controller, uneven terrain,
fresh-character recreation or artistic sign-off. Existing exporter warnings about
weights above eight and first texture sampler remain; the delivered export was
tested. Existing CC0 MPFB provenance continues.

## Review

- [Side before/after](../tools/blender/locomotion_previews/landing_side_before_after.gif)
- [Three-quarter before/after](../tools/blender/locomotion_previews/landing_before_after.gif)
- [Landing/support poses](../tools/blender/locomotion_previews/landing_contact_sheet.png)
- [Forward travel](../tools/blender/locomotion_previews/walk_travel.gif)
- [Blender report](../tools/blender/locomotion_previews/validation.json)
- [Godot report](../tools/blender/locomotion_previews/godot_validation.json)
- [Viewer report](../tools/blender/locomotion_previews/viewer_validation.json)

Receiving result: R2/R6 technical checks pass. Connected Blender has the new
derivative open, Walk selected, frames 1-73. Human review remains the next gate:
does the settle-and-rise feel supported and natural rather than bouncy?
