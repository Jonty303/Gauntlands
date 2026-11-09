extends "res://tests/test_import.gd"
var poses := []
func run() -> void:
	var demo = load("res://motion_demo.tscn").instantiate()
	demo.auto_test = true
	root.add_child(demo)
	await process_frame
	if "--stance-geometry" in OS.get_cmdline_user_args():
		export_geometry(demo)
		quit()
		return
	if "--stance-capture" in OS.get_cmdline_user_args():
		await capture(demo)
		quit(0 if failures.is_empty() else 1)
		return
	var adapter = demo.animation.stance
	var skeleton: Skeleton3D = demo.animation.skeleton
	var body: MeshInstance3D = demo.animation.body
	print("STANCE_COORDINATES ",skeleton.transform," parent ",skeleton.get_parent().transform," feet ",skeleton.get_bone_global_rest(skeleton.find_bone("foot.L")).origin)
	var max_change := 0.0
	var max_hold_change := 0.0
	var minimum_height := INF
	var maximum_low_sole_adjustment := 0.0
	var maximum_knee_step := 0.0
	var maximum_length_error := 0.0
	var minimum_alignment := 1.0
	var cases := []
	for hz in [30,60,120]:
		demo.reset_demo()
		for frame in range(hz*6):
			var time: float = float(frame)/hz
			var previous := [float(adapter.legs[0].offset),float(adapter.legs[1].offset)]
			var was_swing := [bool(adapter.legs[0].swing),bool(adapter.legs[1].swing)]
			var knees := [skeleton.get_bone_pose_rotation(adapter.legs[0].lower),skeleton.get_bone_pose_rotation(adapter.legs[1].lower)]
			demo.advance_demo(1.0/hz,Vector2.DOWN if time < 4.0 else Vector2.ZERO)
			var heights := sole_heights(demo.animation) if hz == 60 else Vector2(INF,INF)
			for i in range(2):
				var leg: Dictionary = adapter.legs[i]
				var difference := absf(leg.offset-previous[i])
				if hz == 60:
					max_change = maxf(max_change,difference)
					if heights[i] <= 0.001: maximum_low_sole_adjustment = maxf(maximum_low_sole_adjustment,difference)
					maximum_knee_step = maxf(maximum_knee_step,knees[i].angle_to(skeleton.get_bone_pose_rotation(leg.lower)))
				if not leg.swing and not was_swing[i]: max_hold_change = maxf(max_hold_change,difference)
				if time > 2.5 and time < 4.0: check(absf(leg.offset-0.02)<0.0005,"Steady moving placement")
				if time >= 5.0: check(leg.offset < 0.0001 and leg.lift < 0.0001,"Did not restore wide idle")
			if hz == 60 and frame % 6 == 0:
				skeleton.force_update_all_bone_transforms()
				minimum_height = minf(minimum_height,skinned_bounds(body,skeleton)[1][0])
			maximum_length_error = maxf(maximum_length_error,adapter.maximum_length_error)
			minimum_alignment = minf(minimum_alignment,adapter.minimum_bend_alignment)
		cases.append({"hz":hz,"travel_m":demo.travelled,"offsets":[adapter.legs[0].offset,adapter.legs[1].offset]})
	check(maximum_low_sole_adjustment <= 0.0002,"Adjusted a grounded sole more than 0.2 mm in one tick")
	check(max_change < 0.002,"Lateral placement jumped over 2 mm in a 60 Hz tick")
	check(max_hold_change < 0.000001,"Changed lateral placement during support")
	check(maximum_length_error < 0.0001,"Leg length changed")
	check(minimum_alignment > 0.999,"Knee bend plane flipped")
	check(minimum_height >= -0.003,"Stance sole penetrated ground")
	check(maximum_knee_step < deg_to_rad(9.0),"Knee rotation step above runtime guard")
	for i in [1,2]: check(absf(cases[0].travel_m-cases[i].travel_m)<0.02,"Stance changed frame-rate travel")
	# Both stop leads across gait phases, including interruptions during step-out.
	var stop_cases := 0
	for speed in [0.9,2.2]:
		for phase in [0.0,0.125,0.25,0.375,0.5,0.625,0.75,0.875]:
			demo.reset_demo()
			demo.motion.speed = speed
			demo.motion.desired_speed = speed
			demo.animation.phase = phase
			demo.animation.idle_mix = 0.0
			demo.animation.run_mix = 1.0 if speed > 1.0 else 0.0
			demo.animation.was_requested = true
			adapter.previous_requested = true
			for leg in adapter.legs: leg.offset = 0.02
			for frame in range(60):
				var before := [float(adapter.legs[0].offset),float(adapter.legs[1].offset)]
				demo.advance_demo(1.0/60.0,Vector2.ZERO)
				for i in range(2): check(absf(adapter.legs[i].offset-before[i]) <= 0.002,"Phase-stop placement jump")
			for leg in adapter.legs: check(leg.offset < 0.0001 and leg.lift < 0.0001,"Phase stop kept narrow stance")
			stop_cases += 1
	for restart_at in [0.2,0.5,0.7,0.8,0.9]:
		demo.reset_demo()
		for i in range(180): demo.advance_demo(1.0/60.0,Vector2.DOWN)
		for i in range(roundi(restart_at*60)): demo.advance_demo(1.0/60.0,Vector2.ZERO)
		var before := [float(adapter.legs[0].offset),float(adapter.legs[1].offset)]
		demo.advance_demo(1.0/60.0,Vector2.RIGHT)
		check(demo.motion.desired_speed == 2.2,"Restart blocked")
		for i in range(2): check(absf(adapter.legs[i].offset-before[i]) < 0.002,"Restart lateral snap")
		for frame in range(120):
			var prior := [float(adapter.legs[0].offset),float(adapter.legs[1].offset)]
			demo.advance_demo(1.0/60.0,Vector2.RIGHT)
			for i in range(2): check(absf(adapter.legs[i].offset-prior[i]) <= 0.002,"Interrupted swing placement jump")
		for leg in adapter.legs: check(absf(leg.offset-0.02)<0.0005,"Restart did not regain moving stance")
	var report := {"passed":failures.is_empty(),"failures":failures,"cases":cases,"max_lateral_change_m_at_60hz":max_change,"support_offset_drift_m":max_hold_change,"max_lateral_change_with_sole_below_1mm_m":maximum_low_sole_adjustment,"maximum_length_error_m":maximum_length_error,"minimum_bend_alignment":minimum_alignment,"minimum_skin_height_m":minimum_height,"maximum_knee_step_deg_at_60hz":rad_to_deg(maximum_knee_step),"stop_cases":stop_cases,"restart_cases":5,"physical_controller_tested":false}
	FileAccess.open("res://../tools/motion_v04/stance/validation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n")
	print("STANCE ",JSON.stringify(report))
	demo.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)

func capture(demo: Node3D) -> void:
	var output := ProjectSettings.globalize_path("res://../tools/motion_v04/stance/frames")
	for view in range(3):
		demo.reset_demo()
		demo.set_view(view)
		demo.close_view = true
		demo.update_camera()
		var folder := output.path_join(str(view))
		DirAccess.make_dir_recursive_absolute(folder)
		for frame in range(180):
			var input := Vector2.DOWN if frame >= 9 and frame < 120 else Vector2.ZERO
			demo.advance_demo(1.0/30.0,input)
			await process_frame
			await RenderingServer.frame_post_draw
			check(demo.get_viewport().get_texture().get_image().save_png(folder.path_join("%03d.png"%frame)) == OK,"Capture failure")
			if view == 0: poses.append({"frame":frame,"state":demo.animation.state,"offsets":[demo.animation.stance.legs[0].offset,demo.animation.stance.legs[1].offset],"lifts":[demo.animation.stance.legs[0].lift,demo.animation.stance.legs[1].lift]})
	FileAccess.open(output.path_join("capture.json"),FileAccess.WRITE).store_string(JSON.stringify({"fps":30,"frames":180,"samples":poses},"  ")+"\n")

func skin_surface(instance: MeshInstance3D, skeleton: Skeleton3D) -> Dictionary:
	var transforms: Array[Transform3D] = []
	for i in range(instance.skin.get_bind_count()):
		var bone := instance.skin.get_bind_bone(i)
		if bone < 0: bone = skeleton.find_bone(instance.skin.get_bind_name(i))
		transforms.append(skeleton.global_transform*skeleton.get_bone_global_pose(bone)*instance.skin.get_bind_pose(i))
	var vertices := []
	var faces := []
	for surface in range(instance.mesh.get_surface_count()):
		var arrays := instance.mesh.surface_get_arrays(surface)
		var source: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var bones: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
		var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
		var indices: PackedInt32Array = arrays[Mesh.ARRAY_INDEX]
		var offset := vertices.size()
		var count: int = bones.size()/source.size()
		for i in range(source.size()):
			var point := Vector3.ZERO
			for slot in range(count): point += (transforms[bones[i*count+slot]]*source[i])*weights[i*count+slot]
			vertices.append([point.x,point.y,point.z])
		for i in range(0,indices.size(),3): faces.append([indices[i]+offset,indices[i+2]+offset,indices[i+1]+offset])
	return {"vertices":vertices,"faces":faces}

func export_geometry(demo: Node3D) -> void:
	var skeleton: Skeleton3D = demo.animation.skeleton
	var body: MeshInstance3D = demo.animation.body
	var cloth: MeshInstance3D = demo.actor.find_child("Gauntlands_Boxer_Briefs",true,false)
	var result := []
	for frame in range(330):
		demo.advance_demo(1.0/60.0,Vector2.DOWN if frame < 240 else Vector2.ZERO)
		if frame not in [24,60,90,120,150,180,210,240,252,270,280,284,288,294,300,329]: continue
		skeleton.force_update_all_bone_transforms()
		var sample := {"frame":frame,"state":demo.animation.state,"stance":{"body":skin_surface(body,skeleton),"cloth":skin_surface(cloth,skeleton)}}
		demo.animation.apply_pose(0.0)
		skeleton.force_update_all_bone_transforms()
		sample.baseline = {"body":skin_surface(body,skeleton),"cloth":skin_surface(cloth,skeleton)}
		result.append(sample)
	FileAccess.open("res://../tools/motion_v04/stance/geometry_samples.json",FileAccess.WRITE).store_string(JSON.stringify(result))
	print("EXPORTED_GEOMETRY ",result.size()," coordinate basis ",skeleton.transform," rest foot ",skeleton.get_bone_global_rest(skeleton.find_bone("foot.L")).origin)

func sole_heights(animation: Node) -> Vector2:
	var skeleton: Skeleton3D = animation.skeleton
	var body: MeshInstance3D = animation.body
	var transforms: Array[Transform3D] = []
	for i in range(animation.bind_bones.size()): transforms.append(skeleton.get_bone_global_pose(animation.bind_bones[i])*body.skin.get_bind_pose(i))
	var result := Vector2(INF,INF)
	for probe in animation.probes:
		var point := Vector3.ZERO
		for influence in probe[1]: point += (transforms[influence[0]]*probe[0])*influence[1]
		var side := 0 if probe[0].x > 0.0 else 1
		result[side] = minf(result[side],point.y+animation.ground_lift)
	return result
