"""Bake one additional native dummy clip. Usage: -- SOURCE_ROOT Idle|Run."""
import bpy, json, hashlib, sys, zipfile
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2]
SOURCE=Path(sys.argv[sys.argv.index("--")+1]) if "--" in sys.argv else ROOT.parent/"Human"
CLIP=sys.argv[sys.argv.index("--")+2] if "--" in sys.argv and len(sys.argv)>sys.argv.index("--")+2 else "Run"
assert CLIP in ["Idle","Run"]
LAST=82 if CLIP=="Idle" else 19
COUNT=(LAST-1)*2+1
DURATION=(LAST-1)/30
SOURCE_ACTION="HumanM@Idle01" if CLIP=="Idle" else "HumanM@Run01_Forward [RM]"
CACHE=ROOT/".local/kevin"; OUT=ROOT/"prototype/assets/kevin_local"
CACHE.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
archives=[SOURCE/"Animations/HumanBasicMotionsFREE_BlenderFiles.zip",SOURCE/"Models/HumanDummyModels_Source.zip"]
names=["HumanM_BasicMotionsFREE_2.4.blend","HumanCharacterDummy_M.blend"]
for archive,name in zip(archives,names):
 with zipfile.ZipFile(archive) as z:(CACHE/name).write_bytes(z.read(name))
bpy.ops.wm.open_mainfile(filepath=str(CACHE/names[1]),load_ui=False,use_scripts=False)
dummy_vertices=[v.co.copy() for v in bpy.data.objects["HumanM_BodyMesh"].data.vertices]
bpy.ops.wm.open_mainfile(filepath=str(CACHE/names[0]),load_ui=False,use_scripts=False)
rig=bpy.data.objects["Rig"];mesh=bpy.data.objects["HumanM_BodyMesh"]
mesh_match=max((v.co-dummy_vertices[i]).length for i,v in enumerate(mesh.data.vertices))
assert mesh_match<0.00001,mesh_match
action=bpy.data.actions[SOURCE_ACTION]
rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
scene=bpy.context.scene
source_surfaces=[]
def sample(frame):
 scene.frame_set(int(frame),subframe=frame-int(frame))
 bpy.context.view_layer.update()
 dg=bpy.context.evaluated_depsgraph_get();ev=mesh.evaluated_get(dg);me=ev.to_mesh()
 source_surfaces.append([ev.matrix_world@v.co for v in me.vertices]);ev.to_mesh_clear()
 return {b.name:b.matrix.copy() for b in rig.pose.bones if b.name.startswith("B-")}
# Prime stateful constraint evaluation after changing the active source action.
if CLIP=="Idle":
 sample(LAST)
 sample(1)
 source_surfaces.clear()
samples=[sample(1+i*.5) for i in range(COUNT)]
travel=samples[-1]["B-root"].translation-samples[0]["B-root"].translation
assert abs(travel.length-(0 if CLIP=="Idle" else 4*DURATION))<0.0001
# Bake source control-rig evaluation onto a plain copy of its deformation skeleton.
clean=rig.copy();clean.data=rig.data.copy();scene.collection.objects.link(clean)
clean.name="DummyRig";clean.animation_data_clear()
for p in clean.pose.bones:
 for c in list(p.constraints):p.constraints.remove(c)
bpy.ops.object.select_all(action="DESELECT");clean.select_set(True)
bpy.context.view_layer.objects.active=clean
bpy.ops.object.mode_set(mode="EDIT")
for b in list(clean.data.edit_bones):
 if not b.name.startswith("B-"):clean.data.edit_bones.remove(b)
bpy.ops.object.mode_set(mode="OBJECT")
for i,matrices in enumerate(samples):
 translated={name:mat.copy() for name,mat in matrices.items()}
 for mat in translated.values():mat.translation -= travel*(i/(COUNT-1))
 if i==COUNT-1:translated={name:mat.copy() for name,mat in samples[0].items()}
 for p in clean.pose.bones:
  kwargs={}
  if p.parent:
   kwargs={"parent_matrix":translated[p.parent.name],"parent_matrix_local":p.parent.bone.matrix_local}
  p.rotation_mode="QUATERNION"
  p.matrix_basis=p.bone.convert_local_to_pose(translated[p.name],p.bone.matrix_local,invert=True,**kwargs)
  for path in ["location","rotation_quaternion","scale"]:p.keyframe_insert(data_path=path,frame=i+1,group=p.name)
baked=clean.animation_data.action;baked.name=CLIP
for c in baked.layers[0].strips[0].channelbag(baked.slots[0]).fcurves:
 for key in c.keyframe_points:key.interpolation="LINEAR"
world=mesh.matrix_world.copy();mesh.parent=clean;mesh.matrix_world=world
for mod in mesh.modifiers:
 if mod.type=="ARMATURE":mod.object=clean
for obj in list(bpy.data.objects):
 if obj not in [mesh,clean]:bpy.data.objects.remove(obj,do_unlink=True)
for a in list(bpy.data.actions):
 if a!=baked:bpy.data.actions.remove(a)
mesh.name="KevinMaleDummy"
material=bpy.data.materials.new("Neutral clay - evaluation")
material.diffuse_color=(.55,.65,.7,1);material.use_nodes=True
bsdf=material.node_tree.nodes.get("Principled BSDF")
bsdf.inputs["Base Color"].default_value=material.diffuse_color
bsdf.inputs["Roughness"].default_value=.78
mesh.data.materials.clear();mesh.data.materials.append(material)
for polygon in mesh.data.polygons:polygon.material_index=0
scene.render.fps=60;scene.frame_start=1;scene.frame_end=COUNT
def vertices(f):
 scene.frame_set(int(f),subframe=f-int(f));dg=bpy.context.evaluated_depsgraph_get();dg.update()
 ev=mesh.evaluated_get(dg);me=ev.to_mesh()
 result=[ev.matrix_world@v.co for v in me.vertices];ev.to_mesh_clear();return result
poses=[vertices(1+i*.5) for i in range((COUNT-1)*2+1)]
floor_min=min(v.z for pose in poses for v in pose)
loop_error=max((a-b).length for a,b in zip(poses[0],poses[-1]))
assert loop_error<0.0001,loop_error
preservation=max((poses[2*i][j]-(v-travel*(i/(COUNT-1)))).length for i,vs in enumerate(source_surfaces) for j,v in enumerate(vs))
assert preservation<.002,preservation
assert floor_min>-.03,floor_min
scene.frame_set(1)
bpy.ops.object.select_all(action="DESELECT");clean.select_set(True);mesh.select_set(True)
bpy.context.view_layer.objects.active=clean
output=OUT/("dummy_"+CLIP.lower()+".glb")
bpy.ops.export_scene.gltf(filepath=str(output),export_format="GLB",use_selection=True,
 export_animations=True,export_animation_mode="ACTIONS",export_force_sampling=True,
 export_frame_range=True,export_frame_step=1,export_anim_slide_to_zero=True,
 export_skins=True,export_influence_nb=8,export_morph=False,export_yup=True,export_apply=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
report={"source_files":[{"path":str(p.relative_to(SOURCE)),"sha256":sha(p)} for p in archives],
 "source_action":SOURCE_ACTION,"publisher":"Kevin Iglesias",
 "source_url":"https://kevdev.itch.io/basic-motions-free","licence_url":"https://www.keviniglesias.com/#license",
 "blender":bpy.app.version_string,"source_frames":[1,LAST],"source_fps":30,
 "export_frames":[1,COUNT],"export_fps":60,"duration_s":DURATION,"stride_m":travel.length,
 "speed_mps":travel.length/DURATION,"dummy_source_mesh_max_difference_m":mesh_match,
 "bones":len(clean.data.bones),"export_evaluated_vertices":len(poses[0]),
 "source_floor_min_m":floor_min,"ground_offset_m":max(0,-floor_min)+.0005,
 "floor_samples_m":[min(v.z for v in pose) for pose in poses],
 "loop_surface_max_error_m":loop_error,"source_to_bake_max_surface_error_m":preservation,
 "bounds":[[min(v[i] for pose in poses for v in pose),max(v[i] for pose in poses for v in pose)] for i in range(3)],
 "godot_forward":"+Z","blender_forward":"-Y","output_sha256":sha(output)}
(ROOT/("tools/kevin_locomotion/"+CLIP.lower()+"_build.json")).write_text(json.dumps(report,indent=2)+"\n")
(OUT/(CLIP.lower()+".json")).write_text(json.dumps(report,indent=2)+"\n")
template=(ROOT/"tools/kevin_walk/dummy_walk.glb.import").read_text()
template="\n".join(line for line in template.splitlines() if not line.startswith("uid="))+"\n"
template=template.replace("dummy_walk","dummy_"+CLIP.lower()).replace("animation/remove_immutable_tracks=true","animation/remove_immutable_tracks=false")
import_path=OUT/("dummy_"+CLIP.lower()+".glb.import")
if not import_path.exists():import_path.write_text(template)
print(json.dumps(report))