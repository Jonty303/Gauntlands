extends "res://tests/test_import.gd"

func run() -> void:
	var demo = load("res://dummy_walk.tscn").instantiate()
	demo.auto_test = true
	root.add_child(demo)
	await process_frame
	if demo.player == null:
		check(false,"Dummy failed to initialise")
		quit(1)
		return
	var skeleton: Skeleton3D = demo.actor.find_child("Skeleton3D",true,false)
	var mesh: MeshInstance3D = demo.actor.find_child("KevinMaleDummy",true,false)
	check(skeleton != null and mesh != null,"Missing dummy mesh/rig")
	if skeleton == null or mesh == null:
		demo.actor.print_tree_pretty()
		quit(1)
		return
	check(skeleton.get_bone_count()==56,"Unexpected bone count")
	check(absf(demo.player.get_animation("Walk").length-.8)<.0001,"Wrong walk duration")
	check(mesh.get_active_material(0)!=null,"Missing review material")
	var cases := []
	for hz in [30,60,120]:
		for view in range(3):
			for facing in range(8):
				demo.reset_demo()
				demo.set_view(view)
				var input := Vector2.from_angle(facing*TAU/8.0)
				var direction: Vector3 = demo.direction_for(input)
				for frame in range(hz*2): demo.advance_demo(1.0/hz,input)
				var position: Vector3 = demo.actor.position
				position.y = 0
				check(position.distance_to(direction*4)<.0001,"Travel rate/direction mismatch")
				check(absf(demo.travelled-4)<.0001,"Incorrect travel distance")
				var phase: float = demo.phase_time
				demo.advance_demo(.5,Vector2.ZERO)
				check(is_equal_approx(demo.phase_time,phase),"Release advanced walk")
				check(demo.actor.position.distance_to(Vector3(position.x,demo.actor.position.y,position.z))<.0001,"Release moved actor")
				cases.append({"hz":hz,"view":view,"facing":facing,"travel_m":demo.travelled})
	demo.reset_demo()
	for frame in range(120): demo.advance_demo(1.0/60.0,Vector2(0,-.5))
	check(absf(demo.travelled-2)<.0001 and absf(demo.phase_time-.2)<.0001,"Half-tilt travel/cadence mismatch")
	var held_position: Vector3 = demo.actor.position
	var held_phase: float = demo.phase_time
	demo.toggle_pause()
	demo.advance_demo(.25,Vector2.UP)
	check(demo.actor.position.is_equal_approx(held_position) and demo.phase_time==held_phase,"Pause moved actor")
	demo.toggle_pause()
	demo.reset_demo()
	var minimum_floor := INF
	var maximum_floor := -INF
	var maximum_height := 0.0
	var loop_start := []
	for i in range(97):
		demo.phase_time = float(i)/120.0
		if i==96: demo.phase_time = 0.0
		demo.apply_pose()
		skeleton.force_update_all_bone_transforms()
		var bounds := skinned_bounds(mesh,skeleton)
		minimum_floor = minf(minimum_floor,bounds[1][0])
		maximum_floor = maxf(maximum_floor,bounds[1][0])
		maximum_height = maxf(maximum_height,bounds[1][1])
		if i==0: loop_start=bounds
		if i==96: check(bounds==loop_start,"Loop seam mismatch")
	check(minimum_floor>=-.001,"Foot penetrated floor over 1 mm")
	check(maximum_floor<.003,"Ground contact floated above 3 mm")
	check(maximum_height>1.7 and maximum_height<1.9,"Incorrect model scale")
	demo.controls.focused=false
	check(demo.controls.read().is_zero_approx(),"Focus loss did not suppress input")
	demo.controls.focused=true
	var report := {"engine":Engine.get_version_info().string,"passed":failures.is_empty(),"failures":failures,
		"cases":cases,"minimum_floor_m":minimum_floor,"maximum_floor_m":maximum_floor,"maximum_height_m":maximum_height,
		"joypads_detected":Input.get_connected_joypads(),"physical_joypad_test":"not performed"}
	FileAccess.open("res://../tools/kevin_walk/validation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"
")
	print("DUMMY_WALK_VALIDATION ", report)
	if "--capture" in OS.get_cmdline_user_args():
		demo.close_view=true
		for view in range(3):
			demo.reset_demo()
			demo.set_view(view)
			var folder := ProjectSettings.globalize_path("res://../tools/kevin_walk/frames/"+str(view))
			DirAccess.make_dir_recursive_absolute(folder)
			for frame in range(48):
				demo.advance_demo(1.0/30.0,Vector2.UP)
				await process_frame
				await RenderingServer.frame_post_draw
				get_root().get_texture().get_image().save_png(folder.path_join("%03d.png" % frame))
		for view in range(3):
			demo.set_view(view)
			for facing in range(8):
				demo.reset_demo()
				demo.advance_demo(.2,Vector2.from_angle(facing*TAU/8.0))
				await process_frame
				await RenderingServer.frame_post_draw
				get_root().get_texture().get_image().save_png("res://../tools/kevin_walk/frames/facing_%d_%d.png" % [view,facing])
	quit(0 if failures.is_empty() else 1)
