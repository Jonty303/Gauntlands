extends "res://tests/test_import.gd"

func run() -> void:
	var demo = load("res://dummy_locomotion.tscn").instantiate()
	demo.auto_test=true
	root.add_child(demo)
	await process_frame
	if demo.gait_tree==null:
		check(false,"Gait initialisation failed")
		quit(1)
		return
	for entry in [["Idle",2.7],["Walk",.8],["Run",.6]]:
		check(demo.player.has_animation(entry[0]),"Missing clip "+entry[0])
		check(absf(demo.player.get_animation(entry[0]).length-entry[1])<.0001,"Incorrect clip length")
	check(not demo.player.has_animation("Sprint"),"Sprint outside scope")
	# Compare the pure Walk pose against the approved standalone player.
	var baseline = load("res://dummy_walk.tscn").instantiate()
	baseline.auto_test=true
	root.add_child(baseline)
	await process_frame
	var approved: Skeleton3D = baseline.actor.find_child("Skeleton3D",true,false)
	var walk_error := 0.0
	for i in range(24):
		baseline.phase_time=i/30.0
		baseline.apply_pose()
		approved.force_update_all_bone_transforms()
		demo.run_mix=0
		demo.idle_mix=0
		demo.gait_phase=float(i)/24.0
		demo.apply_pose()
		for bone in range(approved.get_bone_count()):
			var difference: float = approved.get_bone_global_pose(bone).origin.distance_to(demo.skeleton.get_bone_global_pose(bone).origin)
			walk_error=maxf(walk_error,difference)
	check(walk_error<.0001,"Approved walk pose changed")
	baseline.queue_free()
	await process_frame
	var results := []
	var minimum_floor := INF
	var max_knee_step := 0.0
	var maximum_lift := 0.0
	var knee: int = demo.skeleton.find_bone("B-shin.L")
	for hz in [30,60,120]:
		for view in range(3):
			demo.reset_demo()
			demo.set_view(view)
			var previous: Quaternion = demo.skeleton.get_bone_pose_rotation(knee)
			for frame in range(hz*9):
				demo.advance_demo(1.0/hz,demo.rehearsal(float(frame)/hz))
				if hz==60:
					var now: Quaternion = demo.skeleton.get_bone_pose_rotation(knee)
					max_knee_step=maxf(max_knee_step,rad_to_deg(previous.angle_to(now)))
					previous=now
					if frame%6==0:
						minimum_floor=minf(minimum_floor,skinned_bounds(demo.body,demo.skeleton)[1][0])
				maximum_lift=maxf(maximum_lift,demo.ground_lift)
			check(demo.speed<.001 and demo.idle_mix>.999,"Did not settle to idle")
			results.append({"hz":hz,"view":view,"travel":demo.travelled,"phase":demo.gait_phase})
	check(minimum_floor>=-.001,"Blended pose penetrates floor")
	check(max_knee_step<25,"Knee rotation jumped more than 25 degrees in a 60 Hz tick")
	for result in results:
		check(absf(result.travel-results[0].travel)<.0001,"Frame-rate/view travel mismatch")
		check(absf(result.phase-results[0].phase)<.0001,"Frame-rate/view phase mismatch")
	var transitions := 0
	for phase in [0.0,.125,.25,.375,.5,.625,.75,.875]:
		demo.reset_demo()
		demo.speed=4
		demo.desired_speed=4
		demo.run_mix=1
		demo.idle_mix=0
		demo.gait_phase=phase
		demo.apply_pose()
		for i in range(60): demo.advance_demo(1.0/60.0,Vector2(0,-.65))
		check(absf(demo.speed-2)<.001 and demo.run_mix<.001,"Run did not return to walk")
		for i in range(120): demo.advance_demo(1.0/60.0,Vector2.ZERO)
		check(demo.speed==0 and demo.idle_mix>.999,"Phase-dependent stop failed")
		transitions+=1
	demo.reset_demo()
	demo.advance_demo(.1,Vector2.UP)
	var held_phase: float=demo.gait_phase
	var held_position: Vector3=demo.actor.position
	demo.toggle_pause()
	demo.advance_demo(.2,Vector2.UP)
	check(demo.actor.position.is_equal_approx(held_position) and demo.gait_phase==held_phase,"Pause advanced motion")
	demo.toggle_pause()
	var report := {"passed":failures.is_empty(),"failures":failures,"engine":Engine.get_version_info().string,
		"walk_pose_max_error_m":walk_error,"rehearsal_cases":results,"run_to_walk_to_idle_phases":transitions,
		"minimum_floor_m":minimum_floor,"max_knee_step_degrees_60hz":max_knee_step,
		"maximum_floor_correction_m":maximum_lift,"physical_joypad":"not tested"}
	FileAccess.open("res://../tools/kevin_locomotion/validation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"
")
	print("LOCOMOTION_VALIDATION ",report)
	if "--capture" in OS.get_cmdline_user_args():
		demo.close_view=true
		for view in range(3):
			demo.reset_demo()
			demo.set_view(view)
			var folder := ProjectSettings.globalize_path("res://../tools/kevin_locomotion/frames/"+str(view))
			DirAccess.make_dir_recursive_absolute(folder)
			for frame in range(270):
				demo.advance_demo(1.0/30.0,demo.rehearsal(frame/30.0))
				await process_frame
				await RenderingServer.frame_post_draw
				get_root().get_texture().get_image().save_png(folder.path_join("%03d.png" % frame))
		for view in range(3):
			demo.set_view(view)
			for clip in ["Idle","Run"]:
				for facing in range(8):
					demo.reset_demo()
					demo.idle_mix=1.0 if clip=="Idle" else 0.0
					demo.run_mix=1.0 if clip=="Run" else 0.0
					demo.gait_phase=.25
					demo.actor.rotation.y=facing*TAU/8
					demo.apply_pose()
					demo.update_camera()
					await process_frame
					await RenderingServer.frame_post_draw
					get_root().get_texture().get_image().save_png("res://../tools/kevin_locomotion/frames/%s_%d_%d.png" % [clip,view,facing])
	quit(0 if failures.is_empty() else 1)