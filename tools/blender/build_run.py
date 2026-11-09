"""Relaxed unarmed Run and contact-matched gait changes, based on frozen v0.2."""
import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_locomotion import ease5, pose_curve, pose_matrix, soft_positive
OUT=ROOT/'tools/blender/locomotion_v03';OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'assets/Blender Models/Human-Male-Locomotion-v0.2.blend'
FPS=60; PERIOD=.8; SPEED=2.2; DUTY=.4
# One second gives 61 samples; a small interior correction preserves phase
# endpoint rates while advancing exactly one cycle.
TRANSITION=1.0

def integral_ease(u):return 2.5*u**4-3*u**5+u**6

def bridge_phase(t,to_run):
    u=t/TRANSITION;a,b=(1/1.2,1/PERIOD) if to_run else (1/PERIOD,1/1.2)
    total=(a+b)*TRANSITION/2
    return a*t+(b-a)*TRANSITION*integral_ease(u)+(1-total)*ease5(u)

def distance(t,to_run):
    a,b=(.9,SPEED) if to_run else (SPEED,.9)
    return a*t+(b-a)*TRANSITION*integral_ease(t/TRANSITION)

def main():
    manifest=json.loads((ROOT/'tools/blender/locomotion_v02/v02_manifest.json').read_text())
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==manifest['files']['assets/Blender Models/Human-Male-Locomotion-v0.2.blend']
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE));scene=bpy.context.scene;scene.render.fps=FPS
    rig=bpy.data.objects['Human.rig'];rest={b.name:b for b in rig.data.bones}
    original_actions={a.name:a for a in bpy.data.actions}
    # The larger hip range exposes up to 3.8 mm penetration at the exported
    # centre-front crotch. Add local fabric ease in this derivative only.
    garment=bpy.data.objects['Gauntlands_Boxer_Briefs']
    inverse=garment.matrix_world.inverted().to_3x3()
    for vertex in garment.data.vertices:
        point=garment.matrix_world@vertex.co
        amount=.008*math.exp(-(point.x/.065)**2)*max(0,min(1,(-point.y-.025)/.07))
        vertex.co+=inverse@Vector((0,-amount,0))

    initial_scale={p.name:p.scale.copy() for p in rig.pose.bones}
    def read_pose():return {p.name:(p.location.copy(),p.rotation_quaternion.copy()) for p in rig.pose.bones}
    walk=bpy.data.actions['Walk'];rig.animation_data.action=walk;rig.animation_data.action_slot=walk.slots[0]
    walk_cache=[]
    for i in range(73):scene.frame_set(i+1);walk_cache.append(read_pose())
    def sample(cache,phase):
        f=(phase%1)*(len(cache)-1);i=int(f);u=f-i
        return {n:(cache[i][n][0].lerp(cache[i+1][n][0],u),cache[i][n][1].slerp(cache[i+1][n][1],u)) for n in cache[0]}
    def apply(a,b=None,w=0):
        for p in rig.pose.bones:
            p.rotation_mode='QUATERNION';p.scale=initial_scale[p.name]
            p.location=a[p.name][0] if b is None else a[p.name][0].lerp(b[p.name][0],w)
            p.rotation_quaternion=a[p.name][1] if b is None else a[p.name][1].slerp(b[p.name][1],w)
        bpy.context.view_layer.update()
    tips={s:Vector(v) for s,v in json.loads((ROOT/'tools/blender/locomotion_previews/build.json').read_text())['sole_tip_anchors'].items()}
    def solve(targets):
        drop=0.
        for side,(ankle,_) in targets.items():
            h=rig.pose.bones['upperleg01.'+side].head.copy();h0=rest['upperleg01.'+side].head_local;k0=rest['lowerleg01.'+side].head_local;a0=rest['foot.'+side].head_local
            reach=(k0-h0).length+(a0-k0).length-.005;horizontal=(h.x-ankle.x)**2+(h.y-ankle.y)**2
            assert horizontal<reach*reach
            drop=max(drop,h.z-ankle.z-math.sqrt(reach*reach-horizontal))
        if drop>0:
            m=rig.pose.bones['root'].matrix.copy();m.translation.z-=drop;rig.pose.bones['root'].matrix=m;bpy.context.view_layer.update()
        for side,(ankle,rotations) in targets.items():
            upper=rig.pose.bones['upperleg01.'+side];lower=rig.pose.bones['lowerleg01.'+side];foot=rig.pose.bones['foot.'+side]
            hip=upper.head.copy();h0=rest[upper.name].head_local;k0=rest[lower.name].head_local;a0=rest[foot.name].head_local
            l1=(k0-h0).length;l2=(a0-k0).length;delta=ankle-hip;d=delta.length;axis=delta.normalized();bend=Vector((0,-1,0));bend=(bend-axis*bend.dot(axis)).normalized()
            along=(l1*l1-l2*l2+d*d)/(2*d);knee=hip+axis*along+bend*math.sqrt(max(0,l1*l1-along*along))
            upper.matrix=pose_matrix(rest[upper.name],hip,(k0-h0).rotation_difference(knee-hip));bpy.context.view_layer.update()
            lower.matrix=pose_matrix(rest[lower.name],knee,(a0-k0).rotation_difference(ankle-knee));bpy.context.view_layer.update()
            foot.matrix=pose_matrix(rest[foot.name],ankle,rotations[0]);bpy.context.view_layer.update()
            toe=rig.pose.bones['toe1-1.'+side];toe.matrix=pose_matrix(rest[toe.name],toe.head.copy(),rotations[1]);bpy.context.view_layer.update()
    def new_action(name):
        rig.animation_data.action=None
        a=bpy.data.actions.new(name);a.use_fake_user=True;rig.animation_data.action=a;return a
    def key(frame):
        for p in rig.pose.bones:
            p.keyframe_insert('location',frame=frame,group=p.name);p.keyframe_insert('rotation_quaternion',frame=frame,group=p.name)
    def foot_target(side,phase):
        sign=1 if side=='L' else -1;p=phase%1;stride=SPEED*PERIOD;travel=stride*DUTY
        if p<=DUTY:y=-travel/2+stride*p;lift=0
        else:
            u=(p-DUTY)/(1-DUTY);velocity=stride*(1-DUTY)
            y=travel/2+velocity*u-(travel+velocity)*ease5(u)
            lift=.115*16*u*u*(1-u)**2+.055*(u*u*(1-u)**4)/((1/3)**2*(2/3)**4)
        pitch=math.radians(pose_curve(p,((0,-5,0),(.08,0,0),(.16,0,0),(.32,22,160),(.40,34,100),(.48,40,0),(.72,4,-160),(1,-5,0))))
        peel=math.radians(pose_curve(p,((.32,0,0),(.40,8,120),(.48,14,0),(.64,0,0))))
        heel=Vector((rest['foot.'+side].head_local.x,.045,0));ball=rest['toe1-1.'+side].head_local.copy()
        pivot=heel if p<.16 else ball
        toe_angle=peel if p>=.16 else pitch
        if p>DUTY:
            u=(p-DUTY)/(1-DUTY);pivot=ball.lerp(heel,ease5(u));release=ease5(min(1,(p-DUTY)/.12));toe_angle=peel*(1-release)+pitch*release
        q=Quaternion((1,0,0),pitch);offset=q@(rest['foot.'+side].head_local-pivot)-(rest['foot.'+side].head_local-pivot)
        if p>=.16:offset+=(tips[side]-ball)-Quaternion((1,0,0),peel)@(tips[side]-ball)
        yaw=Quaternion((0,0,1),math.radians(sign*4))
        return Vector((sign*.125,y,rest['foot.'+side].head_local.z+.003+lift))+yaw@offset,(yaw@q,yaw@Quaternion((1,0,0),toe_angle))
    run=new_action('Run');run_cache=[]
    for i in range(49):
        scene.frame_set(i+1);phase=i/48;cycle=2*math.pi*phase;apply(sample(walk_cache,phase))
        yaw=-math.radians(6)*math.cos(cycle);tilt=-math.radians(1.6)*math.sin(cycle);lean=math.radians(6)
        bob=pose_curve(phase%.5,((0,-.080,-.20),(.11,-.090,0),(.32,-.045,.30),(.42,-.025,0),(.5,-.080,-.20)))
        root=rig.pose.bones['root'];rotation=Quaternion((1,0,0),lean)@Quaternion((0,0,1),yaw)@Quaternion((0,1,0),tilt)
        root.matrix=pose_matrix(rest['root'],rest['root'].head_local+Vector((.018*math.sin(cycle),-.025,bob)),rotation);bpy.context.view_layer.update()
        chest_yaw=math.radians(7)*math.cos(cycle-.12)
        for j,name in enumerate(['spine05','spine04','spine03','spine02','spine01'],1):
            amount=j/5;bone=rig.pose.bones[name];rot=Quaternion((1,0,0),lean)@Quaternion((0,0,1),yaw*(1-amount)+chest_yaw*amount)@Quaternion((0,1,0),tilt*(1-.5*amount))
            bone.matrix=pose_matrix(rest[name],bone.head.copy(),rot);bpy.context.view_layer.update()
        head=rig.pose.bones['head'];head.matrix=pose_matrix(rest['head'],head.head.copy(),Quaternion((1,0,0),math.radians(1.5)));bpy.context.view_layer.update()
        for side,sign in [('L',1),('R',-1)]:
            chest=rig.pose.bones['spine01'].matrix.to_quaternion()@rest['spine01'].matrix_local.to_quaternion().inverted()
            upper=rig.pose.bones['upperarm01.'+side];lower=rig.pose.bones['lowerarm01.'+side];wrist=rig.pose.bones['wrist.'+side]
            swing=math.cos(cycle-.20)*sign;across=.075-.012*max(0,-swing)**2
            direction=chest@Vector((sign*across,.18*swing,-.27))
            q=(rest[lower.name].head_local-rest[upper.name].head_local).rotation_difference(direction);upper.matrix=pose_matrix(rest[upper.name],upper.head.copy(),q);bpy.context.view_layer.update()
            lag=math.cos(cycle-.30)*sign;angle=math.atan2(.18*lag,.27)-math.radians(70-8*lag)
            direction=chest@Vector((sign*.035,.27*math.sin(angle),-.27*math.cos(angle)))
            q=(rest[wrist.name].head_local-rest[lower.name].head_local).rotation_difference(direction);lower.matrix=pose_matrix(rest[lower.name],lower.head.copy(),q);bpy.context.view_layer.update()
            wrist.matrix=pose_matrix(rest[wrist.name],wrist.head.copy(),q);bpy.context.view_layer.update()
        targets={s:foot_target(s,phase+o) for s,o in [('L',0),('R',.5)]}
        for side,o in [('L',0),('R',.5)]:
            p=(phase+o)%1
            if p<=DUTY:continue
            ankle,_=targets[side];hip=rig.pose.bones['upperleg01.'+side].head
            h0=rest['upperleg01.'+side].head_local;k0=rest['lowerleg01.'+side].head_local;a0=rest['foot.'+side].head_local
            l1=(k0-h0).length;l2=(a0-k0).length
            flex=math.radians(pose_curve(p,((.4,40,30),(.6,82,0),(.7,60,-260),(.85,35,-100),(.93,28,-50),(1,34.632,265))))
            reach2=l1*l1+l2*l2+2*l1*l2*math.cos(flex)
            ankle.z=hip.z-math.sqrt(max(.01,reach2-(hip.x-ankle.x)**2-(hip.y-ankle.y)**2))
            clearance=max(0,min(1,(p-.4)/.16))
            ankle.z+=.010*64*clearance**3*(1-clearance)**3
        solve(targets);key(i+1);run_cache.append(read_pose())
    travel={};metadata={};clips={'Run':PERIOD}
    # Blend complete poses at a common gait phase, then lock each stance interval
    # in travelling world space. Swing corrections join the locked intervals.
    for to_run in [True,False]:
      for lead,offset in [('L',0),('R',.5)]:
        name=('WalkToRun' if to_run else 'RunToWalk')+lead;action=new_action(name);frames=60;raw=[];records={s:[] for s in ['L','R']};travel[name]=[]
        for i in range(frames+1):
            t=i/FPS;u=t/TRANSITION;w=ease5(u);phase=bridge_phase(t,to_run)+offset;run_weight=w if to_run else 1-w
            scene.frame_set(i+1);apply(sample(walk_cache,phase),sample(run_cache,phase),run_weight);raw.append(read_pose());d=distance(t,to_run);travel[name].append(d)
            for side,o in [('L',0),('R',.5)]:
                p=(phase+o)%1
                if i==frames:p=(offset+o)%1
                duty=.6*(1-run_weight)+DUTY*run_weight;heel_end=.12*(1-run_weight)+.08*run_weight;toe_start=.34*(1-run_weight)+.16*run_weight;tip_start=.52*(1-run_weight)+.32*run_weight
                stage=None if p>duty+1e-8 else ('heel' if p<heel_end else 'sole' if p<toe_start else 'toe' if p<tip_start else 'tip')
                foot=rig.pose.bones['foot.'+side];toe=rig.pose.bones['toe1-1.'+side]
                rotations=tuple(b.matrix.to_quaternion()@rest[b.name].matrix_local.to_quaternion().inverted() for b in [foot,toe])
                anchors={}
                for st in ['heel','sole','toe','tip']:
                    bn=toe if st in ['toe','tip'] else foot;anchor=rest[bn.name].head_local.copy();anchor.z=0
                    if st=='heel':anchor.y=.045
                    if st=='toe':anchor.y=-.19
                    if st=='tip':anchor=tips[side]
                    anchors[st]=bn.matrix@rest[bn.name].matrix_local.inverted()@anchor
                if stage is not None:stage=min(anchors,key=lambda st:anchors[st].z)
                records[side].append({'ankle':foot.head.copy(),'rotations':rotations,'stage':stage,'anchors':anchors})
        corrections={}
        for side,data in records.items():
            corr=[None]*(frames+1);groups=[];j=0
            while j<=frames:
                if data[j]['stage'] is None:j+=1;continue
                start=j
                while j<frames and data[j+1]['stage'] is not None:j+=1
                end=j;groups.append((start,end));j+=1
                backward=end==frames
                indices=list(range(end,start-1,-1) if backward else range(start,end+1))
                seed=indices[0];corr[seed]=Vector()
                if start>0 and end<frames:
                    corr[seed].z=.003-data[seed]['anchors'][data[seed]['stage']].z
                for previous,current in zip(indices,indices[1:]):
                    st=data[current]['stage'];corr[current]=corr[previous].copy()
                    if st==data[previous]['stage']:
                        delta=data[current]['anchors'][st]-data[previous]['anchors'][st]
                        corr[current].y+=travel[name][current]-travel[name][previous]-delta.y
                        corr[current].z-=delta.z
                        corr[current].x-=delta.x
            # Quintic correction blends preserve position, velocity and acceleration
            # at take-off and touchdown. Endpoints are exactly the source poses.
            if corr[0] is None:corr[0]=Vector()
            if corr[-1] is None:corr[-1]=Vector()
            j=1
            while j<frames:
                if corr[j] is not None:j+=1;continue
                a=j-1
                while corr[j] is None:j+=1
                b=j;n=b-a
                va=(corr[a]-corr[a-1]) if a>0 and corr[a-1] is not None else Vector()
                vb=(corr[b+1]-corr[b]) if b<frames and corr[b+1] is not None else Vector()
                for k in range(a+1,b):
                    u=(k-a)/n;c0=corr[a];c1=va*n;end=corr[b];v1=vb*n
                    c3=10*(end-c0)-6*c1-4*v1;c4=-15*(end-c0)+8*c1+7*v1;c5=6*(end-c0)-3*c1-3*v1
                    corr[k]=c0+c1*u+c3*u**3+c4*u**4+c5*u**5
            corrections[side]=corr
        desired=[];root_offsets=[]
        for i in range(frames+1):
            scene.frame_set(i+1);apply(raw[i]);angles={};offsets=[]
            for side in ['L','R']:
                h=rig.pose.bones['upperleg01.'+side].head;k=rig.pose.bones['lowerleg01.'+side].head;a=rig.pose.bones['foot.'+side].head
                flex=math.pi-(h-k).angle(a-k);angles[side]=flex
                if records[side][i]['stage'] is None:continue
                ankle=records[side][i]['ankle']+corrections[side][i]
                h0=rest['upperleg01.'+side].head_local;k0=rest['lowerleg01.'+side].head_local;a0=rest['foot.'+side].head_local
                l1=(k0-h0).length;l2=(a0-k0).length
                reach2=l1*l1+l2*l2+2*l1*l2*math.cos(flex)
                offsets.append(ankle.z+math.sqrt(max(.01,reach2-(h.x-ankle.x)**2-(h.y-ankle.y)**2))-h.z)
            desired.append(angles);root_offsets.append(min(offsets) if offsets else None)
        root_offsets[0]=root_offsets[-1]=0.
        for i in range(1,frames):
            if root_offsets[i] is not None:continue
            a=i-1;b=i+1
            while root_offsets[b] is None:b+=1
            root_offsets[i]=root_offsets[a]+(root_offsets[b]-root_offsets[a])/(b-a)
        smooth=[sum(weight*root_offsets[max(0,min(frames,i+j))] for j,weight in [(-2,1),(-1,4),(0,6),(1,4),(2,1)])/16 for i in range(frames+1)]
        support_delta={side:{} for side in ['L','R']}
        for i in range(frames+1):
            scene.frame_set(i+1);apply(raw[i])
            height_offset=smooth[i]*ease5(min(1,i/5))*ease5(min(1,(frames-i)/5))
            for side in ['L','R']:
                if records[side][i]['stage'] is None:continue
                h=rig.pose.bones['upperleg01.'+side].head.copy();h.z+=height_offset
                ankle=records[side][i]['ankle']+corrections[side][i]
                h0=rest['upperleg01.'+side].head_local;k0=rest['lowerleg01.'+side].head_local;a0=rest['foot.'+side].head_local
                l1=(k0-h0).length;l2=(a0-k0).length
                cosine=((ankle-h).length_squared-l1*l1-l2*l2)/(2*l1*l2)
                support_delta[side][i]=math.acos(max(-1,min(1,cosine)))-desired[i][side]
        for i in range(frames+1):
            scene.frame_set(i+1);apply(raw[i])
            envelope=ease5(min(1,i/5))*ease5(min(1,(frames-i)/5))
            m=rig.pose.bones['root'].matrix.copy();m.translation.z+=smooth[i]*envelope;rig.pose.bones['root'].matrix=m;bpy.context.view_layer.update()
            targets={side:(records[side][i]['ankle']+corrections[side][i],records[side][i]['rotations']) for side in ['L','R']}
            if i not in [0,frames]:
                for side in ['L','R']:
                    if records[side][i]['stage'] is not None:continue
                    h=rig.pose.bones['upperleg01.'+side].head;ankle=targets[side][0];flex=desired[i][side]
                    previous=max((j for j in support_delta[side] if j<i),default=None)
                    following=min((j for j in support_delta[side] if j>i),default=None)
                    if previous is not None:flex+=support_delta[side][previous]*(1-ease5(min(1,(i-previous)/6)))
                    if following is not None:flex+=support_delta[side][following]*(1-ease5(min(1,(following-i)/6)))
                    h0=rest['upperleg01.'+side].head_local;k0=rest['lowerleg01.'+side].head_local;a0=rest['foot.'+side].head_local
                    l1=(k0-h0).length;l2=(a0-k0).length
                    reach2=l1*l1+l2*l2+2*l1*l2*math.cos(flex)
                    ankle.z=h.z-math.sqrt(max(.01,reach2-(h.x-ankle.x)**2-(h.y-ankle.y)**2))
                    lowest=min(p.z for p in records[side][i]['anchors'].values())+ankle.z-records[side][i]['ankle'].z
                    ankle.z+=soft_positive(.003-lowest,.003)
                solve(targets)
            key(i+1)
        clips[name]=TRANSITION;metadata[name]={'from':'Walk' if to_run else 'Run','to':'Run' if to_run else 'Walk','phase':offset,'contact_stages':{s:[r['stage'] for r in records[s]] for s in records}}
    for a in bpy.data.actions:
        if a.name in original_actions:continue
        for layer in a.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for c in bag.fcurves:
                        for k in c.keyframe_points:k.interpolation='LINEAR'
    for p in rig.pose.bones:p.scale=initial_scale[p.name]
    rig.animation_data.action=run;rig.animation_data.action_slot=run.slots[0];scene.frame_start=1;scene.frame_end=49;scene.frame_set(1)
    for o in scene.objects:o.select_set(False)
    for o in [rig,*rig.children_recursive]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    blend=SOURCE.with_name('Human-Male-Locomotion-v0.3.blend');glb=ROOT/'prototype/assets/human_locomotion_v03.glb'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend),copy=True)
    for name,duration in clips.items():
        action=bpy.data.actions[name];rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0];angles=[]
        for i in range(round(duration*FPS)+1):
            scene.frame_set(i+1);row=[]
            for side in ['L','R']:
                h=rig.pose.bones['upperleg01.'+side].head;k=rig.pose.bones['lowerleg01.'+side].head;a=rig.pose.bones['foot.'+side].head
                row.append(180-math.degrees((h-k).angle(a-k)))
            angles.append(row)
        acceleration=max((abs(c[j]-2*b[j]+a[j]),i+1,j) for i,(a,b,c) in enumerate(zip(angles,angles[1:],angles[2:])) for j in [0,1])
        print('SOURCE_KNEE',name,acceleration,flush=True)
    if '--source-only' in sys.argv:return
    # Preserve the original export's active Idle scale state.
    rig.animation_data.action=original_actions['Idle'];rig.animation_data.action_slot=original_actions['Idle'].slots[0];scene.frame_set(1)
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_animation_mode='ACTIONS',export_animations=True,export_frame_range=False,export_anim_slide_to_zero=True,export_force_sampling=True,export_influence_nb=8,export_morph=False)
    report={'version':'0.3-run-first-pass','fps':FPS,'run_period':PERIOD,'run_speed':SPEED,'run_duty':DUTY,'clips':clips,'transitions':metadata,'travel_m_at_60hz':travel,'glb_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest()}
    (OUT/'build.json').write_text(json.dumps(report,indent=2)+'\n');print('RUN_BUILT',clips,flush=True)
if __name__=='__main__':main()
