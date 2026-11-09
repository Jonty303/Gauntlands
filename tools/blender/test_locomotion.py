"""Validate exported Idle/Walk at every authored 60 Hz frame; --quick samples every sixth frame."""
import bpy,json,hashlib,sys,math
from pathlib import Path
from mathutils.bvhtree import BVHTree
from mathutils import Vector
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'tools/blender/locomotion_previews'
GLB=ROOT/'prototype/assets/human_locomotion.glb'
build_manifest=json.loads((OUT/'build.json').read_text())
bpy.ops.wm.open_mainfile(filepath=str(ROOT/'assets/Blender Models/Human-Male-Locomotion.blend'))
assert {'Idle','Walk'}.issubset(bpy.data.actions.keys())
assert len(bpy.data.objects['Human'].data.shape_keys.key_blocks)==9
assert all(bpy.data.images[n].packed_file for n in ['brown_eye.png','young_lightskinned_male_diffuse.png'])
assert hashlib.sha256((ROOT/'assets/Blender Models/Human-Male-180cm.blend').read_bytes()).hexdigest()==build_manifest['source_sha256']
bpy.ops.wm.read_factory_settings(use_empty=True);bpy.context.scene.render.fps=60
bpy.ops.import_scene.gltf(filepath=str(GLB))
rig=bpy.data.objects['Human.rig'];body=bpy.data.objects['Human'];cloth=bpy.data.objects['Gauntlands_Boxer_Briefs']
actions={name:next(a for a in bpy.data.actions if a.name.startswith(name)) for name in ['Idle','Walk']}
def surface(o):
    ev=o.evaluated_get(bpy.context.evaluated_depsgraph_get());m=ev.to_mesh()
    vs=[ev.matrix_world@v.co for v in m.vertices];ps=[tuple(p.vertices) for p in m.polygons]
    ev.to_mesh_clear();return vs,ps
# Pick actual sole vertices from the exported bind mesh, independently of the
# generator's ankle targets. Track their contact drift as well as bone anchors.
rig.animation_data.action=None
for bone in rig.pose.bones:bone.matrix_basis.identity()
bpy.context.view_layer.update()
bind,bind_faces=surface(body)
# Spatial regions in the exported bind mesh, independent of authoring curves.
# Hands are well outside the trunk in this model's bind pose.
hand_ids={i for i,v in enumerate(bind) if abs(v.x)>.455 and v.z<1.25}
thigh_ids={i for i,v in enumerate(bind) if abs(v.x)<.30 and v.z<1.10}
core_ids={i for i,v in enumerate(bind) if abs(v.x)<.32 and v.z<1.55}
core_faces=[p for p in bind_faces if all(i in core_ids for i in p)]
hand_faces=[p for p in bind_faces if all(i in hand_ids for i in p)]
thigh_faces=[p for p in bind_faces if all(i in thigh_ids for i in p)]
assert hand_faces and thigh_faces and core_faces
contact_vertices={};tip_anchors={}
for side,sign in [('L',1),('R',-1)]:
    contact_vertices[side]={}
    for stage,y in [('heel',.045),('sole',0),('toe',-.19),('tip',-.202)]:
        target=Vector((sign*.19,y,0))
        contact_vertices[side][stage]=min(range(len(bind)),key=lambda i:(bind[i]-target).length_squared)
    ball=rig.data.bones['toe1-1.'+side].head_local
    limit=rig.data.bones['foot.'+side].head_local.z*.11
    tip_id=min((i for i,v in enumerate(bind) if abs(v.x-ball.x)<.02 and v.z<limit),key=lambda i:bind[i].y)
    contact_vertices[side]['tip']=tip_id
    tip_anchors[side]=bind[tip_id].copy()
report=dict(saved_source_reopened=True,original_preserved=True,shape_keys=9,glb_sha256=hashlib.sha256(GLB.read_bytes()).hexdigest(),clips={},samples={},quick='--quick' in sys.argv)
for name,action in actions.items():
    rig.animation_data.action=action;rig.animation_data.action_slot=action.slots[0]
    frames=240 if name=='Idle' else 72
    results=[];samples={};endpoints=[];motion=[];arm_motion=[];foot_stance={s:[] for s in ['L','R']}
    for frame in range(0,frames+1,6 if report['quick'] else 1):
        bpy.context.scene.frame_set(frame)
        skin,faces=surface(body);fabric,polys=surface(cloth)
        a=BVHTree.FromPolygons(skin,faces);b=BVHTree.FromPolygons(fabric,polys)
        hand_tree=BVHTree.FromPolygons(skin,hand_faces)
        hand_pairs={(min(i,j),max(i,j)) for i,j in hand_tree.overlap(hand_tree) if i!=j and not set(hand_faces[i]).intersection(hand_faces[j]) and not any((skin[x]-skin[y]).length_squared<1e-12 for x in hand_faces[i] for y in hand_faces[j])}
        corners=[{tuple(round(c,5) for c in fabric[v]) for v in poly} for poly in polys]
        self_pairs={(min(i,j),max(i,j)) for i,j in b.overlap(b) if i!=j and not corners[i].intersection(corners[j]) and not any((fabric[x]-fabric[y]).length_squared<1e-12 for x in polys[i] for y in polys[j])}
        signed=[]
        for v in fabric:
            hit,n,_,dist=a.find_nearest(v);signed.append((v-hit).dot(n))
        results.append(dict(frame=frame,hand_self_intersections=len(hand_pairs),body_intersections=len(a.overlap(b)),self_intersections=len(self_pairs),inside=sum(d<-.0001 for d in signed),minimum_clearance=min(signed),floor_min=min(v.z for v in skin)))
        if frame in [0,frames]:endpoints.append(skin+fabric)
        if frame%(frames//4)==0:
            sample={}
            for o in [body,cloth,bpy.data.objects['Human.high-poly']]:
                vs,_=surface(o);vs=[(v.x,v.z,-v.y) for v in vs]
                sample[o.name]=[[min(v[i] for v in vs),max(v[i] for v in vs)] for i in range(3)]
            samples[str(frame)]=sample
        if name=='Walk':
            hand_tree=BVHTree.FromPolygons(skin,hand_faces)
            thigh_tree=BVHTree.FromPolygons(skin,thigh_faces)
            hand_clearance=min(thigh_tree.find_nearest(skin[i])[3] for i in hand_ids)
            core_tree=BVHTree.FromPolygons(skin,core_faces)
            core_clearance=min(core_tree.find_nearest(skin[i])[3] for i in hand_ids)
            elbow_flex=[]
            for side in ['L','R']:
                shoulder=rig.pose.bones['upperarm01.'+side].head
                elbow=rig.pose.bones['lowerarm01.'+side].head
                wrist=rig.pose.bones['wrist.'+side].head
                elbow_flex.append(180-math.degrees((shoulder-elbow).angle(wrist-elbow)))
            arm_motion.append(dict(frame=frame,hand_core_clearance_m=core_clearance,hand_core_intersections=len(hand_tree.overlap(core_tree)),hand_thigh_clearance_m=hand_clearance,
                hand_thigh_intersections=len(hand_tree.overlap(thigh_tree)),elbow_flex_degrees=elbow_flex))
            hips=[rig.pose.bones['upperleg01.'+side].head.copy() for side in ['L','R']]
            knees=[rig.pose.bones['lowerleg01.'+side].head.copy() for side in ['L','R']]
            ankles=[rig.pose.bones['foot.'+side].head.copy() for side in ['L','R']]
            hip_axis=hips[0]-hips[1]
            heel_heights=[];foot_headings=[]
            for side in ['L','R']:
                foot=rig.pose.bones['foot.'+side]
                forward=(rig.matrix_world@foot.matrix@foot.bone.matrix_local.inverted()).to_3x3()@Vector((0,-1,0))
                foot_headings.append(math.degrees(math.atan2(forward.x,-forward.y)))
                marker=Vector((foot.bone.head_local.x,.045,0))
                heel_heights.append((rig.matrix_world@foot.matrix@foot.bone.matrix_local.inverted()@marker).z)
            motion.append(dict(frame=frame,foot_heading_degrees=foot_headings,heel_marker_height_m=heel_heights,pelvis=list((hips[0]+hips[1])*.5),head=list(rig.pose.bones['head'].head),
                hip_yaw_degrees=math.degrees(math.atan2(hip_axis.y,hip_axis.x)),
                hip_tilt_degrees=math.degrees(math.atan2(hip_axis.z,math.hypot(hip_axis.x,hip_axis.y))),
                knee_flex_degrees=[180-math.degrees((hips[i]-knees[i]).angle(ankles[i]-knees[i])) for i in range(2)]))
            for side,offset in [('L',0),('R',.5)]:
                phase=(frame/frames+offset)%1
                if phase<=.6:
                    # Track a sole contact anchor, not the ankle which now rolls.
                    stage='heel' if phase<.12 else ('sole' if phase<.34 else ('toe' if phase<.52 else 'tip'))
                    bone=rig.pose.bones[('toe1-1.' if stage in ['toe','tip'] else 'foot.')+side]
                    anchor=bone.bone.head_local.copy()
                    anchor.z=0
                    if stage=='heel':anchor.y=.045
                    elif stage=='toe':anchor.y=-.19
                    elif stage=='tip':anchor=tip_anchors[side].copy()
                    foot=rig.matrix_world@bone.matrix@bone.bone.matrix_local.inverted()@anchor
                    foot_stance[side].append(dict(frame=frame,phase=phase,stage=stage,foot=list(foot),skin=list(skin[contact_vertices[side][stage]])))
    interpolated_floor=None;interpolated_knee_step=None;interpolated_hand_core_clearance=None;interpolated_hand_core_intersections=0
    if name=='Walk' and not report['quick']:
        # New swing timing is also checked halfway between the baked samples.
        interpolated_floor=float('inf');interpolated_knee_step=0.0;interpolated_hand_core_clearance=float('inf')
        for frame in range(frames):
            bpy.context.scene.frame_set(frame,subframe=.5)
            vs,_=surface(body)
            interpolated_floor=min(interpolated_floor,min(v.z for v in vs))
            core_tree=BVHTree.FromPolygons(vs,core_faces);hand_tree=BVHTree.FromPolygons(vs,hand_faces)
            interpolated_hand_core_clearance=min(interpolated_hand_core_clearance,min(core_tree.find_nearest(vs[i])[3] for i in hand_ids))
            interpolated_hand_core_intersections+=len(hand_tree.overlap(core_tree))
            for i,side in enumerate(['L','R']):
                hip=rig.pose.bones['upperleg01.'+side].head
                knee=rig.pose.bones['lowerleg01.'+side].head
                ankle=rig.pose.bones['foot.'+side].head
                angle=180-math.degrees((hip-knee).angle(ankle-knee))
                # Normalise each half-frame change to the existing 60 Hz limit.
                interpolated_knee_step=max(interpolated_knee_step,2*abs(angle-motion[frame]['knee_flex_degrees'][i]),2*abs(motion[frame+1]['knee_flex_degrees'][i]-angle))
    seam=max((v-w).length for v,w in zip(*endpoints))
    # Stance heel/sole/toe anchors travel backwards at 0.9 m/s. Add virtual forward
    # travel (-Y in Blender) and compare within each uninterrupted stance.
    slip=0.0;skin_slip=0.0;contact_height=0.0
    for entries in foot_stance.values():
        for a,b in zip(entries,entries[1:]):
            if b['stage']==a['stage'] and b['phase']>a['phase'] and b['frame']-a['frame'] <= (6 if report['quick'] else 1):
                dt=(b['frame']-a['frame'])/60
                skin_slip=max(skin_slip,abs(b['skin'][1]-a['skin'][1]-.9*dt),abs(b['skin'][0]-a['skin'][0]),abs(b['skin'][2]-a['skin'][2]))
                contact_height=max(contact_height,abs(a['skin'][2]),abs(b['skin'][2]))
                slip=max(slip,abs(b['foot'][1]-a['foot'][1]-.9*dt),abs(b['foot'][0]-a['foot'][0]),abs(b['foot'][2]-a['foot'][2]))
    arm_checks={}
    if arm_motion:
        arm_checks=dict(minimum_hand_core_clearance_m=min(v['hand_core_clearance_m'] for v in arm_motion),hand_core_intersections=sum(v['hand_core_intersections'] for v in arm_motion),minimum_hand_thigh_clearance_m=min(v['hand_thigh_clearance_m'] for v in arm_motion),
            hand_thigh_intersections=sum(v['hand_thigh_intersections'] for v in arm_motion),
            elbow_flex_range_degrees=[min(x for v in arm_motion for x in v['elbow_flex_degrees']),max(x for v in arm_motion for x in v['elbow_flex_degrees'])],
            maximum_elbow_change_per_60hz_frame_degrees=max(abs(b['elbow_flex_degrees'][i]-a['elbow_flex_degrees'][i])/(b['frame']-a['frame']) for a,b in zip(arm_motion,arm_motion[1:]) for i in range(2)),samples=arm_motion)
        arm_checks['passed']=arm_checks['minimum_hand_core_clearance_m']>.005 and not arm_checks['hand_core_intersections'] and arm_checks['minimum_hand_thigh_clearance_m']>.005 and not arm_checks['hand_thigh_intersections'] and arm_checks['maximum_elbow_change_per_60hz_frame_degrees']<6
    movement={}
    if motion:
        movement=dict(pelvis_range_m=[max(v['pelvis'][i] for v in motion)-min(v['pelvis'][i] for v in motion) for i in range(3)],
            head_range_m=[max(v['head'][i] for v in motion)-min(v['head'][i] for v in motion) for i in range(3)],
            knee_flex_range_degrees=[min(x for v in motion for x in v['knee_flex_degrees']),max(x for v in motion for x in v['knee_flex_degrees'])],
            maximum_knee_change_per_60hz_frame_degrees=max(abs(b['knee_flex_degrees'][i]-a['knee_flex_degrees'][i])/(b['frame']-a['frame']) for a,b in zip(motion,motion[1:]) for i in range(2)),
            samples=motion)
        # Task-local guard against new knee snapping, beyond the prior 4.33 deg
        # maximum change per 60 Hz sample; full validation covers every sample.
        # Cyclic second differences include the landing at the loop boundary.
        # Task-local knee-stability target: <2.2 degrees/frame^2 at 60 Hz.
        cycle=motion[:-1];step=motion[1]['frame']-motion[0]['frame']
        movement['maximum_knee_acceleration_degrees_per_60hz_frame_squared']=max(
            abs(cycle[(j+1)%len(cycle)]['knee_flex_degrees'][i]
                -2*entry['knee_flex_degrees'][i]
                +cycle[(j-1)%len(cycle)]['knee_flex_degrees'][i])/(step*step)
            for j,entry in enumerate(cycle) for i in range(2))
        # A fixed toe-out must not swivel during heel/ball/toe roll or recovery.
        expected_heading=build_manifest.get('foot_toe_out_degrees',0)
        movement['maximum_foot_heading_error_degrees']=max(
            abs(v['foot_heading_degrees'][i]-sign*expected_heading)
            for v in motion for i,sign in enumerate([1,-1]))
        movement['passed']=(movement['maximum_knee_change_per_60hz_frame_degrees']<6
            and movement['knee_flex_range_degrees'][0]>5
            and movement['maximum_knee_acceleration_degrees_per_60hz_frame_squared']<2.2
            and movement['maximum_foot_heading_error_degrees']<.1)
    report['clips'][name]=dict(interpolated_hand_core_clearance_m=interpolated_hand_core_clearance,interpolated_hand_core_intersections=interpolated_hand_core_intersections,interpolated_floor_min_m=interpolated_floor,interpolated_knee_change_per_60hz_frame_degrees=interpolated_knee_step,arms=arm_checks,movement=movement,frames=results,loop_max_vertex_error=seam,stance_step_error_m=slip,skin_contact_step_error_m=skin_slip,skin_contact_height_m=contact_height,foot_stance=foot_stance)
    report['samples'][name]=samples
report['passed']=all((c['interpolated_hand_core_clearance_m'] is None or c['interpolated_hand_core_clearance_m']>.005) and not c['interpolated_hand_core_intersections'] and (c['interpolated_knee_change_per_60hz_frame_degrees'] is None or c['interpolated_knee_change_per_60hz_frame_degrees']<6) and (c['interpolated_floor_min_m'] is None or c['interpolated_floor_min_m']>=-.003) and c['arms'].get('passed',True) and c['movement'].get('passed',True) and c['loop_max_vertex_error']<1e-5 and c['stance_step_error_m']<1e-4 and c['skin_contact_step_error_m']<.003 and c['skin_contact_height_m']<.012 and all(not(f['body_intersections'] or f['inside'] or f['self_intersections'] or f['hand_self_intersections']) and f['floor_min']>=-.003 for f in c['frames']) for c in report['clips'].values())
(OUT/'validation.json').write_text(json.dumps(report,indent=2)+'\n')
(ROOT/'prototype/tests/locomotion_bounds.json').write_text(json.dumps(report['samples'],indent=2)+'\n')
print('LOCOMOTION_TEST',report['passed'])
for name,c in report['clips'].items():
    print(name,'loop',c['loop_max_vertex_error'],'slip',c['stance_step_error_m'],'skin slip',c['skin_contact_step_error_m'],'contact height',c['skin_contact_height_m'],'floor',min(f['floor_min'] for f in c['frames']),'bad',[f for f in c['frames'] if f['body_intersections'] or f['inside'] or f['self_intersections'] or f['hand_self_intersections']][:4])
print('HALF_FRAME_FLOOR',report['clips']['Walk']['interpolated_floor_min_m'],'KNEE_STEP_60HZ',report['clips']['Walk']['interpolated_knee_change_per_60hz_frame_degrees'])
print('ARMS',json.dumps({k:v for k,v in report['clips']['Walk']['arms'].items() if k!='samples'}))
print('MOVEMENT',json.dumps({k:v for k,v in report['clips']['Walk']['movement'].items() if k!='samples'}))
assert report['passed'],'See locomotion validation report'
