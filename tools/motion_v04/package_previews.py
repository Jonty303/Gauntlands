"""Package Godot --motion-capture frames; requires Pillow."""
from pathlib import Path
import json
from PIL import Image, ImageDraw
ROOT = Path(__file__).resolve().parent
report = json.loads((ROOT / "frames/capture.json").read_text(encoding="utf-8"))
labels = ["isometric", "three_quarter", "top_down"]
for view, label in enumerate(labels):
    paths = sorted((ROOT / "frames" / str(view)).glob("*.png"))
    assert len(paths) == 336, (label, len(paths))
    frames = [Image.open(path).convert("RGB").resize((660, 540)) for path in paths[::3]]
    frames[0].save(ROOT / (label + ".gif"), save_all=True, append_images=frames[1:], duration=100, loop=0, optimize=False)
    with Image.open(ROOT / (label + ".gif")) as gif:
        assert gif.n_frames == 112
        duration = 0
        for i in range(gif.n_frames):
            gif.seek(i)
            duration += gif.info["duration"]
        assert duration == 11200
    sheet = Image.new("RGB", (1320, 600), (18, 24, 30))
    draw = ImageDraw.Draw(sheet)
    for i, frame in enumerate([18, 30, 65, 100, 145, 185, 231, 260]):
        image = Image.open(paths[frame]).convert("RGB").crop((370, 270, 740, 610)).resize((280, 258))
        x, y = (i % 4) * 330, (i // 4) * 300
        sheet.paste(image, (x + 25, y + 26))
        draw.text((x + 16, y + 8), f"{label}  {frame / 30:.2f}s", fill="white")
    sheet.save(ROOT / (label + "_poses.png"))
(ROOT / "preview_manifest.json").write_text(json.dumps({"source_frames_per_view":336,"source_fps":30,"preview_frames":112,"preview_fps":10,"duration_seconds":11.2,"views":labels}, indent=2) + "\n", encoding="utf-8")
print("Three previews and contact sheets verified: 112 frames / 11.2 s each")
