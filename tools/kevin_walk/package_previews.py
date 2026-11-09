from pathlib import Path
from PIL import Image, ImageDraw
import json
root=Path(__file__).resolve().parent
for view,name in enumerate(["isometric","three_quarter","top_down"]):
 paths=sorted((root/'frames'/str(view)).glob('*.png'));assert len(paths)==48
 frames=[Image.open(p).convert("RGB").resize((660,540)) for p in paths]
 frames[0].save(root/(name+'.gif'),save_all=True,append_images=frames[1:],duration=[30,30,40]*16,loop=0,optimize=False)
 with Image.open(root/(name+'.gif')) as gif:
  assert gif.n_frames==48
  assert sum(gif.seek(i) or gif.info["duration"] for i in range(48))==1600
 sheet=Image.new("RGB",(1280,860),(18,24,30));d=ImageDraw.Draw(sheet)
 for i,f in enumerate([0,3,6,9,12,15,18,21]):
  im=Image.open(paths[f]).crop((280,160,820,780)).resize((300,350))
  x=(i%4)*320;y=(i//4)*430
  sheet.paste(im,(x+10,y+35));d.text((x+12,y+12),f'{name}: {(f+1)/30:.2f}s',fill='white')
 sheet.save(root/(name+'_poses.png'))
 sheet=Image.new("RGB",(1280,860),(18,24,30));d=ImageDraw.Draw(sheet)
 for i in range(8):
  im=Image.open(root/'frames'/f'facing_{view}_{i}.png').crop((280,160,820,780)).resize((300,350))
  x=(i%4)*320;y=(i//4)*430
  sheet.paste(im,(x+10,y+35));d.text((x+12,y+12),f'{name}: facing {i}',fill='white')
 sheet.save(root/(name+'_facings.png'))
(root/'preview_manifest.json').write_text(json.dumps({'views':3,'facings_per_view':8,'frames_per_view':48,'fps':30,'duration_s':1.6},indent=2)+'\n')
print('Packaged three 1.6-second previews, three cycle sheets, three facing sheets.')