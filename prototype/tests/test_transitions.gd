extends "res://tests/test_import.gd"
func run() -> void:
	var viewer = load("res://locomotion_v02.tscn").instantiate()
	root.add_child(viewer)
	await process_frame
	viewer.set_process(false)
	var player: AnimationPlayer = viewer.player
	var skeleton: Skeleton3D = viewer.actor.find_child("Skeleton3D",true,false)
	var body: MeshInstance3D = viewer.actor.find_child("Human",true,false)
	var reference: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/locomotion_v02_bounds.json"))
	var blender_report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://../tools/blender/locomotion_v02/validation.json"))
	check(blender_report.passed, "Blender gates failed")
	check(FileAccess.get_sha256("res://assets/human_locomotion_v02.glb")==blender_report.glb_sha256,"Stale export reference")
	check(skeleton.get_bone_count()==137,"Rig changed")
	var start_duration: float = viewer.travel_data.clips.WalkStart
	var maximum_error := 0.0
	for name in reference:
		check(player.has_animation(name),"Missing "+name)
		check(absf(player.get_animation(name).length-float(viewer.travel_data.clips[name]))<0.001,"Clip length changed")
		check(player.get_animation(name).loop_mode==(Animation.LOOP_LINEAR if name=="Idle" else Animation.LOOP_NONE),"Incorrect loop mode")
		viewer.start_clip(name)
		for frame in reference[name]:
			player.seek(float(frame)/60.0,true)
			skeleton.force_update_all_bone_transforms()
			for pair in [["Human","Human"],["Gauntlands_Boxer_Briefs","Gauntlands_Boxer_Briefs"],["Human.high-poly","Human_high-poly"]]:
				var mesh: MeshInstance3D = viewer.actor.find_child(pair[1],true,false)
				var bounds := skinned_bounds(mesh,skeleton)
				for axis in range(3):
					for end in range(2):
						maximum_error=maxf(maximum_error,absf(bounds[axis][end]-reference[name][frame][pair[0]][axis][end]))
	check(maximum_error<0.0001,"Godot/Blender pose mismatch")
	var cases := []
	var floor_min := INF
	for phase in [0.0,0.1,0.59,0.6,0.8,1.19]:
		viewer.start_clip(&"Walk")
		viewer.wants_walk=true
		player.seek(phase,true)
		viewer.select_clip(&"Idle")
		var seen_stop := ""
		for i in range(90):
			viewer.advance_sequence(1.0/60.0)
			if String(viewer.clip).begins_with("WalkStop"): seen_stop=String(viewer.clip)
			if i%3==0:
				skeleton.force_update_all_bone_transforms()
				floor_min=minf(floor_min,skinned_bounds(body,skeleton)[1][0])
		check(viewer.clip==&"Idle","Stop did not complete from "+str(phase))
		check(not seen_stop.is_empty(),"Missing authored stop from "+str(phase))
		cases.append({"request_phase_s":phase,"stop_clip":seen_stop})
	# Measure the visible chest through the real Idle-to-start blend.
	var chest_index := skeleton.find_bone("spine01")
	check(chest_index >= 0,"Missing chest bone")
	var entry_cases := []
	var maximum_entry_jump := 0.0
	var maximum_early_chest_speed := 0.0
	var maximum_early_chest_step_change := 0.0
	# Start from different breathing phases; feet must remain planted during entry blending.
	for phase in [0.0,1.0,2.0,3.0]:
		viewer.start_clip(&"Idle")
		player.seek(phase,true)
		viewer.ground_distance=0.0
		skeleton.force_update_all_bone_transforms()
		var chest_before: Vector3 = skeleton.global_transform * skeleton.get_bone_global_pose(chest_index).origin
		viewer.select_clip(&"Walk")
		skeleton.force_update_all_bone_transforms()
		var chest_entry: Vector3 = skeleton.global_transform * skeleton.get_bone_global_pose(chest_index).origin
		maximum_entry_jump=maxf(maximum_entry_jump,chest_entry.distance_to(chest_before))
		var chest_samples: Array[float] = [chest_entry.z]
		for i in range(roundi((start_duration+0.1)*60)):
			viewer.advance_sequence(1.0/60.0)
			if i < 18:
				skeleton.force_update_all_bone_transforms()
				var chest: Vector3 = skeleton.global_transform * skeleton.get_bone_global_pose(chest_index).origin
				chest_samples.append(chest.z+viewer.ground_distance)
			if i%2==0:
				skeleton.force_update_all_bone_transforms()
				floor_min=minf(floor_min,skinned_bounds(body,skeleton)[1][0])
		var entry_speed := 0.0
		var entry_step_change := 0.0
		for index in range(1,chest_samples.size()):
			entry_speed=maxf(entry_speed,absf(chest_samples[index]-chest_samples[index-1])*60.0)
		for index in range(1,chest_samples.size()-1):
			entry_step_change=maxf(entry_step_change,absf(chest_samples[index+1]-2*chest_samples[index]+chest_samples[index-1]))
		maximum_early_chest_speed=maxf(maximum_early_chest_speed,entry_speed)
		maximum_early_chest_step_change=maxf(maximum_early_chest_step_change,entry_step_change)
		entry_cases.append({"idle_phase_s":phase,"chest_forward_samples_m":chest_samples,"maximum_speed_m_s":entry_speed,"maximum_step_change_m":entry_step_change})
		check(viewer.clip==&"Walk","Start did not reach Walk")
		check(absf(player.current_animation_position-.1)<0.00001,"Start discarded overshoot")
	check(floor_min>=-.003,"Runtime transition penetrates floor")
	check(maximum_entry_jump<.001,"Immediate chest pose jump at start")
	check(maximum_early_chest_speed<.30,"Early chest surge exceeds 0.30 m/s")
	check(maximum_early_chest_step_change<.001,"Early chest acceleration is abrupt")
	# A changed intention finishes the current authored transition without a pose jump.
	viewer.start_clip(&"Idle")
	viewer.select_clip(&"Walk")
	viewer.advance_sequence(.3)
	viewer.select_clip(&"Idle")
	viewer.advance_sequence(.6)
	check(viewer.clip==&"WalkStopL","Stop during start not queued")
	viewer.select_clip(&"Walk")
	viewer.advance_sequence(1.6)
	check(viewer.clip==&"Walk","Restart during stop not completed")
	# Pause freezes both clip and virtual movement; intent is retained until resume.
	viewer.paused=true
	var time := player.current_animation_position
	var distance: float = viewer.ground_distance
	viewer.select_clip(&"Idle")
	viewer.advance_sequence(1.0)
	check(player.current_animation_position==time and viewer.ground_distance==distance,"Pause moved animation")
	viewer.paused=false
	viewer.advance_sequence(1.5)
	check(viewer.clip==&"Idle","Paused stop intent lost")
	viewer.start_clip(&"Idle")
	viewer.ground_distance=0
	viewer.select_clip(&"Walk")
	viewer.advance_sequence(start_duration+1.2)
	check(viewer.clip==&"Walk" and absf(viewer.ground_distance-1.296)<0.00001,"Travel integration or large delta failed")
	viewer.select_clip(&"Idle")
	viewer.advance_sequence(.8)
	check(viewer.clip==&"Idle" and absf(viewer.ground_distance-1.62)<0.00001,"Stop displacement wrong")
	for name in viewer.REVIEW_VIEWS:
		viewer.set_review_view(name)
		check(viewer.camera.global_basis.is_finite(),"Invalid review camera")
	var report := {"passed":failures.is_empty(),"failures":failures,"maximum_bounds_error_m":maximum_error,"runtime_floor_min_m":floor_min,"stop_cases":cases,"pause_restart_large_delta_checks":true,"chest_entry":{"maximum_immediate_jump_m":maximum_entry_jump,"maximum_speed_m_s":maximum_early_chest_speed,"maximum_step_change_m":maximum_early_chest_step_change,"cases":entry_cases}}
	var file := FileAccess.open("res://../tools/blender/locomotion_v02/godot_validation.json",FileAccess.WRITE)
	file.store_string(JSON.stringify(report,"  ")+"\n")
	print("V02_GODOT ",report.passed," failures ",failures," bounds ",maximum_error," floor ",floor_min," chest ",[maximum_entry_jump,maximum_early_chest_speed,maximum_early_chest_step_change])
	quit(0 if failures.is_empty() else 1)
