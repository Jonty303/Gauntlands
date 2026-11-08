"""Create the bounded diagnostic animation and GLB from the accepted test source.
Run Blender --background --factory-startup Human-Male-180cm.blend
--python-exit-code 1 --python tools/blender/build_animation_proof.py
"""
import bpy
import hashlib
import json
import math
from pathlib import Path
from mathutils import Quaternion
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'tools/blender/animation_previews'
SOURCE=ROOT/'assets/Blender Models/Human-Male-180cm.blend'
DEST=SOURCE.with_name('Human-Male-Animation-Proof.blend')
GLB=ROOT/'prototype/assets/human_diagnostic.glb'

def main():
    if Path(bpy.data.filepath).resolve()!=SOURCE.resolve():
        raise RuntimeError('Load the accepted 180cm source first.')
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    rig=bpy.data.objects['Human.rig']
    assert not rig.animation_data
    scene=bpy.context.scene
    scene.render.fps=30
    scene.frame_start=1;scene.frame_end=241
    # Eight-second isolated diagnostic; return to rest between each movement.
    # Axes are Blender armature-space axes, converted into each rest bone frame.
    poses={1:{},31:{'upperleg01.L':((1,0,0),-30),'lowerleg01.L':((1,0,0),45)},
           61:{},91:{'upperleg01.R':((1,0,0),-30),'lowerleg01.R':((1,0,0),45)},
           121:{},151:{'upperarm01.L':((1,0,0),-25),'upperarm01.R':((1,0,0),25)},
           181:{},196:{'head':((0,0,1),25)},211:{'head':((0,0,1),-25)},241:{}}
    controlled=sorted({n for pose in poses.values() for n in pose})
    for frame,pose in poses.items():
        for name in controlled:
            p=rig.pose.bones[name];p.rotation_mode='QUATERNION'
            axis,angle=pose.get(name,((1,0,0),0))
            rest=p.bone.matrix_local.to_quaternion()
            p.rotation_quaternion=rest.inverted()@Quaternion(axis,math.radians(angle))@rest
            p.keyframe_insert(data_path='rotation_quaternion',frame=frame,group=name)
    action=rig.animation_data.action;action.name='Diagnostic'
    # Explicit linear sampling avoids untested Bezier overshoot between diagnostic poses.
    for layer in action.layers:
        for strip in layer.strips:
            for bag in strip.channelbags:
                for curve in bag.fcurves:
                    for key in curve.keyframe_points:key.interpolation='LINEAR'
    scene.frame_set(1)
    # Pack only textures actually used by the character; no machine-specific dependency.
    images=set()
    for o in [rig,*rig.children_recursive]:
        if o.type=='MESH':
            for material in o.data.materials:
                for node in material.node_tree.nodes:
                    if node.type=='TEX_IMAGE' and node.image:
                        images.add(node.image)
    for image in images:
        image.reload()
        if len(image.pixels)==0:raise RuntimeError('Missing texture '+image.name)
        image.pack()
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig,*rig.children_recursive]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.wm.save_as_mainfile(filepath=str(DEST),copy=True)
    bpy.ops.export_scene.gltf(filepath=str(GLB),export_format='GLB',use_selection=True,
        export_apply=True,export_animations=True,export_animation_mode='ACTIONS',
        export_frame_range=True,export_anim_slide_to_zero=True,export_force_sampling=True,export_influence_nb=8,
        export_all_influences=False,export_morph=False)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==digest
    manifest=dict(source_sha256=digest,blender=bpy.app.version_string,frames=[1,241],fps=30,
        duration_seconds=8,animation='Diagnostic',controlled_bones=controlled,
        poses={str(k):v for k,v in poses.items()},textures=sorted(i.name for i in images),
        export_policy='Current shape and non-armature modifiers baked; max 8 influences; no morphs',
        source_preserved=True)
    (OUT/'build.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('ANIMATION_BUILT',manifest)

if __name__=='__main__':main()
