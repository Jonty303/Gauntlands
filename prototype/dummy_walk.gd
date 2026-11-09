extends Node3D
const MotionInput = preload("res://motion/motion_input.gd")
const VIEWS := ["Isometric", "Raised 3/4", "Top-down"]
const OFFSETS := [Vector3(4,4,4), Vector3(2.5,5,4.330127), Vector3(0,6,0)]
const SPEED := 2.0
const PERIOD := 0.8
const ASSET := "res://assets/kevin_local/dummy_walk.glb"
var controls := MotionInput.new()
var actor: Node3D
var player: AnimationPlayer
var camera: Camera3D
var floor_mesh: MeshInstance3D
var status: Label
var devices: Label
var view_index := 0
var close_view := false
var paused := false
var auto_test := false
var replaying := false
var phase_time := 0.0
var travelled := 0.0
var speed := 0.0
var floor_samples: Array = []
var pause_button: Button
var replay_button: Button

func _ready() -> void:
	DisplayServer.window_set_title("Gauntlands — Prototype 02 / Dummy walk")
	get_viewport().msaa_3d = Viewport.MSAA_4X
	controls.configure()
	build_stage()
	build_ui()
	if not ResourceLoader.exists(ASSET):
		status.text = "Build the local dummy asset first — see tools/kevin_walk/README.md"
		push_error(status.text)
		set_physics_process(false)
		return
	actor = load(ASSET).instantiate()
	add_child(actor)
	player = actor.find_child("AnimationPlayer", true, false) as AnimationPlayer
	assert(player != null and player.has_animation("Walk"), "Missing dummy Walk animation")
	player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	player.get_animation("Walk").loop_mode = Animation.LOOP_LINEAR
	var data: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://assets/kevin_local/walk.json"))
	floor_samples = data.floor_samples_m
	player.play("Walk")
	apply_pose()
	update_camera()
	Input.joy_connection_changed.connect(func(_id: int, connected: bool) -> void:
		if not connected: controls.suspend(); replaying = false
		update_devices()
	)
	update_devices()

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
	for side in ["left","right","top","bottom"]:
		margin.add_theme_constant_override("margin_"+side,22)
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(margin)
	var box := VBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	margin.add_child(box)
	var title := Label.new()
	title.text = "GAUNTLANDS  /  DUMMY WALK TEST"
	title.add_theme_font_size_override("font_size",24)
	box.add_child(title)
	var subtitle := Label.new()
	subtitle.text = "Kevin Iglesias · Male dummy · One forward walk · 1 metre grid"
	box.add_child(subtitle)
	var row := HBoxContainer.new()
	box.add_child(row)
	for i in range(3):
		button("%d  %s" % [i+1,VIEWS[i]],row).pressed.connect(func() -> void: set_view(i))
	button("Close view",row).pressed.connect(func() -> void:
		close_view = not close_view
		update_camera())
	pause_button = button("P  Pause",row)
	pause_button.pressed.connect(toggle_pause)
	button("R  Reset",row).pressed.connect(reset_demo)
	replay_button = button("Space  Auto-walk",row)
	replay_button.pressed.connect(toggle_replay)
	var spacer := Control.new()
	spacer.size_flags_vertical = Control.SIZE_EXPAND_FILL
	spacer.mouse_filter = Control.MOUSE_FILTER_IGNORE
	box.add_child(spacer)
	status = Label.new()
	status.add_theme_font_size_override("font_size",20)
	box.add_child(status)
	devices = Label.new()
	box.add_child(devices)
	var help := Label.new()
	help.text = "Left stick / WASD / arrows: walk · Release: hold pose
1–3 / right bumper: view · Start / P: pause · R: reset · Space: auto-walk"
	box.add_child(help)

func button(text: String, parent: Node) -> Button:
	var b := Button.new()
	b.text = text
	b.focus_mode = Control.FOCUS_NONE
	parent.add_child(b)
	return b

func set_view(index: int) -> void:
	view_index = index
	update_camera()
	update_hud()

func update_camera() -> void:
	var target := Vector3(0,0.9,0)
	if actor: target += Vector3(actor.position.x,0,actor.position.z)
	camera.position = target + OFFSETS[view_index]
	camera.look_at(target, Vector3(0,0,-1) if view_index == 2 else Vector3.UP)
	camera.size = 3.2 if close_view else 5.0
	floor_mesh.position = Vector3(floorf(target.x),0,floorf(target.z))

func direction_for(value: Vector2) -> Vector3:
	var right := camera.basis.x
	var up := camera.basis.y
	right.y = 0
	up.y = 0
	return (right.normalized()*value.x - up.normalized()*value.y).normalized()

func apply_pose() -> void:
	player.seek(phase_time, true)
	var sample_position := phase_time / PERIOD * float(floor_samples.size()-1)
	var index := mini(int(sample_position),floor_samples.size()-2)
	# Small measured sole correction only; do not modify the authored limb motion.
	actor.position.y = 0.0005 - lerpf(float(floor_samples[index]),float(floor_samples[index+1]),sample_position-index)

func advance_demo(delta: float, value: Vector2) -> void:
	if paused or not actor or delta <= 0.0: return
	var input := value.limit_length()
	speed = SPEED * input.length()
	if speed > 0.00001:
		var direction := direction_for(input)
		actor.rotation.y = atan2(direction.x,direction.z)
		actor.position += direction*speed*delta
		travelled += speed*delta
		phase_time = fposmod(phase_time + delta*speed/SPEED,PERIOD)
		if PERIOD-phase_time < 0.000001: phase_time = 0.0
		apply_pose()
	update_camera()
	update_hud()

func _physics_process(delta: float) -> void:
	if auto_test or not actor: return
	var value := controls.read()
	if controls.source == "Keyboard" and not value.is_zero_approx(): value = value.normalized()
	if not value.is_zero_approx(): replaying = false
	advance_demo(delta,Vector2.UP if replaying else value)

func update_hud() -> void:
	if not status: return
	status.text = "%s · %.2f m/s · %.2f m · %s%s" % [
		"Walking" if speed > 0 else "Pose held",speed,travelled,VIEWS[view_index]," · PAUSED" if paused else ""]
	if replay_button: replay_button.text = "Space  Stop auto-walk" if replaying else "Space  Auto-walk"

func update_devices() -> void:
	var ids := Input.get_connected_joypads()
	devices.text = "No joypad detected — keyboard available" if ids.is_empty() else "Joypad: "+Input.get_joy_name(ids[0])

func toggle_pause() -> void:
	paused = not paused
	replaying = false
	pause_button.text = "P  Resume" if paused else "P  Pause"
	controls.suspend()
	update_hud()

func toggle_replay() -> void:
	replaying = not replaying
	update_hud()

func reset_demo() -> void:
	replaying = false
	phase_time = 0
	travelled = 0
	speed = 0
	if actor:
		actor.position = Vector3.ZERO
		actor.rotation = Vector3.ZERO
		apply_pose()
	controls.suspend()
	update_camera()
	update_hud()

func _notification(what: int) -> void:
	if what == NOTIFICATION_APPLICATION_FOCUS_OUT:
		controls.focused = false
		controls.suspend()
		replaying = false
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
		KEY_SPACE: toggle_replay()

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventJoypadButton and event.pressed:
		if event.button_index == JOY_BUTTON_RIGHT_SHOULDER: set_view((view_index+1)%3)
		if event.button_index == JOY_BUTTON_START: toggle_pause()
