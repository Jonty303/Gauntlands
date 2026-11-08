# Class weapons — staged roadmap

**Status:** Approved staged roadmap — Stage 01 fixed, Stage 02 direction agreed but unscheduled, later options provisional  
**Approved:** 8 November 2026  
**Scope gate:** Roadmap approval does not authorise development of Stage 02 or later weapons, nor expand the underwear-only human Prototype 01.

## Stage matrix

| Class | Stage 01 — fixed initial loadout | Stage 02 — planned expansion | Later — under consideration |
| --- | --- | --- | --- |
| Champion | Mace + shield | Two-handed weapons | Throwing axe |
| Hunter | Longbow + longsword | Dual wield; throwing knives | One-handed axe; throwing axes |
| Rogue | Shortsword + shortbow | Dual wield; throwing knives | Rapier |
| Evoker | Staff | Wand | Not specified |
| Priest | Staff | Wand | Not specified |

**Important:** Later entries are options, not commitments. Stage 02 is a sequenced development goal, **not** an instruction to include those weapons in the initial playable build.

## Stage 01 — deliberate restriction

The fixed starting weapons reduce distinct models, grip poses, animation sets, inventory UI and equipment rules that must be finished before combat can be evaluated.

- **Champion:** One-handed crushing weapon plus shield, including a distinct block reaction.
- **Hunter:** Bow and one-handed sword, with an explicit fixed-loadout melee/ranged switch.
- **Rogue:** Shortbow and shortsword, with the same switch framework as Hunter.
- **Evoker and Priest:** Staff-based presentation and casting mechanics, reusing core staff/casting foundations while their powers express distinct roles.

No open-ended weapon selection, armour swaps or visible equipment upgrade catalogue in Stage 01.

## Stage 02 — next weapon-development pass

### Champion: two-handed weapons

A separate two-handed grip and attack family, with wider arcs, more obvious anticipation and longer recovery. Reuse fundamental movement, targeting, damage, hit reaction and timing infrastructure; introduce weapon-specific two-handed animation where needed. The exact first two-handed weapon is unselected.

### Hunter and Rogue: dual wield

Both classes gain access to paired one-handed weapons. Share the base dual-wield animation family, alternating-strike logic and equipment attachment system. Different powers, cadence, movement and recovery can distinguish Hunter and Rogue. Exact weapon pairings remain to be chosen.

### Evoker and Priest: wands

Share one-handed wand-casting foundations and existing spell/projectile plumbing. Wand mechanics should offer meaningful distinctions from staff use, but faster or more mobile casting is **a design possibility**, not yet a fixed rule.

### Hunter and Rogue: throwing knives

Share throw/release animations, inventory/ammunition abstractions (if necessary), targeting and projectile collision rules. Knife throwing should retain its own release/flight presentation rather than inheriting a bow draw. Range, ammunition and damage balance are unconfirmed.

## Later ideas — not scheduled

- **Rogue rapier:** A precision/thrust-focused option with lunges and a narrow attack profile; likely needs specialised thrust animations while sharing one-handed locomotion.
- **Hunter one-handed axe:** Chop-focused melee option that should reuse a substantial part of the mace/one-handed attack foundation.
- **Hunter throwing axe:** A thrown-weapon alternative using the throwing-knife projectile system with different model, release, flight rotation and impact effects.
- **Champion throwing axe:** A possible limited ranged option for a primarily melee class; behaviour and restrictions remain to be defined.

## Weapon families (production taxonomy)

| Family | Examples | Shared foundations | Important differences |
| --- | --- | --- | --- |
| One-handed melee | Mace, longsword, shortsword, axe | Grip system, locomotion, attack state machine, hit checks | Crushing vs cutting feel, swing arcs, impact timing |
| Thrust-focused one-handed | Rapier | One-handed locomotion and attack framework | Lunges, point alignment, thrust hit detection |
| Two-handed melee | Future Champion weapon | Movement, targeting, impact logic | Two-hand grip, pose, reach, recovery |
| Bows | Longbow, shortbow | Draw, aim, release and arrow projectile logic | Bow geometry, animation scaling, speed |
| Staff / casting | Evoker and Priest staffs | Staff grip, casting triggers, spell VFX hooks | Powers and class-specific delivery |
| Wand casting | Future wands | Spell framework, one-handed cast | Wand pose, presentation, potential handling difference |
| Thrown weapons | Throwing knives and axes | Targeting, spawning, collision, hit resolution | Release pose, speed, flight, spin, impact |
| Dual wield | Future Hunter/Rogue pairs | Equipment slots, combo framework, alternating attacks | Class cadence, combos and individual weapon geometry |

This table describes opportunities for reuse, not proof that all listed moves can use identical clips. For instance, mace strikes and sword cuts can share a controller and common poses without looking physically convincing when played as the exact same animation.

## Data-oriented weapon definition (proposed)

Define equipment data separately from class code. Candidate fields:

- `weapon_id`, `weapon_family`, `animation_set`
- `grip` (one-handed, shield pairing, two-handed, dual, casting)
- `attack_mode` (melee, bow projectile, thrown projectile, spell)
- `reach` / effective range, attack speed, wind-up and recovery
- Allowed classes and available weapon stances
- Associated powers and VFX/SFX identifiers

Avoid hard-coding each class/weapon combination into a bespoke controller. This is an architectural guideline; the final data schema belongs in a later technical specification.

## Roadmap guardrails

1. Ship and polish Stage 01 combat before implementing Stage 02 weapon models and animation libraries.
2. When expanding, reuse existing movement/combat/projectile mechanisms first.
3. Add specialisation only where it changes readability, class identity or gameplay.
4. Treat proposed balance characteristics as design questions until tested, not as locked numerical rules.
