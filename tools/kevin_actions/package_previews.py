from pathlib import Path
import json, math
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parent
rows=json.loads((ROOT/'preview_manifest.json').read_text(encoding='utf-8'))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',15)
for view in range(3):
 entries=[r for r in rows if r['view']==view and 'index' in r]
 for page in range(math.ceil(len(entries)/24)):
  batch=entries[page*24:(page+1)*24];sheet=Image.new('RGB',(4*320,math.ceil(len(batch)/4)*270),(20,24,30));draw=ImageDraw.Draw(sheet)
  for i,r in enumerate(batch):
   im=Image.open(ROOT/'frames'/r['file']).convert('RGB');im=im.crop((190,215,910,770));im.thumbnail((320,245));x=(i%4)*320;y=(i//4)*270;sheet.paste(im,(x,y));draw.text((x+5,y+244),str(r['index']+1)+' '+r['name'],font=font,fill='white')
  sheet.save(ROOT/f'catalogue_{view}_{page}.jpg',quality=88)
for name in sorted({r['name'] for r in rows if 'frame' in r}):
 entries=[r for r in rows if r['name']==name and 'frame' in r];sheet=Image.new('RGB',(8*270,3*240),(20,24,30));draw=ImageDraw.Draw(sheet)
 for r in entries:
  im=Image.open(ROOT/'frames'/r['file']).convert('RGB').crop((190,215,910,770));im.thumbnail((270,215));x=r['frame']*270;y=r['view']*240;sheet.paste(im,(x,y));draw.text((x+5,y+215),f"View {r['view']+1} / {r['frame']+1}",font=font,fill='white')
 sheet.save(ROOT/('sequence_'+name.replace(' ','_')+'.jpg'),quality=90)
print('Packaged',len(rows),'rendered frames')

for name in sorted({r['name'] for r in rows if 'facing' in r}):
 entries=[r for r in rows if r['name']==name and 'facing' in r];sheet=Image.new('RGB',(8*270,3*240),(20,24,30));draw=ImageDraw.Draw(sheet)
 for r in entries:
  im=Image.open(ROOT/'frames'/r['file']).convert('RGB').crop((190,215,910,770));im.thumbnail((270,215));x=r['facing']*270;y=r['view']*240;sheet.paste(im,(x,y));draw.text((x+5,y+215),f"View {r['view']+1} / {r['facing']*45} degrees",font=font,fill='white')
 sheet.save(ROOT/('facings_'+name.replace(' ','_')+'.jpg'),quality=90)
