"""Compare saved original/corrected rest rig, keys, weights, materials and transforms."""
import bpy
import json
from pathlib import Path
from mathutils import Vector
ROOT=Path(__file__).resolve().parent
source=ROOT.parent.parent/'assets/Blender Models/Human-Male.blend'
output=source.with_name('Human-Male-180cm.blend')
def capture():
    rig=bpy.data.objects['Human.rig']
    result={}
    for name in ['Human','Human.rig','Human.high-poly']:
        o=bpy.data.objects[name]
        result[name]=dict(matrix=[list(r) for r in o.matrix_world],parent_inverse=[list(r) for r in o.matrix_parent_inverse],parent=o.parent.name if o.parent else None)
        if o.type=='MESH':
            result[name].update(weights=[[(g.group,g.weight) for g in v.groups] for v in o.data.vertices],materials=[m.name for m in o.data.materials],keys={k.name:dict(value=k.value,coords=[tuple(v.co) for v in k.data]) for k in o.data.shape_keys.key_blocks} if o.data.shape_keys else {})
    return result,{b.name:(tuple(b.head_local),tuple(b.tail_local)) for b in rig.data.bones}
bpy.ops.wm.open_mainfile(filepath=str(source));before,bones=capture()
bpy.ops.wm.open_mainfile(filepath=str(output));after,newbones=capture()
factor=json.loads((ROOT/'scale_previews/scale_validation.json').read_text())['scale_factor']
for name in before:
    for field in ['matrix','parent_inverse','parent','weights','materials']:
        assert before[name].get(field)==after[name].get(field),(name,field)
    for key, old in before[name].get('keys',{}).items():
        new=after[name]['keys'][key]
        assert old['value']==new['value']
        assert len(old['coords'])==len(new['coords'])
        assert max((Vector(a)*factor-Vector(b)).length for a,b in zip(old['coords'],new['coords']))<1e-6
assert bones.keys()==newbones.keys()
error=max((Vector(a)*factor-Vector(b)).length for name in bones for a,b in zip(bones[name],newbones[name]))
assert error<1e-6
report=dict(saved_data_integrity=True,bone_count=len(bones),max_bone_endpoint_error_m=error,
            before_transforms={n:{k:v for k,v in d.items() if k in ['matrix','parent_inverse','parent']} for n,d in before.items()},
            after_transforms={n:{k:v for k,v in d.items() if k in ['matrix','parent_inverse','parent']} for n,d in after.items()})
(ROOT/'scale_previews/integrity_validation.json').write_text(json.dumps(report,indent=2)+'\n')
print('INTEGRITY_PASS',len(bones),error)
