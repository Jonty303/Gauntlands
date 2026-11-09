extends "res://proof.gd"
## In-place clip review; ground marks show the nominal 0.9 m/s travel speed.
var marks: Array[MeshInstance3D] = []
var ground_reference := true
var ground_distance := 0.0
var pending_idle := false
var previous_walk_time := 0.0
const REVIEW_VIEWS := ["isometric", "three_quarter", "top_down"]
var review_view := "isometric"

func _ready() -> void:
	get_viewport().msaa_3d = Viewport.MSAA_4X
	character = preload("res://assets/human_locomotion.glb")
	initial_animation = &"Idle"
	heading = "GAUNTLANDS  /  IDLE & WALK"
	description = "Relaxed idle · 1.2-second walk · reference travel 0.9 m/s"
	instructions = "Choose Idle or Walk. Stopping finishes the current step. Ground marks show travel speed."
	super._ready()
	for name in ["Idle", "Walk"]:
		player.get_animation(name).loop_mode = Animation.LOOP_LINEAR
	var row := HBoxContainer.new()
	row.position = Vector2(24, 210)
	get_child(get_child_count()-1).add_child(row)
	for label_text in ["Idle", "Walk", "Ground reference"]:
		var button := Button.new()
		button.text = label_text
		row.add_child(button)
		button.pressed.connect(func() -> void:
			if label_text == "Ground reference":
				ground_reference = not ground_reference
			else:
				select_clip(label_text)
		)
	# Keep view controls to the left so the elevated character stays unobscured.
	var views := VBoxContainer.new()
	views.position = Vector2(24, 250)
	get_child(get_child_count()-1).add_child(views)
	# Permanent review presets for the model's three requested sign-off views.
	for entry in [["Isometric", "isometric"], ["Raised 3/4", "three_quarter"], ["Top-down", "top_down"]]:
		var button := Button.new()
		button.text = entry[0]
		views.add_child(button)
		button.pressed.connect(func() -> void: set_review_view(entry[1]))
	var facing := OptionButton.new()
	for angle in range(0, 360, 45): facing.add_item("Facing %ddeg" % angle)
	views.add_child(facing)
	facing.item_selected.connect(func(index: int) -> void: actor.rotation.y = deg_to_rad(index * 45.0))
	for button in find_children("*", "Button", true, false):
		if button.text == "Three-quarter": button.text = "Low 3/4"
	set_review_view("isometric")
	for index in range(13):
		var mark := MeshInstance3D.new()
		var mesh := PlaneMesh.new()
		mesh.size = Vector2(2.2, 0.025)
		mark.mesh = mesh
		var material := StandardMaterial3D.new()
		material.albedo_color = Color(0.28, 0.32, 0.36)
		material.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		mark.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
		mark.material_override = material
		mark.position = Vector3(0, 0.006, index * 0.54 - 3.24)
		add_child(mark)
		marks.append(mark)

func set_review_view(view_name: String) -> void:
	assert(view_name in REVIEW_VIEWS)
	review_view = view_name
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 2.8
	var target := Vector3(0, 0.9, 0)
	var offset := Vector3(4, 4, 4) # Equal axes: 35.264deg elevation, 45deg azimuth.
	var up := Vector3.UP
	if view_name == "three_quarter":
		offset = Vector3(2.5, 5, 4.330127) # 45deg elevation, 30deg azimuth.
	elif view_name == "top_down":
		offset = Vector3(0, 6, 0)
		up = Vector3(0, 0, -1) # Explicit up avoids a singular vertical look-at.
	camera.position = target + offset
	camera.look_at(target, up)

func select_clip(name: StringName) -> void:
	if name == clip:
		pending_idle = false
		return
	if name == &"Idle" and clip == &"Walk" and not paused:
		pending_idle = true
		previous_walk_time = player.current_animation_position
		return
	start_clip(name)

func start_clip(name: StringName) -> void:
	pending_idle = false
	clip = name
	timeline.max_value = player.get_animation(clip).length
	player.play(clip, 0.0 if paused else 0.10)
	if clip == &"Walk": player.seek(0.36, true)
	player.speed_scale = 0.0 if paused else 1.0

func _process(delta: float) -> void:
	super._process(delta)
	if pending_idle and not paused:
		var current := player.current_animation_position
		for passing in [0.36, 0.96]:
			if (previous_walk_time < passing and current >= passing) or (previous_walk_time > current and current >= passing):
				player.seek(passing, true)
				start_clip(&"Idle")
				break
		previous_walk_time = current
		if pending_idle: status.text += " - finishing step"
	if clip == &"Walk" and not paused and not capture_mode:
		ground_distance += delta * 0.9
	for index in range(marks.size()):
		marks[index].visible = ground_reference
		marks[index].position.z = fposmod(index * 0.54 - ground_distance, 7.02) - 3.51

func capture_evidence() -> void:
	if "--review" in OS.get_cmdline_user_args():
		await record_review_views()
		return
	set_view(Vector3(2.5, 1.5, 4.5))
	if "--record" in OS.get_cmdline_user_args():
		await record_frames()
		return
	player.speed_scale = 0
	var output := ProjectSettings.globalize_path("res://../tools/blender/locomotion_previews")
	for entry in [["idle", "Idle", 0.0], ["walk_contact", "Walk", 0.0], ["walk_passing", "Walk", 0.3], ["walk_opposite", "Walk", 0.6], ["walk_side", "Walk", 0.3], ["walk_back", "Walk", 0.9]]:
		clip = entry[1]
		player.play(clip)
		player.seek(entry[2], true)
		if entry[0] == "walk_side": set_view(Vector3(5, 1.35, 0))
		if entry[0] == "walk_back": set_view(Vector3(0, 1.35, -5))
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		assert(get_viewport().get_texture().get_image().save_png(output.path_join(entry[0]+".png")) == OK)
	get_tree().quit()

func record_frames() -> void:
	var travel := "--travel" in OS.get_cmdline_user_args()
	var side_view := travel or "--side-view" in OS.get_cmdline_user_args()
	if side_view: set_view(Vector3(5, 1.35, 0))
	clip = &"Walk"
	timeline.max_value = 1.2
	player.play(clip)
	player.speed_scale = 0
	var folder := "frames_travel" if travel else ("frames_side" if side_view else "frames")
	var output := ProjectSettings.globalize_path("res://../tools/blender/locomotion_previews/" + folder)
	DirAccess.make_dir_recursive_absolute(output)
	for frame in range(72 if travel else 36):
		player.seek(fposmod(frame / 30.0, 1.2), true)
		ground_distance = 0.0 if travel else frame / 30.0 * 0.9
		if travel: actor.position.z = (frame / 30.0 - 1.2) * 0.9
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		assert(get_viewport().get_texture().get_image().save_png(output.path_join("%03d.png" % frame)) == OK)
	get_tree().quit()

func record_review_views() -> void:
	for child in get_children():
		if child is CanvasLayer: child.hide()
	clip = &"Walk"
	player.play(clip)
	player.speed_scale = 0
	var output := ProjectSettings.globalize_path("res://../tools/blender/locomotion_previews/frames_review")
	var cameras := {}
	for view_name in REVIEW_VIEWS:
		set_review_view(view_name)
		cameras[view_name] = {"position": [camera.position.x, camera.position.y, camera.position.z], "orthographic_size": camera.size}
		var folder: String = output.path_join(view_name)
		DirAccess.make_dir_recursive_absolute(folder)
		actor.rotation.y = 0
		ground_reference = true
		for frame in range(36):
			ground_distance = frame / 30.0 * 0.9
			await save_review_frame(folder.path_join("%03d.png" % frame), frame / 30.0)
		ground_reference = false
		for facing in range(8):
			actor.rotation.y = deg_to_rad(facing * 45.0)
			for frame in [0, 9, 18, 27]:
				await save_review_frame(folder.path_join("facing_%d_%02d.png" % [facing, frame]), frame / 30.0)
	var manifest := FileAccess.open(output.path_join("cameras.json"), FileAccess.WRITE)
	manifest.store_string(JSON.stringify({"views": cameras, "facing_degrees": [0,45,90,135,180,225,270,315], "pose_times_s": [0,0.3,0.6,0.9], "loop_seconds": 1.2, "frames": 36}, "  ")+"\n")
	manifest.close()
	get_tree().quit()

func save_review_frame(path: String, time: float) -> void:
	player.seek(time, true)
	await get_tree().process_frame
	await RenderingServer.frame_post_draw
	assert(get_viewport().get_texture().get_image().save_png(path) == OK)
