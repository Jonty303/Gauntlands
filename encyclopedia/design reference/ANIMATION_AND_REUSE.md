# Animation, systems reuse and production efficiency

**Status:** Approved production and reuse principles — proposed implementation architecture remains to be specified and tested  
**Approved:** 8 November 2026  
**Scope gate:** These principles guide future work but do not expand the single-human Prototype 01 or authorise Stage 02 development.

## Guiding rule

> **Reuse wherever possible; specialise where it matters.**

Before creating a new asset, animation or subsystem, check whether an existing one can fulfil most of the need. This is a production discipline, **not** a rule to sacrifice clarity, character identity or quality.

The aim is to build assets and systems that **pull double duty** across classes, weapons, enemies and environments.

## Layers of reuse

1. **Shared systems:** Controller, locomotion, targeting, lock-on/aim logic, collision, hit resolution, damage, reactions, death, projectiles, equipment attachments and interactables.
2. **Shared animation families:** Compatible grips, wind-ups, strikes, block/recovery, bow draw/release and casting sequences.
3. **Class-specific configuration:** Timing, speed, reach, movement restrictions, defensive behaviour, available attacks and powers.
4. **Distinct presentation when valuable:** Hero silhouettes, signatures, VFX/SFX, weapon-specific impact and unique ability animations.

Reuse does not mean identical gameplay. A Hunter and Rogue may use the same foundational bow set, yet feel different through their powers, cadence and movement. Do not assume a fixed percentage of animation reuse without testing.

## Stage 01 animation scope

Prioritise three **primary weapon animation families**, with class-specific extensions:

| Family | Users | Shared moves / systems | Exceptions and refinements |
| --- | --- | --- | --- |
| One-handed melee | Champion, Hunter, Rogue | Locomotion integration, anticipation, attack, impact, recovery | Mace/sword silhouette and contact pose adjustments; Champion shield block |
| Archery | Hunter, Rogue | Equip/switch, draw, aim, release, recovery | Longbow/shortbow hand placement, draw length and cadence |
| Staff/casting | Evoker, Priest | Staff grip, casting start/hold/release, spell hooks | Class-specific spells, effects and signature gestures |

Also provide suitable foundational locomotion, idle, turn, flinch/hit, death and interaction states for every playable character. The precise animation list and counts are not yet fixed.

## Stage 02 additions

| Animation family | Users | Reuse objective |
| --- | --- | --- |
| Two-handed melee | Champion | Reuse combat state machine, anticipation/hit/recovery logic; build correct new two-handed clips |
| Dual wield | Hunter, Rogue | One shared alternating/combo foundation, varied per class |
| Wand casting | Evoker, Priest | Build on existing spell framework with one-handed casting |
| Throwing knives | Hunter, Rogue | Reuse targeting and projectile collision; add a distinct throw animation |

## Later proposals

- **Rapier:** Prefer a distinct thrust/lunge attack set, reused locomotion and combat plumbing.
- **One-handed axe:** Reuse existing one-handed/mace foundations; tune swing arcs and impact.
- **Throwing axes:** Reuse thrown-weapon targeting/projectiles with suitable throwing pose, spin and hit VFX.

## Five poster characters and rig compatibility

The planned character set consists of a female dwarf Champion, young human male Hunter, female halfling Rogue, female elf Evoker and older/mature human male Priest. Consult [CHARACTERS_AND_INITIAL_SCOPE.md](CHARACTERS_AND_INITIAL_SCOPE.md) for current artwork links.

A common rig specification and animation contract are desirable, but **shorter-limbed dwarf and halfling bodies may require retargeting, animation variants, IK or hand-contact adjustments**. Verify weapon grip and ground contact rather than assuming every humanoid clip is transferable as-is.

## Architecture direction

Prefer a shared character controller with data-selected class, equipment/stance and animation resources. A possible decomposition:

- **Character controller:** movement, targeting, state transitions, shared reactions.
- **Weapon definition:** family, grip, timing, range, animation mapping and allowed attacks.
- **Animation layer:** common locomotion with family-specific actions and compatible overrides.
- **Combat resolver:** hit detection, damage/miss/glancing logic and effects independent of model.
- **Class/power definition:** distinctive actions, modifiers and power effects that layer on top.

Do not implement these as five unrelated controllers. Similarly, do not merge all moves into a single universal animation clip where weapon weight, hand placement or motion becomes implausible.

## Wider asset reuse opportunities

The same design principle extends beyond weapons:

- **Environment kits:** Share modular walls, doors, floors, structural pieces and props between compatible dungeon rooms, crypts and buildings; specialise dressing and materials.
- **Settlements:** Cottages, the inn and the blacksmith may share structural modules while keeping distinctive interactables and props.
- **Enemies:** Compatible humanoid enemies may reuse a rig/controller/locomotion foundation, with adjusted combat behaviour and animation.
- **Traps and interactions:** Shared trigger, event, damage and state systems can power different visible traps, switches, plates and doors.

These are reuse examples, **not additional scope commitments** in this particular weapon/character discussion.

## Acceptance principles for future iteration plans

A future iteration should only claim asset reuse when it has been validated in-engine:

- Weapon orientation and both-hand grips appear correct.
- Hit frames, collision and contact line up with the visible strike or projectile release.
- Shared animations remain believable on the dwarf and halfling as well as human/elf rigs.
- Each class remains visually and mechanically identifiable despite shared foundations.
- Class-specific overrides do not fork or duplicate the main controller unnecessarily.
- Stage 01 only includes its fixed loadouts; Stage 02+ must be explicitly scheduled.

**Production test:** If a new feature needs an entirely new model, clip family and special-case controller, check whether its contribution justifies the cost before approving it.
