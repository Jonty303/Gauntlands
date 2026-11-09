# Walk heel/toe revision — 8 November 2026

Historical heel/toe pass. Current generated assets and validation reports now
reflect [the pelvis revision](WALK_PELVIS_REVIEW.md). The original before/after
GIF and heel/toe contact sheet remain unchanged.

## Scope and handoff

User authorised this flatfooted-walk revision on existing `human-prototype-01`
in Jonty303/Gauntlands. R3 primary; R2 integration and R6 QA performed sequentially
by the same agent. No independent sign-off. Human artistic acceptance pending.
No branch, commit, push or merge created.

R3 -> R2/R6 artifacts: regenerated
[Human-Male-Locomotion.blend](../assets/Blender%20Models/Human-Male-Locomotion.blend)
and [human_locomotion.glb](../prototype/assets/human_locomotion.glb), using
[build_locomotion.py](../tools/blender/build_locomotion.py).
Previous uncommitted source/export/scripts and previews were backed up to
`%TEMP%/gauntlands-walk-before-20261108-212843` before editing.

Preserved interface: 137 bones, nine source shape keys, underwear and materials,
metres, Blender Z-up/-Y-forward, Godot Y-up/+Z-facing, 60 fps bake,
4-second Idle, 1.2-second in-place Walk, 0.9 m/s reference travel, 60% stance,
half-cycle opposite-leg offset, eight skin influences and viewer transitions.
No gameplay/controller, costume, retargeting or rig-framework additions.
Existing pelvis and arm motion retained; analytic knees respond to new ankles.

## Foot-motion contract

| Per-leg phase | Behaviour |
| --- | --- |
| 0–0.12 | 12-degree toes-up heel contact settles smoothly to sole |
| 0.12–0.42 | Flat supporting foot |
| 0.42–0.60 | Heel lifts to 22 degrees around ball/toe joint; toe remains level |
| 0.60–1.00 | Lifted swing returns pitch to heel contact; toe counter-rotation releases over first 30% of swing |

Ankle translation compensates rotation about the heel or toe pivot before the
analytic leg solve. Existing toe bones supply articulation. Pivots and pitch
values are authored for this human, not certified for other proportions.

[test_locomotion.py](../tools/blender/test_locomotion.py) now tracks heel/sole/toe
anchors rather than treating moving ankles as slip. Independently selected
exported bind-mesh sole vertices also track evaluated skin contact. Task-local
sanity limits: 0.1 mm anchor step error, 3 mm sampled skin step error and 12 mm
sampled contact-vertex height. These are diagnostics, not general foot-lock
specifications; representative contact vertices need not be the lowest sole
points. Existing -3 mm floor tolerance retained. Actual loop frames stay above
floor. No resource-budget or performance claims introduced.

## Verification

Blender 5.2.3 LTS; Godot 4.5.2 stable. Ran the original
[reproduction commands](LOCOMOTION_REVIEW.md#reproduction): build generator,
full Blender validation, headless editor import, `test_locomotion.gd`,
`test_locomotion_viewer.gd`, `test_import.gd`, GPU `--capture`, GPU `--record`,
and `encode_walk_preview.py`. All exited 0. Final `validation.json` is full
(`quick: false`), following an earlier quick check. Python syntax compilation
and `git diff --check` passed. No physical gamepad test performed.

| Check | Result |
| --- | --- |
| Source preserved / derivative reopened | Pass: source hash unchanged; nine shape keys and packed textures |
| Full geometry | 241 Idle and 73 Walk frames; zero body/cloth, cloth self intersections or inside vertices |
| Walk floor minimum | 1.851 mm above floor |
| Walk clothing minimum clearance | 2.936 mm |
| Loop seam | Zero endpoint vertex difference |
| Contact anchor step error | Maximum 0.000468 mm |
| Sampled skin contact step error | Maximum 0.189 mm |
| Sampled contact vertex height | Maximum 8.473 mm |
| Godot pose bounds comparison | Pass; maximum error 0.049710 mm |
| Cross-fade floor | -1.228 mm, within existing -3 mm tolerance |
| Actual viewer transitions | Pass; minimum -0.016856 mm |
| Diagnostic regression | Pass; maximum bounds error 0.050306 mm |
| Visual inspection | Blender side pose strips and actual Godot cycle/contact frames reviewed; heel strike and raised trailing heel visible |
| Human artistic acceptance | Pending |

Blender MCP inspected source and toe bones, loaded the regenerated derivative,
and supplied pose strips. Connection was previously verified as add-on 1.8,
matching protocol 15, telemetry disabled. No generator service or downloaded
motion capture used. Existing CC0 MPFB material provenance continues;
animation is project-authored.

Earlier export warnings remain: weights above eight are reduced; the first
texture-node sampler is used. Actual exported geometry was tested. Checks cover
authored 60 Hz samples, not every subframe or uneven terrain. Per-frame contact
drift does not certify zero cumulative skin deformation. Pose/frame inspection
does not substitute for human judgement of the running loop.

The diagnostic regression test regenerated
`tools/blender/animation_previews/godot_validation.json`. Automatic approval
review rejected restoring it from HEAD because that could overwrite uncommitted
work; the regenerated report is left in place. All other unrelated work preserved.

## Review artifacts

- [Before / after](../tools/blender/locomotion_previews/walk_before_after.gif)
- [Updated walk](../tools/blender/locomotion_previews/walk.gif)
- [Godot contact sheet](../tools/blender/locomotion_previews/heel_to_toe_contact_sheet.png)
- [Build manifest](../tools/blender/locomotion_previews/build.json)
- [Blender validation](../tools/blender/locomotion_previews/validation.json)
- [Godot validation](../tools/blender/locomotion_previews/godot_validation.json)
- [Viewer validation](../tools/blender/locomotion_previews/viewer_validation.json)

Receiving R2/R6 result: technically accepted for human review based on the checks
above. Next owner: human gait review. No first-human or gameplay milestone sign-off.
