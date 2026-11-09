extends RefCounted
## Pure locomotion state. Render/animation nodes never decide input intent.
const WALK_SPEED := 0.9
const RUN_SPEED := 2.2
const ACCELERATION := 3.2
const BRAKING := 5.5
const START_DURATION := 0.7
const FIRST_WALK_STEP_DISTANCE := 0.54 # Half the accepted 1.08 m walk cycle.
const RUN_BUILD_DURATION := 0.55
var position := Vector3.ZERO
var speed := 0.0
var heading := 0.0
var angular_speed := 0.0
var desired_speed := 0.0
var turning_error := 0.0
var starting := false
var start_time := 0.0
var first_step_remaining := 0.0
var run_build_time := RUN_BUILD_DURATION
var input_vector := Vector2.ZERO

static func speed_for_tilt(amount: float) -> float:
	amount = clampf(amount, 0.0, 1.0)
	if amount <= 0.55: return WALK_SPEED * amount / 0.55
	return lerpf(WALK_SPEED, RUN_SPEED, (amount - 0.55) / 0.45)

static func camera_direction(stick: Vector2, right: Vector3, up: Vector3) -> Vector3:
	right.y = 0.0
	up.y = 0.0
	return (right.normalized() * stick.x - up.normalized() * stick.y).limit_length(1.0)

func reset() -> void:
	position = Vector3.ZERO
	speed = 0.0
	heading = 0.0
	angular_speed = 0.0
	desired_speed = 0.0
	turning_error = 0.0
	starting = false
	start_time = 0.0
	first_step_remaining = 0.0
	run_build_time = RUN_BUILD_DURATION
	input_vector = Vector2.ZERO

func step(delta: float, direction: Vector3, magnitude: float) -> float:
	if delta <= 0.0: return 0.0
	var moving := magnitude > 0.001 and direction.length_squared() > 0.000001
	if moving and desired_speed == 0.0 and speed < 0.03:
		starting = true
		start_time = 0.0
		first_step_remaining = FIRST_WALK_STEP_DISTANCE
		run_build_time = 0.0
	if not moving: starting = false
	desired_speed = speed_for_tilt(magnitude) if moving else 0.0
	var target := desired_speed
	var old_heading := heading
	if moving:
		var desired_heading := atan2(direction.x, direction.z)
		turning_error = angle_difference(heading, desired_heading)
		var turn_limit := deg_to_rad(lerpf(420.0, 210.0, clampf(speed / RUN_SPEED, 0.0, 1.0)))
		var target_angular := clampf(turning_error * 9.0, -turn_limit, turn_limit)
		angular_speed = move_toward(angular_speed, target_angular, deg_to_rad(1800.0) * delta)
		var turn := angular_speed * delta
		if absf(turn) > absf(turning_error) and signf(turn) == signf(turning_error):
			turn = turning_error
			angular_speed = 0.0
		heading = wrapf(heading + turn, -PI, PI)
		# Brake into a reversal rather than slide sideways/backwards at full speed.
		target *= pow(maxf(0.0, cos(turning_error)), 2.0)
	else:
		turning_error = 0.0
		angular_speed = 0.0
	if starting:
		start_time = minf(start_time + delta, START_DURATION)
		# Preserve the authored initial weight transfer before the first step.
		var ramp := smoothstep(0.1, START_DURATION, start_time)
		target = minf(target, WALK_SPEED * ramp)
		if start_time >= START_DURATION: starting = false
	# A run request never skips the first travelling walk step. Count actual
	# distance so a turn or light tilt cannot expire the lead-up while stationary.
	# This only caps acceleration; release and steering still act this tick.
	if first_step_remaining > 0.0:
		target = minf(target, WALK_SPEED)
	elif run_build_time < RUN_BUILD_DURATION:
		run_build_time = minf(run_build_time + delta, RUN_BUILD_DURATION)
		var run_limit := lerpf(WALK_SPEED, RUN_SPEED, smoothstep(0.0, RUN_BUILD_DURATION, run_build_time))
		target = minf(target, run_limit)
	var old_speed := speed
	speed = move_toward(speed, target, (ACCELERATION if target > speed else BRAKING) * delta)
	var distance := (old_speed + speed) * 0.5 * delta
	if not starting: first_step_remaining = maxf(0.0, first_step_remaining - distance)
	var middle_heading := old_heading + angle_difference(old_heading, heading) * 0.5
	position += Vector3(sin(middle_heading), 0.0, cos(middle_heading)) * distance
	return distance
