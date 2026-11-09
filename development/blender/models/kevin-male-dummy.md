# Kevin Iglesias male dummy — test 01

Scope: Basic Motions FREE 2.4 male dummy walk, Blender 5.2.3 / Godot 4.5.2.
This does not change the accepted Gauntlands human.

[Build, interface, licence and evidence](../../../tools/kevin_walk/README.md)
are the authoritative test record. Local GLB: DummyRig, 56 B-prefixed bones,
KevinMaleDummy mesh, one Walk action; metres, +Z forward, 0.8 s stride, 2 m/s.
No retargeting. Runtime adds the documented measured floor correction.
Owner review and physical joypad input remain unverified.

## Test 02 additions

Walk accepted and preserved in 426f7e2. [Idle/run interface](../../../tools/kevin_locomotion/README.md)
adds Idle (2.7 s) and Run (0.6 s, 2.4 m, 4 m/s) to the same 56-bone rig.
Native Blender sources require idle constraint-state priming before sampling.
Runtime blends share gait phase and correct actual skinned sole penetration.
No sprint or retargeting. Test 02 owner acceptance remains pending.

## Test 03: action catalogue

Owner accepted test 02 as excellent. The new viewer uses the native male body
and deformation rig from each supplied pack, preserving the accepted locomotion
actor. 112 unique source actions plus one complete bow sequence are available;
five sprint directions are selection-only. [Current interface and evidence](../../../tools/kevin_actions/README.md).
Most packs retain 56 B-bones; Archer adds six bow and two sword-transfer bones.
Hand props, source-derived floor curves, import naming settings and measured
clearance are viewer-specific. This establishes neither retargeting nor
production equipment/armour compatibility. Owner acceptance of test 03 is pending.

## Owner checkpoint decision — 9 November 2026

Resource evaluation accepted: sufficient models/animations for the initial
prototype game structures. The viewer was approved except arrow firing.
[P02-ARCHERY-01 and the checkpoint](../../PROTOTYPE_02_CHECKPOINT.md) supersede
the pending owner-review status above. This does not certify production archery,
other-race retargeting or armour/clothing compatibility.
