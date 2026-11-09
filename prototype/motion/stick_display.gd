extends Control
var value := Vector2.ZERO
func _draw() -> void:
	var centre := size * 0.5
	draw_circle(centre, 31.0, Color(0.06, 0.09, 0.12))
	draw_arc(centre, 31.0, 0.0, TAU, 48, Color(0.3, 0.4, 0.46), 1.0, true)
	draw_line(centre - Vector2(31, 0), centre + Vector2(31, 0), Color(0.18, 0.23, 0.27))
	draw_line(centre - Vector2(0, 31), centre + Vector2(0, 31), Color(0.18, 0.23, 0.27))
	draw_line(centre, centre + value * 27.0, Color(0.32, 0.83, 0.78), 2.0, true)
	draw_circle(centre + value * 27.0, 5.0, Color(0.48, 0.92, 0.85))
