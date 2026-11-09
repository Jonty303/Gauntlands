"""v0.2 transition block-in, preserving the approved v0.1 Walk action.
Run Blender --background --factory-startup --python-exit-code 1 --python this_file.
"""
import bpy, math, json, hashlib, sys
from pathlib import Path
from mathutils import Vector, Matrix, Quaternion
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(Path(__file__).resolve().parent))
from build_locomotion import ease5, pose_curve, pose_matrix, FOOT_ROLL_KEYS, TOE_PEEL_KEYS, soft_positive
OUT=ROOT/'tools/blender/locomotion_v02';OUT.mkdir(exist_ok=True)
SOURCE=ROOT/'assets/Blender Models/Human-Male-Locomotion.blend'
FPS=60; DURATION=.8
START_DURATION=.7
START_LIFT_TIME=.1
START_LEAN_DEGREES=1.25
START_HIP_LEAD_M=.006

def unit(x):return max(0.,min(1.,x))
def integral_ease(u):return 2.5*u**4-3*u**5+u**6

def distance(name,t):
    if name=='WalkStart':
        # Integral of a smooth asymmetric speed ramp: same 0.216 m endpoint.
        u=unit((t-.14)/.56)
        return .9*.56*(3*u**5-4*u**6+(10/7)*u**7)
    if name.startswith('WalkStop'):
        u=unit(t/.72);return .9*.72*(u-integral_ease(u))
    return .9*t if name=='Walk' else 0.

def main():
    manifest=json.loads((ROOT/'tools/blender/locomotion_previews/v01_manifest.json').read_text())
    source_hash=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert source_hash==manifest['files']['assets/Blender Models/Human-Male-Locomotion.blend']
    bpy.ops.wm.open_mainfile(filepath=str(SOURCE))
    scene=bpy.context.scene;scene.render.fps=FPS
    rig=bpy.data.objects['Human.rig'];rest={b.name:b for b in rig.data.bones}
    walk=bpy.data.actions['Walk'];old_idle=bpy.data.actions['Idle']
    def curves(action):
        return [(c.data_path,c.array_index,[(tuple(k.co),k.interpolation) for k in c.keyframe_points]) for layer in action.layers for strip in layer.strips for bag in strip.channelbags for c in bag.fcurves]
    walk_curves=curves(walk)
    def read_pose(action,frame):
        rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
        scene.frame_set(math.floor(frame),subframe=frame%1)
        return {b.name:(b.location.copy(),b.rotation_quaternion.copy()) for b in rig.pose.bones}
    cache={'Idle':[read_pose(old_idle,i+1) for i in range(241)],'Walk':[read_pose(walk,i+1) for i in range(73)]}
    def sample(name,time):
        data=cache[name];f=(time*FPS)%(len(data)-1);i=int(f);u=f-i
        return {n:(data[i][n][0].lerp(data[i+1][n][0],u),data[i][n][1].slerp(data[i+1][n][1],u)) for n in data[0]}
    def apply(a,b=None,w=0):
        for p in rig.pose.bones:
            p.rotation_mode='QUATERNION'
            p.location=a[p.name][0] if b is None else a[p.name][0].lerp(b[p.name][0],w)
            p.rotation_quaternion=a[p.name][1] if b is None else a[p.name][1].slerp(b[p.name][1],w)
        bpy.context.view_layer.update()
    tips={s:Vector(v) for s,v in json.loads((ROOT/'tools/blender/locomotion_previews/build.json').read_text())['sole_tip_anchors'].items()}
    def rocker(side,p,strength=1.):
        heel=Vector((rest['foot.'+side].head_local.x,.045,0));ball=rest['toe1-1.'+side].head_local.copy()
        peel=0
        if p<.12:
            u=unit(p/.12);pitch=math.radians(-12)*(1-u*u*(3-2*u));toe=pitch;pivot=heel
        elif p<.34:pitch=toe=0.;pivot=heel
        else:
            pitch=math.radians(pose_curve(p,FOOT_ROLL_KEYS));peel=math.radians(pose_curve(p,TOE_PEEL_KEYS));toe=peel;pivot=ball
            if p>.6:
                pivot=ball.lerp(heel,ease5(unit((p-.6)/.4)))
                release=ease5(unit((p-.6)/.1));toe=peel*(1-release)+pitch*release
        pitch*=strength;toe*=strength;peel*=strength
        local=rest['foot.'+side].head_local-pivot
        offset=Quaternion((1,0,0),pitch)@local-local
        if p>=.34:offset+=(tips[side]-ball)-Quaternion((1,0,0),peel)@(tips[side]-ball)
        return offset,pitch,toe
    def target(side,y,lift,p=None,strength=1.):
        sign=1 if side=='L' else -1;heading=math.radians(sign*4)
        offset,pitch,toe=rocker(side,p,strength) if p is not None else (Vector(),0.,0.)
        ankle=Vector((sign*.125,y,rest['foot.'+side].head_local.z+.003+lift))+Quaternion((0,0,1),heading)@offset
        return ankle,(pitch,toe,heading)
    def solve(targets):
        # Same analytic knee plane and 5 mm reach reserve as approved v0.1.
        drop=0.
        for side,(ankle,_) in targets.items():
            h=rig.pose.bones['upperleg01.'+side].head.copy()
            h0=rest['upperleg01.'+side].head_local;k0=rest['lowerleg01.'+side].head_local;a0=rest['foot.'+side].head_local
            reach=(k0-h0).length+(a0-k0).length-.005
            horizontal=(h.x-ankle.x)**2+(h.y-ankle.y)**2
            assert horizontal<reach*reach
            drop=max(drop,h.z-ankle.z-math.sqrt(reach*reach-horizontal))
        if drop>0:
            m=rig.pose.bones['root'].matrix.copy();m.translation.z-=drop;rig.pose.bones['root'].matrix=m;bpy.context.view_layer.update()
        for side,(ankle,(pitch,toe_angle,heading)) in targets.items():
            upper=rig.pose.bones['upperleg01.'+side];lower=rig.pose.bones['lowerleg01.'+side];foot=rig.pose.bones['foot.'+side]
            hip=upper.head.copy();h0=rest[upper.name].head_local;k0=rest[lower.name].head_local;a0=rest[foot.name].head_local
            l1=(k0-h0).length;l2=(a0-k0).length;delta=ankle-hip;d=delta.length;axis=delta.normalized()
            bend=Vector((0,-1,0));bend=(bend-axis*bend.dot(axis)).normalized();along=(l1*l1-l2*l2+d*d)/(2*d)
            knee=hip+axis*along+bend*math.sqrt(max(0,l1*l1-along*along))
            upper.matrix=pose_matrix(rest[upper.name],hip,(k0-h0).rotation_difference(knee-hip));bpy.context.view_layer.update()
            lower.matrix=pose_matrix(rest[lower.name],knee,(a0-k0).rotation_difference(ankle-knee));bpy.context.view_layer.update()
            yaw=Quaternion((0,0,1),heading)
            foot.matrix=pose_matrix(rest[foot.name],ankle,yaw@Quaternion((1,0,0),pitch));bpy.context.view_layer.update()
            toe=rig.pose.bones['toe1-1.'+side];toe.matrix=pose_matrix(rest[toe.name],toe.head.copy(),yaw@Quaternion((1,0,0),toe_angle));bpy.context.view_layer.update()
    rig.animation_data.action=None;bpy.data.actions.remove(old_idle)
    clips={};travel={}
    for name,frames in [('Idle',240),('WalkStart',round(START_DURATION*FPS)),('WalkStopL',48),('WalkStopR',48)]:
        rig.animation_data.action=None
        action=bpy.data.actions.new(name);action.use_fake_user=True;rig.animation_data.action=action
        travel[name]=[]
        for i in range(frames+1):
            t=i/FPS;duration=START_DURATION if name=='WalkStart' else DURATION;u=t/duration;w=ease5(unit(u));d=distance(name,t)
            scene.frame_set(i+1)
            if name=='Idle':apply(sample('Idle',t))
            elif name=='WalkStart':
                join_time=(t-START_DURATION)*ease5(unit((u-.6)/.4))
                apply(sample('Idle',t),sample('Walk',join_time),w)
                m=rig.pose.bones['root'].matrix.copy()
                m.translation.x-=.018*math.sin(math.pi*unit(u))**2
                # Tip the whole body from the planted base, rather than bowing at the waist.
                lean=ease5(unit((t-.06)/.30))*(1-ease5(unit((t-.38)/.27)))
                m=Matrix.Rotation(math.radians(START_LEAN_DEGREES)*lean,4,'X')@m
                lead=ease5(unit(t/.20))*(1-ease5(unit((t-.30)/.30)))
                m.translation.y-=START_HIP_LEAD_M*lead
                rig.pose.bones['root'].matrix=m;bpy.context.view_layer.update()
            else:apply(sample('Walk',t+(0 if name=='WalkStopL' else .6)),sample('Idle',t-DURATION),w)
            targets={}
            if name=='Idle':targets={s:target(s,0,0) for s in ['L','R']}
            elif name=='WalkStart':
                a=unit((t-START_LIFT_TIME)/.6);lift=.065*math.sin(math.pi*a)**2
                targets['L']=target('L',d-.54*ease5(a),lift,p=.34+.66*a,strength=.4+.6*ease5(unit((a-.6)/.4)))
                # Fixed support foot, then roll onto its ball with the Walk join velocity.
                p=.34 if t<.4 else .34+.16*pose_curve(t,((.4,0,0),(.7,1,(1/1.2)/.16)))
                targets['R']=target('R',d,0,p=p)
            else:
                leading='L' if name=='WalkStopL' else 'R';trailing='R' if leading=='L' else 'L'
                targets[leading]=target(leading,-.324+d,0,p=min(.2,t/1.2))
                a=unit((t-.12)/.52)
                lift=.055*(a*a*(1-a)**4)/((1/3)**2*(2/3)**4)+.04*math.sin(math.pi*a)**2
                p=.5+t/1.2 if t<=.12 else (.6+.4*a if t<.64 else min(.12,(t-.64)/1.2))
                targets[trailing]=target(trailing,.216-.54*ease5(a)+d,lift,p=p)
            if name=='WalkStart' and START_LIFT_TIME<t<START_DURATION:
                # Keep the airborne knee softly flexed through recovery, as in Walk.
                # This avoids using the pelvis reach clamp to straighten the swing leg.
                ankle,roll=targets['L'];hip=rig.pose.bones['upperleg01.L'].head
                h0=rest['upperleg01.L'].head_local;k0=rest['lowerleg01.L'].head_local;a0=rest['foot.L'].head_local
                l1=(k0-h0).length;l2=(a0-k0).length
                flex=math.radians(pose_curve(a,((0,12,0),(.3,46,0),(.65,34,-60),(.9,17,-40),(1,16.5,100))))
                reach2=l1*l1+l2*l2+2*l1*l2*math.cos(flex)
                required=hip.z-math.sqrt(reach2-(hip.x-ankle.x)**2-(hip.y-ankle.y)**2)-ankle.z
                width=.02*ease5(unit(a/.15))*(1-ease5(unit((a-.82)/.10)))
                ankle.z+=soft_positive(required,width) if width>1e-9 else max(0,required)
            solve(targets)
            for p in rig.pose.bones:
                p.keyframe_insert('location',frame=i+1,group=p.name);p.keyframe_insert('rotation_quaternion',frame=i+1,group=p.name)
            travel[name].append(d)
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:key.interpolation='LINEAR'
        clips[name]=frames/FPS
    assert curves(walk)==walk_curves,'Approved Walk curves changed'
    clips['Walk']=1.2
    rig.animation_data.action=bpy.data.actions['Idle'];rig.animation_data.action_slot=bpy.data.actions['Idle'].slots[0]
    scene.frame_start=1;scene.frame_end=241;scene.frame_set(1)
    for o in scene.objects:o.select_set(False)
    for o in [rig,*rig.children_recursive]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    blend=SOURCE.with_name('Human-Male-Locomotion-v0.2.blend');glb=ROOT/'prototype/assets/human_locomotion_v02.glb'
    bpy.ops.wm.save_as_mainfile(filepath=str(blend),copy=True)
    bpy.ops.export_scene.gltf(filepath=str(glb),export_format='GLB',use_selection=True,export_apply=True,export_animation_mode='ACTIONS',export_animations=True,export_frame_range=False,export_anim_slide_to_zero=True,export_force_sampling=True,export_influence_nb=8,export_all_influences=False,export_morph=False)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==source_hash
    report={'version':'0.2-work-in-progress','baseline_tag':'human_male_prototype_v0.1','source_sha256':source_hash,'walk_curves_unchanged':True,'fps':60,'clips':clips,'travel_m_at_60hz':travel,'glb_sha256':hashlib.sha256(glb.read_bytes()).hexdigest(),'start_profile':{'duration_s':START_DURATION,'foot_lift_s':START_LIFT_TIME,'speed_ramp_start_s':.14,'speed_ramp_duration_s':.56,'whole_body_lean_degrees':START_LEAN_DEGREES,'hip_lead_m':START_HIP_LEAD_M,'lean_onset_s':.06,'lean_rise_s':.30,'hip_rise_s':.20},'start_walk_phase':0,'stop_walk_phases':{'WalkStopL':0,'WalkStopR':.5}}
    (OUT/'build.json').write_text(json.dumps(report,indent=2)+'\n')
    print('V02_BUILT',clips)
if __name__=='__main__':main()
