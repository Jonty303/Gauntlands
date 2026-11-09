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
var replay_time := 0.0
var accumulator := 0.0
var gait_phase := 0.0
var idle_time := 0.0
var run_mix := 0.0
var idle_mix := 1.0
var first_step_remaining := 0.0
var desired_speed := 0.0
var gait_tree: AnimationTree
var skeleton: Skeleton3D
var body: MeshInstance3D
var probes: Array = []
var bind_bones: Array[int] = []
var ground_lift := 0.0
var maximum_ground_lift := 0.0
var replay_button: Button

func _ready() -> void:
	DisplayServer.window_set_title("Gauntlands - Prototype 02 / Dummy locomotion")
	get_viewport().msaa_3d = Viewport.MSAA_4X
	controls.configure()
	build_stage()
	build_ui()
	if not ResourceLoader.exists(ASSET) or not ResourceLoader.exists("res://assets/kevin_local/dummy_idle.glb") or not ResourceLoader.exists("res://assets/kevin_local/dummy_run.glb"):
		status.text = "Build the local clips first - see tools/kevin_locomotion/README.md"
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
	setup_gait()
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
	title.text = "GAUNTLANDS  /  DUMMY LOCOMOTION TEST"
	title.add_theme_font_size_override("font_size",24)
	box.add_child(title)
	var subtitle := Label.new()
	subtitle.text = "Kevin Iglesias | Male dummy | Idle / Walk / Run | 1 metre grid"
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
	replay_button = button("Space  Replay",row)
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
	help.text = "Left stick: walk / run | WASD: walk | Shift: run | Release: idle\n1-3 / right bumper: view | Start / P: pause | R: reset | Space: replay"
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

func setup_gait() -> void:
	player.stop()
	for clip in ["Idle","Run"]:
		var source: Node3D = load("res://assets/kevin_local/dummy_"+clip.to_lower()+".glb").instantiate()
		var source_player := source.find_child("AnimationPlayer",true,false) as AnimationPlayer
		assert(source_player.has_animation(clip))
		player.get_animation_library("").add_animation(clip,source_player.get_animation(clip).duplicate())
		source.free()
	skeleton = actor.find_child("Skeleton3D",true,false) as Skeleton3D
	body = actor.find_child("KevinMaleDummy",true,false) as MeshInstance3D
	cache_sole_probes()
	var graph := AnimationNodeBlendTree.new()
	for clip in ["Idle","Walk","Run"]:
		player.get_animation(clip).loop_mode = Animation.LOOP_LINEAR
		var node := AnimationNodeAnimation.new()
		node.animation = clip
		graph.add_node(clip,node)
		graph.add_node(clip+"Time",AnimationNodeTimeSeek.new())
		graph.connect_node(clip+"Time",0,clip)
	for entry in [["Gait","WalkTime","RunTime"],["Rest","Gait","IdleTime"]]:
		var blend := AnimationNodeBlend2.new()
		blend.sync = true
		graph.add_node(entry[0],blend)
		graph.connect_node(entry[0],0,entry[1])
		graph.connect_node(entry[0],1,entry[2])
	graph.connect_node("output",0,"Rest")
	gait_tree = AnimationTree.new()
	actor.add_child(gait_tree)
	gait_tree.anim_player = gait_tree.get_path_to(player)
	gait_tree.tree_root = graph
	gait_tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	gait_tree.active = true

func apply_pose() -> void:
	if not gait_tree: return
	gait_tree.set("parameters/IdleTime/seek_request",idle_time)
	gait_tree.set("parameters/WalkTime/seek_request",gait_phase*.8)
	gait_tree.set("parameters/RunTime/seek_request",gait_phase*.6)
	gait_tree.set("parameters/Gait/blend_amount",run_mix)
	gait_tree.set("parameters/Rest/blend_amount",smoothstep(0.0,1.0,idle_mix))
	gait_tree.advance(0.0)
	correct_ground_height()
	actor.position.y = ground_lift

func advance_demo(delta: float, value: Vector2) -> void:
	if paused or not actor or delta <= 0.0: return
	var input := value.limit_length()
	var amount := input.length()
	var requested := 2.0*amount/.65 if amount<=.65 else lerpf(2.0,4.0,(amount-.65)/.35)
	if desired_speed<=.001 and requested>.001 and speed<.01:
		first_step_remaining = .8
	desired_speed = requested
	if requested<=.001: first_step_remaining=0
	accumulator += minf(delta,.25)
	var direction := direction_for(input)
	const STEP := 1.0/120.0
	while accumulator+0.00000001>=STEP:
		var target := minf(requested,2.0) if first_step_remaining>0 else requested
		var old_speed := speed
		speed = move_toward(speed,target,STEP*(3.0 if target>speed else 5.0))
		var distance := (old_speed+speed)*.5*STEP
		# On release, keep travelling in the current facing while braking.
		var forward := Vector3(sin(actor.rotation.y),0,cos(actor.rotation.y))
		if not direction.is_zero_approx():
			forward=direction
			actor.rotation.y=atan2(direction.x,direction.z)
		actor.position += forward*distance
		travelled += distance
		first_step_remaining=maxf(0,first_step_remaining-distance)
		run_mix=move_toward(run_mix,smoothstep(2.0,4.0,speed),STEP/.25)
		idle_mix=move_toward(idle_mix,1.0 if requested<.001 and speed<.05 else 0.0,STEP/.32)
		gait_phase=fposmod(gait_phase+distance/lerpf(1.6,2.4,run_mix),1.0)
		idle_time=fposmod(idle_time+STEP,2.7)
		accumulator-=STEP
	apply_pose()
	update_camera()
	update_hud()

static func rehearsal(time: float) -> Vector2:
	if time<.6: return Vector2.ZERO
	if time<2.4: return Vector2(0,-.65)
	if time<5.0: return Vector2.UP
	if time<7.0: return Vector2(0,-.65)
	return Vector2.ZERO

func _physics_process(delta: float) -> void:
	if auto_test or not actor: return
	var value := controls.read()
	if controls.source=="Keyboard" and not value.is_zero_approx():
		value=value.normalized()*(1.0 if Input.is_action_pressed("demo_key_run") else .65)
	if not value.is_zero_approx(): replaying=false
	if replaying and not paused:
		advance_demo(delta,rehearsal(replay_time))
		replay_time+=delta
		if replay_time>=9.0: replaying=false
	else: advance_demo(delta,value)

func update_hud() -> void:
	if not status: return
	var state := "Idle" if idle_mix>.99 else "Run" if run_mix>.99 else "Walk / run" if run_mix>.01 else "Walk"
	if desired_speed<.001 and idle_mix<.99: state="Settling to idle"
	status.text = "%s · %.2f m/s · %.2f m · %s%s" % [state,speed,travelled,VIEWS[view_index]," · PAUSED" if paused else ""]
	if replay_button: replay_button.text="Space  Stop replay" if replaying else "Space  Replay"

func update_devices() -> void:
	var ids := Input.get_connected_joypads()
	devices.text = "No joypad detected - keyboard available" if ids.is_empty() else "Joypad: "+Input.get_joy_name(ids[0])

func toggle_pause() -> void:
	paused = not paused
	replaying = false
	pause_button.text = "P  Resume" if paused else "P  Pause"
	controls.suspend()
	update_hud()

func toggle_replay() -> void:
	var start := not replaying
	reset_demo()
	replaying = start
	update_hud()

func reset_demo() -> void:
	replaying = false
	phase_time = 0
	replay_time = 0
	gait_phase = 0
	idle_time = 0
	run_mix = 0
	idle_mix = 1
	accumulator = 0
	first_step_remaining = 0
	desired_speed = 0
	ground_lift = 0
	maximum_ground_lift = 0
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

func cache_sole_probes() -> void:
	# Cache actual exported foot vertices/weights, not arbitrary bone-tail anchors.
	for index in range(body.skin.get_bind_count()):
		var bone := body.skin.get_bind_bone(index)
		if bone < 0: bone = skeleton.find_bone(body.skin.get_bind_name(index))
		bind_bones.append(bone)
	for surface in range(body.mesh.get_surface_count()):
		var arrays := body.mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var bones: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
		var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
		var count: int = bones.size() / vertices.size()
		for vertex in range(vertices.size()):
			var foot_weight := 0.0
			var influences := []
			for slot in range(count):
				var weight := weights[vertex * count + slot]
				if weight <= 0.0: continue
				var bind := bones[vertex * count + slot]
				var name := String(skeleton.get_bone_name(bind_bones[bind]))
				if name.begins_with("B-foot.") or name.begins_with("B-toe."): foot_weight += weight
				influences.append([bind, weight])
			if foot_weight > 0.15: probes.append([vertices[vertex], influences])

func correct_ground_height() -> void:
	# Root-only floor clearance for mixed poses. This does not lock feet in X/Z,
	# alter joint rotations, or claim authored turn/contact quality.
	skeleton.force_update_all_bone_transforms()
	var to_model := actor.global_transform.affine_inverse() * skeleton.global_transform
	var transforms: Array[Transform3D] = []
	for index in range(bind_bones.size()):
		transforms.append(to_model * skeleton.get_bone_global_pose(bind_bones[index]) * body.skin.get_bind_pose(index))
	var minimum := INF
	for probe in probes:
		var point := Vector3.ZERO
		for influence in probe[1]: point += (transforms[influence[0]] * probe[0]) * influence[1]
		minimum = minf(minimum, point.y)
	var required := maxf(0.0, 0.0005-minimum)
	# Correct penetration only, preserving any authored run flight.
	ground_lift = required
	maximum_ground_lift = maxf(maximum_ground_lift, ground_lift)
