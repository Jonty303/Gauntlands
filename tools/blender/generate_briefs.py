"""Fitted boxer briefs v2 for the inspected MPFB Human / default rig.
Run in Blender with Human-Male.blend open. Never saves or changes source data.
Coordinates are measured in the rig's rest frame; fitting uses evaluated skin.
"""
import math
import bpy
import bmesh
from mathutils import Vector, Matrix
from mathutils.bvhtree import BVHTree
from mathutils.geometry import barycentric_transform

GARMENT_NAME = 'Gauntlands_Boxer_Briefs'
N = 64
BRIDGE_SEGMENTS = 12
GAP = 0.016  # In inspected rig units; scaled by hip separation below.


def source_surface():
    candidates = [o for o in bpy.context.scene.objects if o.type == 'MESH'
                  and 'body' in o.vertex_groups and o.data.shape_keys]
    if len(candidates) != 1:
        raise RuntimeError('Expected exactly one MPFB body with a body group and shape keys.')
    body = candidates[0]
    arms = [m for m in body.modifiers if m.type == 'ARMATURE' and m.object]
    if len(arms) != 1:
        raise RuntimeError('Expected one existing body armature.')
    arm = arms[0].object
    required = ['pelvis.L', 'pelvis.R', 'upperleg01.L', 'upperleg01.R',
                'upperleg02.L', 'upperleg02.R', 'spine04', 'spine05', 'head', 'foot.L']
    if any(n not in arm.data.bones for n in required):
        raise RuntimeError('Unsupported rig: expected MPFB default pelvis/spine/leg bones.')
    if any(sum(v*v for row in (p.matrix_basis - Matrix.Identity(4)) for v in row) > 1e-5
           for p in arm.pose.bones):
        raise RuntimeError('Generate in the neutral pose; pose the rig after generation.')
    # Evaluate a temporary object with shape keys and helper mask, but no deformation.
    # Original modifier visibility, pose, mesh and shape-key values remain untouched.
    temp = body.copy()
    bpy.context.scene.collection.objects.link(temp)
    try:
        for mod in list(temp.modifiers):
            if mod.type != 'MASK':
                temp.modifiers.remove(mod)
        bpy.context.view_layer.update()
        ev = temp.evaluated_get(bpy.context.evaluated_depsgraph_get())
        mesh = ev.to_mesh(preserve_all_data_layers=True, depsgraph=bpy.context.evaluated_depsgraph_get())
        transform = arm.matrix_world.inverted() @ body.matrix_world
        coords = [transform @ v.co for v in mesh.vertices]
        mesh.calc_loop_triangles()
        triangles = [tuple(t.vertices) for t in mesh.loop_triangles]
        deform = {g.index: g.name for g in body.vertex_groups
                  if g.name in arm.data.bones and arm.data.bones[g.name].use_deform}
        weights = [{deform[g.group]: g.weight for g in v.groups if g.group in deform}
                   for v in mesh.vertices]
        ev.to_mesh_clear()
    finally:
        bpy.data.objects.remove(temp, do_unlink=True)
    return body, arm, coords, triangles, weights, arms[0].use_deform_preserve_volume


def material(name, colour):
    m = bpy.data.materials.new(name)
    m.diffuse_color = (*colour, 1)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value = (*colour, 1)
    bsdf.inputs['Roughness'].default_value = .9
    return m


def topology_report(mesh):
    bm = bmesh.new(); bm.from_mesh(mesh)
    try:
        boundary = {e for e in bm.edges if e.is_boundary}
        loops = []
        while boundary:
            seed = boundary.pop(); edges = {seed}; todo = list(seed.verts)
            while todo:
                v = todo.pop()
                if sum(e.is_boundary for e in v.link_edges) != 2:
                    raise RuntimeError('Branching garment boundary')
                for e in v.link_edges:
                    if e in boundary:
                        boundary.remove(e); edges.add(e); todo.extend(e.verts)
            loops.append(len(edges))
        unseen = set(bm.verts); components = 0
        while unseen:
            components += 1; todo = [unseen.pop()]
            while todo:
                for e in todo.pop().link_edges:
                    for v in e.verts:
                        if v in unseen: unseen.remove(v); todo.append(v)
        return dict(vertices=len(bm.verts), faces=len(bm.faces),
                    triangles=sum(len(f.verts)-2 for f in bm.faces),
                    boundary_loops=sorted(loops), components=components,
                    bad_edges=sum(not(e.is_manifold or e.is_boundary) for e in bm.edges),
                    degenerate_faces=sum(f.calc_area() < 1e-10 for f in bm.faces))
    finally:
        bm.free()


def build_briefs():
    if bpy.context.mode != 'OBJECT':
        raise RuntimeError('Switch to Object Mode before running.')
    body, arm, skin, tris, weights, preserve = source_surface()
    bones = arm.data.bones
    left = bones['upperleg01.L'].head_local
    right = bones['upperleg01.R'].head_local
    origin = (left + right) / 2
    across = (left-right).normalized()
    up = (bones['head'].tail_local-origin).normalized()
    up = (up-across*up.dot(across)).normalized()
    forward = up.cross(across).normalized()
    toe = bones['foot.L'].tail_local-bones['foot.L'].head_local
    if forward.dot(toe) < 0: forward = -forward
    # Anatomical frame: x left, y posterior, z up. Confirm rather than guess axes.
    back = -forward
    frame = Matrix(((across.x,back.x,up.x,origin.x),
                    (across.y,back.y,up.y,origin.y),
                    (across.z,back.z,up.z,origin.z),(0,0,0,1)))
    inverse = frame.inverted()
    skin = [inverse @ v for v in skin]
    landmark = lambda name, end='head_local': inverse @ getattr(bones[name],end)
    scale = (left-right).length / .27784133
    gap = GAP*scale
    waist = landmark('spine04').z
    hem = landmark('upperleg02.L').z - .12*scale
    tree = BVHTree.FromPolygons(skin, tris, all_triangles=True)
    # Lowest centre skin hit gives perineum; no full-body height fractions.
    crotch_hit = tree.ray_cast(Vector((0,0,hem)), Vector((0,0,1)), 1*scale)[0]
    if crotch_hit is None: raise RuntimeError('Cannot locate closed skin crotch.')
    saddle = crotch_hit.z-gap
    split = saddle + .085*scale
    if not hem < saddle < split < waist:
        raise RuntimeError('Invalid anatomical garment landmarks.')
    vertices=[]; faces=[]; zones=[]
    def add(p): vertices.append(tuple(p)); return len(vertices)-1
    def face(indices, zone=0): faces.append(indices); zones.append(zone)
    def ring_fit(cx, cy, z, angle):
        d = Vector((math.sin(angle),-math.cos(angle),0))
        centre = Vector((cx,cy,z))
        # First exit from inside this torso/leg avoids hands and the opposite leg.
        hit = tree.ray_cast(centre, d, .6*scale)[0]
        if hit is None: raise RuntimeError('Skin fitting ray missed; unsupported body proportions.')
        return hit+d*gap
    rings=[]
    levels=[waist,waist-.008*scale,waist-.027*scale]
    levels += [levels[-1]+(split-levels[-1])*i/7 for i in range(1,8)]
    for z in levels:
        ring=[add(ring_fit(0,0,z,2*math.pi*j/N)) for j in range(N)]
        if rings:
            for j in range(N): face([rings[-1][j],rings[-1][(j+1)%N],ring[(j+1)%N],ring[j]],1 if len(rings)<=2 else 0)
        rings.append(ring)
    bottom=rings[-1]
    front=Vector(vertices[bottom[0]]); rear=Vector(vertices[bottom[N//2]])
    bridge=[bottom[0]]
    for j in range(1,BRIDGE_SEGMENTS):
        t=j/BRIDGE_SEGMENTS; p=front.lerp(rear,t)
        h=tree.ray_cast(Vector((0,p.y,hem)),Vector((0,0,1)),scale)[0]
        if h is None: raise RuntimeError('Crotch bridge skin sample missed.')
        p.z=min(split,h.z-1.5*gap)
        bridge.append(add(p))
    bridge.append(bottom[N//2])
    # Each leg owns half of the torso ring and one side of the shared sewn seam.
    top_loops=[bottom[:N//2+1]+list(reversed(bridge[1:-1])),
               bottom[N//2:]+[bottom[0]]+bridge[1:-1]]
    for side,top in zip(['L','R'],top_loops):
        hip=landmark('upperleg01.'+side)
        knee=landmark('upperleg02.'+side,'tail_local')
        starts=[Vector(vertices[i]) for i in top]
        angles=[math.atan2(p.x-hip.x,-(p.y-hip.y)) for p in starts]
        previous=top
        for row,t in enumerate([.15,.3,.45,.6,.75,.9,.96,1]):
            ring=[]
            for p,a in zip(starts,angles):
                z=p.z+(hem-p.z)*t
                factor=(hip.z-z)/(hip.z-knee.z)
                c=hip.lerp(knee,factor)
                fitted=ring_fit(c.x,c.y,z,a)
                # Ease from the sewn saddle into fitted leg tubes.
                q=p.lerp(fitted,min(1,t*4)); q.z=z
                # At the rear saddle the skin is still a single volume. An inner
                # ray can cross the midline; each tube must stay on its own side.
                sign=1 if side=='L' else -1
                q.x=sign*max(sign*q.x,.025*scale*t)
                ring.append(add(q))
            for j in range(len(top)):
                k=(j+1)%len(top); face([previous[j],previous[k],ring[k],ring[j]],1 if row>=6 else 0)
            previous=ring
    mesh=bpy.data.meshes.new(GARMENT_NAME+'_Mesh')
    mesh.from_pydata(vertices,[],faces); mesh.update()
    bm=bmesh.new(); bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm,faces=list(bm.faces)); bm.to_mesh(mesh); bm.free()
    report=topology_report(mesh)
    if report['components'] != 1 or len(report['boundary_loops']) != 3 or report['bad_edges'] or report['degenerate_faces'] or report['triangles']>5000:
        bpy.data.meshes.remove(mesh); raise RuntimeError(f'Invalid garment topology: {report}')
    obj=bpy.data.objects.new(GARMENT_NAME,mesh)
    bpy.context.scene.collection.objects.link(obj)
    obj.matrix_world=arm.matrix_world @ frame
    # Blender suffixes preserve earlier generated or hand-edited garments on rerun.
    obj.parent=arm; obj.matrix_world=arm.matrix_world @ frame
    for name in {n for w in weights for n in w}: obj.vertex_groups.new(name=name)
    for v in mesh.vertices:
        hit,normal,idx,distance=tree.find_nearest(v.co)
        ids=tris[idx]; a,b,c=[skin[i] for i in ids]
        bary=barycentric_transform(hit,a,b,c,Vector((1,0,0)),Vector((0,1,0)),Vector((0,0,1)))
        result={}
        for source,amount in zip(ids,bary):
            for name,w in weights[source].items(): result[name]=result.get(name,0)+max(0,amount)*w
        total=sum(result.values())
        if total<1e-8: raise RuntimeError('Unweighted source skin point.')
        for name,w in result.items():
            if w>0: obj.vertex_groups[name].add([v.index],w/total,'REPLACE')
    # Smooth transferred weights below the waistband. Nearest skin triangles
    # can switch abruptly between thighs even though the cloth is continuous.
    neighbours=[set() for _ in mesh.vertices]
    for e in mesh.edges:
        a,b=e.vertices; neighbours[a].add(b); neighbours[b].add(a)
    for _ in range(6):
        current=[{g.group:g.weight for g in v.groups} for v in mesh.vertices]
        for v in mesh.vertices:
            if v.co.z > waist-.03*scale:
                continue
            adjacent=neighbours[v.index]
            names=set(current[v.index])
            for j in adjacent: names.update(current[j])
            for group in names:
                w=.5*current[v.index].get(group,0)+.5*sum(current[j].get(group,0) for j in adjacent)/len(adjacent)
                obj.vertex_groups[group].add([v.index],w,'REPLACE')
    mesh.materials.append(material('GNT_Briefs_Charcoal',(.12,.14,.17)))
    mesh.materials.append(material('GNT_Briefs_Trim',(.045,.055,.07)))
    for p,z in zip(mesh.polygons,zones): p.material_index=z; p.use_smooth=True
    bpy.ops.object.select_all(action='DESELECT'); obj.select_set(True)
    bpy.context.view_layer.objects.active=obj
    # Non-overlapping packed UV islands; explicit editable UV data, not generated coords.
    bpy.ops.object.mode_set(mode='EDIT'); bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.uv.smart_project(angle_limit=math.radians(66),island_margin=.02)
    bpy.ops.object.mode_set(mode='OBJECT')
    mod=obj.modifiers.new('Follow Human Rig','ARMATURE'); mod.object=arm
    mod.use_deform_preserve_volume=preserve
    mod=obj.modifiers.new('Soften Cloth Folds','SMOOTH'); mod.factor=.7; mod.iterations=4
    mod=obj.modifiers.new('Fabric Thickness','SOLIDIFY'); mod.thickness=.0015*scale; mod.offset=1
    obj['gauntlands_generator']='generate_briefs.py v2'
    obj['gauntlands_source_mesh']=body.name
    obj['gauntlands_landmarks']=dict(waist=waist,hem=hem,crotch=saddle,split=split)
    print('BRIEFS_V2',report,'landmarks',dict(waist=waist,hem=hem,crotch=saddle), 'object',obj.name)
    return obj

if __name__=='__main__': build_briefs()
