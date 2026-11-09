extends "res://tests/test_import.gd"
var metrics := {}
func run() -> void:
	var demo = load("res://motion_demo.tscn").instantiate()
	demo.auto_test = true
	root.add_child(demo)
	await process_frame
	var skeleton: Skeleton3D = demo.actor.find_child("Skeleton3D", true, false)
	check(skeleton != null and skeleton.get_bone_count() == 137, "Expected accepted skeleton")
	check(FileAccess.get_sha256("res://assets/human_locomotion_v03.glb") == "98e80de0c02fd70007d7949a861b012bf1b9b349df59b914c72585a3a79171c7", "Accepted export changed")
	var positions := []
	var maximum_yaw_step := 0.0
	var maximum_bone_step := 0.0
	var peak_bone := ""
	var peak_frame := 0
	var minimum_skin_height := INF
	var maximum_ground_lift := 0.0
	var body: MeshInstance3D = demo.actor.find_child("Human", true, false)
	var states := {}
	for hz in [30, 60, 120]:
		demo.reset_demo()
		var previous_heading: float = demo.motion.heading
		var previous_rotations: Array[Quaternion] = []
		for i in range(skeleton.get_bone_count()): previous_rotations.append(skeleton.get_bone_pose_rotation(i))
		for frame in range(hz * 12):
			demo.advance_demo(1.0/hz, demo.rehearsal(float(frame)/hz))
			check(demo.motion.speed <= 2.200001, "Speed limit")
			check(demo.motion.position.is_finite(), "Non-finite position")
			states[demo.animation.state] = true
			maximum_ground_lift = maxf(maximum_ground_lift, demo.animation.ground_lift)
			if hz == 60:
				maximum_yaw_step = maxf(maximum_yaw_step, absf(angle_difference(previous_heading, demo.motion.heading)))
				for i in range(skeleton.get_bone_count()):
					var rotation := skeleton.get_bone_pose_rotation(i)
					check(rotation.is_finite(), "Non-finite bone")
					var bone_step := previous_rotations[i].angle_to(rotation)
					if bone_step > maximum_bone_step:
						maximum_bone_step = bone_step
						peak_bone = skeleton.get_bone_name(i)
						peak_frame = frame
					previous_rotations[i] = rotation
				if frame % 6 == 0:
					skeleton.force_update_all_bone_transforms()
					minimum_skin_height = minf(minimum_skin_height, skinned_bounds(body, skeleton)[1][0])
			previous_heading = demo.motion.heading
		positions.append(demo.motion.position)
		check(demo.motion.speed < 0.00001 and demo.animation.state == "Idle", "Did not settle to idle")
	var frame_rate_error: float = maxf(positions[0].distance_to(positions[1]), positions[0].distance_to(positions[2]))
	check(frame_rate_error < 0.02, "Frame-rate dependent path")
	check(minimum_skin_height >= -0.003, "Runtime blend penetrates floor by more than 3 mm")
	check(maximum_yaw_step <= deg_to_rad(7.01), "Heading snapped")
	check(states.has("Run") and states.has("Starting") and states.has("Stopping"), "Missing runtime states")
	# Straight full-speed travel and stop distance, independent of facing/camera.
	var heading_results := []
	for view in range(3):
		demo.set_view(view)
		for facing in range(8):
			demo.reset_demo()
			var input := Vector2.from_angle(facing * TAU / 8.0)
			var direction: Vector3 = demo.direction_for(input)
			demo.motion.heading = atan2(direction.x, direction.z)
			for i in range(240): demo.advance_demo(1.0/60.0, input)
			check(absf(demo.motion.speed - 2.2) < 0.00001, "Full tilt failed")
			heading_results.append(demo.travelled)
			var stop_start: Vector3 = demo.motion.position
			for i in range(30): demo.advance_demo(1.0/60.0, Vector2.ZERO)
			check(demo.motion.speed < 0.00001, "Release took more than 0.5 seconds")
			check(demo.motion.position.distance_to(stop_start) < 0.5, "Excessive run stopping distance")
	var diagonal_error: float = heading_results.max() - heading_results.min()
	check(diagonal_error < 0.00001, "Diagonal / view speed mismatch")
	# Arbitrary-phase stops and changed intent: both leads in both steady gaits.
	var stop_cases := 0
	for speed in [0.9, 2.2]:
		for phase in [0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875]:
			demo.reset_demo()
			demo.motion.speed = speed
			demo.motion.desired_speed = speed
			demo.animation.idle_mix = 0.0
			demo.animation.run_mix = 1.0 if speed > 1.0 else 0.0
			demo.animation.phase = phase
			demo.animation.was_requested = true
			for frame in range(60):
				demo.advance_demo(1.0/60.0, Vector2.ZERO)
				if frame % 6 == 0:
					skeleton.force_update_all_bone_transforms()
					check(skinned_bounds(body, skeleton)[1][0] >= -0.003, "Phase stop floor penetration")
			check(demo.animation.state == "Idle" and demo.motion.speed == 0.0, "Phase stop failed to settle")
			stop_cases += 1
	# No queue: cancel and restart during start/stop, not after their clips finish.
	demo.reset_demo()
	demo.advance_demo(0.2, Vector2(0, -1))
	demo.advance_demo(1.0/60.0, Vector2.ZERO)
	check(not demo.motion.starting and demo.motion.desired_speed == 0.0, "Start cancellation queued")
	demo.advance_demo(1.0/60.0, Vector2(1, 0))
	check(demo.motion.desired_speed == 2.2, "Restart queued")
	var before_pause: Vector3 = demo.motion.position
	var phase_before_pause: float = demo.animation.phase
	demo.paused = true
	demo.advance_demo(0.2, Vector2(0, 1))
	check(demo.motion.position == before_pause and demo.animation.phase == phase_before_pause, "Pause advanced simulation")
	demo.paused = false
	demo.reset_demo()
	# Real InputMap keyboard path, including circular diagonal limiting and focus.
	Input.action_press("demo_key_up")
	Input.action_press("demo_key_right")
	demo.controls.neutral_required = false
	check(absf(demo.controls.read().length() - 0.55) < 0.00001, "Keyboard walk mapping")
	Input.action_press("demo_key_run")
	check(absf(demo.controls.read().length() - 1.0) < 0.00001, "Keyboard run mapping")
	demo.controls.focused = false
	check(demo.controls.read() == Vector2.ZERO, "Focus loss did not suppress input")
	demo.controls.focused = true
	demo.joy_changed(0, false)
	check(demo.controls.read() == Vector2.ZERO, "Disconnect left movement active")
	for direction in ["left", "right", "up", "down"]:
		check(InputMap.action_get_events("demo_stick_" + direction).size() > 0, "Missing joy axis action")
	# Synthetic analog events exercise radial deadzone without a physical pad.
	for sample in [0.0, 0.1, 0.17, 0.5, 1.0]:
		Input.action_press("demo_stick_right", sample)
		var value := Input.get_vector("demo_stick_left", "demo_stick_right", "demo_stick_up", "demo_stick_down", 0.18)
		check(value == Vector2.ZERO if sample <= 0.18 else value.x > 0.0, "Radial deadzone")
	Input.action_release("demo_stick_right")
	metrics = {"passed":failures.is_empty(),"failures":failures,"frame_rates":[30,60,120],"path_difference_m":frame_rate_error,"arbitrary_phase_stop_cases":stop_cases,"direction_cases":24,"direction_distance_difference_m":diagonal_error,"maximum_yaw_step_deg_at_60hz":rad_to_deg(maximum_yaw_step),"maximum_bone_rotation_step_deg_at_60hz":rad_to_deg(maximum_bone_step),"maximum_ground_lift_m":maximum_ground_lift,"sole_probe_count":demo.animation.probes.size(),"peak_bone":peak_bone,"peak_bone_frame":peak_frame,"minimum_sampled_skin_height_m":minimum_skin_height,"states":states.keys(),"physical_controller_tested":false,"connected_devices":Input.get_connected_joypads()}
	FileAccess.open("res://../tools/motion_v04/validation.json",FileAccess.WRITE).store_string(JSON.stringify(metrics,"  ") + "\n")
	print("MOTION_DEMO ", JSON.stringify(metrics))
	demo.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
