extends "res://tests/test_import.gd"
func run() -> void:
	var viewer = load("res://locomotion.tscn").instantiate()
	root.add_child(viewer)
	await process_frame
	viewer.set_process(false)
	var player: AnimationPlayer = viewer.player
	player.callback_mode_process=AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	var skeleton: Skeleton3D=viewer.actor.find_child("Skeleton3D",true,false)
	var body: MeshInstance3D=viewer.actor.find_child("Human",true,false)
	var minimum_floor := INF
	var cases := []
	for phase in [0.0,0.2,0.6,1.05]:
		viewer.start_clip(&"Walk")
		player.advance(0.2)
		player.seek(phase,true)
		viewer.select_clip(&"Idle")
		var wait_time := 0.0
		for frame in range(60):
			player.advance(1.0/60.0)
			viewer._process(1.0/60.0)
			if viewer.pending_idle: wait_time+=1.0/60.0
			skeleton.force_update_all_bone_transforms()
			minimum_floor=minf(minimum_floor,skinned_bounds(body,skeleton)[1][0])
		check(viewer.clip==&"Idle" and not viewer.pending_idle,"Stop request did not complete")
		check(wait_time<=0.61,"Stop waited more than one step")
		cases.append({"requested_at":phase,"wait_seconds":wait_time})
	check(minimum_floor>=-0.003,"Review selector exceeded floor tolerance")
	viewer.paused=true
	viewer.select_clip(&"Walk")
	check(viewer.clip==&"Walk" and player.speed_scale==0.0,"Paused selection failed")
	viewer.select_clip(&"Idle")
	check(viewer.clip==&"Idle" and not viewer.pending_idle,"Paused idle selection failed")
	var view_checks := []
	for entry in [["Isometric", "isometric", 35.26439], ["Raised 3/4", "three_quarter", 45.0], ["Top-down", "top_down", 90.0]]:
		var found := false
		for button in viewer.find_children("*", "Button", true, false):
			if button.text == entry[0]:
				button.pressed.emit()
				found = true
		check(found and viewer.review_view == entry[1], "Review camera button failed: " + entry[0])
		var offset: Vector3 = viewer.camera.position - Vector3(0, 0.9, 0)
		var elevation := rad_to_deg(asin(offset.normalized().y))
		check(absf(elevation - float(entry[2])) < 0.001, "Incorrect review elevation")
		check(viewer.camera.projection == Camera3D.PROJECTION_ORTHOGONAL, "Review must be orthographic")
		check(viewer.camera.global_basis.is_finite(), "Invalid review camera basis")
		check(viewer.camera.unproject_position(Vector3(0,0.9,0)).is_finite(), "Invalid projected review centre")
		view_checks.append({"view": entry[1], "elevation_degrees": elevation, "size": viewer.camera.size})
	for selector in viewer.find_children("*", "OptionButton", true, false):
		for index in range(8):
			selector.item_selected.emit(index)
			check(absf(viewer.actor.rotation.y - deg_to_rad(index*45.0)) < 0.00001, "Facing selector failed")
	viewer.actor.rotation.y = 0
	viewer.set_review_view("isometric")
	var report := {"passed":failures.is_empty(),"failures":failures,"minimum_floor_m":minimum_floor,"stop_cases":cases,"paused_selection":true,"review_views":view_checks}
	var output:=FileAccess.open("res://../tools/blender/locomotion_previews/viewer_validation.json",FileAccess.WRITE)
	output.store_string(JSON.stringify(report,"  ")+"\n");output.close()
	print("LOCOMOTION_VIEWER ",report.passed," floor ",minimum_floor)
	quit(0 if failures.is_empty() else 1)
