extends "res://tests/test_import.gd"
const State = preload("res://motion/motion_state.gd")
func run() -> void:
	var demo = load("res://motion_demo.tscn").instantiate()
	demo.auto_test = true
	root.add_child(demo)
	await process_frame
	if "--run-up-capture" in OS.get_cmdline_user_args():
		await capture(demo)
		quit()
		return
	var cases := []
	var minimum_height := INF
	var skeleton: Skeleton3D = demo.actor.find_child("Skeleton3D", true, false)
	var body: MeshInstance3D = demo.actor.find_child("Human", true, false)
	for hz in [30, 60, 120]:
		demo.reset_demo()
		var direction: Vector3 = demo.direction_for(Vector2.DOWN)
		demo.motion.heading = atan2(direction.x, direction.z)
		var step_at := -1.0
		var run_at := -1.0
		var top_at := -1.0
		var phase_at_step := -1.0
		for frame in range(hz * 3):
			demo.advance_demo(1.0/hz, Vector2.DOWN)
			var time: float = float(frame + 1)/hz
			if demo.motion.first_step_remaining > 0.000001:
				check(demo.motion.speed <= 0.900001, "Ran before first walking step")
				check(demo.animation.run_mix == 0.0, "Run pose appeared before walking step")
			elif step_at < 0.0:
				step_at = time
				phase_at_step = demo.animation.phase
			if demo.animation.run_mix > 0.001 and run_at < 0.0: run_at = time
			if demo.motion.speed >= 2.19999 and top_at < 0.0: top_at = time
			if hz == 60 and frame % 3 == 0:
				skeleton.force_update_all_bone_transforms()
				minimum_height = minf(minimum_height, skinned_bounds(body, skeleton)[1][0])
		check(step_at >= 1.28 and step_at <= 1.35, "First walk step timing")
		check(absf(phase_at_step - 0.5) < 0.04, "Run-up did not finish a half walk cycle")
		check(run_at > step_at and top_at <= 2.1, "Run-up timing outside contract")
		cases.append({"hz":hz,"first_step_s":step_at,"phase_at_step":phase_at_step,"run_blend_s":run_at,"full_speed_s":top_at,"distance_3s_m":demo.travelled})
	check(minimum_height >= -0.003, "Run-up sole penetration")
	for i in [1,2]:
		check(absf(cases[i].distance_3s_m-cases[0].distance_3s_m) < 0.02, "Run-up frame-rate path mismatch")
	# Pure-state interruption checks exercise each stage without render overhead.
	for release_at in [0.2,0.8,1.2,1.5,1.8]:
		var motion := State.new()
		for i in range(roundi(release_at * 120)): motion.step(1.0/120.0, Vector3.BACK, 1.0)
		var before := motion.speed
		motion.step(1.0/120.0, Vector3.ZERO, 0.0)
		check(motion.desired_speed == 0.0 and not motion.starting and motion.speed <= before, "Release queued")
		for i in range(60): motion.step(1.0/120.0, Vector3.ZERO, 0.0)
		check(motion.speed == 0.0, "Release did not stop in 0.5 s")
		motion.step(1.0/120.0, Vector3.RIGHT, 1.0)
		check(motion.starting and motion.first_step_remaining > 0.53, "Stopped restart skipped lead-up")
	var turning := State.new()
	for i in range(120): turning.step(1.0/120.0, Vector3.BACK, 1.0)
	turning.step(1.0/120.0, Vector3.RIGHT, 1.0)
	check(turning.heading > 0.0 and turning.speed <= 0.9, "Lead-up steering queued")
	# Established walking accelerates from the existing phase, without a new start.
	demo.reset_demo()
	for i in range(240): demo.advance_demo(1.0/60.0, Vector2(0,0.55))
	var prior_phase: float = demo.animation.phase
	demo.advance_demo(1.0/60.0, Vector2.DOWN)
	check(not demo.motion.starting and demo.motion.speed > 0.9, "Established walk delayed run request")
	check(fposmod(demo.animation.phase-prior_phase,1.0) < 0.04, "Established walk phase reset")
	# Paused state must not consume any of the lead-up distance.
	demo.reset_demo()
	demo.advance_demo(0.2, Vector2.DOWN)
	var remaining: float = demo.motion.first_step_remaining
	demo.paused = true
	demo.advance_demo(0.2, Vector2.DOWN)
	check(demo.motion.first_step_remaining == remaining, "Pause consumed lead-up")
	var report := {"passed":failures.is_empty(),"failures":failures,"cases":cases,"minimum_sampled_skin_height_m":minimum_height,"release_cases":5,"steering_restart_established_walk_pause":true,"physical_controller_tested":false}
	FileAccess.open("res://../tools/motion_v04/run_up/validation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n")
	print("RUN_UP ",JSON.stringify(report))
	demo.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)

func capture(demo: Node3D) -> void:
	var output := ProjectSettings.globalize_path("res://../tools/motion_v04/run_up/frames")
	var samples := []
	for view in range(3):
		demo.reset_demo()
		demo.set_view(view)
		demo.close_view = true
		demo.update_camera()
		var folder := output.path_join(str(view))
		DirAccess.make_dir_recursive_absolute(folder)
		for frame in range(126):
			var input := Vector2.DOWN if frame >= 9 and frame < 93 else Vector2.ZERO
			demo.advance_demo(1.0/30.0,input)
			await process_frame
			await RenderingServer.frame_post_draw
			check(demo.get_viewport().get_texture().get_image().save_png(folder.path_join("%03d.png"%frame)) == OK,"Capture failed")
			if view == 0: samples.append({"frame":frame,"speed":demo.motion.speed,"phase":demo.animation.phase,"state":demo.animation.state,"run_mix":demo.animation.run_mix,"step_remaining_m":demo.motion.first_step_remaining})
	FileAccess.open(output.path_join("capture.json"),FileAccess.WRITE).store_string(JSON.stringify({"fps":30,"frames":126,"samples":samples},"  ")+"\n")
