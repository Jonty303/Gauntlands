"""Run with Blender --background --factory-startup SOURCE --python-exit-code 1
--python tools/blender/test_briefs.py. Writes previews/report and a separate test
copy under tools/blender/previews; never overwrites the loaded source file.
"""
import hashlib
import json
import math
from pathlib import Path
import runpy
import bpy
from mathutils import Vector, Quaternion
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'previews'
OUT.mkdir(exist_ok=True)
source = Path(bpy.data.filepath).resolve()
source_hash = hashlib.sha256(source.read_bytes()).hexdigest()
ns = runpy.run_path(str(ROOT / 'generate_briefs.py'))
body = bpy.data.objects['Human']
rig = bpy.data.objects['Human.rig']

def fingerprint():
    return ([(tuple(v.co), [(g.group,g.weight) for g in v.groups]) for v in body.data.vertices],
            [(k.name,k.value) for k in body.data.shape_keys.key_blocks],
            [(m.name,m.type,m.show_viewport,m.show_render) for m in body.modifiers],
            [tuple(row) for row in body.matrix_world])

before = fingerprint()
garment = ns['build_briefs']()
assert fingerprint() == before
report = ns['topology_report'](garment.data)
assert report['boundary_loops'] == [44,44,64]
assert report['components']==1 and not report['bad_edges'] and not report['degenerate_faces']
assert all(abs(sum(g.weight for g in v.groups)-1)<1e-5 for v in garment.data.vertices)
assert all(g.name in rig.data.bones for g in garment.vertex_groups)
assert len(garment.data.uv_layers.active.data)==len(garment.data.loops)
assert len(garment.data.materials)==2
assert all(math.isfinite(c) for v in garment.data.vertices for c in v.co)
second = ns['build_briefs']()
assert second.name != garment.name
assert [tuple(v.co) for v in second.data.vertices]==[tuple(v.co) for v in garment.data.vertices]
assert fingerprint()==before
second_mesh=second.data; second_materials=list(second_mesh.materials)
bpy.data.objects.remove(second,do_unlink=True);bpy.data.meshes.remove(second_mesh)
for m in second_materials: bpy.data.materials.remove(m)

scene=bpy.context.scene
scene.render.engine='BLENDER_WORKBENCH'
scene.render.resolution_x=800;scene.render.resolution_y=900;scene.render.resolution_percentage=100
scene.display.shading.light='STUDIO';scene.display.shading.color_type='MATERIAL'
scene.display.shading.show_shadows=True;scene.display.shading.show_cavity=True
scene.display.shading.background_type='WORLD';scene.world.color=(.12,.12,.12)
cam=scene.camera;cam.data.type='ORTHO';cam.data.ortho_scale=1.05

def render(name,position,target=(0,0,1.34)):
    cam.location=position
    cam.rotation_euler=(Vector(target)-cam.location).to_track_quat('-Z','Y').to_euler()
    scene.render.filepath=str(OUT/(name+'.png'))
    bpy.ops.render.render(write_still=True)

def evaluated(obj):
    bpy.context.view_layer.update()
    ev=obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=ev.to_mesh()
    coords=[obj.matrix_world@v.co for v in mesh.vertices]
    polys=[tuple(p.vertices) for p in mesh.polygons]
    topo=ns['topology_report'](mesh)
    ev.to_mesh_clear()
    return coords,polys,topo

def fit_report():
    skin,polys,_=evaluated(body)
    cloth,faces,topo=evaluated(garment)
    a=BVHTree.FromPolygons(skin,polys);b=BVHTree.FromPolygons(cloth,faces)
    signed=[]
    for p in cloth:
        hit,n,_,d=a.find_nearest(p);signed.append((p-hit).dot(n))
    self_pairs={(min(i,j),max(i,j)) for i,j in b.overlap(b) if i != j and not set(faces[i]).intersection(faces[j])}
    return dict(solidified_topology=topo, nonadjacent_self_intersections=len(self_pairs), body_triangle_intersection_pairs=len(a.overlap(b)),
                vertices_inside_skin=sum(d < -.0001 for d in signed),
                minimum_signed_skin_distance=min(signed))

report.update(blender=bpy.app.version_string,source_file_version=list(bpy.data.version),
              source_sha256=source_hash, source_mesh_vertices=len(body.data.vertices),
              evaluated_skin_vertices=len(evaluated(body)[0]),materials=2,
              uv_layers=len(garment.data.uv_layers), normalized_weights=True,
              rerun_identical_geometry=True,source_unchanged=True,rest_fit=fit_report())
for name,position in [('front',(0,-4,1.36)),('side',(4,0,1.36)),('back',(0,4,1.36)),('under',(0,-3,.4))]:
    render(name,position)
report['poses']={}
for name,axis,angle in [('hip_flex_45',(1,0,0),-45),('hip_abduct_20',(0,1,0),-20)]:
    p=rig.pose.bones['upperleg01.L'];p.rotation_mode='QUATERNION'
    rest=p.bone.matrix_local.to_quaternion()
    p.rotation_quaternion=rest.inverted() @ Quaternion(axis,math.radians(angle)) @ rest
    bpy.context.view_layer.update()
    report['poses'][name]=fit_report()
    render(name,(2,-4,1.5))
    p.rotation_quaternion=(1,0,0,0)
bpy.context.view_layer.update()
assert fingerprint()==before
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
for fit in [report['rest_fit'], *report['poses'].values()]:
    assert fit['body_triangle_intersection_pairs']==0, fit
    assert fit['vertices_inside_skin']==0, fit
    assert fit['nonadjacent_self_intersections']==0, fit
    assert fit['solidified_topology']['boundary_loops']==[], fit
    assert fit['solidified_topology']['bad_edges']==0, fit
    assert fit['solidified_topology']['triangles']<=6000, fit
output=(OUT/'Human-Male-Briefs-test.blend').resolve()
assert output != source
bpy.ops.wm.save_as_mainfile(filepath=str(output),copy=True)
bpy.ops.wm.open_mainfile(filepath=str(output))
reopened=bpy.data.objects['Gauntlands_Boxer_Briefs']
assert ns['topology_report'](reopened.data)['boundary_loops']==[44,44,64]
assert reopened.modifiers['Follow Human Rig'].object==bpy.data.objects['Human.rig']
assert reopened.data.uv_layers.active is not None
assert all(m is not None for m in reopened.data.materials)
report['saved_copy_reopened']=True
assert hashlib.sha256(source.read_bytes()).hexdigest()==source_hash
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('VALIDATION',json.dumps(report))
