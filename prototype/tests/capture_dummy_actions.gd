extends SceneTree
func _initialize() -> void: run.call_deferred()
func run() -> void:
	var demo = load("res://dummy_actions.tscn").instantiate()
	demo.auto_test=true
	root.add_child(demo)
	await process_frame
	var folder := "res://../tools/kevin_actions/frames"
	DirAccess.make_dir_recursive_absolute(folder)
	var manifest := []
	for view in range(3):
		demo.set_view(view)
		for index in range(demo.catalogue.size()):
			demo.select_action(index)
			demo.trigger_action()
			var entry: Dictionary=demo.catalogue[index]
			if demo.preview==null:continue
			demo.action_time=float(entry.duration)*.45
			demo.blend_time=1
			demo.apply_action_pose()
			demo.update_hud()
			await process_frame
			await RenderingServer.frame_post_draw
			var filename := "%d_%03d.png" % [view,index]
			root.get_texture().get_image().save_png(folder+"/"+filename)
			manifest.append({"file":filename,"name":entry.name,"category":entry.category,"view":view,"index":index})
	# Eight facings for sword and bow; sequences expose draw/release/weapon paths.
	for target in ["Attack1H01_R","Attack2H01","AttackPolearm01","BowShot - Complete","BowShot01 - Load","BowShot01 - Hold","BowShot01 - Release","SheatheBack01_R","UnsheatheBack01_R","HammeringGround01_R - Loop","Fishing01 - Loop"]:
		var index := -1
		for i in range(demo.catalogue.size()):
			if demo.catalogue[i].name==target:index=i
		if index<0:continue
		for view in range(3):
			demo.set_view(view)
			for frame in range(8):
				demo.select_action(index)
				demo.trigger_action()
				if demo.preview==null:
					quit(1)
					return
				demo.action_time=float(demo.active_entry.duration)*frame/7.0
				demo.blend_time=1
				demo.apply_action_pose()
				demo.update_hud()
				await process_frame
				await RenderingServer.frame_post_draw
				var filename := "sequence_%s_%d_%d.png" % [demo.active_entry.id,view,frame]
				root.get_texture().get_image().save_png(folder+"/"+filename)
				manifest.append({"file":filename,"name":target,"view":view,"frame":frame})
	for target in ["Attack1H01_R","BowShot - Complete","MagicAttackDirect2H01"]:
		var index := -1
		for i in range(demo.catalogue.size()):
			if demo.catalogue[i].name==target:index=i
		for view in range(3):
			demo.set_view(view)
			for facing in range(8):
				demo.actor.rotation.y=facing*PI/4
				demo.select_action(index)
				demo.trigger_action()
				demo.action_time=float(demo.active_entry.duration)*.45
				demo.blend_time=1
				demo.apply_action_pose()
				demo.update_hud()
				await process_frame
				await RenderingServer.frame_post_draw
				var filename := "facing_%s_%d_%d.png" % [demo.active_entry.id,view,facing]
				root.get_texture().get_image().save_png(folder+"/"+filename)
				manifest.append({"file":filename,"name":target,"view":view,"facing":facing})
	FileAccess.open("res://../tools/kevin_actions/preview_manifest.json",FileAccess.WRITE).store_string(JSON.stringify(manifest,"  ")+"\n")
	print("ACTION_CAPTURES ",manifest.size())
	demo.queue_free()
	await process_frame
	quit()
