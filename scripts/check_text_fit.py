#!/usr/bin/env python3
"""Read-only preflight: verify Japanese text stays in each card's layout regions."""
import json
import pathlib
import re
import sys
from PIL import ImageFont

ROOT=pathlib.Path(__file__).resolve().parents[1]
FONT="/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
def check(article):
    if not re.fullmatch(r"OSN-[0-9]{3,}-[0-9]{8}",article):
        raise ValueError("Invalid article ID")
    spec=json.loads((ROOT/"specs"/(article+".json")).read_text(encoding="utf-8"))
    if spec.get("article_id")!=article or len(spec.get("slides",[]))!=6:
        raise ValueError("Invalid slide specification")
    if not pathlib.Path(FONT).is_file():
        raise ValueError("Japanese font not installed")
    sizes={"kicker":(34,340),"title":(66,820),"body":(40,820),"footer":(27,720)}
    for index,slide in enumerate(spec["slides"],1):
        for field,(size,maxwidth) in sizes.items():
            value=slide.get(field)
            lines=value if isinstance(value,list) else str(value or "").split("\n")
            if not lines or any(not isinstance(line,str) or not line.strip() for line in lines):
                raise ValueError(f"Slide {index} {field}: missing text")
            font=ImageFont.truetype(FONT,size)
            for line in lines:
                width=font.getlength(line)
                if width>maxwidth:
                    raise ValueError(f"Slide {index} {field}: overflow {width:.1f}px > {maxwidth}px: {line}")
        if len(slide["title"].split("\n"))>3 or len(slide["body"])>4:
            raise ValueError(f"Slide {index}: too many text lines")
    print("PASS: six-slide Japanese text fits designated regions; human visual review still required")
if __name__=="__main__":
    try: check(sys.argv[1])
    except (ValueError,OSError,IndexError,TypeError) as e: sys.exit("BLOCKED: "+str(e))
