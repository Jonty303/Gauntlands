# Gauntlands — Godot 4 coding standards

**Status:** Approved coding policy · **Recorded:** 11 November 2026  
**Applies to:** New and materially modified production GDScript in `Jonty303/Gauntlands`. Existing prototype code may be migrated incrementally.

This document defines coding conventions. It does **not** authorise gameplay implementation, additional branches, changes to the first-human prototype scope, or a merge. Follow the root `AGENTS.md` and the project-specific agent operating model first.

## Language and engine

- Target the repository's documented **Godot 4.5.2 stable** baseline until it is explicitly revised.
- Use Godot 4 GDScript syntax and annotations such as `@export`, `@export_range`, `@onready`, `@tool` where appropriate. Do not introduce Godot 3 `export`/`onready` syntax.
- Prefer native Godot scenes, nodes, typed Resources and signals. Do not add an ECS framework or another architectural dependency without an approved design decision.

## Static typing policy

**Use static typing by default.** For production GDScript:

1. Type all function parameters and return values, including `-> void`.
2. Type member variables, exported properties, node references and signal parameters; `:=` is acceptable when the inferred type is stable and unambiguous.
3. Use typed arrays (`Array[WeaponDefinition]`, for example) where supported and appropriate. Godot's type system has limitations; do not invent nested generics or unsupported type constructs.
4. Prefer typed data objects/Resources over dictionaries with undocumented keys when data crosses gameplay-system boundaries.
5. Restrict `Variant`, untyped `Dictionary`, unsafe casts and `Object`-typed values to genuine dynamic/API boundaries. Document why they are needed; validate inputs and narrow types at the boundary.
6. Do not suppress warnings or use `@warning_ignore` simply to hide a defect. Explain and scope any necessary suppression.
7. Never claim “strict” means Godot can statically prove every property or dynamic scene path; use runtime assertions/validation where type checking cannot help.

Example:

```gdscript
extends Node
class_name HealthComponent

signal health_changed(current_health: int)
signal died

@export_range(1, 500) var max_health: int = 100
var current_health: int

func _ready() -> void:
    current_health = max_health

func take_damage(amount: int) -> void:
    if amount <= 0 or current_health <= 0:
        return
    current_health = maxi(0, current_health - amount)
    health_changed.emit(current_health)
    if current_health == 0:
        died.emit()
```

## Component and scene boundaries

- Prefer composition over deep inheritance. Each reusable component should have one coherent responsibility and a small typed public interface.
- **Call down, signal up** is a default heuristic within a scene: parents invoke children; children report outcomes through typed signals. It is not an absolute prohibition on direct calls between cooperating objects.
- Prefer explicit commands for requested actions and signals for events that have already occurred. Avoid hidden dependencies, sibling path traversal, and indiscriminate global event buses.
- Keep gameplay rules/state distinct from input mapping, animation, VFX, UI and mesh/rig implementation. Prefer data definitions separate from mutable runtime state.
- Design only the abstractions needed for the approved playable slice; do not build a general-purpose RPG framework speculatively.

## Validation and enforcement

When a Godot project and executable toolchain exist:

1. Enable and review applicable GDScript warnings, particularly unsafe method access, unsafe property access, unsafe casts and untyped declarations. Prefer warnings-as-errors **after** establishing a clean baseline and reviewing intentional exceptions.
2. Run Godot's headless editor import/parse check using the pinned build and the actual project path; add deterministic tests for core gameplay rules where feasible.
3. Inspect the diff for untyped public APIs, unvalidated dynamic values, stale scene paths, unsupported annotations and unnecessary warning suppression.
4. Record exact commands, version, pass/fail/not-run results and limitations. Headless parsing does not validate animation, rendering, controller feel or playability.
5. Do not edit `project.godot` or claim enforcement is active until such a file exists and the configuration has been tested.

## Agent implementation checklist

Before coding: read `AGENTS.md`, this document, approved design references and the relevant scene/API contracts; confirm the repository and authorised branch; identify acceptance criteria and tests.

During coding: make the smallest coherent change; retain typed interfaces; use supported Godot 4 annotations; keep runtime state and visual presentation separated; avoid unapproved system expansion.

Before hand-off: review types and warnings; run available checks; report exact files changed and commands executed; distinguish verified results from not-run tests. Do not merge without approval.

## Evolution

These are **Gauntlands-specific** standards. They may be used as a candidate for a future cross-game agent template, but do not silently apply Gauntlands' classes, assets, prototype branch rules or design choices to another project.
