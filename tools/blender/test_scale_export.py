"""Disposable GLB scale round-trip; does not save the loaded Blender scene."""
import bpy
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'scale_previews'
assert Path(bpy.data.filepath).name == 'Human-Male-180cm.blend'
bpy.ops.object.select_all(action='DESELECT')
for o in bpy.context.scene.objects:
    if o.type in {'MESH','ARMATURE'}: o.select_set(True)
path=OUT/'Human-Male-180cm-test.glb'
bpy.ops.export_scene.gltf(filepath=str(path),export_format='GLB',use_selection=True,export_animations=False,export_apply=True,export_all_influences=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(path))
bpy.context.view_layer.update()
body=bpy.data.objects.get('Human')
assert body and body.type=='MESH'
ev=body.evaluated_get(bpy.context.evaluated_depsgraph_get()); mesh=ev.to_mesh()
vs=[ev.matrix_world@v.co for v in mesh.vertices]; ev.to_mesh_clear()
height=max(v.z for v in vs)-min(v.z for v in vs)
assert abs(height-1.8)<1e-5, height
arms=[m.object for m in body.modifiers if m.type=='ARMATURE']
assert len(arms)==1 and arms[0]
assert bpy.data.objects.get('Gauntlands_Boxer_Briefs')
report=dict(export_policy='Apply non-armature modifiers; baked shape mix, no editable morphs; all joint influences',glb_bytes=path.stat().st_size,roundtrip_height_m=height,armature=arms[0].name,
            shape_keys=len(body.data.shape_keys.key_blocks) if body.data.shape_keys else 0,
            objects=[o.name for o in bpy.context.scene.objects],godot_import='not run')
(OUT/'export_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('EXPORT_VALIDATION',report)
