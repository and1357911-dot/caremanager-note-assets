#!/usr/bin/env python3
"""Prepare six visual briefs from an approved slide spec. No image generation or posting."""
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
STYLE = (
    "Instagram vertical 4:5 editorial design for Japanese care managers. "
    "Warm, bright Japanese care-office setting with a professional care manager; "
    "combine an expressive human figure or friendly illustration with practical "
    "information panels. Large bold navy Japanese headline, selective vivid pink "
    "emphasis and yellow marker strokes; white or cream panels, pale blue/pink "
    "section backgrounds, clear numbering and page counter. Use speech bubbles "
    "or small icons where they clarify the slide; maintain generous safe margins. "
    "Avoid generic blank corporate cards. Use only the supplied copy; never invent "
    "facts, dates, rates, names, medical claims or legal conclusions. "
    "Mark proposals and unknowns exactly as the source does."
)
ROLES = (
    "Cover: prominent question, subject and an engaging care-work scene.",
    "Problem: show a realistic question and its practical implications.",
    "Explanation: clearly group the key points with numbered visual hierarchy.",
    "Example: contrast appropriate and inappropriate actions where supported.",
    "Checklist: numbered items and distinct pastel panels for practical checks.",
    "Summary: key takeaways and next action, with a clear closing message.",
)

def build(article, spec):
    if not re.fullmatch(r"OSN-[0-9]{3,}-[0-9]{8}", article):
        raise ValueError("Invalid article ID")
    slides = spec.get("slides")
    if spec.get("article_id") != article or not isinstance(slides, list) or len(slides) != 6:
        raise ValueError("Expected exactly six slides for the requested article")
    if spec.get("publication_approved") is not False:
        raise ValueError("Spec must explicitly be non-published")
    briefs = []
    for i, slide in enumerate(slides):
        if not isinstance(slide, dict):
            raise ValueError("Slide must be an object")
        for k in ("kicker", "title", "footer"):
            if not isinstance(slide.get(k), str) or not slide[k].strip():
                raise ValueError("Missing slide copy: " + k)
        body = slide.get("body")
        if not isinstance(body, list) or not 1 <= len(body) <= 4 or any(
            not isinstance(line, str) or not line.strip() for line in body
        ):
            raise ValueError("Invalid body")
        briefs.append({
            "slide": i + 1,
            "aspect_ratio": "4:5",
            "style": STYLE,
            "role": ROLES[i],
            "copy_verbatim": {k: slide[k] for k in ("kicker", "title", "body", "footer")},
            "quality_gate": "HOLD until human verifies every character, readability, safe margins, source accuracy, and six unique images",
        })
    return {"article_id": article, "visual_qc": "NOT_CHECKED", "publication_approved": False,
            "generation_performed": False, "slides": briefs}

def main():
    article = sys.argv[1]
    if not re.fullmatch(r"OSN-[0-9]{3,}-[0-9]{8}", article):
        raise ValueError("Invalid article ID")
    spec = json.loads((ROOT / "specs" / (article + ".json")).read_text(encoding="utf-8"))
    print(json.dumps(build(article, spec), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, IndexError, TypeError) as exc:
        sys.exit("BLOCKED: " + str(exc))
