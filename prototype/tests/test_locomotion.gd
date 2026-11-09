extends "res://tests/test_import.gd"
## Reuse the independently tested CPU skinning evaluator for both locomotion clips.
func run() -> void:
	var actor: Node3D = load("res://assets/human_locomotion.glb").instantiate()
	root.add_child(actor)
	await process_frame
	var skeleton := actor.find_child("Skeleton3D",true,false) as Skeleton3D
	var player := actor.find_child("AnimationPlayer",true,false) as AnimationPlayer
	check(skeleton != null and player != null,"Missing locomotion rig/player")
	if skeleton == null or player == null:
		quit(1)
		return
	check(skeleton.get_bone_count()==137,"Bone count changed")
	var reference: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/locomotion_bounds.json"))
	var export_report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://../tools/blender/locomotion_previews/validation.json"))
	check(FileAccess.get_sha256("res://assets/human_locomotion.glb")==export_report.glb_sha256,"Stale Blender reference")
	var meshes: Dictionary = {}
	for pair in [["Human","Human"],["Gauntlands_Boxer_Briefs","Gauntlands_Boxer_Briefs"],["Human.high-poly","Human_high-poly"]]:
		meshes[pair[0]]=actor.find_child(pair[1],true,false) as MeshInstance3D
		check(meshes[pair[0]]!=null,"Missing character mesh")
	var maximum_error := 0.0
	var results := {}
	for clip_name in ["Idle","Walk"]:
		check(player.has_animation(clip_name),"Missing clip "+clip_name)
		var expected_length := 4.0 if clip_name=="Idle" else 1.2
		check(absf(player.get_animation(clip_name).length-expected_length)<0.001,"Wrong clip duration")
		player.play(clip_name)
		player.speed_scale=0
		var samples := {}
		for frame in reference[clip_name]:
			player.seek(float(frame)/60.0,true)
			skeleton.force_update_all_bone_transforms()
			var sample := {}
			for name in meshes:
				var bounds := skinned_bounds(meshes[name],skeleton)
				sample[name]=bounds
				for axis in range(3):
					for endpoint in range(2):
						var error := absf(bounds[axis][endpoint]-reference[clip_name][frame][name][axis][endpoint])
						maximum_error=maxf(maximum_error,error)
						check(error<0.0001,"Pose bounds differ: %s %s %s" % [clip_name,frame,error])
			samples[frame]=sample
		results[clip_name]=samples
	# Test real cross-fades in the same AnimationPlayer used by the viewer.
	player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	player.speed_scale=1
	var transition_min_floor := INF
	for pair in [["Idle","Walk"],["Walk","Idle"]]:
		player.play(pair[0],0)
		player.advance(0.36)
		player.play(pair[1],0.10)
		if pair[1]=="Walk":player.seek(0.36,true)
		for frame in range(16):
			player.advance(1.0/60.0)
			skeleton.force_update_all_bone_transforms()
			var bounds := skinned_bounds(meshes["Human"],skeleton)
			transition_min_floor=minf(transition_min_floor,bounds[1][0])
	check(transition_min_floor>=-0.003,"Cross-fade penetrates floor")
	var report := {"engine":Engine.get_version_info().string,"passed":failures.is_empty(),"failures":failures,"maximum_bounds_error_m":maximum_error,"transition_min_floor_m":transition_min_floor,"samples":results}
	var output := FileAccess.open("res://../tools/blender/locomotion_previews/godot_validation.json",FileAccess.WRITE)
	output.store_string(JSON.stringify(report,"  ")+"\n")
	output.close()
	print("LOCOMOTION_GODOT ",report.passed," error ",maximum_error," transition floor ",transition_min_floor)
	quit(0 if failures.is_empty() else 1)
