extends Node3D
## Review-only animation viewer. No gameplay/controller implementation.
var actor: Node3D
var player: AnimationPlayer
var camera: Camera3D
var timeline: HSlider
var status: Label
var paused := false
var clip: StringName
var capture_mode := false

func _ready() -> void:
	capture_mode = "--capture" in OS.get_cmdline_user_args()
	actor = preload("res://assets/human_diagnostic.glb").instantiate()
	add_child(actor)
	player = actor.find_child("AnimationPlayer", true, false) as AnimationPlayer
	for name in player.get_animation_list():
		if name != "RESET":
			clip = name
	assert(not clip.is_empty())
	player.get_animation(clip).loop_mode = Animation.LOOP_LINEAR
	var floor_mesh := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(6, 6)
	floor_mesh.mesh = plane
	var floor_material := StandardMaterial3D.new()
	floor_material.albedo_color = Color(0.16, 0.19, 0.22)
	floor_material.roughness = 1.0
	floor_mesh.material_override = floor_material
	add_child(floor_mesh)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-35, -30, 0)
	sun.light_energy = 0.65
	sun.shadow_enabled = true
	sun.shadow_bias = 0.08
	sun.shadow_normal_bias = 3.0
	add_child(sun)
	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-20, 145, 0)
	fill.light_energy = 0.25
	add_child(fill)
	var environment_node := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.055, 0.065, 0.08)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.75, 0.80, 0.9)
	environment.ambient_light_energy = 0.35
	environment_node.environment = environment
	add_child(environment_node)
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 2.8
	add_child(camera)
	set_view(Vector3(2.5, 1.5, 4.5))
	build_ui()
	player.play(clip)
	if capture_mode:
		capture_evidence.call_deferred()

func set_view(position_value: Vector3) -> void:
	camera.position = position_value
	camera.look_at(Vector3(0, 1.16, 0))

func build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var panel := VBoxContainer.new()
	panel.position = Vector2(24, 20)
	panel.size.x = 1052
	layer.add_child(panel)
	var title := Label.new()
	title.text = "GAUNTLANDS  /  ANIMATED RIG PROOF"
	title.add_theme_font_size_override("font_size", 24)
	panel.add_child(title)
	var subtitle := Label.new()
	subtitle.text = "1.80 m human · diagnostic motion · Blender → Godot 4.5.2"
	panel.add_child(subtitle)
	status = Label.new()
	panel.add_child(status)
	var buttons := HBoxContainer.new()
	panel.add_child(buttons)
	for label_text in ["Play / pause", "Front", "Side", "Back", "Three-quarter"]:
		var button := Button.new()
		button.text = label_text
		buttons.add_child(button)
		button.pressed.connect(func() -> void:
			match label_text:
				"Play / pause":
					paused = not paused
					player.speed_scale = 0.0 if paused else 1.0
				"Front": set_view(Vector3(0, 1.1, 5))
				"Side": set_view(Vector3(5, 1.1, 0))
				"Back": set_view(Vector3(0, 1.1, -5))
				"Three-quarter": set_view(Vector3(2.5, 1.5, 4.5))
		)
	timeline = HSlider.new()
	timeline.min_value = 0
	timeline.max_value = 8
	timeline.step = 1.0 / 30.0
	panel.add_child(timeline)
	timeline.value_changed.connect(func(value: float) -> void:
		player.seek(value, true)
	)
	var note := Label.new()
	note.text = "Left leg → right leg → arms → head turn. Drag the timeline to inspect a pose."
	panel.add_child(note)

func _process(_delta: float) -> void:
	if player and player.is_playing():
		timeline.set_value_no_signal(player.current_animation_position)
		status.text = "Diagnostic  •  %.2f / 8.00 seconds" % player.current_animation_position

func capture_evidence() -> void:
	player.speed_scale = 0
	var output := ProjectSettings.globalize_path("res://../tools/blender/animation_previews")
	for entry in [["godot_neutral", 0.0], ["godot_left_leg", 1.0], ["godot_right_leg", 3.0], ["godot_arms", 5.0], ["godot_head", 6.5], ["godot_side", 1.0], ["godot_back", 3.0]]:
		if entry[0] == "godot_side": set_view(Vector3(5, 1.1, 0))
		if entry[0] == "godot_back": set_view(Vector3(0, 1.1, -5))
		player.seek(entry[1], true)
		await get_tree().process_frame
		await RenderingServer.frame_post_draw
		var error := get_viewport().get_texture().get_image().save_png(output.path_join(entry[0] + ".png"))
		assert(error == OK)
	get_tree().quit()
