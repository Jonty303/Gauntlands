# Human male prototype: model and animation contract

Last verified: 9 November 2026. Applies to the accepted v0.3 derivative in
Blender 5.2.3 LTS and Godot 4.5.2. Read [playbook](../playbook.md) first.

## Checkpoints and dependencies

| Version | Local commit / tag | Scope |
| --- | --- | --- |
| v0.1 | f4579d0 / human_male_prototype_v0.1 | Approved relaxed unarmed walk |
| v0.2 | 12b2b0b / human_male_prototype_v0.2 | Planted Idle, setting off and stops; corrected chest entry |
| v0.3 | 5161379 / human_male_prototype_v0.3 | Approved Run and left/right gait changes |

These are accepted animation checkpoints, not proof of equipment, controller or
full-character regeneration support. v0.2/v0.3 were committed locally, not pushed
by this chat. Recheck Git before reporting current remote state.

Dependency chain: original Human-Male.blend -> normalised Human-Male-180cm.blend
-> v0.1 locomotion -> v0.2 transitions -> v0.3 run. The [scale review](../../HUMAN_SCALE_REVIEW.md)
explains the original 2.4308 m height and provisional 1.80 m normalisation.
Changing body proportions is not covered by the existing animation acceptance.

Current [source](../../../assets/Blender%20Models/Human-Male-Locomotion-v0.3.blend),
[export](../../../prototype/assets/human_locomotion_v03.glb),
[authoring](../../../tools/blender/build_run.py),
[manifest](../../../tools/blender/locomotion_v03/v03_manifest.json),
[build data](../../../tools/blender/locomotion_v03/build.json).
Predecessor generators: [walk](../../../tools/blender/build_locomotion.py),
[transitions](../../../tools/blender/build_transitions.py). They are frozen inputs,
not invitations to regenerate over approved checkpoints.

## Live source inventory

Read-only MCP inspection on 9 November 2026 confirmed this hierarchy in v0.3:

| Object | Parent | Modifier order |
| --- | --- | --- |
| Human.rig | none | Armature object; 137 bones |
| Human | Human.rig | Armature; Hide helpers (Mask) |
| Human.high-poly | Human.rig | Armature; Subdivision |
| Gauntlands_Boxer_Briefs | Human.rig | Follow Human Rig (Armature); Soften Cloth Folds (Smooth); Fabric Thickness (Solidify) |

No pose-bone constraints were present. The scripts solve leg poses analytically
and bake keys; this is not an interactive IK-control-rig contract. Key bone names
include root, spine05 through spine01, head, clavicle.L/R, upperarm01.L/R,
lowerarm01.L/R, wrist.L/R, upperleg01.L/R, lowerleg01.L/R, foot.L/R and toe1-1.L/R.
Human retains nine shape keys. brown_eye.png and
young_lightskinned_male_diffuse.png were both packed. All ten actions have one slot.

## Units, sampling and export

Metres; Blender Z-up and -Y forward; Godot Y-up and +Z facing. Source 60 fps.
Actions bake location and quaternion channels. Clips are in place; recorded
virtual-travel curves drive the moving-ground review reference.
GLB: selected hierarchy, ACTIONS animation export, forced sampling, slide to zero,
eight skin influences, no exported morph targets. Existing weight-reduction and
texture-sampler warnings remain recorded; a warning alone is not a failed gate.
Use the committed [.import settings](../../../prototype/assets/human_locomotion_v03.glb.import):
60 fps, animation optimisation disabled, mesh compression disabled, no generated
LODs. Validate Godot poses against exported reference bounds after changes.

## Actions

| Action | Source frames inclusive | Duration | Travel / entry |
| --- | --- | --- | --- |
| Idle | 1-241 | 4.0 s | Planted breathing loop |
| WalkStart | 1-43 | 0.7 s | 0.216 m; left lead; joins Walk phase 0 |
| Walk | 1-73 | 1.2 s | 0.9 m/s; 60% stance per leg |
| WalkStopL/R | 1-49 | 0.8 s | 0.324 m; enters Walk phase 0 / 0.5 |
| Run | 1-49 | 0.8 s | 2.2 m/s; intended 40% stance per leg |
| WalkToRunL/R | 1-61 | 1.0 s | 1.55 m; phase 0 / 0.5 preserved |
| RunToWalkL/R | 1-61 | 1.0 s | 1.55 m; phase 0 / 0.5 preserved |

Export frames start at zero. L/R label the leading contact, not a turning direction.
Run has a 6-degree torso lean, earlier recovery behind the body and unfolding into
landing. v0.3 adds up to 8 mm local centre-front fabric ease; original garment
topology is retained. v0.2 files and all five v0.2 exported action channels remain
unchanged. The v0.3 garment fit is therefore a deliberate derivative difference.

## Runtime and validation

The accepted review remains [locomotion_v03.tscn](../../../prototype/locomotion_v03.tscn),
opened with F6. F5 now opens the separate [motion demo](../../../prototype/motion_demo.tscn).
The [viewer](../../../prototype/locomotion_v03.gd) waits for matching contacts,
finishes authored bridges and retains latest intent. Idle -> Run uses WalkStart
then WalkToRun; Run -> Idle uses RunToWalk then WalkStop. Direct run starts/stops,
turning, collision movement and joypad control are not implemented here.

Current reproduction, limits, validation commands and results:
[run review](../../RUN_REVIEW.md), [export report](../../../tools/blender/locomotion_v03/validation.json),
[Godot report](../../../tools/blender/locomotion_v03/godot_validation.json).
293 authored new poses, 288 half poses and 155 older-clip fabric-clearance samples
were checked. Godot gait changes passed 30/60/120 Hz tests. These are sampled
checks, not continuous collision guarantees. Rig anchors and actual sole skin
are different measurements; sampled sole heights approach 10 mm during toe roll.

Review cameras and acceptance remain the [three-view contract](../../HUMAN_MODEL_REVIEW.md).
The owner approved v0.3 in this chat. The subsequently authorised [v0.4 motion demo](../../MOTION_DEMO_V04.md)
uses the same GLB with phase-synchronised runtime blends and model-specific vertical
sole clearance. It implements steering/joypad control, not dedicated turning clips.
Its runtime blend quality has separate evidence and is pending owner feel approval;
this does not supersede the accepted v0.3 source checkpoint.

Runtime follow-up: [run-up pass](../../RUN_UP_REVIEW.md) adds a travelling walk step
and eased run-speed ceiling from rest; the same source clips and interfaces remain.

Runtime follow-up: [moving stance](../../STANCE_REVIEW.md) adds a rig-specific
two-bone leg adjustment after clip blending: 20 mm inward landings during swing,
then sequential outward recovery to wide Idle by 0.96 s after release. Source
actions and frozen exports remain unchanged. Runtime IK/settling is a separate
interface from the source rig, which still has no pose-bone constraints.
