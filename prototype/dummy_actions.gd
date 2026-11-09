extends "res://dummy_locomotion.gd"
## Deliberately a motion viewer: no hitboxes, damage, inventory or projectiles.
const PREVIEW_CLEARANCE := 0.004 # Measured imported/interpolated skin differs by up to 3.8 mm.
var catalogue: Array = []
var selected := 0
var selector: OptionButton
var details: Label
var action_button: Button
var packs := {}
var preview: Node3D
var preview_player: AnimationPlayer
var preview_skeleton: Skeleton3D
var active_entry: Dictionary = {}
var action_time := 0.0
var blend_time := 0.0
var returning := false
var start_pose := {}
var playback_rate := 1.0
var rate_selector: OptionButton

func _ready() -> void:
	if FileAccess.file_exists("res://action_catalogue.json"):
		catalogue = JSON.parse_string(FileAccess.get_file_as_string("res://action_catalogue.json"))
	super._ready()
	DisplayServer.window_set_title("Gauntlands - Prototype 02 / Animation viewer")
	for entry in catalogue:
		if packs.has(entry.pack): continue
		if not ResourceLoader.exists(entry.asset):
			push_error("Build missing action pack: "+entry.asset)
			continue
		var node: Node3D = load(entry.asset).instantiate()
		add_child(node)
		node.hide()
		var animation := node.find_child("AnimationPlayer",true,false) as AnimationPlayer
		animation.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
		packs[entry.pack] = node
	select_action(0)

func build_ui() -> void:
	var layer := CanvasLayer.new()
	add_child(layer)
	var margin := MarginContainer.new()
	margin.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	for side in ["left","right","top","bottom"]: margin.add_theme_constant_override("margin_"+side,20)
	margin.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(margin)
	var box := VBoxContainer.new()
	box.mouse_filter = Control.MOUSE_FILTER_IGNORE
	margin.add_child(box)
	var title := Label.new()
	title.text = "GAUNTLANDS  /  ANIMATION VIEWER"
	title.add_theme_font_size_override("font_size",24)
	box.add_child(title)
	var subtitle := Label.new()
	subtitle.text = "Kevin Iglesias | Male dummy | %d selectable clips | Motion preview only" % catalogue.size()
	box.add_child(subtitle)
	var row := HBoxContainer.new()
	box.add_child(row)
	button("LB  Previous",row).pressed.connect(func() -> void: cycle_action(-1))
	selector = OptionButton.new()
	selector.focus_mode = Control.FOCUS_NONE
	selector.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	selector.get_popup().max_size = Vector2i(850,600)
	for i in range(catalogue.size()):
		var entry: Dictionary = catalogue[i]
		selector.add_item("%03d  %s / %s" % [i+1,entry.category,display_name(entry.name)])
	selector.item_selected.connect(select_action)
	row.add_child(selector)
	button("RB  Next",row).pressed.connect(func() -> void: cycle_action(1))
	var actions := HBoxContainer.new()
	box.add_child(actions)
	action_button = button("A / Space  Play",actions)
	action_button.pressed.connect(trigger_action)
	button("B / Esc  Return to movement",actions).pressed.connect(cancel_action)
	rate_selector = OptionButton.new()
	rate_selector.focus_mode = Control.FOCUS_NONE
	for label in ["0.5x slow motion","1x normal speed","1.5x playback"]: rate_selector.add_item(label)
	rate_selector.select(1)
	rate_selector.item_selected.connect(func(index: int) -> void: playback_rate=[.5,1.0,1.5][index])
	actions.add_child(rate_selector)
	var views := HBoxContainer.new()
	box.add_child(views)
	for i in range(3): button("%d  %s" % [i+1,VIEWS[i]],views).pressed.connect(func() -> void: set_view(i))
	button("Close view",views).pressed.connect(func() -> void:
		close_view=not close_view
		update_camera())
	pause_button=button("P  Pause",views)
	pause_button.pressed.connect(toggle_pause)
	button("R  Reset",views).pressed.connect(reset_demo)
	button("Rotate 45 degrees",views).pressed.connect(func() -> void: rotate_preview(PI/4))
	details=Label.new()
	details.autowrap_mode=TextServer.AUTOWRAP_WORD_SMART
	box.add_child(details)
	var spacer := Control.new()
	spacer.size_flags_vertical=Control.SIZE_EXPAND_FILL
	spacer.mouse_filter=Control.MOUSE_FILTER_IGNORE
	box.add_child(spacer)
	status=Label.new()
	status.add_theme_font_size_override("font_size",20)
	box.add_child(status)
	devices=Label.new()
	box.add_child(devices)
	var help := Label.new()
	help.text="LB/RB or [ / ]: select | A / Space: play or restart | B / Esc: return\nLeft stick / WASD: move | Shift: run | Y / 1-3: view | D-pad left/right: facing\nStart / P: pause | Loops continue until cancelled. Movement cancels the preview."
	box.add_child(help)

static func display_name(raw: String) -> String:
	return raw.replace("01", " 01").replace("02", " 02").replace("03", " 03").replace("04", " 04").replace("_", " ")

func select_action(index: int) -> void:
	if catalogue.is_empty(): return
	finish_preview()
	selected=posmod(index,catalogue.size())
	selector.select(selected)
	var entry: Dictionary=catalogue[selected]
	var props := "No equipment" if entry.props.is_empty() else "Equipment: "+", ".join(entry.props)
	var ending := "loop" if entry.loop else "hold final pose" if entry.hold else "one-shot"
	details.text="%s | %.2f s | %s | %s" % [entry.name,entry.duration,ending,props]
	update_hud()

func cycle_action(direction: int) -> void:
	select_action(selected+direction)

func pose_snapshot(source: Skeleton3D) -> Dictionary:
	var result := {}
	for bone in range(source.get_bone_count()): result[source.get_bone_name(bone)]=source.get_bone_pose(bone)
	return result

func trigger_action() -> void:
	if catalogue.is_empty() or not actor: return
	var from_pose := pose_snapshot(preview_skeleton if preview else skeleton)
	finish_preview()
	active_entry=catalogue[selected]
	if not packs.has(active_entry.pack): return
	preview=packs[active_entry.pack]
	preview_player=preview.find_child("AnimationPlayer",true,false) as AnimationPlayer
	preview_skeleton=preview.find_child("Skeleton3D",true,false) as Skeleton3D
	if not preview_player.has_animation(active_entry.id):
		push_error("Missing action: "+active_entry.id)
		finish_preview()
		return
	preview.transform=actor.transform
	for node in preview.find_children("*","MeshInstance3D",true,false):
		node.visible=node.name=="KevinMaleDummy" or active_entry.props.has(String(node.name))
	preview.show()
	actor.hide()
	replaying=false
	controls.suspend()
	speed=0
	desired_speed=0
	first_step_remaining=0
	accumulator=0
	action_time=0
	blend_time=0
	returning=false
	start_pose=from_pose
	preview_player.get_animation(active_entry.id).loop_mode=Animation.LOOP_NONE
	preview_player.play(active_entry.id)
	apply_action_pose()
	update_hud()

func blend_pose(from: Dictionary, amount: float, toward_base := false) -> void:
	for bone in range(preview_skeleton.get_bone_count()):
		var name := preview_skeleton.get_bone_name(bone)
		if not from.has(name): continue
		var target := preview_skeleton.get_bone_pose(bone)
		if toward_base:
			var base_index := skeleton.find_bone(name)
			if base_index<0: continue
			target=skeleton.get_bone_pose(base_index)
		preview_skeleton.set_bone_pose(bone,(from[name] as Transform3D).interpolate_with(target,amount))
	preview_skeleton.force_update_all_bone_transforms()

func apply_action_pose() -> void:
	if not preview: return
	var length: float=active_entry.duration
	var time := fposmod(action_time,length) if active_entry.loop else minf(action_time,length)
	preview_player.seek(time,true)
	preview_skeleton.force_update_all_bone_transforms()
	if blend_time<.16: blend_pose(start_pose,smoothstep(0.0,.16,blend_time))
	if active_entry.has("floor_samples"):
		var samples: Array=active_entry.floor_samples
		var frame := clampf(time*60,0,samples.size()-1)
		var lo := int(floorf(frame))
		preview.position.y=lerpf(float(samples[lo]),float(samples[mini(lo+1,samples.size()-1)]),frame-lo)
	else: preview.position.y=active_entry.ground_offset
	preview.position.y+=PREVIEW_CLEARANCE
	# Release the visible arrow; the viewer deliberately has no projectile system.
	var arrow := preview.find_child("Arrow",true,false) as Node3D
	if arrow and active_entry.name=="BowShot01 - Release": arrow.visible=time<.10
	if arrow and active_entry.has("arrow_release_time"): arrow.visible=time<float(active_entry.arrow_release_time)+.10

func advance_action(delta: float) -> void:
	if paused or not preview: return
	idle_time=fposmod(idle_time+delta,2.7)
	idle_mix=1
	run_mix=0
	apply_pose()
	if returning:
		blend_time+=delta
		blend_pose(start_pose,smoothstep(0.0,.18,blend_time),true)
		preview.position.y=lerpf(float(active_entry.ground_offset)+PREVIEW_CLEARANCE,actor.position.y,smoothstep(0.0,.18,blend_time))
		if blend_time>=.18: finish_preview()
	else:
		action_time+=delta*playback_rate
		blend_time+=delta
		apply_action_pose()
		if not active_entry.loop and not active_entry.hold and action_time>=float(active_entry.duration): cancel_action()
	update_hud()

func cancel_action() -> void:
	if not preview or returning: return
	returning=true
	blend_time=0
	start_pose=pose_snapshot(preview_skeleton)

func finish_preview() -> void:
	if preview:
		preview.hide()
		preview_player.stop()
	preview=null
	preview_player=null
	preview_skeleton=null
	active_entry={}
	returning=false
	if actor: actor.show()

func rotate_preview(amount: float) -> void:
	if not actor: return
	actor.rotate_y(amount)
	if preview: preview.rotation.y=actor.rotation.y

func _physics_process(delta: float) -> void:
	if auto_test or not actor: return
	if not preview:
		super._physics_process(delta)
		return
	var value := controls.read()
	if not value.is_zero_approx(): cancel_action()
	advance_action(delta)

func update_hud() -> void:
	if not status: return
	if preview:
		status.text="%s | %.2f / %.2f s | %s%s" % ["Returning to idle" if returning else display_name(active_entry.name),minf(action_time,float(active_entry.duration)) if not active_entry.loop else fposmod(action_time,float(active_entry.duration)),active_entry.duration,VIEWS[view_index]," | PAUSED" if paused else ""]
	else:
		super.update_hud()
	if action_button: action_button.text="A / Space  Restart" if preview else "A / Space  Play"

func reset_demo() -> void:
	finish_preview()
	super.reset_demo()

func _unhandled_key_input(event: InputEvent) -> void:
	if not event.is_pressed() or event.is_echo(): return
	match event.keycode:
		KEY_BRACKETLEFT: cycle_action(-1)
		KEY_BRACKETRIGHT: cycle_action(1)
		KEY_SPACE: trigger_action()
		KEY_ESCAPE: cancel_action()
		KEY_1: set_view(0)
		KEY_2: set_view(1)
		KEY_3: set_view(2)
		KEY_P: toggle_pause()
		KEY_R: reset_demo()
		KEY_Q: rotate_preview(-PI/4)
		KEY_E: rotate_preview(PI/4)

func _unhandled_input(event: InputEvent) -> void:
	if event is InputEventJoypadButton and event.pressed:
		match event.button_index:
			JOY_BUTTON_LEFT_SHOULDER: cycle_action(-1)
			JOY_BUTTON_RIGHT_SHOULDER: cycle_action(1)
			JOY_BUTTON_A: trigger_action()
			JOY_BUTTON_B: cancel_action()
			JOY_BUTTON_Y: set_view((view_index+1)%3)
			JOY_BUTTON_DPAD_LEFT: rotate_preview(-PI/4)
			JOY_BUTTON_DPAD_RIGHT: rotate_preview(PI/4)
			JOY_BUTTON_START: toggle_pause()
