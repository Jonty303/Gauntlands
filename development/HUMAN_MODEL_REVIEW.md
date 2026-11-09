# Human Prototype 01 - model review contract

Recorded 9 November 2026 following the user's explicit instruction: review this
model in isometric, three-quarter and top-down views as the target sign-off set.
Applies to `human-prototype-01` in Jonty303/Gauntlands. This records the review
requirement; it does not grant artistic sign-off, branch creation or a merge.

## Required views

All three views must accompany model/animation polish reviews. The repeatable
implementation presets below are the initial interpretation of the requested
views; the user has not separately approved these exact camera angles.

| Preset | Projection | Elevation | Azimuth | Size / target |
| --- | --- | --- | --- | --- |
| Isometric | Orthographic | 35.264 degrees | 45 degrees | 2.8 / (0, 0.9, 0) metres |
| Raised three-quarter | Orthographic | 45 degrees | 30 degrees | Same |
| Top-down | Orthographic | 90 degrees | Image up = world -Z | Same |

Angles describe camera position about the target, with azimuth from +Z towards
+X in Godot. The top-down camera has an explicit up vector to avoid a singular
look-at. Identical projection size preserves a consistent world scale across
views; this is a review scale, not a signed-off gameplay zoom.

## Acceptance questions

- Is silhouette, facing and limb separation readable throughout the walk?
- Do foot contact, heel rise, push-off and recovery read coherently in the raised views?
- Do the feet and arm swing remain readable from above, including torso occlusion?
- Are knee stability, body rhythm, loose fists and shoulder movement preserved?
- Do eight facings reveal clipping, twisted joints or an unreadable silhouette?
- Do the source, export and Godot viewer pass the applicable technical checks?

Top-down naturally hides parts of the legs behind the torso. Use the three views
together: vertical clearance and knee bend cannot be signed off from overhead
alone. A technical pass does not establish animation feel. Human acceptance is
required before declaring this prototype approved.

## Repeatable review

Open the prototype and press F5. Use **Isometric**, **Raised 3/4**, **Top-down**,
the facing selector, Walk/Idle, pause and timeline. Isometric is the default.
Front/side/back and Low 3/4 remain available for diagnosis.

From the repository root, using the installed Godot 4.5.2 executable:

```powershell
godot --path prototype -- --record --review
python tools/blender/encode_review_views.py --baseline <saved-frames_review-folder>
```

Captures contain normal-speed loops in all three views, plus four walk phases
at eight facings per view. PNGs are disposable; encoded loops, pose sheets and
[the camera manifest](../tools/blender/locomotion_previews/review_cameras.json)
are the review artifacts. Baseline/current comparisons use identical cameras,
lighting, timing and scale. No controllable movement or turning system is implied.

[Latest implementation and evidence](WALK_UPPER_BODY_REVIEW.md).
