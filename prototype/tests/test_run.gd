extends "res://tests/test_import.gd"
func run() -> void:
	var viewer = load("res://locomotion_v03.tscn").instantiate()
	root.add_child(viewer)
	await process_frame
	viewer.set_process(false)
	var player: AnimationPlayer = viewer.player
	var skeleton: Skeleton3D = viewer.actor.find_child("Skeleton3D",true,false)
	var reference: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/locomotion_v03_bounds.json"))
	var report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://../tools/blender/locomotion_v03/validation.json"))
	check(report.passed,"Blender run validation failed")
	check(FileAccess.get_sha256("res://assets/human_locomotion_v03.glb")==report.glb_sha256,"Stale export reference")
	check(skeleton.get_bone_count()==137,"Rig changed")
	var maximum_error := 0.0
	for name in reference:
		check(player.has_animation(name),"Missing "+name)
		check(absf(player.get_animation(name).length-float(viewer.run_data.clips[name]))<0.001,"Clip duration")
		viewer.start_clip(name)
		for frame in reference[name]:
			player.seek(float(frame)/60.0,true)
			skeleton.force_update_all_bone_transforms()
			for pair in [["Human","Human"],["Gauntlands_Boxer_Briefs","Gauntlands_Boxer_Briefs"],["Human.high-poly","Human_high-poly"]]:
				var mesh: MeshInstance3D = viewer.actor.find_child(pair[1],true,false)
				var bounds := skinned_bounds(mesh,skeleton)
				for axis in range(3):
					for end in range(2): maximum_error=maxf(maximum_error,absf(bounds[axis][end]-reference[name][frame][pair[0]][axis][end]))
	check(maximum_error<0.0001,"Godot/Blender pose mismatch")
	var cases := []
	for hz in [30,60,120]:
		for from_state in [&"Walk",&"Run"]:
			for phase in [0.0,0.1,0.49,0.5,0.9]:
				viewer.enter_phase(from_state,phase)
				viewer.ground_distance=0
				var target: StringName = &"Run" if from_state==&"Walk" else &"Walk"
				viewer.select_clip(target)
				var seen := ""
				for i in range(2*hz):
					if String(viewer.clip) in viewer.run_data.transitions: seen=String(viewer.clip)
					viewer.advance_sequence(1.0/hz)
				check(viewer.clip==target,"Gait request incomplete")
				check(not seen.is_empty(),"Missing authored gait transition")
				var expected := ("WalkToRun" if from_state==&"Walk" else "RunToWalk")+("L" if phase==0.0 or phase>0.5 else "R")
				check(seen==expected,"Wrong leading foot: "+seen+" expected "+expected)
				cases.append({"hz":hz,"from":from_state,"phase":phase,"bridge":seen,"distance":viewer.ground_distance})
	# Frame-rate-independent virtual travel for the same requests.
	for i in range(10):
		check(absf(cases[i].distance-cases[i+10].distance)<0.00001,"30/60 Hz travel mismatch")
		check(absf(cases[i].distance-cases[i+20].distance)<0.00001,"30/120 Hz travel mismatch")
	viewer.enter_phase(&"Idle");viewer.ground_distance=0;viewer.select_clip(&"Run")
	viewer.advance_sequence(3.3)
	check(viewer.clip==&"Run","Idle-to-Run or large delta failed")
	var expected_distance := .216+1.55+1.6*float(viewer.run_data.run_speed)
	check(absf(viewer.ground_distance-expected_distance)<0.00001,"Run virtual travel")
	viewer.paused=true
	var time := player.current_animation_position
	viewer.select_clip(&"Idle");viewer.advance_sequence(1)
	check(absf(player.current_animation_position-time)<0.00001,"Paused animation advanced")
	viewer.paused=false;viewer.advance_sequence(4)
	check(viewer.clip==&"Idle","Run-to-Idle chain did not finish")
	viewer.enter_phase(&"Walk");viewer.select_clip(&"Run");viewer.advance_sequence(.25);viewer.select_clip(&"Idle");viewer.advance_sequence(4)
	check(viewer.clip==&"Idle","Changed intent was lost")
	viewer.enter_phase(&"Run",.5);viewer.select_clip(&"Walk");viewer.advance_sequence(.25);viewer.select_clip(&"Run");viewer.advance_sequence(3)
	check(viewer.clip==&"Run","Restart request was lost")
	var result := {"passed":failures.is_empty(),"failures":failures,"maximum_bounds_error_m":maximum_error,"cases":cases,"pause_large_delta_changed_intent":true}
	FileAccess.open("res://../tools/blender/locomotion_v03/godot_validation.json",FileAccess.WRITE).store_string(JSON.stringify(result,"  ")+"\n")
	print("RUN_GODOT ",result.passed," failures ",failures," bounds ",maximum_error)
	quit(0 if failures.is_empty() else 1)
