extends "res://tests/test_import.gd"

func press(demo: Node, button: JoyButton) -> void:
	var event := InputEventJoypadButton.new()
	event.button_index=button
	event.pressed=true
	demo._unhandled_input(event)

func run() -> void:
	var demo = load("res://dummy_actions.tscn").instantiate()
	demo.auto_test=true
	root.add_child(demo)
	await process_frame
	check(demo.catalogue.size()>=90,"Catalogue unexpectedly incomplete")
	check(demo.packs.size()==5,"Expected all five source packs")
	var results := []
	var sprint_count := 0
	for i in range(demo.catalogue.size()):
		demo.select_action(i)
		press(demo,JOY_BUTTON_A)
		var entry: Dictionary=demo.catalogue[i]
		check(demo.preview!=null,"Action failed to start: "+entry.name)
		if demo.preview==null: continue
		if entry.name.begins_with("Sprint"): sprint_count+=1
		check(absf(demo.preview_player.get_animation(entry.id).length-entry.duration)<.002,"Duration mismatch: "+entry.name)
		var visible := []
		for node in demo.preview.find_children("*","MeshInstance3D",true,false):
			if node.visible and node.name!="KevinMaleDummy":visible.append(String(node.name))
		for prop in entry.props:check(visible.has(prop),"Missing equipped prop %s on %s" % [prop,entry.name])
		for prop in visible:check(entry.props.has(prop),"Unexpected prop "+prop)
		var floor_min := INF
		var body := demo.preview.find_child("KevinMaleDummy",true,false) as MeshInstance3D
		for fraction in [0.0,.1,.25,.4,.5,.6,.75,.9,.999]:
			demo.action_time=float(entry.duration)*fraction
			demo.blend_time=1
			demo.apply_action_pose()
			for bone in range(demo.preview_skeleton.get_bone_count()):
				var transform: Transform3D=demo.preview_skeleton.get_bone_global_pose(bone)
				check(transform.is_finite(),"Non-finite pose: "+entry.name)
			var bounds := skinned_bounds(body,demo.preview_skeleton)
			floor_min=minf(floor_min,float(bounds[1][0]))
			check(float(bounds[1][1])-float(bounds[1][0])<3.2,"Exploded body: "+entry.name)
		check(floor_min>-.001,"Body penetrated more than 1 mm: "+entry.name)
		var frozen: float=demo.action_time
		press(demo,JOY_BUTTON_START)
		demo.advance_action(.1)
		check(demo.action_time==frozen,"Pause advanced action")
		press(demo,JOY_BUTTON_START)
		demo.action_time=float(entry.duration)-.001
		demo.advance_action(.02)
		if entry.loop or entry.hold:
			check(not demo.returning,"Loop/held pose returned unexpectedly")
			press(demo,JOY_BUTTON_B)
		else: check(demo.returning,"One-shot did not return automatically")
		for frame in range(15):demo.advance_action(1.0/60.0)
		check(demo.preview==null and demo.actor.visible,"Recovery failed: "+entry.name)
		results.append({"id":entry.id,"duration":entry.duration,"props":entry.props,"minimum_y_m":floor_min})
	check(sprint_count==5,"Expected five selectable sprint directions")
	check(not demo.player.has_animation("Sprint"),"Sprint leaked into locomotion")
	demo.select_action(0)
	press(demo,JOY_BUTTON_LEFT_SHOULDER)
	check(demo.selected==demo.catalogue.size()-1,"LB did not wrap")
	press(demo,JOY_BUTTON_RIGHT_SHOULDER)
	check(demo.selected==0,"RB did not wrap")
	var old_view: int=demo.view_index
	press(demo,JOY_BUTTON_Y)
	check(demo.view_index==(old_view+1)%3,"Y did not switch view")
	press(demo,JOY_BUTTON_A)
	press(demo,JOY_BUTTON_RIGHT_SHOULDER)
	check(demo.preview==null and demo.selected==1,"Selection did not stop previous action")
	demo.reset_demo()
	for i in range(360):demo.advance_demo(1.0/60.0,Vector2.UP)
	check(absf(demo.speed-4)<.001 and demo.run_mix>.999,"Approved top run changed")
	for i in range(90):demo.advance_demo(1.0/60.0,Vector2.ZERO)
	check(demo.idle_mix>.999,"Movement did not return to idle")
	# Exercise the real Godot event dispatch, not only the handler mapping above.
	demo.select_action(0)
	for button in [JOY_BUTTON_RIGHT_SHOULDER,JOY_BUTTON_A,JOY_BUTTON_B]:
		var event := InputEventJoypadButton.new()
		event.button_index=button
		event.pressed=true
		Input.parse_input_event(event)
		await process_frame
		if button==JOY_BUTTON_RIGHT_SHOULDER:check(demo.selected==1,"Dispatched RB failed")
		if button==JOY_BUTTON_A:check(demo.preview!=null,"Dispatched A failed")
		if button==JOY_BUTTON_B:check(demo.returning,"Dispatched B failed")
		event=event.duplicate()
		event.pressed=false
		Input.parse_input_event(event)
		await process_frame
	demo.selector.item_selected.emit(4)
	check(demo.selected==4 and demo.preview==null,"Dropdown selection failed")
	var report := {"passed":failures.is_empty(),"failures":failures,"engine":Engine.get_version_info().string,"clips":results,"selectable_sprints":sprint_count,"controller_events":"synthetic A/B/LB/RB/Y/Start; real Godot dispatch of A/B/RB; dropdown signal; physical controller not operated"}
	FileAccess.open("res://../tools/kevin_actions/validation.json",FileAccess.WRITE).store_string(JSON.stringify(report,"  ")+"\n")
	print("ACTION_VIEWER ",JSON.stringify({"passed":failures.is_empty(),"clips":results.size(),"failures":failures}))
	demo.queue_free()
	await process_frame
	quit(0 if failures.is_empty() else 1)
