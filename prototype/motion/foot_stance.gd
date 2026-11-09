extends RefCounted
## Model-specific contact-aware placement, applied after authored animation.
const INWARD := 0.02
const SETTLE_BEGIN := 0.64
const SETTLE_END := 0.96
const SETTLE_LIFT := 0.018
const MAX_LATERAL_SPEED := 0.115
var skeleton: Skeleton3D
var legs: Array[Dictionary] = []
var previous_requested := false
var settling := false
var maximum_target_error := 0.0
var maximum_length_error := 0.0
var minimum_bend_alignment := 1.0

func setup(value: Skeleton3D) -> void:
	skeleton = value
	for side in ["L", "R"]:
		var foot := skeleton.find_bone("foot." + side)
		legs.append({"side":side,"upper":skeleton.find_bone("upperleg01."+side),
			"lower":skeleton.find_bone("lowerleg01."+side),"foot":foot,
			"sign":signf(skeleton.get_bone_global_rest(foot).origin.x),
			"offset":0.0,"lift":0.0,"mode":"","from":0.0,"goal":0.0,
			"begin":0.0,"last":0.0,"swing":false,"settle_needed":false})

func reset() -> void:
	previous_requested = false
	settling = false
	maximum_target_error = 0.0
	maximum_length_error = 0.0
	minimum_bend_alignment = 1.0
	for leg in legs:
		leg.offset = 0.0
		leg.lift = 0.0
		leg.mode = ""
		leg.swing = false
		leg.settle_needed = false

static func placement_ease(value: float) -> float:
	var u := clampf(value,0.0,1.0)
	return u*u*u*(10.0+u*(-15.0+6.0*u))

func update(delta: float, animation: Node, requested: bool) -> void:
	settling = false
	for i in range(2):
		var leg := legs[i]
		var mode := ""
		var progress := 0.0
		var leading: bool = (i == 1) == animation.stop_right
		if not requested and previous_requested:
			leg.settle_needed = absf(leg.offset) > 0.00001
		if requested:
			if animation.was_starting:
				if i == 0 and animation.start_time >= 0.1:
					mode = "start"
					progress = clampf((animation.start_time - 0.1)/0.6,0.0,1.0)
			else:
				var phase := fposmod(animation.phase + i*0.5,1.0)
				var duty := lerpf(0.6,0.4,animation.run_mix)
				if phase > duty:
					mode = "gait"
					progress = (phase-duty)/(1.0-duty)
		else:
			if not leading and animation.stop_time >= 0.12 and animation.stop_time <= 0.64:
				mode = "stop_recovery"
				progress = (animation.stop_time-0.12)/0.52
			elif leading and animation.stop_time >= SETTLE_BEGIN and animation.stop_time <= SETTLE_END and leg.settle_needed:
				mode = "settle"
				progress = (animation.stop_time-SETTLE_BEGIN)/(SETTLE_END-SETTLE_BEGIN)
		var desired: float = INWARD if requested else 0.0
		# Keep the reached placement at touchdown. Never snap to a missed target
		# when an interruption leaves too little swing time; finish on the next swing.
		if not mode.is_empty():
			if mode != leg.mode or progress < leg.last:
				leg.from = leg.offset
				leg.goal = desired
				leg.begin = progress
			var fraction: float = (progress-leg.begin)/maxf(0.001,1.0-leg.begin)
			leg.offset = move_toward(leg.offset,lerpf(leg.from,leg.goal,placement_ease(fraction)),MAX_LATERAL_SPEED*delta)
			leg.last = progress
		leg.swing = not mode.is_empty()
		leg.mode = mode
		var lift := SETTLE_LIFT * pow(sin(PI*progress),2.0) if mode == "settle" else 0.0
		# Interrupted settle releases its extra lift smoothly into the new action.
		leg.lift = lift if not requested else move_toward(leg.lift,0.0,0.12*delta)
		if not requested and (leg.offset > 0.0001 or leg.lift > 0.0001): settling = true
	previous_requested = requested

func apply() -> void:
	for leg in legs:
		if leg.offset < 0.0000001 and leg.lift < 0.0000001: continue
		var upper: Transform3D = skeleton.get_bone_global_pose(leg.upper)
		var lower: Transform3D = skeleton.get_bone_global_pose(leg.lower)
		var foot: Transform3D = skeleton.get_bone_global_pose(leg.foot)
		var hip := upper.origin
		var knee := lower.origin
		var ankle := foot.origin
		var target := ankle + Vector3(-leg.sign*leg.offset, leg.lift, 0.0)
		var thigh_length := hip.distance_to(knee)
		var shin_length := knee.distance_to(ankle)
		var axis := (target-hip).normalized()
		var distance := hip.distance_to(target)
		# Keep the authored knee's bend plane; narrowing never chooses a new pole.
		var bend := knee-hip-axis*(knee-hip).dot(axis)
		if bend.length_squared() < 0.00000001:
			bend = Vector3.BACK-axis*Vector3.BACK.dot(axis)
		bend = bend.normalized()
		var reach := clampf(distance,absf(thigh_length-shin_length)+0.0001,thigh_length+shin_length-0.0001)
		var along := (thigh_length*thigh_length-shin_length*shin_length+reach*reach)/(2.0*reach)
		var new_knee := hip + axis*along + bend*sqrt(maxf(0.0,thigh_length*thigh_length-along*along))
		var upper_rotation := Quaternion((knee-hip).normalized(),(new_knee-hip).normalized())
		var lower_rotation := Quaternion((ankle-knee).normalized(),(target-new_knee).normalized())
		skeleton.set_bone_global_pose(leg.upper,Transform3D(Basis(upper_rotation)*upper.basis,hip))
		skeleton.set_bone_global_pose(leg.lower,Transform3D(Basis(lower_rotation)*lower.basis,new_knee))
		foot.origin = target
		skeleton.set_bone_global_pose(leg.foot,foot)
		var actual := skeleton.get_bone_global_pose(leg.foot).origin
		maximum_target_error = maxf(maximum_target_error,actual.distance_to(target))
		maximum_length_error = maxf(maximum_length_error,absf(new_knee.distance_to(target)-shin_length))
		var new_bend := new_knee-hip-axis*(new_knee-hip).dot(axis)
		minimum_bend_alignment = minf(minimum_bend_alignment,bend.dot(new_bend.normalized()))
