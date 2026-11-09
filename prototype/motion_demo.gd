extends Node3D
const MotionState = preload("res://motion/motion_state.gd")
const MotionAnimation = preload("res://motion/motion_animation.gd")
const MotionInput = preload("res://motion/motion_input.gd")
const VIEWS := ["Isometric", "Raised 3/4", "Top-down"]
const OFFSETS := [Vector3(4, 4, 4), Vector3(2.5, 5, 4.330127), Vector3(0, 6, 0)]
const STEP := 1.0 / 120.0
var motion := MotionState.new()
var controls := MotionInput.new()
var animation := MotionAnimation.new()
var actor: Node3D
var camera: Camera3D
var floor_mesh: MeshInstance3D
var status: Label
var device_status: Label
var stick_display: Control
var pause_button: Button
var view_buttons: Array[Button] = []
var view_index := 0
var paused := false
var close_view := false
var auto_test := false
var capture_mode := false
var replaying := false
var replay_time := 0.0
var replay_button: Button
var accumulator := 0.0
var input_value := Vector2.ZERO
var travelled := 0.0
var demo_time := 0.0

func _ready() -> void:
	DisplayServer.window_set_title("Gauntlands — Joypad motion demo v0.4")
	get_viewport().msaa_3d = Viewport.MSAA_4X
	controls.configure()
	actor = preload("res://assets/human_locomotion_v03.glb").instantiate()
	add_child(actor)
	add_child(animation)
	animation.setup(actor)
	build_stage()
	build_ui()
	set_view(0)
	Input.joy_connection_changed.connect(joy_changed)
	update_device_status()
	capture_mode = "--motion-capture" in OS.get_cmdline_user_args()
	if capture_mode: capture_evidence.call_deferred()

func build_stage() -> void:
	floor_mesh = MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(100, 100)
	floor_mesh.mesh = plane
	var material := ShaderMaterial.new()
	var shader := Shader.new()
	shader.code = """shader_type spatial;
varying vec3 world;
void vertex(){ world = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz; }
void fragment(){
 vec2 p = world.xz;
 vec2 edge = abs(fract(p + 0.5) - 0.5);
 vec2 aa = max(fwidth(p), vec2(0.001));
 float grid = 1.0 - min(smoothstep(0.009, 0.009 + aa.x, edge.x), smoothstep(0.009, 0.009 + aa.y, edge.y));
 vec3 colour = mix(vec3(0.095, 0.122, 0.145), vec3(0.17, 0.205, 0.23), grid);
 if(abs(p.x) < 0.018) colour = vec3(0.20, 0.38, 0.38);
 if(abs(p.y) < 0.018) colour = vec3(0.42, 0.29, 0.17);
 ALBEDO = colour; ROUGHNESS = 1.0;
}"""
	material.shader = shader
	floor_mesh.material_override = material
	add_child(floor_mesh)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-40, -30, 0)
	sun.light_energy = 0.85
	sun.shadow_enabled = true
	sun.directional_shadow_max_distance = 30
	add_child(sun)
	var fill := DirectionalLight3D.new()
	fill.rotation_degrees = Vector3(-20, 145, 0)
	fill.light_energy = 0.3
	add_child(fill)
	var environment_node := WorldEnvironment.new()
	var environment := Environment.new()
	environment.background_mode = Environment.BG_COLOR
	environment.background_color = Color(0.055, 0.065, 0.08)
	environment.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	environment.ambient_light_color = Color(0.75, 0.80, 0.9)
	environment.ambient_light_energy = 0.45
	environment_node.environment = environment
	add_child(environment_node)
	camera = Camera3D.new()
	camera.projection = Camera3D.PROJECTION_ORTHOGONAL
	camera.size = 6.5
	camera.far = 120
	add_child(camera)
	camera.current = true

func build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]: margin.add_theme_constant_override("margin_" + side, 22)
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(margin)
	var column := VBoxContainer.new()
	column.mouse_filter = Control.MOUSE_FILTER_IGNORE
	margin.add_child(column)
	var title := Label.new()
	title.text = "GAUNTLANDS  /  MOTION LAB"
	title.add_theme_font_size_override("font_size", 24)
	column.add_child(title)
	var subtitle := Label.new()
	subtitle.text = "Human prototype v0.4  ·  Left stick to walk / run  ·  1 metre grid"
	subtitle.modulate = Color(0.7, 0.8, 0.83)
	column.add_child(subtitle)
	var buttons := HBoxContainer.new()
	buttons.add_theme_constant_override("separation", 8)
	column.add_child(buttons)
	for i in range(3):
		var button := make_button("%d  %s" % [i+1, VIEWS[i]], buttons)
		button.pressed.connect(func() -> void: set_view(i))
		view_buttons.append(button)
	var close_button := make_button("Close view", buttons)
	close_button.toggle_mode = true
	close_button.toggled.connect(func(value: bool) -> void:
		close_view = value
		update_camera()
	)
	pause_button = make_button("P  Pause", buttons)
	pause_button.pressed.connect(toggle_pause)
	make_button("R  Reset", buttons).pressed.connect(reset_demo)
	replay_button = make_button("Replay test", buttons)
	replay_button.pressed.connect(func() -> void:
		var start_replay := not replaying
		reset_demo()
		replaying = start_replay
		replay_button.text = "Stop replay" if replaying else "Replay test"
	)
	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	column.add_child(spacer)
	var bottom := PanelContainer.new()
	var style := StyleBoxFlat.new()
	style.bg_color = Color(0.025, 0.045, 0.06, 0.94)
	style.content_margin_left = 16
	style.content_margin_right = 16
	style.content_margin_top = 12
	style.content_margin_bottom = 12
	bottom.add_theme_stylebox_override("panel", style)
	column.add_child(bottom)
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 18)
	bottom.add_child(row)
	stick_display = preload("res://motion/stick_display.gd").new()
	stick_display.custom_minimum_size = Vector2(70, 76)
	row.add_child(stick_display)
	var info := VBoxContainer.new()
	row.add_child(info)
	status = Label.new()
	status.add_theme_font_size_override("font_size", 18)
	info.add_child(status)
	device_status = Label.new()
	device_status.modulate = Color(0.65, 0.79, 0.8)
	info.add_child(device_status)
	var help := Label.new()
	help.text = "WASD / arrows: walk   ·   Shift: run   ·   Release: stop   ·   P: pause   ·   R: reset"
	info.add_child(help)
	update_hud()

func make_button(text: String, parent: Node) -> Button:
	var button := Button.new()
	button.text = text
	button.focus_mode = Control.FOCUS_NONE
	parent.add_child(button)
	return button

func set_view(index: int) -> void:
	view_index = index
	for i in range(view_buttons.size()): view_buttons[i].modulate = Color(0.4, 0.95, 0.86) if i == index else Color.WHITE
	update_camera()

func update_camera() -> void:
	var target := motion.position + Vector3(0, 0.9, 0)
	camera.position = target + OFFSETS[view_index]
	camera.look_at(target, Vector3(0, 0, -1) if view_index == 2 else Vector3.UP)
	camera.size = 2.8 if close_view else 6.5
	floor_mesh.position = Vector3(floorf(motion.position.x), 0, floorf(motion.position.z))

func direction_for(value: Vector2) -> Vector3:
	return MotionState.camera_direction(value, camera.basis.x, camera.basis.y)

func advance_demo(delta: float, value: Vector2) -> void:
	if paused or delta <= 0.0: return
	input_value = value.limit_length(1.0)
	accumulator += minf(delta, 0.25)
	var direction := direction_for(input_value)
	while accumulator + 0.00000001 >= STEP:
		var distance := motion.step(STEP, direction, input_value.length())
		animation.step(STEP, motion, distance)
		travelled += distance
		demo_time += STEP
		accumulator -= STEP
	actor.position = motion.position + Vector3.UP * animation.ground_lift
	actor.rotation.y = motion.heading
	update_camera()
	update_hud()

func _physics_process(delta: float) -> void:
	if not auto_test and not capture_mode:
		var live_input := controls.read()
		if not live_input.is_zero_approx() and replaying:
			replaying = false
			replay_button.text = "Replay test"
		if replaying and not paused:
			advance_demo(delta, rehearsal(replay_time))
			replay_time += delta
			if replay_time >= 11.2:
				replaying = false
				replay_button.text = "Replay test"
		else:
			advance_demo(delta, live_input)

func update_hud() -> void:
	status.text = "%s  ·  %.2f m/s  ·  tilt %d%%  ·  %.1f m travelled%s" % [animation.state, motion.speed, roundi(input_value.length() * 100), travelled, "  ·  PAUSED" if paused else ""]
	stick_display.value = input_value
	stick_display.queue_redraw()

func joy_changed(_device: int, connected: bool) -> void:
	if not connected: controls.suspend()
	update_device_status()

func update_device_status() -> void:
	var devices := Input.get_connected_joypads()
	device_status.text = "No joypad detected — keyboard available" if devices.is_empty() else "Joypad: " + Input.get_joy_name(devices[0]) + "  ·  light tilt walks / full tilt runs"

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		controls.focused = false
		controls.suspend()
	elif what == NOTIFICATION_APPLICATION_FOCUS_IN:
		controls.focused = true

func _unhandled_key_input(event: InputEvent) -> void:
	if not event.is_pressed() or event.is_echo(): return
	match event.keycode:
		KEY_1: set_view(0)
		KEY_2: set_view(1)
		KEY_3: set_view(2)
		KEY_P: toggle_pause()
		KEY_R: reset_demo()

func toggle_pause() -> void:
	paused = not paused
	pause_button.text = "P  Resume" if paused else "P  Pause"
	controls.suspend()
	update_hud()

func reset_demo() -> void:
	replaying = false
	replay_time = 0.0
	if replay_button: replay_button.text = "Replay test"
	motion.reset()
	animation.reset()
	travelled = 0.0
	demo_time = 0.0
	accumulator = 0.0
	input_value = Vector2.ZERO
	actor.position = Vector3.ZERO
	actor.rotation = Vector3.ZERO
	controls.suspend()
	update_camera()
	update_hud()

static func rehearsal(time: float) -> Vector2:
	if time < 0.6: return Vector2.ZERO
	if time < 3.4: return Vector2(0, -1)
	if time < 4.5: return Vector2(0, -0.55)
	if time < 6.2: return Vector2(1, 0)
	if time < 7.6: return Vector2(-1, 0)
	if time < 8.8: return Vector2.ZERO
	if time < 10.0: return Vector2(-0.3889, 0.3889)
	return Vector2.ZERO

func capture_evidence() -> void:
	var output := ProjectSettings.globalize_path("res://../tools/motion_v04/frames")
	var states := []
	for view in range(3):
		set_view(view)
		reset_demo()
		var folder := output.path_join(str(view))
		DirAccess.make_dir_recursive_absolute(folder)
		for frame in range(336):
			advance_demo(1.0/30.0, rehearsal(frame/30.0))
			await get_tree().process_frame
			await RenderingServer.frame_post_draw
			get_viewport().get_texture().get_image().save_png(folder.path_join("%03d.png" % frame))
			if view == 0: states.append({"frame":frame,"state":animation.state,"speed":motion.speed,"phase":animation.phase,"position":[motion.position.x, motion.position.y, motion.position.z]})
	FileAccess.open(output.path_join("capture.json"), FileAccess.WRITE).store_string(JSON.stringify({"fps":30,"frames_per_view":336,"views":VIEWS,"states":states}, "  ") + "\n")
	get_tree().quit()
