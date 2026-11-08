# Gauntlands — approved design references

**Status:** Index of design decisions approved on 8 November 2026.  
**Repository:** `Jonty303/Gauntlands` · **Branch:** `main`

This folder holds approved design baselines and existing controller references. **Approved** means the explicitly agreed scope or principle is authoritative; it does **not** mean all detailed mechanics, implementation contracts or later-stage proposals are settled.

## Newly approved baselines

| Document | Approved scope | Deliberately unresolved |
| --- | --- | --- |
| [Characters and initial scope](CHARACTERS_AND_INITIAL_SCOPE.md) | Five poster characters and fixed first-playable loadouts, deferred equipment customisation | Rogue vs Thief final display name; exact class attack moves |
| [Weapon roadmap](WEAPON_ROADMAP.md) | Stage 01 fixed loadouts; Stage 02 planned weapon-family direction, not scheduled | Exact Stage 02 two-handed/dual-wield choices; later weapons tentative |
| [Animation and reuse](ANIMATION_AND_REUSE.md) | Reuse wherever possible, specialise where necessary; animation-family and shared-system principles | Exact rig/retargeting specification, clip list, performance targets and runtime architecture |

## Existing controller reference

- [Xbox controller mapping](xbox-controller-controls.md), including tap and possible hold actions; hold assignments and several detailed targeting behaviours remain provisional.
- [Xbox controller diagram](xbox-controller-control-map.svg).

## Approval boundary and next decisions

The **current human Prototype 01** is only an underwear-clad believable human model, reusable Blender generation/rig/animation pipeline, and eight-direction walking on a single flat Godot plane. The **five-class first playable release** is a later milestone. Approving these references does not bypass the prototype scope or Git branch safeguards.

Open items remain open, not implicitly approved:

1. Confirm whether the player-facing fifth class is **Rogue** or **Thief** (Rogue retained as working terminology).
2. Before class-combat implementation: specify exact Stage 01 attacks, combos and power actions for each class.
3. Before staff combat: decide whether Evoker/Priest use physical staff strikes, casting, or both; identify genuinely shared versus unique animations.
4. At Stage 02 planning: pick Champion two-handed weapon(s) and Hunter/Rogue dual-wield combinations.
5. Before implementing visible progression: specify equipment-upgrade appearance rules and their scope.

**Approval authority:** The project owner approved the three existing design documents as a baseline in the 8 November 2026 conversation. Their internal proposals remain conditional unless explicitly identified as agreed. Any subsequent design changes require versioned review.

Technical workflow, agent ownership and configuration belong in [development](../../development/); the original [drafts index](../../drafts/README.md) retains provenance.
