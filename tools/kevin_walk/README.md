# Prototype 02: dummy walk test 01

9 November 2026. R2 lead; R3 asset and R6 validation responsibilities performed
by the same agent. Owner animation/feel approval remains pending.

## Scope and controls

F5 in this checkout launches [dummy_walk.tscn](../../prototype/dummy_walk.tscn).
The earlier [motion demo](../../prototype/motion_demo.tscn) remains available.

- Left stick: camera-relative movement, 18% deadzone, full tilt 2 m/s.
- WASD/arrows: full-speed walk; no diagonal speed advantage.
- Partial tilt scales travel and cadence together; no acceleration.
- Release holds the current pose. No idle or stopping clip in this slice.
- 1/2/3 or right bumper: isometric, raised 3/4, top-down.
- P or controller Start: pause. R: reset. Space: auto-walk.
- Close view button enlarges the character.
- Turns face the new travel direction immediately.

## Source and licence

Source root: S:/OneDrive/__Github/Human.
[Publisher](https://www.keviniglesias.com/) /
[Free Basic Motions](https://kevdev.itch.io/basic-motions-free).
The publisher's [licence](https://www.keviniglesias.com/#license), reviewed
9 November 2026, permits game use including commercial projects but restricts
redistribution of accessible standalone assets.

Original archives and derived GLB stay local and gitignored. Only build code,
source hashes and test evidence are prepared for version control. A fresh
checkout needs independently obtained free archives. No purchase, publication,
push or merge was performed in this test.

Source archive hashes are in [build.json](build.json).
The animation source's body mesh matches the separate male dummy exactly
(0 vertex difference). This is the supplied dummy, with no retargeting.

## Rebuild

From S:/OneDrive/__Github/Gauntlands-human-prototype-02:

    & "C:/Program Files/Blender Foundation/Blender 5.2/blender.exe" --background --factory-startup --python tools/kevin_walk/build_dummy_walk.py -- "S:/OneDrive/__Github/Human"

The builder extracts the two male source files into .local/kevin with scripts
disabled, samples the control rig, and exports a plain 56-bone skeleton with
eight skin influences. It creates local files under prototype/assets/kevin_local:
dummy_walk.glb, walk.json and controlled import settings.

Godot 4.5.2 checks:

    godot --headless --editor --path prototype --quit
    godot --headless --path prototype --script res://tests/test_dummy_walk.gd

Tested console executable on this machine:
C:/Users/jonat/AppData/Local/Temp/gauntlands-godot-4.5.2/Godot_v4.5.2-stable_win64_console.exe

For captures, run the test without --headless and append -- --capture.
Then run python tools/kevin_walk/package_previews.py with Pillow available.
The current machine used the existing Pillow library in
%TEMP%/gauntlands-preview-libs through PYTHONPATH.

## Animation interface

- Source: HumanM@Walk01_Forward [RM], frames 1-25 at 30 fps.
- Output: Walk, frames 1-49 at 60 fps, 0.8 s full stride.
- Root travel 1.5999999 m per stride is removed from the clip and applied by
  the demo at 2 m/s; cadence follows requested travel.
- Metres, Blender Z-up/-Y forward; Godot Y-up/+Z forward.
- Final key equals the first, closing a sub-millimetre source seam.
- Bake differs from the sampled source surface by at most 0.605 mm.
- Source soles dip below zero by up to 12.251 mm in sampled poses. The demo
  applies measured phase-dependent vertical correction up to 12.751 mm,
  targeting 0.5 mm clearance. It does not lock feet horizontally or edit limbs.
- Neutral clay material added; source had no material slots. No textures needed.
- Godot imports at 60 fps with animation optimisation, mesh compression and
  generated LODs disabled.

## Evidence

- Repeat Blender build produced identical SHA256:
  ad2499a0e8409c6506fcafa82bfad285f3d1ffbeaccc74077e6f6003f009b8a5.
- Godot headless editor/import passed without error lines.
- Headless and rendered focused tests passed: [validation](validation.json).
  72 travel cases (3 rates x 3 views x 8 facings), 4 m in 2 seconds;
  half-tilt travel/cadence, held-pose release, pause, focus suppression,
  skeleton/material/stature, exact loop seam.
- 97 skinned surface samples: floor clearance 0.495-0.505 mm; maximum posed
  height 1.78223 m. This is not proof of horizontal locking during sharp turns.
- Three 48-frame/1.6-second captures and 24 facing poses generated.
  All six cycle/facing sheets visually inspected: complete character,
  working material, readable gait poses, no obvious explosive deformation.
- Joypad detected during rendered run. Physical controller operation and
  owner feel approval remain unverified.
- [Preview manifest](preview_manifest.json): GIF frame counts/durations verified.
- Original Prototype 01 checkout and source downloads were not edited.

## Failed approaches and limits

Initial FBX imports matched skeleton rest matrices but showed greater
between-frame sole penetration (16.102 mm). A quaternion-sign hypothesis
produced zero corrections and was not the cause. The FBX route was abandoned
in favour of evaluated native Blender source.

The publisher's source reports dependency cycles in hand controls.
The baked export has no constraints; sampled source preservation and repeat
export checks pass. The original authoring rig has not been repaired.

Setting quaternion mode after assigning matrix_basis caused a 0.615 mm bake
seam. Setting it before assignment and closing the last key resolved it.
Source polygon material indices without slots caused an export warning;
assigning the review material and resetting those indices removed it.

Sharp turns can pivot planted feet. Release may freeze a foot in the air.
Partial tilt slows this same clip. First review full-speed straight walking.
Retargeting, start/stop, turn polish, acceleration, jog/run, clothing and combat
remain outside this slice.
