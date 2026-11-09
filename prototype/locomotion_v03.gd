extends "res://locomotion_v02.gd"
## Animation-review sequence; input intent is queued through authored bridges.
var requested: StringName = &"Idle"
var run_data: Dictionary

func configure_viewer() -> void:
	character = preload("res://assets/human_locomotion_v03.glb")
	initial_animation = &"Idle"
	heading = "GAUNTLANDS / RUN — FIRST PASS"
	description = "Walk · relaxed unarmed run · matching foot contacts"
	instructions = "Choose Idle, Walk or Run. Gait changes finish the current support step."

func _ready() -> void:
	super._ready()
	run_data = JSON.parse_string(FileAccess.get_file_as_string("res://../tools/blender/locomotion_v03/build.json"))
	travel_data.clips.merge(run_data.clips)
	travel_data.travel_m_at_60hz.merge(run_data.travel_m_at_60hz)
	player.get_animation(&"Run").loop_mode = Animation.LOOP_LINEAR
	for name in run_data.transitions: player.get_animation(name).loop_mode = Animation.LOOP_NONE
	for button in find_children("*", "Button", true, false):
		if button.text == "Walk":
			var run_button := Button.new()
			run_button.text = "Run"
			button.get_parent().add_child(run_button)
			run_button.pressed.connect(func() -> void: select_clip(&"Run"))
			break
	for choice in find_children("*", "OptionButton", true, false):
		if choice.get_item_text(0) == "Inspect a single clip":
			choice.add_item("Run")
			for name in run_data.transitions: choice.add_item(name)

func select_clip(name: StringName) -> void:
	assert(name in [&"Idle", &"Walk", &"Run"])
	requested = name
	wants_walk = name != &"Idle"
	direct_review = false
	if not paused: resolve_request()

func enter_phase(name: StringName, phase: float = 0.0) -> void:
	start_clip(name)
	player.seek(phase * player.get_animation(name).length, true)

func resolve_request() -> void:
	if clip == &"Idle" and requested != &"Idle":
		start_clip(&"WalkStart", 0.12)
		return
	if clip not in [&"Walk", &"Run"] or clip == requested: return
	var period := player.get_animation(clip).length
	var phase := fposmod(player.current_animation_position / period, 1.0)
	var lead := "L" if phase < 0.00001 or phase > 0.99999 else "R" if absf(phase-0.5) < 0.00001 else ""
	if lead.is_empty(): return
	if clip == &"Walk":
		start_clip(StringName(("WalkToRun" if requested == &"Run" else "WalkStop") + lead))
	else:
		start_clip(StringName("RunToWalk" + lead))

func displacement(name: StringName, time: float) -> float:
	if name == &"Run": return float(run_data.run_speed)*time
	return super.displacement(name, time)

func advance_sequence(delta: float) -> void:
	if paused or delta <= 0.0: return
	player.speed_scale = 1.0
	if direct_review:
		var t := player.current_animation_position
		ground_distance += displacement(clip, t+delta)-displacement(clip,t)
		player.advance(delta)
		return
	var remaining := delta
	while remaining > 0.0000001:
		resolve_request()
		var t := player.current_animation_position
		var end := player.get_animation(clip).length
		if clip == &"Idle" or (clip == requested and clip in [&"Walk", &"Run"]):
			ground_distance += displacement(clip,t+remaining)-displacement(clip,t)
			player.advance(remaining)
			break
		if clip in [&"Walk", &"Run"]:
			end = end/2 if t < end/2-0.000001 else end
		var amount := minf(remaining,maxf(0.0,end-t))
		ground_distance += displacement(clip,t+amount)-displacement(clip,t)
		player.advance(amount)
		remaining -= amount
		if t+amount < end-0.000001: break
		if String(clip) in run_data.transitions:
			var meta: Dictionary = run_data.transitions[String(clip)]
			enter_phase(StringName(meta.to),float(meta.phase))
		elif clip == &"WalkStart":
			enter_phase(&"Walk")
		elif String(clip).begins_with("WalkStop"):
			enter_phase(&"Idle")
		elif clip in [&"Walk", &"Run"]:
			player.seek(fposmod(end,player.get_animation(clip).length),true)
			resolve_request()
		else: break

func capture_evidence() -> void:
	for child in get_children():
		if child is CanvasLayer: child.hide()
	var output := ProjectSettings.globalize_path("res://../tools/blender/locomotion_v03/frames")
	var cameras := {}
	var segments := [["Idle",.6],["WalkStart",.7],["Walk",1.2],["WalkToRunL",1.0],["Run",1.6],["RunToWalkL",1.0],["Walk",.6],["WalkStopR",.8],["Idle",.6]]
	var requests := {18:&"Walk",75:&"Run",153:&"Walk",201:&"Idle"}
	var states := []
	for view in REVIEW_VIEWS:
		set_review_view(view)
		cameras[view] = {"position":[camera.position.x,camera.position.y,camera.position.z],"orthographic_size":camera.size}
		var folder := output.path_join(view)
		DirAccess.make_dir_recursive_absolute(folder)
		actor.rotation.y=0; ground_distance=0; ground_reference=true; requested=&"Idle"; direct_review=false; paused=false
		enter_phase(&"Idle")
		for frame in range(243):
			if frame in requests: select_clip(requests[frame])
			if view == "isometric": states.append(String(clip))
			await get_tree().process_frame
			await RenderingServer.frame_post_draw
			assert(get_viewport().get_texture().get_image().save_png(folder.path_join("%03d.png"%frame))==OK)
			advance_sequence(1.0/30.0)
		for name in ["Run","WalkToRunR","RunToWalkR"]:
			enter_phase(name);direct_review=true
			var count := roundi(player.get_animation(name).length*30)
			for frame in range(count):
				ground_distance=displacement(name,frame/30.0)
				await save_review_frame(folder.path_join("%s_%03d.png"%[name,frame]),frame/30.0)
		ground_reference=false
		for facing in range(8):
			actor.rotation.y=deg_to_rad(facing*45.0)
			for frame in [0,6,12,18]:
				enter_phase(&"Run")
				await save_review_frame(folder.path_join("facing_%d_%02d.png"%[facing,frame]),frame/30.0)
	var file := FileAccess.open(output.path_join("cameras.json"),FileAccess.WRITE)
	file.store_string(JSON.stringify({"views":cameras,"segments":segments,"states":states,"fps":30},"  ")+"\n")
	get_tree().quit()
