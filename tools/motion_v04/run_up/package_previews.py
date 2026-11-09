from pathlib import Path
import json
from PIL import Image, ImageDraw
root = Path(__file__).resolve().parent
for view, name in enumerate(["isometric", "three_quarter", "top_down"]):
    paths = sorted((root / "frames" / str(view)).glob("*.png"))
    assert len(paths) == 126
    frames = [Image.open(path).convert("RGB").resize((660,540)) for path in paths[::2]]
    durations = [70,60,70] * 21
    frames[0].save(root / (name + ".gif"),save_all=True,append_images=frames[1:],duration=durations,loop=0,optimize=False)
    with Image.open(root / (name + ".gif")) as gif:
        assert gif.n_frames == 63
        total = 0
        for i in range(gif.n_frames):
            gif.seek(i)
            total += gif.info["duration"]
        assert total == 4200
    sheet = Image.new("RGB",(1320,840),(18,24,30))
    draw = ImageDraw.Draw(sheet)
    for i, frame in enumerate([12,30,42,48,54,60,66,105]):
        image = Image.open(paths[frame]).convert("RGB").crop((310,140,790,780)).resize((285,380))
        x,y = (i%4)*330,(i//4)*420
        sheet.paste(image,(x+15,y+26))
        draw.text((x+16,y+8),f"{name} / {frame/30-0.3:.2f}s from input",fill="white")
    sheet.save(root / (name + "_poses.png"))
(root / "preview_manifest.json").write_text(json.dumps({"source_frames_per_view":126,"source_fps":30,"preview_frames":63,"duration_seconds":4.2,"preview_fps":15,"views":["isometric","three_quarter","top_down"]},indent=2)+"\n",encoding="utf-8")
print("Verified three 63-frame / 4.2 s run-up previews")
