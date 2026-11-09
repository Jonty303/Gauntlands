from pathlib import Path
from PIL import Image, ImageDraw
import json
root=Path(__file__).resolve().parent
for view,name in enumerate(['isometric','three_quarter','top_down']):
 paths=sorted((root/'frames'/str(view)).glob('*.png'))
 assert len(paths)==270
 frames=[Image.open(p).convert('RGB').resize((660,540)) for p in paths[::2]]
 frames[0].save(root/(name+'.gif'),save_all=True,append_images=frames[1:],duration=[70,60,70]*45,loop=0,optimize=False)
 with Image.open(root/(name+'.gif')) as gif:
  assert gif.n_frames==135
  assert sum(gif.seek(i) or gif.info['duration'] for i in range(gif.n_frames))==9000
 sheet=Image.new('RGB',(1280,1200),(18,24,30));d=ImageDraw.Draw(sheet)
 for i,f in enumerate([0,30,60,75,105,145,165,195,210,225,239,269]):
  im=Image.open(paths[f]).crop((280,160,820,730)).resize((290,310))
  x=(i%4)*320;y=(i//4)*400
  sheet.paste(im,(x+15,y+35));d.text((x+15,y+12),f'{name} / {(f+1)/30:.2f}s',fill='white')
 sheet.save(root/(name+'_sequence.png'))
 sheet=Image.new('RGB',(1600,760),(18,24,30));d=ImageDraw.Draw(sheet)
 for row,clip in enumerate(['Idle','Run']):
  for facing in range(8):
   im=Image.open(root/'frames'/f'{clip}_{view}_{facing}.png').crop((280,160,820,730)).resize((190,280))
   x=facing*200;y=row*380
   sheet.paste(im,(x+5,y+35));d.text((x+5,y+12),f'{clip} / {facing}',fill='white')
 sheet.save(root/(name+'_facings.png'))
(root/'preview_manifest.json').write_text(json.dumps({'source_frames_per_view':270,'source_fps':30,'preview_frames':135,'duration_s':9,'views':3,'new_clip_facing_poses':48},indent=2)+'\n')
print('Verified three 9-second previews, three sequences, three idle/run facing sheets.')
