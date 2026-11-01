#!/usr/bin/env python3
"""Create a six-slide contact sheet for human visual QC. No publishing."""
import pathlib
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT=pathlib.Path(__file__).resolve().parents[1]
def build(article):
    import re
    if not re.fullmatch(r"OSN-[0-9]{3,}-[0-9]{8}",article):
        raise ValueError("invalid article ID")
    folder=ROOT/article
    output=ROOT/"qc-previews"
    output.mkdir(exist_ok=True)
    thumb_w,thumb_h=324,405
    margin=24
    sheet=Image.new("RGB",(3*thumb_w+4*margin,2*thumb_h+3*margin),(229,234,237))
    for i in range(6):
        path=folder/f"instagram_{i+1:02d}.png"
        with Image.open(path) as im:
            im.load()
            if im.size!=(1080,1350):
                raise ValueError("incorrect image dimensions")
            tile=im.convert("RGB").resize((thumb_w,thumb_h),Image.Resampling.LANCZOS)
        x=margin+(i%3)*(thumb_w+margin)
        y=margin+(i//3)*(thumb_h+margin)
        sheet.paste(tile,(x,y))
    target=output/(article+"-contact-sheet.jpg")
    sheet.save(target,quality=92,optimize=True)
    print("VISUAL REVIEW REQUIRED:",target)
    print("This preview is NOT visual approval and NOT publication authorization")
if __name__=="__main__":
    try: build(sys.argv[1])
    except (ValueError,OSError,IndexError) as e: sys.exit("BLOCKED: "+str(e))
