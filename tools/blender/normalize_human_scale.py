"""Convert the inspected pristine MPFB source to metres without overwriting it.
Run Blender SOURCE --background --python-exit-code 1 --python tools/blender/normalize_human_scale.py
Only the identity-transform, neutral, unanimated source contract is supported.
"""
import bpy
import hashlib
import json
import math
import runpy
from pathlib import Path
from mathutils import Matrix, Quaternion

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'scale_previews'
TARGET = 1.80

def coords(obj):
    bpy.context.view_layer.update()
    ev = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh = ev.to_mesh()
    result = [ev.matrix_world @ v.co for v in mesh.vertices]
    ev.to_mesh_clear()
    return result

def snapshot(objects):
    return {o.name: dict(matrix_world=[list(r) for r in o.matrix_world],
                        bounds=[[min(v[i] for v in coords(o)), max(v[i] for v in coords(o))] for i in range(3)])
            for o in objects if o.type == 'MESH'}

def main():
    source = Path(bpy.data.filepath).resolve()
    output = source.with_name('Human-Male-180cm.blend')
    if source.name != 'Human-Male.blend' or output.exists():
        raise RuntimeError('Load pristine Human-Male.blend; move existing 180cm output aside first.')
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    ns = runpy.run_path(str(ROOT / 'generate_briefs.py'))
    body, rig, *_ = ns['source_surface']()
    objects = [rig, *rig.children_recursive]
    if set(o.name for o in objects) != {'Human', 'Human.rig', 'Human.high-poly'}:
        raise RuntimeError('Unexpected character hierarchy; inspect before conversion.')
    for o in objects:
        if o.animation_data or o.constraints or (o.type == 'MESH' and o.data.shape_keys and o.data.shape_keys.animation_data):
            raise RuntimeError('Animated/constrained source requires a separate migration.')
        if any(abs(o.matrix_world[i][j] - (i == j)) > 1e-6 for i in range(4) for j in range(4)):
            raise RuntimeError('Non-identity source transforms require explicit migration.')
        if o.data.users != 1:
            raise RuntimeError('Shared data is unsupported.')
    if any(p.constraints for p in rig.pose.bones):
        raise RuntimeError('Constrained rig unsupported.')
    before = snapshot(objects)
    height = before[body.name]['bounds'][2][1] - before[body.name]['bounds'][2][0]
    factor = TARGET / height
    # Capture independently evaluated deformation samples before touching any data.
    samples = {}
    for name, axis, angle in [('neutral',(1,0,0),0),('flex',(1,0,0),-45),('abduct',(0,1,0),-20)]:
        p = rig.pose.bones['upperleg01.L']
        p.rotation_mode = 'QUATERNION'
        rest = p.bone.matrix_local.to_quaternion()
        p.rotation_quaternion = rest.inverted() @ Quaternion(axis,math.radians(angle)) @ rest
        samples[name] = {o.name: coords(o) for o in objects if o.type == 'MESH'}
    p.rotation_quaternion = (1,0,0,0)
    keys = {k.name: [v.co.copy() for v in k.data] for k in body.data.shape_keys.key_blocks}
    matrix = Matrix.Scale(factor,4)
    for o in objects:
        if o.type == 'MESH':
            o.data.transform(matrix, shape_keys=True)
            o.data.update()
        elif o.type == 'ARMATURE':
            o.data.transform(matrix)
    bpy.context.view_layer.update()
    key_error = max((v.co - old*factor).length for k in body.data.shape_keys.key_blocks for v,old in zip(k.data,keys[k.name]))
    assert key_error < 1e-6
    errors = {}
    for name, axis, angle in [('neutral',(1,0,0),0),('flex',(1,0,0),-45),('abduct',(0,1,0),-20)]:
        rest = p.bone.matrix_local.to_quaternion()
        p.rotation_quaternion = rest.inverted() @ Quaternion(axis,math.radians(angle)) @ rest
        errors[name] = max((v-old*factor).length for o in objects if o.type == 'MESH' for v,old in zip(coords(o),samples[name][o.name]))
        assert errors[name] < 1e-5, errors
    p.rotation_quaternion = (1,0,0,0)
    bpy.context.view_layer.update()
    bpy.context.scene.unit_settings.system = 'METRIC'
    bpy.context.scene.unit_settings.scale_length = 1
    after = snapshot(objects)
    assert abs(after[body.name]['bounds'][2][1]-after[body.name]['bounds'][2][0]-TARGET)<1e-6
    garment = ns['build_briefs']()
    bpy.context.scene['gauntlands_scale_contract'] = '1 Blender unit = 1 metre; Z up, -Y forward; target skin height 1.80 m'
    OUT.mkdir(exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), copy=True)
    bpy.ops.wm.open_mainfile(filepath=str(output))
    assert abs(max(v.z for v in coords(bpy.data.objects['Human'])) - min(v.z for v in coords(bpy.data.objects['Human']))-TARGET)<1e-6
    assert bpy.data.objects['Gauntlands_Boxer_Briefs'].modifiers['Follow Human Rig'].object == bpy.data.objects['Human.rig']
    assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
    report = dict(source_sha256=digest, blender=bpy.app.version_string, units='METRIC',scale_length=1,
                  before=before,after=after,scale_factor=factor,target_height_m=TARGET,
                  shape_key_count=len(keys),max_shape_key_scale_error=key_error,
                  max_deformation_scale_errors=errors,source_preserved=True,save_reopen=True)
    (OUT/'scale_validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print('SCALE_VALIDATION',json.dumps(report))

if __name__ == '__main__': main()
