"""Package v0.2 Godot sequence captures. Requires Pillow."""
from pathlib import Path
import json,argparse
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent/'locomotion_v02';RAW=ROOT/'frames'
VIEWS=[('isometric','ISOMETRIC'),('three_quarter','RAISED 3/4'),('top_down','TOP-DOWN')]
parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path);parser.add_argument('--comparison-name',default='start');args=parser.parse_args()
manifest=json.loads((RAW/'cameras.json').read_text());labels=[]
for name,duration in manifest['segments']:labels.extend([name]*round(duration*30))
def tile(path,size=360):
    with Image.open(path) as im:
        w,h=im.size;return im.convert('RGB').crop(((w-h)//2,0,(w+h)//2,h)).resize((size,size),Image.Resampling.LANCZOS)
frames=[]
for i,label in enumerate(labels):
    out=Image.new('RGB',(1080,390),'#151922');draw=ImageDraw.Draw(out)
    for c,(name,title) in enumerate(VIEWS):
        out.paste(tile(RAW/name/f'{i:03d}.png'),(c*360,30));draw.text((c*360+10,9),title+' / '+label,fill='white')
    frames.append(out)
frames[0].save(ROOT/'sequence_review.gif',save_all=True,append_images=frames[1:],duration=([30,30,40]*((len(frames)+2)//3))[:len(frames)],loop=0,optimize=False)
for name,title in VIEWS:
    out=Image.new('RGB',(1760,1000),'#151922');draw=ImageDraw.Draw(out)
    for row,clip in enumerate(['Idle','WalkStart','WalkStopL','WalkStopR']):
        for facing in range(8):
            x=facing*220;y=row*250;out.paste(tile(RAW/name/f'facing_{facing}_{clip}.png',220),(x,y+30));draw.text((x+6,y+9),f'{clip} / {facing*45} deg',fill='white')
    out.save(ROOT/f'{name}_facings.png')
out=Image.new('RGB',(1800,1170),'#151922')
transition_indices=[];cursor=0
for name,duration in manifest['segments']:
    count=round(duration*30)
    if name in ['WalkStart','WalkStopL','WalkStopR'] and (name!='WalkStart' or not transition_indices):
        transition_indices.append([cursor+round((count-1)*f) for f in [0,.25,.5,.75,1]])
    cursor+=count
for row,indices in enumerate(transition_indices):
    for col,index in enumerate(indices):
        # Isometric pose strip for each transition, labelled with sequence time.
        out.paste(frames[index].crop((0,0,360,390)),(col*360,row*390))
out.save(ROOT/'transition_poses.png')
(ROOT/'review_cameras.json').write_text(json.dumps(manifest,indent=2)+'\n')
print('V02_REVIEW',len(frames),'frames',len(frames)/30,'seconds')

if args.baseline:
    comparison=[]
    for i in range(72):
        im=Image.new('RGB',(1080,780),'#151922');draw=ImageDraw.Draw(im)
        for col,(name,title) in enumerate(VIEWS):
            for row,(base,label) in enumerate([(args.baseline,'BEFORE'),(RAW,'AFTER')]):
                im.paste(tile(base/name/f'{i:03d}.png'),(col*360,row*390+30))
                draw.text((col*360+10,row*390+9),label+' / '+title,fill='white')
        comparison.append(im)
    comparison[0].save(ROOT/f'{args.comparison_name}_before_after.gif',save_all=True,append_images=comparison[1:],duration=[30,30,40]*24,loop=0,optimize=False)
    sheet=Image.new('RGB',(1760,1500),'#151922');draw=ImageDraw.Draw(sheet)
    for view,(name,title) in enumerate(VIEWS):
        for variant,(base,label) in enumerate([(args.baseline,'BEFORE'),(RAW,'AFTER')]):
            row=view*2+variant
            for col,index in enumerate([24,27,30,33,36,39,42,45]):
                sheet.paste(tile(base/name/f'{index:03d}.png',220),(col*220,row*250+30))
                draw.text((col*220+5,row*250+9),f'{label} {title} {(index-24)/30:.1f}s',fill='white')
    sheet.save(ROOT/f'{args.comparison_name}_before_after_poses.png')
