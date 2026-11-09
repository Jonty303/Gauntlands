"""Validate run and gait-change contact, deformation and v0.2 preservation."""
import bpy, json, math, hashlib, struct, sys
from pathlib import Path
from mathutils import Vector
from mathutils.bvhtree import BVHTree
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'tools/blender/locomotion_v03'
manifest=json.loads((OUT/'build.json').read_text());GLB=ROOT/'prototype/assets/human_locomotion_v03.glb'

def walk_data(path,name="Walk"):
    b=path.read_bytes();size=struct.unpack_from('<I',b,12)[0];j=json.loads(b[20:20+size]);start=20+size+8;data=b[start:]
    a=next(a for a in j['animations'] if a['name']==name);result={}
    for c in a['channels']:
        s=a['samplers'][c['sampler']];values=[]
        for key in ['input','output']:
            acc=j['accessors'][s[key]];view=j['bufferViews'][acc['bufferView']]
            offset=view.get('byteOffset',0)+acc.get('byteOffset',0);n={'SCALAR':1,'VEC3':3,'VEC4':4}[acc['type']];width=4*n;stride=view.get('byteStride',width)
            values.append([struct.unpack_from('<'+'f'*n,data,offset+i*stride) for i in range(acc['count'])])
        result[(j['nodes'][c['target']['node']]['name'],c['target']['path'])]=values
    return result
old=walk_data(ROOT/'prototype/assets/human_locomotion.glb');new=walk_data(GLB)
assert old.keys()==new.keys();walk_error=max(abs(x-y) for key in old for aa,bb in zip(old[key],new[key]) for a,b in zip(aa,bb) for x,y in zip(a,b))
assert all([len(x) for x in old[k]]==[len(x) for x in new[k]] for k in old)
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=60;bpy.ops.import_scene.gltf(filepath=str(GLB))
rig=bpy.data.objects['Human.rig'];body=bpy.data.objects['Human'];cloth=bpy.data.objects['Gauntlands_Boxer_Briefs']
actions={n:next(a for a in bpy.data.actions if a.name.startswith(n)) for n in manifest['clips']}
def surface(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh();v=[ev.matrix_world@p.co for p in m.vertices];f=[tuple(p.vertices) for p in m.polygons];ev.to_mesh_clear();return v,f
rig.animation_data.action=None
for p in rig.pose.bones:p.matrix_basis.identity()
bpy.context.view_layer.update();bind,faces=surface(body)
hands={i for i,v in enumerate(bind) if abs(v.x)>.455 and v.z<1.25};core={i for i,v in enumerate(bind) if abs(v.x)<.32 and v.z<1.55}
hand_faces=[p for p in faces if all(i in hands for i in p)];core_faces=[p for p in faces if all(i in core for i in p)]
tips={};contact_ids={}
for side,sign in [('L',1),('R',-1)]:
    ball=rig.data.bones['toe1-1.'+side].head_local;limit=rig.data.bones['foot.'+side].head_local.z*.11
    tip=min((i for i,v in enumerate(bind) if abs(v.x-ball.x)<.02 and v.z<limit),key=lambda i:bind[i].y);tips[side]=bind[tip]
    contact_ids[side]={stage:min(range(len(bind)),key=lambda i:(bind[i]-Vector((sign*.19,y,0))).length_squared) for stage,y in [('heel',.045),('sole',0),('toe',-.19)]};contact_ids[side]['tip']=tip

def stage_at(name,side,t):
    if name!='Run':
        stages=manifest['transitions'][name]['contact_stages'][side]
        return stages[min(round(t*60),len(stages)-1)]
    p=(t/manifest['run_period']+(0 if side=='L' else .5))%1
    return None if p>manifest['run_duty'] else ('heel' if p<.08 else 'sole' if p<.16 else 'toe' if p<.32 else 'tip')

report={'passed':False,'walk_export_maximum_channel_error':walk_error,'clips':{},'joins':{},'failures':[],'glb_sha256':hashlib.sha256(GLB.read_bytes()).hexdigest()};endpoints={};bounds={};motion={}
for name in manifest['clips']:
    action=actions[name];rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0];frames=round(manifest['clips'][name]*60)
    floor=100.;clearance=100.;body_hits=hand_hits=inside=cloth_self=0;knees=[];slip=skin_slip=height=0.;previous={};forward_motion=[];bounds[name]={};airborne=0
    for i in range(2*frames+1):
        frame=i/2;t=frame/60;bpy.context.scene.frame_set(int(frame),subframe=frame%1)
        v,f=surface(body);floor=min(floor,min(x.z for x in v));angles=[]
        if name=='Run' and i%2==0 and all(min(v[j].z for j,q in enumerate(bind) if q.z<.16 and q.x*sign>0)>.005 for sign in [1,-1]):airborne+=1
        for side in ['L','R']:
            h=rig.pose.bones['upperleg01.'+side].head;k=rig.pose.bones['lowerleg01.'+side].head;a=rig.pose.bones['foot.'+side].head
            angles.append(180-math.degrees((h-k).angle(a-k)))
        knees.append(angles)
        if name=='WalkStart':
            travel_samples=manifest['travel_m_at_60hz'][name];j=int(frame);fraction=frame-j
            virtual_distance=travel_samples[j]*(1-fraction)+travel_samples[min(j+1,frames)]*fraction
            hip=(rig.pose.bones['upperleg01.L'].head+rig.pose.bones['upperleg01.R'].head)*.5
            forward_motion.append(virtual_distance-hip.y)
        if i%2:continue
        fabric,polys=surface(cloth);tree=BVHTree.FromPolygons(v,f);garment=BVHTree.FromPolygons(fabric,polys)
        body_hits+=len(tree.overlap(garment))
        corners=[{tuple(round(c,5) for c in fabric[j]) for j in poly} for poly in polys]
        cloth_self+=len({(min(x,y),max(x,y)) for x,y in garment.overlap(garment) if x!=y and not corners[x].intersection(corners[y]) and not any((fabric[a]-fabric[b]).length_squared<1e-12 for a in polys[x] for b in polys[y])})
        for vertex in fabric:
            hit,normal,_,_=tree.find_nearest(vertex);inside+=int((vertex-hit).dot(normal)<-.0001)
        ct=BVHTree.FromPolygons(v,core_faces);ht=BVHTree.FromPolygons(v,hand_faces);hand_hits+=len(ct.overlap(ht));clearance=min(clearance,min(ct.find_nearest(v[j])[3] for j in hands))
        if frame in [0,frames]:endpoints[(name,int(frame))]=v+fabric
        if int(frame)%(frames//4)==0:
            bounds[name][str(int(frame))]={}
            for obj in [body,cloth,bpy.data.objects['Human.high-poly']]:
                vs,_=surface(obj);vs=[(x.x,x.z,-x.y) for x in vs];bounds[name][str(int(frame))][obj.name]=[[min(x[a] for x in vs),max(x[a] for x in vs)] for a in range(3)]
        travel=manifest['run_speed']*t if name=='Run' else manifest['travel_m_at_60hz'][name][int(frame)]
        for side in ['L','R']:
            stage=stage_at(name,side,t)
            if stage is None:previous.pop(side,None);continue
            bone=rig.pose.bones[('toe1-1.' if stage in ['toe','tip'] else 'foot.')+side];anchor=bone.bone.head_local.copy();anchor.z=0
            if stage=='heel':anchor.y=.045
            elif stage=='toe':anchor.y=-.19
            elif stage=='tip':anchor=tips[side]
            point=rig.matrix_world@bone.matrix@bone.bone.matrix_local.inverted()@anchor;point.y-=travel
            skin=v[contact_ids[side][stage]].copy();skin.y-=travel;height=max(height,abs(skin.z))
            if side in previous and previous[side][0]==stage:
                slip=max(slip,(point-previous[side][1]).length);skin_slip=max(skin_slip,(skin-previous[side][2]).length)
            previous[side]=(stage,point,skin)
    step=max(2*abs(b[s]-a[s]) for a,b in zip(knees,knees[1:]) for s in [0,1])
    whole=knees[::2];motion[name]=whole;accel=max(abs(c[s]-2*b[s]+a[s]) for a,b,c in zip(whole,whole[1:],whole[2:]) for s in [0,1])
    result={'floor_min_m':floor,'knee_min_degrees':min(min(x) for x in knees),'knee_max_degrees':max(max(x) for x in knees),'knee_max_step_degrees_60hz':step,'knee_max_acceleration_degrees_frame2':accel,'hand_core_clearance_m':clearance,'hand_core_intersections':hand_hits,'body_cloth_intersections':body_hits,'cloth_inside_vertices':inside,'cloth_self_intersections':cloth_self,'contact_anchor_step_m':slip,'contact_skin_step_m':skin_slip,'sampled_contact_height_m':height,'authored_frames':frames+1,'half_frames':frames}
    if forward_motion:
        recoil=max(max(forward_motion[:i+1])-x for i,x in enumerate(forward_motion))
        result['maximum_backward_hip_excursion_m']=recoil
        if recoil>.0001:report['failures'].append(name+': hip recoil')
    if name=='Run':
        result['both_feet_airborne_frames_60hz']=airborne
        if airborne<2:report['failures'].append('Run: missing flight')
    report['clips'][name]=result
    for ok,message in [(floor>=-.003,'floor'),(step<12,'knee speed'),(accel<4,'knee acceleration'),(clearance>.005 and hand_hits==0,'hand clearance'),(body_hits==0 and inside==0 and cloth_self==0,'clothing'),(slip<.0001,'contact anchor'),(skin_slip<.003,'contact skin')]:
        if not ok:report['failures'].append(name+': '+message)
    print('RUN_CLIP',name,result,flush=True)
motion['Walk']=[]
walk_action=next(a for a in bpy.data.actions if a.name=='Walk')
rig.animation_data.action=walk_action;rig.animation_data.action_slot=walk_action.slots[0]
for frame in range(73):
    bpy.context.scene.frame_set(frame);angles=[]
    for side in ['L','R']:
        h=rig.pose.bones['upperleg01.'+side].head;k=rig.pose.bones['lowerleg01.'+side].head;a=rig.pose.bones['foot.'+side].head
        angles.append(180-math.degrees((h-k).angle(a-k)))
    motion['Walk'].append(angles)
    if frame in [0,36]:endpoints[('Walk',frame)]=surface(body)[0]+surface(cloth)[0]
rig.animation_data.action=actions['Run'];rig.animation_data.action_slot=actions['Run'].slots[0];bpy.context.scene.frame_set(24)
endpoints[('Run',24)]=surface(body)[0]+surface(cloth)[0]
joins=[(('Run',48),('Run',0))]
for name,meta in manifest['transitions'].items():
    a=meta['from'];b=meta['to'];phase=meta['phase']
    joins.extend([((a,round(phase*(72 if a=='Walk' else 48))),(name,0)),((name,60),(b,round(phase*(72 if b=='Walk' else 48))))])
report['join_knee_acceleration_degrees_frame2']={}
for a,b in joins:
    error=max((x-y).length for x,y in zip(endpoints[a],endpoints[b]));report['joins'][str(a)+' -> '+str(b)]=error
    if error>.0001:report['failures'].append('join '+str(a)+' '+str(b))
    before=[motion[a[0]][(a[1]+offset)%(len(motion[a[0]])-1)] if a[0] in ['Run','Walk'] else motion[a[0]][a[1]+offset] for offset in [-2,-1,0]]
    after=[motion[b[0]][(b[1]+offset)%(len(motion[b[0]])-1)] if b[0] in ['Run','Walk'] else motion[b[0]][b[1]+offset] for offset in [1,2]]
    sequence=before+after
    acceleration=max(abs(z[j]-2*y[j]+x[j]) for x,y,z in zip(sequence,sequence[1:],sequence[2:]) for j in [0,1])
    report['join_knee_acceleration_degrees_frame2'][str(a)+' -> '+str(b)]=acceleration
    if acceleration>=4:report['failures'].append('join knee acceleration '+str(a)+' '+str(b))
if walk_error>1e-6:report['failures'].append('approved Walk changed')
# Existing clips must retain their exported channels; no gait edits to v0.2.
report['preserved_clips']={}
for name in ['Idle','Walk','WalkStart','WalkStopL','WalkStopR']:
    before=walk_data(ROOT/'prototype/assets/human_locomotion_v02.glb',name);after=walk_data(GLB,name)
    assert before.keys()==after.keys()
    assert all([len(x) for x in before[k]]==[len(x) for x in after[k]] for k in before)
    error=max(abs(x-y) for key in before for aa,bb in zip(before[key],after[key]) for a,b in zip(aa,bb) for x,y in zip(a,b))
    report['preserved_clips'][name]=error
    if error>1e-6:report['failures'].append('v0.2 changed '+name)
# The local fabric-ease correction must also remain clear in earlier clips.
report['legacy_cloth']={}
for name,duration in [('Idle',4.0),('Walk',1.2),('WalkStart',.7),('WalkStopL',.8),('WalkStopR',.8)]:
    action=next(a for a in bpy.data.actions if a.name==name)
    rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
    hits=inside=0;count=0
    for frame in range(0,round(duration*60)+1,3):
        bpy.context.scene.frame_set(frame);v,f=surface(body);fabric,polys=surface(cloth)
        tree=BVHTree.FromPolygons(v,f);garment=BVHTree.FromPolygons(fabric,polys)
        hits+=len(tree.overlap(garment));count+=1
        for vertex in fabric:
            hit,normal,_,_=tree.find_nearest(vertex);inside+=int((vertex-hit).dot(normal)<-.0001)
    report['legacy_cloth'][name]={'sampled_poses':count,'body_intersections':hits,'inside_vertices':inside}
    if hits or inside:report['failures'].append('legacy clothing '+name)

report['passed']=not report['failures'];(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n');(ROOT/'prototype/tests/locomotion_v03_bounds.json').write_text(json.dumps(bounds,indent=2)+'\n')
print('RUN_VALIDATION',report['passed'],report['failures'],report['joins'])
assert report['passed'],report['failures']
