extends "res://locomotion.gd"
## v0.2 review sequence, deliberately separate from gameplay movement.
var wants_walk := false
var direct_review := false
var travel_data: Dictionary

func configure_viewer() -> void:
	character = preload("res://assets/human_locomotion_v02.glb")
	initial_animation = &"Idle"
	heading = "GAUNTLANDS / HUMAN MALE v0.2 — WORK IN PROGRESS"
	description = "Planted idle · setting off · approved walk · left/right stop"
	instructions = "Walk starts with a weight transfer. Idle requests a stop at the next foot contact."

func _ready() -> void:
	super._ready()
	travel_data = JSON.parse_string(FileAccess.get_file_as_string("res://../tools/blender/locomotion_v02/build.json"))
	player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	for name in ["WalkStart", "WalkStopL", "WalkStopR"]:
		player.get_animation(name).loop_mode = Animation.LOOP_NONE
	var clips := OptionButton.new()
	clips.position = Vector2(24, 390)
	clips.add_item("Inspect a single clip")
	for name in ["Idle", "WalkStart", "Walk", "WalkStopL", "WalkStopR"]: clips.add_item(name)
	for child in get_children():
		if child is CanvasLayer: child.add_child(clips)
	clips.item_selected.connect(func(index: int) -> void:
		if index > 0:
			direct_review = true
			start_clip(clips.get_item_text(index))
	)

func select_clip(name: StringName) -> void:
	direct_review = false
	wants_walk = name == &"Walk"
	if paused: return
	if clip == &"Idle" and wants_walk: start_clip(&"WalkStart", 0.12)

func start_clip(name: StringName, blend: float = 0.0) -> void:
	clip = name
	pending_idle = false
	timeline.max_value = player.get_animation(name).length
	player.play(name, blend)
	player.seek(0.0, true)
	player.speed_scale = 0.0 if paused else 1.0

func displacement(name: StringName, time: float) -> float:
	if name == &"Walk": return 0.9 * time
	var values: Array = travel_data.travel_m_at_60hz[String(name)]
	var frame := clampf(time * 60.0, 0.0, values.size() - 1.0)
	var index := int(frame)
	return lerpf(float(values[index]), float(values[mini(index + 1, values.size()-1)]), frame-index)

func advance_sequence(delta: float) -> void:
	if paused or delta <= 0.0: return
	player.speed_scale = 1.0
	if direct_review:
		var time := player.current_animation_position
		var end := player.get_animation(clip).length
		ground_distance += 0.9*delta if clip == &"Walk" else displacement(clip,minf(time+delta,end))-displacement(clip,time)
		player.advance(delta)
		return
	var remaining := delta
	while remaining > 0.000001:
		var time := player.current_animation_position
		if clip == &"Idle":
			if wants_walk:
				start_clip(&"WalkStart", 0.12)
				continue
			player.advance(remaining)
			break
		if clip == &"Walk" and wants_walk:
			ground_distance += 0.9 * remaining
			player.advance(remaining)
			break
		var end := player.get_animation(clip).length
		if clip == &"Walk":
			if absf(time) < 0.000001 or absf(time-1.2) < 0.000001:
				start_clip(&"WalkStopL")
				continue
			if absf(time-0.6) < 0.000001:
				start_clip(&"WalkStopR")
				continue
			end = 0.6 if time < 0.6 else 1.2
		var amount := minf(remaining, maxf(0.0, end-time))
		ground_distance += displacement(clip, time+amount) - displacement(clip, time)
		player.advance(amount)
		remaining -= amount
		if time+amount >= end-0.000001:
			match clip:
				&"WalkStart": start_clip(&"Walk" if wants_walk else &"WalkStopL")
				&"Walk": start_clip(&"WalkStopR" if end < 1.0 else &"WalkStopL")
				_: start_clip(&"Idle")
		else: break

func _process(delta: float) -> void:
	if not player: return
	if not capture_mode: advance_sequence(delta)
	timeline.set_value_no_signal(player.current_animation_position)
	status.text = "%s — %.2f / %.2f seconds" % [clip, player.current_animation_position, player.get_animation(clip).length]
	if clip == &"Walk" and not wants_walk and not direct_review: status.text += " — finishing step"
	for index in range(marks.size()):
		marks[index].visible = ground_reference
		marks[index].position.z = fposmod(index * 0.54 - ground_distance, 7.02) - 3.51

func capture_evidence() -> void:
	for child in get_children():
		if child is CanvasLayer: child.hide()
	var output := ProjectSettings.globalize_path("res://../tools/blender/locomotion_v02/frames")
	var camera_manifest := {}
	# Two complete sequences: stop with each leading foot, then settle back to idle.
	var start_duration: float = player.get_animation(&"WalkStart").length
	var segments := [["Idle", 0.8], ["WalkStart", start_duration], ["Walk", 1.2], ["WalkStopL", 0.8], ["Idle", 0.8], ["WalkStart", start_duration], ["Walk", 1.8], ["WalkStopR", 0.8], ["Idle", 0.8]]
	var start_requests: Array[int] = []
	var stop_requests: Array[int] = []
	var total_frames := 0
	for segment in segments:
		var count := roundi(float(segment[1])*30)
		if segment[0] == "WalkStart": start_requests.append(total_frames)
		if segment[0] == "Walk": stop_requests.append(total_frames+count-4)
		total_frames += count
	for view_name in REVIEW_VIEWS:
		set_review_view(view_name)
		camera_manifest[view_name] = {"position": [camera.position.x,camera.position.y,camera.position.z], "orthographic_size": camera.size}
		var folder := output.path_join(view_name)
		DirAccess.make_dir_recursive_absolute(folder)
		actor.rotation.y = 0
		ground_distance = 0.0
		ground_reference = true
		wants_walk = false
		direct_review = false
		paused = false
		start_clip(&"Idle")
		for frame in range(total_frames):
			if frame in start_requests: select_clip(&"Walk")
			if frame in stop_requests: select_clip(&"Idle")
			await get_tree().process_frame
			await RenderingServer.frame_post_draw
			assert(get_viewport().get_texture().get_image().save_png(folder.path_join("%03d.png" % frame)) == OK)
			advance_sequence(1.0/30.0)
		ground_reference = false
		for facing in range(8):
			actor.rotation.y = deg_to_rad(facing*45.0)
			for name in ["Idle", "WalkStart", "WalkStopL", "WalkStopR"]:
				start_clip(name)
				player.speed_scale = 0
				await save_review_frame(folder.path_join("facing_%d_%s.png" % [facing,name]), 0.4)
	var file := FileAccess.open(output.path_join("cameras.json"), FileAccess.WRITE)
	file.store_string(JSON.stringify({"views": camera_manifest, "segments": segments, "fps": 30, "facing_degrees": [0,45,90,135,180,225,270,315]}, "  ")+"\n")
	get_tree().quit()
