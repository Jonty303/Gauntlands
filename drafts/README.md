# Gauntlands — design drafts

**Status:** Working design notes, not an implementation contract  
**Discussion date:** 7 November 2026  
**Branch:** `main`

These documents capture the initial playable character/weapon scope, subsequent weapon expansion ideas, and the production principle of reusing systems and assets where possible. They are deliberately stored in `drafts/` until reviewed and incorporated into authoritative design documents.

## Contents

| Document | Purpose |
| --- | --- |
| [CHARACTERS_AND_INITIAL_SCOPE.md](CHARACTERS_AND_INITIAL_SCOPE.md) | Five approved poster-character archetypes, fixed starting loadouts, prototype boundaries and deferred features |
| [WEAPON_ROADMAP.md](WEAPON_ROADMAP.md) | Stage 01 starting weapons; Stage 02 weapon families; tentative later additions and shared weapon taxonomy |
| [ANIMATION_AND_REUSE.md](ANIMATION_AND_REUSE.md) | Animation-family reuse, class differentiation, data-driven architecture and production-efficiency guidelines |

## Decision status

- **Agreed initial scope:** Five classes, represented by five existing poster-character concepts, with fixed initial loadouts and no character-customisation or visually interchangeable equipment system in the first playable prototype.
- **Agreed development direction:** Stage 02 extends existing class identities with two-handed, dual-wield, wand and thrown-knife options. This is a roadmap, **not** Stage 01 scope.
- **Ideas under consideration:** Rapier for Rogue, axe and throwing axe for Hunter, and throwing axe for Champion. Do not treat as committed features.
- **Cross-cutting principle:** **Reuse wherever possible; specialise where it matters.** Shared assets/systems should pull double duty without making the classes play identically.

## Intent and constraints

1. Build a focused, polished first playable experience before adding a broad equipment catalogue or character creator.
2. Separate **weapon families**, **animation sets**, **class abilities** and **individual weapon definitions** to support later expansion.
3. Allow gameplay systems such as statistics, level progression, damage, loot and powers to exist without requiring every upgrade to change the visible character model.
4. Keep future-roadmap decisions outside first-iteration acceptance criteria.
5. Refer to the existing files in [the concept-art library](../encyclopedia/concept%20art/) for visual direction. Art in that folder is reference material, not proof of production-ready models, rigs or animations.

## Open decisions

- Confirm whether the final fifth-class display name is **Rogue** (used throughout this discussion); earlier project discussions sometimes used **Thief**.
- Define the exact Stage 01 actions and attack chains per class in a dedicated combat specification.
- Confirm how staff attacks work (casting only, physical strikes, or both) and which class powers require unique animations.
- Confirm the exact two-handed weapon(s) and dual-wield combinations when Stage 02 is scheduled.
- Define equipment progression and visual changes only when those systems enter scope.

These are drafts intended to guide the next design pass, not permission to expand Iteration 01.
