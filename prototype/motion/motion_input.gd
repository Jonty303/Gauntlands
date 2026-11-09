extends RefCounted
const DEADZONE := 0.18
var focused := true
var neutral_required := false
var source := "Keyboard"
var raw_stick := Vector2.ZERO

func configure() -> void:
	for entry in [["left", KEY_A, KEY_LEFT, JOY_AXIS_LEFT_X, -1.0], ["right", KEY_D, KEY_RIGHT, JOY_AXIS_LEFT_X, 1.0],
		["up", KEY_W, KEY_UP, JOY_AXIS_LEFT_Y, -1.0], ["down", KEY_S, KEY_DOWN, JOY_AXIS_LEFT_Y, 1.0]]:
		var key_action := "demo_key_" + String(entry[0])
		if not InputMap.has_action(key_action):
			InputMap.add_action(key_action)
			for code in [entry[1], entry[2]]:
				var key := InputEventKey.new()
				key.physical_keycode = code
				InputMap.action_add_event(key_action, key)
		var stick_action := "demo_stick_" + String(entry[0])
		if not InputMap.has_action(stick_action):
			InputMap.add_action(stick_action, DEADZONE)
			var axis := InputEventJoypadMotion.new()
			axis.device = -1
			axis.axis = entry[3]
			axis.axis_value = entry[4]
			InputMap.action_add_event(stick_action, axis)
	if not InputMap.has_action("demo_key_run"):
		InputMap.add_action("demo_key_run")
		var shift := InputEventKey.new()
		shift.physical_keycode = KEY_SHIFT
		InputMap.action_add_event("demo_key_run", shift)

func suspend() -> void:
	neutral_required = true
	raw_stick = Vector2.ZERO
	for action in InputMap.get_actions():
		if String(action).begins_with("demo_"): Input.action_release(action)

func read() -> Vector2:
	var keyboard := Input.get_vector("demo_key_left", "demo_key_right", "demo_key_up", "demo_key_down", 0.0)
	var stick := Vector2.ZERO
	if not Input.get_connected_joypads().is_empty():
		stick = Input.get_vector("demo_stick_left", "demo_stick_right", "demo_stick_up", "demo_stick_down", DEADZONE)
	raw_stick = stick
	if not focused: return Vector2.ZERO
	if neutral_required:
		if keyboard.is_zero_approx() and stick.is_zero_approx(): neutral_required = false
		return Vector2.ZERO
	if not keyboard.is_zero_approx():
		source = "Keyboard"
		return keyboard * (1.0 if Input.is_action_pressed("demo_key_run") else 0.55)
	source = "Left stick" if not Input.get_connected_joypads().is_empty() else "Keyboard"
	return stick
