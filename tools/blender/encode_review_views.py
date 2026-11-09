"""Encode the three sign-off views and eight-facing pose sheets from Godot captures.
Run Godot --path prototype -- --record --review first. Requires Pillow.
--baseline points to a saved frames_review directory for matched comparisons.
"""
import argparse,json
from pathlib import Path
from PIL import Image,ImageDraw
ROOT=Path(__file__).resolve().parent/'locomotion_previews'
VIEWS=[('isometric','ISOMETRIC'),('three_quarter','RAISED 3/4'),('top_down','TOP-DOWN')]
def tile(path):
    with Image.open(path) as image:
        image=image.convert('RGB')
        w,h=image.size
        return image.crop(((w-h)//2,0,(w+h)//2,h)).resize((440,440),Image.Resampling.LANCZOS)
def loop(path,frames):
    frames[0].save(path,save_all=True,append_images=frames[1:],duration=[30,30,40]*12,loop=0,optimize=False)
def labelled(images,labels):
    frame=Image.new('RGB',(440*len(images),470),'#151922');draw=ImageDraw.Draw(frame)
    for i,(image,label) in enumerate(zip(images,labels)):
        frame.paste(image,(440*i,30));draw.text((440*i+12,9),label,fill='white')
    return frame
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--baseline',type=Path);args=parser.parse_args()
    combined=[]
    all_frames={name:[tile(ROOT/'frames_review'/name/f'{i:03d}.png') for i in range(36)] for name,_ in VIEWS}
    for i in range(36):combined.append(labelled([all_frames[name][i] for name,_ in VIEWS],[label for _,label in VIEWS]))
    loop(ROOT/'review_views.gif',combined)
    for name,label in VIEWS:
        loop(ROOT/f'review_{name}.gif',[labelled([im],[label]) for im in all_frames[name]])
        if args.baseline:
            before=[tile(args.baseline/name/f'{i:03d}.png') for i in range(36)]
            loop(ROOT/f'review_{name}_before_after.gif',[labelled([a,b],['BEFORE - '+label,'AFTER - '+label]) for a,b in zip(before,all_frames[name])])
        sheet=Image.new('RGB',(1760,1000),'#151922');draw=ImageDraw.Draw(sheet)
        for row,frame in enumerate([0,9,18,27]):
            for facing in range(8):
                im=tile(ROOT/'frames_review'/name/f'facing_{facing}_{frame:02d}.png').resize((220,220),Image.Resampling.LANCZOS)
                x=facing*220;y=row*250;sheet.paste(im,(x,y+30))
                draw.text((x+6,y+9),f'{facing*45} deg / {frame/30:.1f}s',fill='white')
        sheet.save(ROOT/f'review_{name}_facings.png')
    sheet=Image.new('RGB',(1760,750),'#151922');draw=ImageDraw.Draw(sheet)
    for row,(name,label) in enumerate(VIEWS):
        for col,frame in enumerate([0,5,10,15,20,25,30,35]):
            sheet.paste(all_frames[name][frame].resize((220,220),Image.Resampling.LANCZOS),(col*220,row*250+30))
            draw.text((col*220+6,row*250+9),f'{label} {frame/30:.2f}s',fill='white')
    sheet.save(ROOT/'review_views_poses.png')
    manifest=json.loads((ROOT/'frames_review/cameras.json').read_text())
    (ROOT/'review_cameras.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print('REVIEW_VIEWS',ROOT)
