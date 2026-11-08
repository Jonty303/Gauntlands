"""Validate the actual exported GLB at every animation frame, plus reference bounds."""
import bpy,json,hashlib
from pathlib import Path
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'tools/blender/animation_previews'
GLB=ROOT/'prototype/assets/human_diagnostic.glb'
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/Blender Models/Human-Male-Animation-Proof.blend'))
saved_rig=bpy.data.objects['Human.rig']
assert saved_rig.animation_data.action.name=='Diagnostic'
assert len(bpy.data.objects['Human'].data.shape_keys.key_blocks)==9
assert all(bpy.data.images[n].packed_file for n in ['brown_eye.png','young_lightskinned_male_diffuse.png'])
accepted=ROOT/'assets/Blender Models/Human-Male-180cm.blend'
assert hashlib.sha256(accepted.read_bytes()).hexdigest()==json.loads((OUT/'build.json').read_text())['source_sha256']
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.context.scene.render.fps=30
bpy.ops.import_scene.gltf(filepath=str(GLB))
rig=bpy.data.objects['Human.rig']
assert rig.animation_data and rig.animation_data.action
body=bpy.data.objects['Human'];cloth=bpy.data.objects['Gauntlands_Boxer_Briefs']
assert all(o.modifiers[0].object==rig for o in [body,cloth,bpy.data.objects['Human.high-poly']])
def surface(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
    vs=[ev.matrix_world@v.co for v in m.vertices];ps=[tuple(p.vertices) for p in m.polygons]
    ev.to_mesh_clear();return vs,ps
report=dict(saved_animation_reopened=True,editable_keys=9,used_textures_packed=True,accepted_source_preserved=True,glb_sha256=hashlib.sha256(GLB.read_bytes()).hexdigest(),frames=[],samples={})
for frame in range(1,242):
    bpy.context.scene.frame_set(frame-1)
    skin,faces=surface(body);fabric,polys=surface(cloth)
    a=BVHTree.FromPolygons(skin,faces);b=BVHTree.FromPolygons(fabric,polys)
    intersections=len(a.overlap(b))
    # glTF splits vertices at UV/material seams. Shared geometric corners are
    # adjacent even when their vertex indices differ after import.
    corners=[{tuple(round(c,5) for c in fabric[v]) for v in poly} for poly in polys]
    self_pairs={(min(i,j),max(i,j)) for i,j in b.overlap(b) if i!=j and not corners[i].intersection(corners[j])}
    inside=0;minimum=100
    for v in fabric:
        hit,n,_,dist=a.find_nearest(v);signed=(v-hit).dot(n)
        inside+=signed < -0.0001;minimum=min(minimum,signed)
    report['frames'].append(dict(frame=frame,body_intersections=intersections,self_intersections=len(self_pairs),inside=inside,min_clearance=minimum))
    if frame in [1,31,61,91,121,151,181,196,211,241]:
        sample={}
        for o in [body,cloth,bpy.data.objects['Human.high-poly']]:
            vs,_=surface(o)
            # Blender -> glTF/Godot basis: (X,Z,-Y).
            vs=[(v.x,v.z,-v.y) for v in vs]
            sample[o.name]=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
        report['samples'][str(frame)]=sample
report['passed']=all(not (f['body_intersections'] or f['self_intersections'] or f['inside']) for f in report['frames'])
(OUT/'export_animation_validation.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'prototype/tests/reference_bounds.json').write_text(json.dumps(report['samples'],indent=2)+'\n')
print('EXPORTED_ANIMATION',report['passed'],'bad frames',[f for f in report['frames'] if f['body_intersections'] or f['self_intersections'] or f['inside']][:5])
assert report['passed'],'Exported clothing failed; inspect report'
