"""Blender background check of paired Godot-skinned meshes, no scene mutation."""
import json
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
root=Path(__file__).resolve().parent
samples=json.loads((root/'geometry_samples.json').read_text())
results=[]
for sample in samples:
    row={'frame':sample['frame'],'state':sample['state']}
    for variant in ['baseline','stance']:
        meshes=sample[variant]
        body=[Vector(p) for p in meshes['body']['vertices']]
        cloth=[Vector(p) for p in meshes['cloth']['vertices']]
        body_tree=BVHTree.FromPolygons(body,meshes['body']['faces'])
        cloth_tree=BVHTree.FromPolygons(cloth,meshes['cloth']['faces'])
        inside=0;depth=0.
        for point in cloth:
            hit,normal,_,_=body_tree.find_nearest(point)
            signed=(point-hit).dot(normal)
            if signed < -.0001: inside+=1;depth=max(depth,-signed)
        row[variant]={'triangle_overlaps':len(body_tree.overlap(cloth_tree)),'inside_vertices':inside,'maximum_depth_m':depth}
    results.append(row)
failures=[r for r in results if r['stance']['triangle_overlaps']>r['baseline']['triangle_overlaps'] or r['stance']['maximum_depth_m']>r['baseline']['maximum_depth_m']+.0001]
report={'passed':not failures,'criterion':'No added body/cloth overlap pairs or >0.1 mm added penetration depth versus same sampled unmodified pose','samples':results,'failures':failures}
(root/'geometry_validation.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print('STANCE_GEOMETRY',report['passed'],'samples',len(results),'failures',len(failures))
for row in results:print(row)
if failures:raise RuntimeError('Stance worsened sampled garment clearance')
