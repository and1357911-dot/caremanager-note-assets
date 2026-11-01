#!/usr/bin/env python3
"""Generate six article-specific 1080x1350 PNG cards from approved-safe copy.
This writes only to the public image assets repo. It never contacts Buffer/note.
"""
import json
import pathlib
import re
import sys
from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATTERN = re.compile(r"OSN-[0-9]{3,}-[0-9]{8}\Z")
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

def render(article):
    if not PATTERN.fullmatch(article):
        raise ValueError("Invalid article ID")
    spec = json.loads((ROOT/"specs"/(article+".json")).read_text(encoding="utf-8"))
    if spec.get("article_id") != article or spec.get("publication_approved") is not False:
        raise ValueError("Unapproved or mismatched article")
    slides = spec.get("slides")
    if not isinstance(slides,list) or len(slides)!=6:
        raise ValueError("Six slides required")
    if not pathlib.Path(FONT).is_file():
        raise ValueError("Required Japanese font unavailable")
    folder = ROOT/article
    folder.mkdir(exist_ok=True)
    for index, slide in enumerate(slides,1):
        kicker,title,body,footer = (slide.get(k) for k in ("kicker","title","body","footer"))
        if not all(isinstance(x,str) and 0<len(x)<=110 for x in (kicker,title,footer)):
            raise ValueError("Invalid slide copy")
        if not isinstance(body,list) or not 1<=len(body)<=4 or any(not isinstance(x,str) or len(x)>70 for x in body):
            raise ValueError("Invalid body copy")
        im = Image.new("RGB",(1080,1350),(248,250,250))
        d=ImageDraw.Draw(im)
        navy=(24,54,70); teal=(12,118,115); muted=(72,92,99)
        d.rounded_rectangle((65,70,1015,1280),radius=42,fill="white")
        d.rounded_rectangle((105,118,520,194),radius=28,fill=(222,242,239))
        d.text((135,128),kicker,font=ImageFont.truetype(FONT,34),fill=teal)
        d.rectangle((112,230,124,620),fill=teal)
        title_font=ImageFont.truetype(FONT,66)
        for n,line in enumerate(title.split("\n")):
            if d.textbbox((0,0),line,font=title_font)[2]>825:
                raise ValueError("Title too wide: "+line)
            d.text((160,250+n*100),line,font=title_font,fill=navy)
        y=660
        body_font=ImageFont.truetype(FONT,40)
        for line in body:
            if d.textbbox((0,0),line,font=body_font)[2]>835:
                raise ValueError("Body too wide: "+line)
            d.text((130,y),line,font=body_font,fill=muted)
            y+=91
        d.line((120,1130,960,1130),fill=(210,226,226),width=3)
        d.text((120,1160),footer,font=ImageFont.truetype(FONT,27),fill=muted)
        d.text((905,1160),f"{index}/6",font=ImageFont.truetype(FONT,27),fill=teal)
        target=folder/f"instagram_{index:02d}.png"
        im.save(target,optimize=True)
        if target.stat().st_size>8*1024*1024:
            raise ValueError("PNG too large")
        print(target.relative_to(ROOT))
if __name__=="__main__":
    try: render(sys.argv[1])
    except (ValueError,OSError,IndexError,KeyError) as e: sys.exit("BLOCKED: "+str(e))
