"""Encode Godot review captures at normal cadence; optionally compare a saved pass.

python tools/blender/encode_walk_preview.py --baseline <previous-preview-folder> --comparison-name pushoff
Requires Pillow. --record, --record --side-view and --record --travel produce inputs.
"""
import argparse
from pathlib import Path
from PIL import Image, ImageDraw, ImageSequence

ROOT=Path(__file__).resolve().parent/'locomotion_previews'

def save_loop(path,frames):
    frames[0].save(path,save_all=True,append_images=frames[1:],
                   duration=([30,30,40]*(len(frames)//3)),loop=0,optimize=False)

def encode(folder,name,count):
    paths=sorted((ROOT/folder).glob('*.png'))
    assert len(paths)==count,(folder,len(paths),count)
    frames=[Image.open(p).convert('RGB').resize((660,540),Image.Resampling.LANCZOS) for p in paths]
    save_loop(ROOT/name,frames)
    return frames

def compare(baseline,current,path):
    with Image.open(baseline) as source:
        before=[im.convert('RGB') for im in ImageSequence.Iterator(source)]
    assert len(before)==len(current)==36
    frames=[]
    for old,new in zip(before,current):
        frame=Image.new('RGB',(1320,570),'#151922')
        frame.paste(old,(0,30));frame.paste(new,(660,30))
        draw=ImageDraw.Draw(frame)
        draw.text((16,9),'BEFORE - previous pass',fill='white')
        draw.text((676,9),'AFTER - current pass',fill='white')
        frames.append(frame)
    save_loop(path,frames)

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--baseline',type=Path)
    parser.add_argument('--comparison-name',default='comparison')
    args=parser.parse_args()
    assert Path(args.comparison_name).name==args.comparison_name
    front=encode('frames','walk.gif',36)
    side=encode('frames_side','walk_side.gif',36) if (ROOT/'frames_side').exists() else None
    if (ROOT/'frames_travel').exists():encode('frames_travel','walk_travel.gif',72)
    if args.baseline:
        compare(args.baseline/'walk.gif',front,ROOT/(args.comparison_name+'_before_after.gif'))
        if side is not None and (args.baseline/'walk_side.gif').exists():
            compare(args.baseline/'walk_side.gif',side,ROOT/(args.comparison_name+'_side_before_after.gif'))
    print('WALK_PREVIEWS',ROOT)
