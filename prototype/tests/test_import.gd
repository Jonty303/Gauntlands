extends SceneTree
## Compare Godot's imported skeleton skinning against independent Blender GLB evaluation.
var failures: Array[String] = []
func check(condition: bool, message: String) -> void:
	if not condition:
		failures.append(message)
		push_error(message)

func _initialize() -> void:
	run.call_deferred()

func skinned_bounds(instance: MeshInstance3D, skeleton: Skeleton3D) -> Array:
	var low := Vector3(INF, INF, INF)
	var high := Vector3(-INF, -INF, -INF)
	var skin := instance.skin
	var transforms: Array[Transform3D] = []
	for index in range(skin.get_bind_count()):
		var bone := skin.get_bind_bone(index)
		if bone < 0:
			bone = skeleton.find_bone(skin.get_bind_name(index))
		check(bone >= 0, "Missing bind bone")
		transforms.append(skeleton.global_transform * skeleton.get_bone_global_pose(bone) * skin.get_bind_pose(index))
	for surface in range(instance.mesh.get_surface_count()):
		var arrays := instance.mesh.surface_get_arrays(surface)
		var vertices: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		var bones: PackedInt32Array = arrays[Mesh.ARRAY_BONES]
		var weights: PackedFloat32Array = arrays[Mesh.ARRAY_WEIGHTS]
		var count := bones.size() / vertices.size()
		for index in range(vertices.size()):
			var position := Vector3.ZERO
			var total := 0.0
			for slot in range(count):
				var weight := weights[index * count + slot]
				position += (transforms[bones[index * count + slot]] * vertices[index]) * weight
				total += weight
			check(absf(total - 1.0) < 0.0001, "Invalid skin weight sum")
			low = low.min(position)
			high = high.max(position)
	return [[low.x, high.x], [low.y, high.y], [low.z, high.z]]

func run() -> void:
	var actor: Node3D = load("res://assets/human_diagnostic.glb").instantiate()
	root.add_child(actor)
	await process_frame
	var skeleton := actor.find_child("Skeleton3D", true, false) as Skeleton3D
	var player := actor.find_child("AnimationPlayer", true, false) as AnimationPlayer
	check(skeleton != null and player != null, "Missing skeleton or animation player")
	if skeleton == null or player == null:
		quit(1)
		return
	var clips: Array[StringName] = []
	for clip in player.get_animation_list():
		if clip != "RESET": clips.append(clip)
	check(clips.size() == 1, "Expected one diagnostic clip")
	check(skeleton.get_bone_count() == 137, "Bone count changed")
	check(absf(player.get_animation(clips[0]).length - 8.0) < 0.001, "Clip length changed")
	var reference: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://tests/reference_bounds.json"))
	var export_report: Dictionary = JSON.parse_string(FileAccess.get_file_as_string("res://../tools/blender/animation_previews/export_animation_validation.json"))
	check(FileAccess.get_sha256("res://assets/human_diagnostic.glb") == export_report.glb_sha256, "Reference belongs to a different GLB; rerun Blender export validation")
	var meshes: Dictionary = {}
	for pair in [["Human", "Human"], ["Gauntlands_Boxer_Briefs", "Gauntlands_Boxer_Briefs"], ["Human.high-poly", "Human_high-poly"]]:
		var mesh := actor.find_child(pair[1], true, false) as MeshInstance3D
		if mesh == null:
			# Imported node names may retain punctuation depending on importer naming version.
			mesh = actor.find_child(pair[0], true, false) as MeshInstance3D
		check(mesh != null, "Missing mesh " + pair[0])
		if mesh: meshes[pair[0]] = mesh
	if meshes.size() != 3:
		actor.print_tree_pretty()
		quit(1)
		return
	for name in meshes:
		var mesh: MeshInstance3D = meshes[name]
		check(mesh.skin != null, "Missing skin on " + name)
		for surface in range(mesh.mesh.get_surface_count()):
			var material := mesh.get_active_material(surface) as StandardMaterial3D
			check(material != null, "Missing material")
			if name != "Gauntlands_Boxer_Briefs":
				check(material.albedo_texture != null, "Missing embedded texture on " + name)
	var samples := {}
	var maximum_error := 0.0
	player.play(clips[0])
	player.speed_scale = 0.0
	for frame in reference:
		player.seek((float(frame) - 1.0) / 30.0, true)
		skeleton.force_update_all_bone_transforms()
		var sample := {}
		for name in meshes:
			var bounds := skinned_bounds(meshes[name], skeleton)
			sample[name] = bounds
			for axis in range(3):
				for end in range(2):
					var error := absf(bounds[axis][end] - reference[frame][name][axis][end])
					maximum_error = maxf(maximum_error, error)
					check(error < 0.0001, "Bounds mismatch frame %s mesh %s axis %s: %s" % [frame, name, axis, error])
		samples[frame] = sample
	var body_bounds: Array = samples["1"]["Human"]
	check(absf(body_bounds[1][1] - body_bounds[1][0] - 1.8) < 0.0001, "Incorrect neutral stature")
	check(samples["31"]["Human"] != samples["1"]["Human"], "Animation did not deform body")
	check(samples["196"]["Human.high-poly"] != samples["1"]["Human.high-poly"], "Eyes did not follow head turn")
	check(samples["31"]["Gauntlands_Boxer_Briefs"] != samples["1"]["Gauntlands_Boxer_Briefs"], "Garment did not deform")
	var report := {"engine": Engine.get_version_info().string, "passed": failures.is_empty(), "failures": failures, "bone_count": skeleton.get_bone_count(), "clip": clips[0], "maximum_bounds_error_m": maximum_error, "samples": samples}
	var output := FileAccess.open("res://../tools/blender/animation_previews/godot_validation.json", FileAccess.WRITE)
	output.store_string(JSON.stringify(report, "  ") + "\n")
	output.close()
	print("GODOT_ANIMATION_VALIDATION ", report.passed, " max bounds error ", maximum_error)
	quit(0 if failures.is_empty() else 1)
