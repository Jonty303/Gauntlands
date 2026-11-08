"""Gauntlands Prototype 01: non-destructive, fitted boxer-brief first pass.

Run from Blender's Scripting workspace with the human file open.
Source: the MPFB body mesh and its existing deform weights. The source mesh
is never changed; the generated garment is a separate object.

Target: Blender 5.2.3 LTS / MPFB 2.0.18 (reported, not yet validated here).
The script intentionally does not save the .blend or write files.
"""

import bpy
from collections import defaultdict, deque
from statistics import median


# Ratios are relative to the body's full standing height (feet -> head).
WAIST_HEIGHT = 0.585
LEG_HEM_HEIGHT = 0.425
MAX_SIDE_REACH = 0.195
MAX_FRONT_BACK_REACH = 0.165
SURFACE_GAP = 0.0055   # Approx. 9–10 mm at normal adult height.
FABRIC_THICKNESS = 0.0015
WAISTBAND_DEPTH = 0.018
HEM_BAND_DEPTH = 0.012

GARMENT_NAME = "Gauntlands_Boxer_Briefs"
EXCLUDED_BONE_TERMS = (
    "arm", "wrist", "hand", "finger", "thumb", "shoulder", "clavicle"
)


def find_body_mesh():
    """Prefer the selected, dense body mesh; otherwise largest dense mesh."""
    candidates = [obj for obj in bpy.context.scene.objects
                  if obj.type == 'MESH'
                  and obj.name != GARMENT_NAME
                  and len(obj.data.polygons) >= 400]
    if not candidates:
        raise RuntimeError("No substantial body mesh found in this Blender scene.")
    active = bpy.context.view_layer.objects.active
    if active in candidates:
        return active
    return max(candidates, key=lambda ob: len(ob.data.polygons))


def candidate_faces(body, height, z_min, centre_x, centre_y):
    mesh = body.data
    low = z_min + LEG_HEM_HEIGHT * height
    high = z_min + WAIST_HEIGHT * height
    x_limit = MAX_SIDE_REACH * height
    y_limit = MAX_FRONT_BACK_REACH * height
    excluded_group_ids = {
        group.index for group in body.vertex_groups
        if any(term in group.name.lower() for term in EXCLUDED_BONE_TERMS)
    }

    def arm_influence(index):
        return sum(assignment.weight
                   for assignment in mesh.vertices[index].groups
                   if assignment.group in excluded_group_ids)

    matches = []
    for face in mesh.polygons:
        coords = [mesh.vertices[index].co for index in face.vertices]
        n = len(coords)
        mx = sum(v.x for v in coords) / n
        my = sum(v.y for v in coords) / n
        mz = sum(v.z for v in coords) / n
        if not (low <= mz <= high
                and abs(mx - centre_x) <= x_limit
                and abs(my - centre_y) <= y_limit):
            continue
        # Avoid copying forearms/hands near the upper-hip region.
        if excluded_group_ids and (sum(arm_influence(i) > 0.40
                                       for i in face.vertices) >= (n + 1) // 2):
            continue
        matches.append(face)
    return matches


def largest_connected_patch(faces):
    """Keep the main pelvis/upper-leg surface; discard isolated hand patches."""
    edge_faces = defaultdict(list)
    by_id = {face.index: face for face in faces}
    for face in faces:
        indices = list(face.vertices)
        for i, vertex in enumerate(indices):
            edge = tuple(sorted((vertex, indices[(i + 1) % len(indices)])))
            edge_faces[edge].append(face.index)
    neighbours = defaultdict(set)
    for attached in edge_faces.values():
        for i in attached:
            neighbours[i].update(j for j in attached if j != i)

    unseen = set(by_id)
    components = []
    while unseen:
        root = unseen.pop()
        queue = deque([root])
        component = {root}
        while queue:
            face_id = queue.popleft()
            for adjacent in neighbours[face_id] & unseen:
                unseen.remove(adjacent)
                component.add(adjacent)
                queue.append(adjacent)
        components.append(component)
    if not components:
        raise RuntimeError("No briefs surface was found. Check body selection and ratios.")
    best = max(components, key=lambda group: sum(by_id[i].area for i in group))
    return [by_id[i] for i in sorted(best)]


def make_material(name, rgb, roughness=0.93):
    material = bpy.data.materials.get(name)
    if material is None:
        material = bpy.data.materials.new(name)
    material.diffuse_color = (*rgb, 1.0)
    material.use_nodes = True
    node = material.node_tree.nodes.get("Principled BSDF")
    if node:
        node.inputs['Base Color'].default_value = (*rgb, 1.0)
        node.inputs['Roughness'].default_value = roughness
        node.inputs['Metallic'].default_value = 0.0
    return material


def build_briefs():
    if bpy.context.mode != 'OBJECT':
        bpy.ops.object.mode_set(mode='OBJECT')
    if bpy.data.objects.get(GARMENT_NAME):
        raise RuntimeError(
            f"{GARMENT_NAME} already exists. Inspect or rename/remove it "
            "before re-running; this script never silently replaces work."
        )

    body = find_body_mesh()
    mesh = body.data
    if any(abs(angle) > 0.001 for angle in body.rotation_euler):
        raise RuntimeError("Body object is rotated. Apply/clear rotation in a copy first.")
    xs = [v.co.x for v in mesh.vertices]
    ys = [v.co.y for v in mesh.vertices]
    zs = [v.co.z for v in mesh.vertices]
    z_min = min(zs)
    height = max(zs) - z_min
    if height < 0.5:
        raise RuntimeError("Human mesh appears too short or in unexpected units.")

    # Prefer median hip-slice position over overall bounding-box centre, because
    # a face/nose or very asymmetric accessories can shift the global bounds.
    hip_points = [v.co for v in mesh.vertices
                  if z_min + 0.47*height <= v.co.z <= z_min + 0.60*height]
    if len(hip_points) < 100:
        raise RuntimeError("Cannot identify pelvis region in the selected mesh.")
    centre_x = median(v.x for v in hip_points)
    centre_y = median(v.y for v in hip_points)

    selected = largest_connected_patch(candidate_faces(
        body, height, z_min, centre_x, centre_y
    ))
    if len(selected) < 160:
        raise RuntimeError(
            f"Only {len(selected)} suitable polygons found. Select the main body "
            "mesh (not the eyes or clothing) and check the geometry before retrying."
        )

    old_indices = sorted({index for face in selected for index in face.vertices})
    new_index = {old: i for i, old in enumerate(old_indices)}
    offset = SURFACE_GAP * height
    new_vertices = [tuple(mesh.vertices[i].co + mesh.vertices[i].normal * offset)
                    for i in old_indices]
    new_faces = [[new_index[i] for i in face.vertices] for face in selected]
    cloth_mesh = bpy.data.meshes.new(GARMENT_NAME + "_Mesh")
    cloth_mesh.from_pydata(new_vertices, [], new_faces)
    cloth_mesh.update()
    briefs = bpy.data.objects.new(GARMENT_NAME, cloth_mesh)
    bpy.context.scene.collection.objects.link(briefs)

    briefs.parent = body.parent
    if body.parent:
        briefs.matrix_parent_inverse = body.matrix_parent_inverse.copy()
    briefs.matrix_world = body.matrix_world.copy()
    briefs.show_in_front = False

    # Copy deform weights for exactly the vertices that were taken from the body.
    groups = {}
    for group in body.vertex_groups:
        groups[group.index] = briefs.vertex_groups.new(name=group.name)
    for old, new in new_index.items():
        for assigned in mesh.vertices[old].groups:
            if assigned.group in groups:
                groups[assigned.group].add([new], assigned.weight, 'REPLACE')

    fabric = make_material("GNT_Briefs_Charcoal", (0.105, 0.116, 0.13))
    binding = make_material("GNT_Briefs_Trim", (0.05, 0.057, 0.065))
    cloth_mesh.materials.append(fabric)
    cloth_mesh.materials.append(binding)
    for polygon, src in zip(cloth_mesh.polygons, selected):
        mz = sum(mesh.vertices[i].co.z for i in src.vertices) / len(src.vertices)
        top = z_min + WAIST_HEIGHT*height - WAISTBAND_DEPTH*height
        bottom = z_min + LEG_HEM_HEIGHT*height + HEM_BAND_DEPTH*height
        polygon.material_index = 1 if mz > top or mz < bottom else 0
        polygon.use_smooth = True

    armatures = [modifier for modifier in body.modifiers if modifier.type == 'ARMATURE']
    if armatures:
        for source_modifier in armatures:
            modifier = briefs.modifiers.new("Follow Human Rig", 'ARMATURE')
            modifier.object = source_modifier.object
            modifier.use_deform_preserve_volume = source_modifier.use_deform_preserve_volume
    else:
        print("WARNING: Source mesh has no Armature modifier. The briefs will not "
              "follow a rig until that is added and checked.")

    thickness = briefs.modifiers.new("Fabric Thickness", 'SOLIDIFY')
    thickness.thickness = FABRIC_THICKNESS * height
    thickness.offset = 1.0
    thickness.use_rim = True

    briefs['gauntlands_source_mesh'] = body.name
    briefs['gauntlands_prototype'] = 'human-prototype-01'
    briefs['gauntlands_generator'] = 'generate_briefs.py v0.1'
    briefs['gauntlands_note'] = 'First-pass garment: inspect crotch, seams and pose clipping.'

    bpy.ops.object.select_all(action='DESELECT')
    briefs.select_set(True)
    bpy.context.view_layer.objects.active = briefs
    print(f"Created {GARMENT_NAME} from {body.name}: "
          f"{len(new_vertices)} vertices, {len(new_faces)} faces.")
    print("Check front/back/side and a raised-knee pose. No .blend file was saved.")
    return briefs


if __name__ == '__main__':
    build_briefs()
