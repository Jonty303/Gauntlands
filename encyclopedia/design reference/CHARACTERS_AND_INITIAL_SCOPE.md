# Characters and initial playable scope

**Status:** Approved design baseline — fixed first-playable roster and initial loadouts  
**Approved:** 8 November 2026  
**Remaining decisions:** Detailed combat actions are explicitly deferred.  
**Naming decision:** **Thief** confirmed as the canonical fifth-class name on 8 November 2026.

## Design intent

**Milestone boundary:** This document governs the future five-class first playable release, **not** the current Prototype 01 task. Prototype 01 remains restricted to one believable underwear-only human with a reusable Blender/rig/animation pipeline and eight-direction walking on a flat Godot plane. Approval of this roster does not authorise implementation of all five characters now.

The first playable version of Gauntlands uses **five fixed, recognisable poster characters**, one per class. Their appearance and starting equipment are predetermined. The intention is to minimise modelling, rigging, texturing and animation work while retaining a clear identity for each class.

## Initial character roster

The concept-art filenames in the current repository establish the class-to-character mapping below. Descriptions are design identifiers, not a promise of exact finished 3D models.

| Class | Initial character | Starting weapons | Existing concept reference |
| --- | --- | --- | --- |
| Champion | Female dwarf | Mace and shield | [Dwarf Champion](../concept%20art/02_Female_Dwarf_Champion.png) |
| Hunter | Young, outdoors-weathered human male | Longbow and longsword | [Male Hunter](../concept%20art/05_Human_Male_Hunter.png) |
| Thief | Female halfling | Shortsword and shortbow | [Halfling Thief](../concept%20art/04_Female_Halfling_Rogue.png) |
| Evoker | Female elf | Staff | [Elf Evoker](../concept%20art/01_Female_Elf_Evoker.png) |
| Priest | Older / mature human male | Staff | [Human Priest](../concept%20art/03_Middle_Aged_Human_Male_Priest.png) |

**Hunter revision:** The **male** human Hunter is the current intended poster/playable character. The earlier `05_Female_Human_Hunter.png` remains in the concept-art library as an earlier concept; it should not be used as the initial Hunter reference.

**Class terminology — resolved 8 November 2026:** **Thief** is the canonical fifth-class name. Earlier references used *Rogue*, and the legacy concept-art filename `04_Female_Halfling_Rogue.png` is retained for provenance and to keep the approved artwork link working. The asset filename does not determine the class name.

## Stage 01 visible equipment

| Class | Equipped / available | Combat expression |
| --- | --- | --- |
| Champion | One-handed mace + shield | Melee strikes and shield block |
| Hunter | Longbow + longsword | Ranged combat with melee fallback; switch between weapons |
| Thief | Shortbow + shortsword | Ranged combat with melee fallback; switch between weapons |
| Evoker | Staff | Spellcasting; precise initial actions to be defined |
| Priest | Staff | Spellcasting/support; precise initial actions to be defined |

Weapon overlap is intentional; abilities, timings, defensive tools and attack behaviour create class distinction.

## In scope for the future first playable release (not Prototype 01)

- Five fixed character appearances with the above loadouts.
- Shared foundational movement, targeting, hit reactions, death and interaction systems, where appropriate.
- Class-appropriate combat actions and powers, without a full weapon inventory.
- Hunter and Thief switching between their **fixed** melee and ranged weapons.
- Rigging and animation that accommodate different character sizes and body proportions.

## Deferred deliberately

- Custom character creation or selectable gender/race/appearance.
- Interchangeable armour, hairstyles, clothing, body parts and other cosmetic equipment.
- Broad weapon selection or free-form weapon swapping outside the specified fixed loadouts.
- Visible model changes for each equipment upgrade.
- Stage 02+ weapon families listed in [WEAPON_ROADMAP.md](WEAPON_ROADMAP.md).

Stats, levelling, powers, loot and progression may be designed or implemented independently; **loot does not imply a visible new weapon or armour model in Stage 01**.

## Technical considerations

Use a shared character-controller and combat contract instead of five unrelated controllers. Class-specific configuration should select weapons, animation sets, attack timing, allowed actions and powers.

The dwarf and halfling have notably different proportions from the human/elf characters. Test animation retargeting, hand grips, weapon placement, contact points and ground alignment early; do not assume a single raw humanoid animation fits all five models without adjustment.

A production-ready initial character should be recognisable from the approved poster reference, usable with its designated loadout, and capable of shared movement/combat actions without conspicuous clipping or incorrect weapon orientation. Final acceptance criteria require a later per-class specification.
