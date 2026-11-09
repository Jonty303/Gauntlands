extends Node
## Phase-synchronised sampling of the frozen clips; no whole-clip request queue.
const CLIPS := ["Idle", "Walk", "Run", "WalkStart", "WalkStopL", "WalkStopR"]
var tree: AnimationTree
var player: AnimationPlayer
var phase := 0.0
var idle_time := 0.0
var start_time := 0.0
var stop_time := 1.0
var stop_right := false
var state := "Idle"
var run_mix := 0.0
var start_mix := 0.0
var stop_mix := 0.0
var idle_mix := 1.0
var was_starting := false
var was_requested := false
var skeleton: Skeleton3D
var actor_root: Node3D
var body: MeshInstance3D
var probes: Array = []
var bind_bones: Array[int] = []
var ground_lift := 0.0
var maximum_ground_lift := 0.0
var stance := preload("res://motion/foot_stance.gd").new()

func setup(actor: Node3D) -> void:
	player = actor.find_child("AnimationPlayer", true, false) as AnimationPlayer
	player.stop()
	actor_root = actor
	skeleton = actor.find_child("Skeleton3D", true, false) as Skeleton3D
	body = actor.find_child("Human", true, false) as MeshInstance3D
	cache_sole_probes()
	stance.setup(skeleton)
	var graph := AnimationNodeBlendTree.new()
	for clip in CLIPS:
		var animation := player.get_animation(clip)
		animation.loop_mode = Animation.LOOP_LINEAR if clip in ["Idle", "Walk", "Run"] else Animation.LOOP_NONE
		var source := AnimationNodeAnimation.new()
		source.animation = clip
		graph.add_node(clip, source)
		graph.add_node(clip + "Time", AnimationNodeTimeSeek.new())
		graph.connect_node(clip + "Time", 0, clip)
	for spec in [["Gait", "WalkTime", "RunTime"], ["Start", "Gait", "WalkStartTime"],
		["StopLead", "WalkStopLTime", "WalkStopRTime"], ["Stop", "Start", "StopLead"], ["Rest", "Stop", "IdleTime"]]:
		var blend := AnimationNodeBlend2.new()
		blend.sync = true
		graph.add_node(spec[0], blend)
		graph.connect_node(spec[0], 0, spec[1])
		graph.connect_node(spec[0], 1, spec[2])
	graph.connect_node("output", 0, "Rest")
	tree = AnimationTree.new()
	actor.add_child(tree)
	tree.anim_player = tree.get_path_to(player)
	tree.tree_root = graph
	tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	tree.active = true
	apply_pose(0.0)

func reset() -> void:
	stance.reset()
	phase = 0.0
	idle_time = 0.0
	start_time = 0.0
	stop_time = 1.0
	state = "Idle"
	run_mix = 0.0
	start_mix = 0.0
	stop_mix = 0.0
	idle_mix = 1.0
	was_starting = false
	was_requested = false
	ground_lift = 0.0
	maximum_ground_lift = 0.0
	apply_pose(0.0)

func step(delta: float, motion: RefCounted, distance: float) -> void:
	var requested: bool = motion.desired_speed > 0.0
	if motion.starting and not was_starting:
		start_time = 0.0
		phase = 0.0
	if not requested and was_requested:
		stop_right = phase >= 0.25 and phase < 0.75
		# A tap cancelled before lift-off should settle, not invent a full step.
		stop_time = 1.0 if was_starting and start_time < 0.15 else 0.0
	if was_starting and not motion.starting and requested: phase = 0.0
	if motion.starting: start_time = motion.start_time
	else: start_time = minf(start_time + delta, 0.7)
	stop_time = minf(stop_time + delta, 1.0)
	idle_time = fposmod(idle_time + delta, 4.0)
	var gait_target := smoothstep(1.05, 1.65, motion.speed)
	run_mix = move_toward(run_mix, gait_target, delta / 0.22)
	# Shared phase gives the same lead foot at every blend weight. Travel, not
	# input magnitude, drives cadence; mixed stride length prevents speed skating.
	if not motion.starting:
		phase = fposmod(phase + distance / lerpf(1.08, 1.76, run_mix), 1.0)
	var stopping := not requested and stop_time < 0.8
	start_mix = move_toward(start_mix, 1.0 if motion.starting else 0.0, delta / 0.14)
	stop_mix = move_toward(stop_mix, 1.0 if stopping else 0.0, delta / 0.22)
	idle_mix = move_toward(idle_mix, 1.0 if not requested and motion.speed < 0.015 and stop_time >= 0.65 else 0.0, delta / 0.18)
	state = "Starting" if motion.starting else "Stopping" if stopping else "Idle" if idle_mix > 0.99 else "Walk lead-in" if requested and motion.first_step_remaining > 0.0 else "Run" if run_mix > 0.95 else "Walk / run" if run_mix > 0.05 else "Walk"
	was_starting = motion.starting
	was_requested = requested
	stance.update(delta,self,requested)
	if not requested and stop_time >= 0.64 and stance.settling: state = "Settling stance"
	apply_pose(delta)
	stance.apply()
	correct_ground_height(delta)

func apply_pose(delta: float) -> void:
	if not tree: return
	var times := [idle_time, phase * 1.2, phase * 0.8, start_time, minf(stop_time,0.8), minf(stop_time,0.8)]
	for i in range(CLIPS.size()): tree.set("parameters/" + CLIPS[i] + "Time/seek_request", times[i])
	tree.set("parameters/Gait/blend_amount", run_mix)
	tree.set("parameters/Start/blend_amount", smoothstep(0.0, 1.0, start_mix))
	tree.set("parameters/StopLead/blend_amount", 1.0 if stop_right else 0.0)
	tree.set("parameters/Stop/blend_amount", smoothstep(0.0, 1.0, stop_mix))
	tree.set("parameters/Rest/blend_amount", smoothstep(0.0, 1.0, idle_mix))
	tree.advance(delta)

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
				if name.begins_with("foot.") or name.begins_with("toe"): foot_weight += weight
				influences.append([bind, weight])
			if foot_weight > 0.15 and vertices[vertex].y < 0.045: probes.append([vertices[vertex], influences])

func correct_ground_height(delta: float) -> void:
	# Root-only floor clearance for mixed poses. This does not lock feet in X/Z,
	# alter joint rotations, or claim authored turn/contact quality.
	skeleton.force_update_all_bone_transforms()
	var to_model := actor_root.global_transform.affine_inverse() * skeleton.global_transform
	var transforms: Array[Transform3D] = []
	for index in range(bind_bones.size()):
		transforms.append(to_model * skeleton.get_bone_global_pose(bind_bones[index]) * body.skin.get_bind_pose(index))
	var minimum := INF
	for probe in probes:
		var point := Vector3.ZERO
		for influence in probe[1]: point += (transforms[influence[0]] * probe[0]) * influence[1]
		minimum = minf(minimum, point.y)
	var required := maxf(0.0, -minimum)
	# Never smooth below the floor; ease only the release of the correction.
	ground_lift = maxf(required, ground_lift * exp(-18.0 * delta))
	maximum_ground_lift = maxf(maximum_ground_lift, ground_lift)
