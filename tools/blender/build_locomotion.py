"""Author Idle and Walk on the accepted human; preserve source and diagnostic.
Walk: 1.2 s, 0.9 m/s reference travel, 60% stance, heel/sole/toe contact.
Run using Blender --background --factory-startup Human-Male-180cm.blend --python-exit-code 1 --python tools/blender/build_locomotion.py
"""
import bpy,math,json,hashlib
from pathlib import Path
from mathutils import Vector,Matrix,Quaternion
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'tools/blender/locomotion_previews'
SOURCE=ROOT/'assets/Blender Models/Human-Male-180cm.blend'
PERIOD=1.2
SPEED=.9
DUTY=.6
FPS=60
# Restrained weight transfer for this human, in metres and degrees.
PELVIS_SWAY=.028
# Per-step root-height poses: brief shallow settling, then one smooth rise/fall.
# Slopes are metres per full gait cycle; matching endpoint slopes close the loop.
PELVIS_HEIGHT_KEYS=((0,-.045,-.04),(.025,-.0455,0),(.27,-.0035,0),(.50,-.045,-.04))
# Soft minimum swing flexion keeps recovery from reaching full extension early.
SWING_KNEE_KEYS=((.60,28,0),(.75,56,-80),(.85,38,-260),(.94,18,-140),(1.0,16.5,180))
SWING_REACH_BLEND_M=.0015
SWING_REACH_RELEASE_PHASE=.94
PELVIS_YAW=4.0
PELVIS_TILT=2.0
PEAK_FOOT_ROLL_DEGREES=38
FOOT_TOE_OUT_DEGREES=4.0
HEEL_RISE_PHASE=.34
WEIGHT_SHIFT_LEAD=.025
# Relaxed unarmed baseline. Equipment-specific poses can override this group later.
UPPER_BODY_PROFILE="relaxed_unarmed"
ARM_SWING_M=.09
UPPER_ARM_INWARD_M=.022
FOREARM_INWARD_M=.018
ARM_RETURN_OUTWARD_M=.004
SHOULDER_FOLLOW=.45
CHEST_YAW_DEGREES=4.5
CHEST_PHASE_LAG=.015
SCAPULAR_YAW_DEGREES=2.2
SHOULDER_BANK_DEGREES=.9
SHOULDER_PHASE_LAG=.030
ARM_PHASE_LAG=.045
FOREARM_PHASE_LAG=.065
WRIST_PHASE_LAG=.085
# (cycle phase, degrees, degrees/cycle). Named poses retain velocity through toe-off.
FOOT_ROLL_KEYS=((.34,0,0),(.50,18,170),(.60,34,120),(.66,PEAK_FOOT_ROLL_DEGREES,0),(.82,5,-220),(1.0,-12,0))
TOE_PEEL_KEYS=((.52,0,0),(.60,12,180),(.65,18,0),(.80,0,0))
FINGER_CURL=(25,40,20)
THUMB_CURL=(0,5,5)
THUMB_ADDUCTION=.15

def ease5(t):
    # Zero velocity and acceleration at both ends.
    return t*t*t*(10+t*(-15+6*t))

def pose_curve(phase, keys):
    """Cubic Hermite between named poses; slopes are per full gait cycle."""
    if phase<=keys[0][0]:return keys[0][1]
    for (a,va,ma),(b,vb,mb) in zip(keys,keys[1:]):
        if phase<=b:
            u=(phase-a)/(b-a)
            return (2*u**3-3*u*u+1)*va+(u**3-2*u*u+u)*(b-a)*ma+(-2*u**3+3*u*u)*vb+(u**3-u*u)*(b-a)*mb
    return keys[-1][1]

def soft_positive(value, width):
    """C1 ramp into a reach correction; no sudden switch at the threshold."""
    if value<=-width:return 0.0
    if value>=width:return value
    return (value+width)**2/(4*width)

def pose_matrix(bone,position,rotation):
    return Matrix.Translation(position) @ (rotation @ bone.matrix_local.to_quaternion()).to_matrix().to_4x4()

def main():
    assert Path(bpy.data.filepath).resolve()==SOURCE.resolve()
    digest=hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    rig=bpy.data.objects['Human.rig'];scene=bpy.context.scene
    assert not rig.animation_data
    scene.render.fps=FPS
    rest={b.name:b for b in rig.data.bones}
    snapshots={};contacts=[]
    # Place the terminal rocker on the actual low front sole, not the toe
    # bone's decorative tail (glTF does not preserve bone tail locations).
    body=bpy.data.objects['Human']
    evaluated=body.evaluated_get(bpy.context.evaluated_depsgraph_get())
    mesh=evaluated.to_mesh()
    sole=[evaluated.matrix_world@v.co for v in mesh.vertices]
    tips={}
    for side in ['L','R']:
        ball=rest['toe1-1.'+side].head_local
        limit=rest['foot.'+side].head_local.z*.11
        tips[side]=min((v.copy() for v in sole if abs(v.x-ball.x)<.02 and v.z<limit),key=lambda v:v.y)
    evaluated.to_mesh_clear()
    # Keep the narrow crotch bridge from folding its inner shell through its
    # outer shell when the legs pass. Only weights in the generated derivative
    # change; geometry, source garment and body remain untouched.
    garment=bpy.data.objects['Gauntlands_Boxer_Briefs']
    neighbours=[set() for _ in garment.data.vertices]
    for edge in garment.data.edges:
        a,b=edge.vertices;neighbours[a].add(b);neighbours[b].add(a)
    for _ in range(10):
        weights=[{g.group:g.weight for g in v.groups} for v in garment.data.vertices]
        for v in garment.data.vertices:
            amount=.5*max(0,1-abs(v.co.x)/.07) if v.co.z<-.04 else 0
            if amount<=0:continue
            adjacent=neighbours[v.index]
            names=set(weights[v.index])
            for j in adjacent:names.update(weights[j])
            for group in sorted(names):
                value=(1-amount)*weights[v.index].get(group,0)+amount*sum(weights[j].get(group,0) for j in adjacent)/len(adjacent)
                garment.vertex_groups[group].add([v.index],value,'REPLACE')
    def reset():
        for p in rig.pose.bones:p.matrix_basis=Matrix.Identity(4);p.rotation_mode='QUATERNION'
        bpy.context.view_layer.update()
    def legs(targets, rolls):
        for side,ankle in targets.items():
            upper=rig.pose.bones['upperleg01.'+side]
            knee_bone=rig.pose.bones['lowerleg01.'+side]
            foot=rig.pose.bones['foot.'+side]
            hip=upper.head.copy()
            h0=rest[upper.name].head_local;k0=rest[knee_bone.name].head_local;a0=rest[foot.name].head_local
            l1=(k0-h0).length;l2=(a0-k0).length
            delta=ankle-hip;distance=delta.length
            if distance>=l1+l2:raise RuntimeError('Unreachable ankle target '+side+str(distance))
            axis=delta.normalized()
            bend=Vector((0,-1,0));bend=(bend-axis*bend.dot(axis)).normalized()
            along=(l1*l1-l2*l2+distance*distance)/(2*distance)
            knee=hip+axis*along+bend*math.sqrt(max(0,l1*l1-along*along))
            q=(k0-h0).rotation_difference(knee-hip)
            upper.matrix=pose_matrix(rest[upper.name],hip,q)
            bpy.context.view_layer.update()
            q=(a0-k0).rotation_difference(ankle-knee)
            knee_bone.matrix=pose_matrix(rest[knee_bone.name],knee,q)
            bpy.context.view_layer.update()
            # Counter-rotate toes for push-off; release smoothly during swing.
            pitch, toe_angle, heading = rolls[side]
            yaw_rotation=Quaternion((0,0,1),heading)
            rotation=yaw_rotation@Quaternion((1,0,0),pitch)
            foot.matrix=pose_matrix(rest[foot.name],ankle,rotation)
            bpy.context.view_layer.update()
            toe=rig.pose.bones['toe1-1.'+side]
            toe.matrix=pose_matrix(rest[toe.name],toe.head.copy(),yaw_rotation@Quaternion((1,0,0),toe_angle))
            bpy.context.view_layer.update()
            assert (foot.head-ankle).length<1e-5
    def arms(phase,walking):
        for side,sign in [('L',1),('R',-1)]:
            upper=rig.pose.bones['upperarm01.'+side];lower=rig.pose.bones['lowerarm01.'+side]
            hand=rest['wrist.'+side]
            if walking:
                cycle=2*math.pi*phase
                # Small delayed clavicle rotation follows the chest; alternating bank
                # raises one shoulder slightly while the other settles.
                clavicle=rig.pose.bones['clavicle.'+side]
                inherited=clavicle.matrix.to_quaternion()@rest[clavicle.name].matrix_local.to_quaternion().inverted()
                shoulder_cycle=cycle-2*math.pi*SHOULDER_PHASE_LAG
                scapula=Quaternion((0,0,1),math.radians(SCAPULAR_YAW_DEGREES)*math.cos(shoulder_cycle))@Quaternion((0,1,0),-math.radians(SHOULDER_BANK_DEGREES)*math.sin(shoulder_cycle))
                clavicle.matrix=pose_matrix(rest[clavicle.name],clavicle.head.copy(),scapula@inherited)
                bpy.context.view_layer.update()
                chest=rig.pose.bones['spine01'].matrix.to_quaternion()@rest['spine01'].matrix_local.to_quaternion().inverted()
                # Shoulder motion contributes to the arm plane without dragging
                # the whole arm rigidly with the clavicle.
                shoulder_frame=scapula@inherited
                arm_frame=chest.slerp(shoulder_frame,SHOULDER_FOLLOW)
                swing=math.cos(cycle-2*math.pi*ARM_PHASE_LAG)*sign
                forward=max(0,-swing)**2
                backward=max(0,swing)**2
                upper_across=.07-UPPER_ARM_INWARD_M*forward+ARM_RETURN_OUTWARD_M*backward
                upper_dir=arm_frame@Vector((sign*upper_across,ARM_SWING_M*swing,-.27))
                q=(rest[lower.name].head_local-rest[upper.name].head_local).rotation_difference(upper_dir)
                upper.matrix=pose_matrix(rest[upper.name],upper.head.copy(),q)
                bpy.context.view_layer.update()
                # Elbow flex increases on the forward swing; forearm lags upper arm.
                delayed=math.cos(cycle-2*math.pi*FOREARM_PHASE_LAG)*sign
                flex=math.radians(18-6*delayed)
                angle=math.atan2(ARM_SWING_M*delayed,.27)-flex
                forearm_across=.015-FOREARM_INWARD_M*max(0,-delayed)**2+ARM_RETURN_OUTWARD_M*max(0,delayed)**2
                lower_dir=arm_frame@Vector((sign*forearm_across,.27*math.sin(angle),-.27*math.cos(angle)))
                q=(hand.head_local-rest[lower.name].head_local).rotation_difference(lower_dir)
                lower.matrix=pose_matrix(rest[lower.name],lower.head.copy(),q)
                bpy.context.view_layer.update()
                wrist=rig.pose.bones['wrist.'+side]
                follow=math.radians(2)*math.sin(cycle-2*math.pi*WRIST_PHASE_LAG)*sign
                wrist.matrix=pose_matrix(rest[wrist.name],wrist.head.copy(),Quaternion((1,0,0),follow)@q)
                bpy.context.view_layer.update()
                continue
            swing=.08*math.sin(phase*2*math.pi)
            upper_dir=Vector((sign*.09,.075*swing,-.27))
            q=(rest[lower.name].head_local-rest[upper.name].head_local).rotation_difference(upper_dir)
            upper.matrix=pose_matrix(rest[upper.name],upper.head.copy(),q)
            bpy.context.view_layer.update()
            lower_dir=Vector((sign*.025,-.055+.08*swing,-.27))
            q=(hand.head_local-rest[lower.name].head_local).rotation_difference(lower_dir)
            lower.matrix=pose_matrix(rest[lower.name],lower.head.copy(),q)
            bpy.context.view_layer.update()
    def loose_fists():
        # Rest-pose palm normal defines flexion on both mirrored hands.
        for side,sign in [('L',1),('R',-1)]:
            along=(rest['finger3-1.'+side].tail_local-rest['finger3-1.'+side].head_local).normalized()
            across=rest['finger2-1.'+side].head_local-rest['finger5-1.'+side].head_local
            palm=along.cross(across).normalized()
            if palm.x*sign>0:palm.negate()
            for digit in range(1,6):
                curls=THUMB_CURL if digit==1 else FINGER_CURL
                for joint,degrees in enumerate(curls,1):
                    bone=rest[f'finger{digit}-{joint}.{side}']
                    axis=(bone.tail_local-bone.head_local).normalized().cross(palm).normalized()
                    local_axis=bone.matrix_local.to_3x3().inverted()@axis
                    rig.pose.bones[bone.name].rotation_quaternion=Quaternion(local_axis,math.radians(degrees))
            # Rest the thumb outside the curl rather than crossing through fingers.
            bone=rest['finger1-1.'+side]
            direction=(bone.tail_local-bone.head_local).normalized()
            target=(rest['finger2-1.'+side].head_local-bone.head_local).normalized()
            turn=Quaternion().slerp(direction.rotation_difference(target),THUMB_ADDUCTION)
            rotation=bone.matrix_local.to_quaternion()
            rig.pose.bones[bone.name].rotation_quaternion=rotation.inverted()@turn@rotation
        bpy.context.view_layer.update()
    for name,duration in [('Idle',4.0),('Walk',PERIOD)]:
        rig.animation_data_clear();reset()
        frames=round(duration*FPS)
        scene.frame_start=1;scene.frame_end=frames+1
        snapshots[name]={}
        for index in range(frames+1):
            phase=index/frames
            reset()
            walking=name=='Walk'
            root=rig.pose.bones['root']
            cycle=2*math.pi*phase
            if walking:
                # Shift towards the supporting leg; soften just after contact.
                sway=PELVIS_SWAY*math.sin(cycle+2*math.pi*WEIGHT_SHIFT_LEAD)
                bob=pose_curve(phase%.5,PELVIS_HEIGHT_KEYS)
                yaw=-math.radians(PELVIS_YAW)*math.cos(cycle)
                tilt=-math.radians(PELVIS_TILT)*math.sin(cycle)
                rotation=Quaternion((0,0,1),yaw)@Quaternion((0,1,0),tilt)
                root.matrix=pose_matrix(rest['root'],rest['root'].head_local+Vector((sway,0,bob)),rotation)
                bpy.context.view_layer.update()
                # Spread counter-rotation through the spine, rather than bending
                # everything at one waist joint. Chest turns opposite the pelvis.
                chest_yaw=math.radians(CHEST_YAW_DEGREES)*math.cos(cycle-2*math.pi*CHEST_PHASE_LAG)
                for order,bone_name in enumerate(['spine05','spine04','spine03','spine02','spine01'],1):
                    amount=order/5
                    spine=rig.pose.bones[bone_name]
                    chest=Quaternion((0,0,1),yaw*(1-amount)+chest_yaw*amount)@Quaternion((0,1,0),tilt*(1-.5*amount))
                    spine.matrix=pose_matrix(rest[bone_name],spine.head.copy(),chest)
                    bpy.context.view_layer.update()
                head=rig.pose.bones['head']
                head_rotation=Quaternion((0,0,1),-.1*yaw)@Quaternion((0,1,0),.15*tilt)
                head.matrix=pose_matrix(rest['head'],head.head.copy(),head_rotation)
                bpy.context.view_layer.update()
            else:
                # Preserve the existing Idle exactly.
                sway=.004*math.sin(cycle)
                bob=.002+.001*math.sin(cycle)
                root.matrix=Matrix.Translation((sway,0,bob)) @ rest['root'].matrix_local
                bpy.context.view_layer.update()
                spine=rig.pose.bones['spine02']
                rot=rest['spine02'].matrix_local.to_quaternion()
                angle=math.radians(.7)*math.sin(cycle)
                spine.rotation_quaternion=rot.inverted()@Quaternion((1,0,0),angle)@rot
                bpy.context.view_layer.update()
            targets={};rolls={}
            for side,sign,offset in [('L',1,0),('R',-1,.5)]:
                p=(phase+offset)%1
                y=0;lift=0
                if walking:
                    travel=SPEED*PERIOD*DUTY
                    if p<=DUTY:
                        y=-travel/2+SPEED*PERIOD*p
                    else:
                        u=(p-DUTY)/(1-DUTY)
                        # Quintic swing matches stance velocity AND acceleration.
                        # Advance the knee/foot clearance peak into initial swing.
                        velocity=SPEED*PERIOD*(1-DUTY)
                        y=travel/2+velocity*u-(travel+velocity)*ease5(u)
                        early=(u*u*(1-u)**4)/((1/3)**2*(2/3)**4)
                        lift=.055*early+.040*math.sin(math.pi*u)**2
                ankle=Vector((sign*.125,y,rest['foot.'+side].head_local.z+.003+lift))
                base_ankle=ankle.copy()
                pitch=0.0;toe_angle=0.0
                if walking:
                    smooth=lambda t: t*t*(3-2*t)
                    heel=Vector((rest['foot.'+side].head_local.x,.045,0))
                    ball=rest['toe1-1.'+side].head_local.copy()
                    if p<.12:
                        pitch=math.radians(-12)*(1-smooth(p/.12));pivot=heel;toe_angle=pitch
                    elif p<HEEL_RISE_PHASE:
                        pivot=heel
                    else:
                        pitch=math.radians(pose_curve(p,FOOT_ROLL_KEYS))
                        peel=math.radians(pose_curve(p,TOE_PEEL_KEYS))
                        pivot=ball
                        toe_angle=peel
                        if p>DUTY:
                            u=(p-DUTY)/(1-DUTY)
                            pivot=ball.lerp(heel,ease5(u))
                            release=ease5(min(1,(p-DUTY)/.10))
                            toe_angle=peel*(1-release)+pitch*release
                        # During terminal stance, rock the toe segment around its
                        # planted tip. Continue that offset into recovery, then
                        # remove it smoothly as the foot swings through.
                        tip=tips[side]
                        ankle+=(tip-ball)-Quaternion((1,0,0),peel)@(tip-ball)
                    # Compensate ankle translation around the planted pivot.
                    local=rest['foot.'+side].head_local-pivot
                    ankle+=Quaternion((1,0,0),pitch)@local-local
                # Rotate the rocker offsets around a common ankle reference.
                # A constant heading keeps the planted heel/ball/tip from swivelling.
                heading=math.radians(sign*FOOT_TOE_OUT_DEGREES) if walking else 0.0
                ankle=base_ankle+Quaternion((0,0,1),heading)@(ankle-base_ankle)
                reach_lift=0.0
                if walking and p>DUTY:
                    # Raise only the airborne ankle when its planned path would
                    # straighten the knee too early. Planted contacts stay fixed.
                    hip=rig.pose.bones['upperleg01.'+side].head
                    h0=rest['upperleg01.'+side].head_local
                    k0=rest['lowerleg01.'+side].head_local
                    a0=rest['foot.'+side].head_local
                    l1=(k0-h0).length;l2=(a0-k0).length
                    flex=math.radians(pose_curve(p,SWING_KNEE_KEYS))
                    reach2=l1*l1+l2*l2+2*l1*l2*math.cos(flex)
                    horizontal=(hip.x-ankle.x)**2+(hip.y-ankle.y)**2
                    required=hip.z-math.sqrt(reach2-horizontal)-ankle.z
                    # Fade the soft correction band to zero before contact,
                    # where the planted ankle must take over without a lift offset.
                    release=ease5(max(0,min(1,(p-SWING_REACH_RELEASE_PHASE)/(1-SWING_REACH_RELEASE_PHASE))))
                    width=SWING_REACH_BLEND_M*(1-release)
                    reach_lift=soft_positive(required,width) if width>1e-9 else max(0,required)
                    ankle.z+=reach_lift
                rolls[side]=(pitch,toe_angle,heading)
                targets[side]=ankle
                if walking:contacts.append(dict(frame=index+1,side=side,stance=p<=DUTY,phase=p,target=list(ankle),swing_reach_lift_m=reach_lift))
            # Lower the pelvis only as needed to keep both knees away from
            # full extension while the opposite foot is still planted.
            drop=0.0
            for side,ankle in targets.items():
                h=rig.pose.bones['upperleg01.'+side].head.copy()
                h0=rest['upperleg01.'+side].head_local
                k0=rest['lowerleg01.'+side].head_local
                a0=rest['foot.'+side].head_local
                reach=(k0-h0).length+(a0-k0).length-.005
                horizontal=(h.x-ankle.x)**2+(h.y-ankle.y)**2
                maximum=ankle.z+math.sqrt(reach*reach-horizontal)
                drop=max(drop,h.z-maximum)
            if drop>0:
                matrix=root.matrix.copy();matrix.translation.z-=drop
                root.matrix=matrix;bpy.context.view_layer.update()
            legs(targets,rolls);arms(phase,walking);loose_fists()
            for p in rig.pose.bones:
                p.keyframe_insert('location',frame=index+1,group=p.name)
                p.keyframe_insert('rotation_quaternion',frame=index+1,group=p.name)
            if index in [0,frames//4,frames//2,3*frames//4,frames]:
                snapshots[name][str(index+1)]={s:list(rig.pose.bones['foot.'+s].head) for s in ['L','R']}
        action=rig.animation_data.action;action.name=name;action.use_fake_user=True
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    for curve in bag.fcurves:
                        for key in curve.keyframe_points:key.interpolation='LINEAR'
    # Export mesh in the original bind/rest pose, never baked in an animated pose.
    rig.animation_data_clear();reset();scene.frame_set(1)
    rig.animation_data_create()
    rig.animation_data.action=bpy.data.actions["Idle"]
    rig.animation_data.action_slot=bpy.data.actions["Idle"].slots[0]
    scene.frame_set(1)
    images=set()
    for o in [rig,*rig.children_recursive]:
        if o.type=='MESH':
            for material in o.data.materials:
                images.update(n.image for n in material.node_tree.nodes if n.type=='TEX_IMAGE' and n.image)
    for image in images:
        image.reload();assert len(image.pixels)>0;image.pack()
    bpy.ops.object.select_all(action='DESELECT')
    for o in [rig,*rig.children_recursive]:o.select_set(True)
    bpy.context.view_layer.objects.active=rig
    bpy.ops.wm.save_as_mainfile(filepath=str(SOURCE.with_name('Human-Male-Locomotion.blend')),copy=True)
    bpy.ops.export_scene.gltf(filepath=str(ROOT/'prototype/assets/human_locomotion.glb'),export_format='GLB',use_selection=True,
        export_apply=True,export_animation_mode='ACTIONS',export_animations=True,export_frame_range=False,
        export_anim_slide_to_zero=True,export_force_sampling=True,export_influence_nb=8,export_all_influences=False,export_morph=False)
    assert hashlib.sha256(SOURCE.read_bytes()).hexdigest()==digest
    (OUT/'build.json').write_text(json.dumps(dict(source_sha256=digest,fps=FPS,walk_period=PERIOD,reference_speed_m_s=SPEED,
        pelvis_sway_m=PELVIS_SWAY,pelvis_height_keys=PELVIS_HEIGHT_KEYS,pelvis_height_period_cycles=.5,swing_knee_keys=SWING_KNEE_KEYS,swing_reach_blend_m=SWING_REACH_BLEND_M,swing_reach_release_phase=SWING_REACH_RELEASE_PHASE,pelvis_yaw_degrees=PELVIS_YAW,pelvis_tilt_degrees=PELVIS_TILT,
        upper_body_profile=UPPER_BODY_PROFILE,arm_swing_m=ARM_SWING_M,upper_arm_inward_m=UPPER_ARM_INWARD_M,forearm_inward_m=FOREARM_INWARD_M,arm_return_outward_m=ARM_RETURN_OUTWARD_M,shoulder_follow=SHOULDER_FOLLOW,
        chest_yaw_degrees=CHEST_YAW_DEGREES,chest_phase_lag=CHEST_PHASE_LAG,shoulder_bank_degrees=SHOULDER_BANK_DEGREES,shoulder_phase_lag=SHOULDER_PHASE_LAG,arm_phase_lag=ARM_PHASE_LAG,forearm_phase_lag=FOREARM_PHASE_LAG,wrist_phase_lag=WRIST_PHASE_LAG,scapular_yaw_degrees=SCAPULAR_YAW_DEGREES,elbow_flex_degrees=[12,24],finger_curl_degrees=FINGER_CURL,thumb_curl_degrees=THUMB_CURL,thumb_adduction_fraction=THUMB_ADDUCTION,
        foot_roll_keys=FOOT_ROLL_KEYS,toe_peel_keys=TOE_PEEL_KEYS,toe_release_phase=.70,heel_rise_phase=HEEL_RISE_PHASE,weight_shift_lead=WEIGHT_SHIFT_LEAD,swing_lift_components_m=[.055,.040],swing_lift_profile="early_beta_plus_sine",swing_path="quintic",
        stance_fraction=DUTY,idle_duration=4,heel_strike_degrees=12,toe_off_degrees=pose_curve(DUTY,FOOT_ROLL_KEYS),peak_foot_roll_degrees=PEAK_FOOT_ROLL_DEGREES,foot_toe_out_degrees=FOOT_TOE_OUT_DEGREES,sole_tip_anchors={k:list(v) for k,v in tips.items()},crotch_weight_smoothing_passes=10,foot_targets=contacts,samples=snapshots,source_preserved=True),indent=2)+'\n')
    print('LOCOMOTION_BUILT',[(a.name,tuple(a.frame_range)) for a in bpy.data.actions])
if __name__=='__main__':main()
