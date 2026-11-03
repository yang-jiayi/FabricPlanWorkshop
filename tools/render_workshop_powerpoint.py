#!/usr/bin/env python3
"""Export every slide using installed Windows PowerPoint, plus a contact sheet."""
import argparse
import json
import math
import shutil
from pathlib import Path


def render(source, output):
    import win32com.client
    from PIL import Image

    source, output = Path(source).resolve(), Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    application = win32com.client.Dispatch('PowerPoint.Application')
    presentation = application.Presentations.Open(str(source), ReadOnly=True,
                                                 Untitled=False, WithWindow=False)
    measurements = []
    try:
        for slide in presentation.Slides:
            destination = output / f'slide-{slide.SlideIndex:02d}.png'
            slide.Export(str(destination), 'PNG', 1920, 1080)
            for shape in slide.Shapes:
                if not shape.HasTextFrame or not shape.TextFrame.HasText:
                    continue
                frame = shape.TextFrame2
                text = frame.TextRange
                measurements.append({
                    'slide': slide.SlideIndex, 'text': text.Text,
                    'shape_height': shape.Height, 'shape_width': shape.Width,
                    'bound_height': text.BoundHeight, 'bound_width': text.BoundWidth,
                    'overflow': (
                        text.BoundHeight > shape.Height - frame.MarginTop - frame.MarginBottom + 1
                        or text.BoundWidth > shape.Width - frame.MarginLeft - frame.MarginRight + 1
                    ),
                })
        count = presentation.Slides.Count
    finally:
        # Close only this read-only presentation; never quit the user's application.
        presentation.Close()
    (output / 'text-bounds.json').write_text(
        json.dumps(measurements, ensure_ascii=False, indent=2), encoding='utf-8',
    )
    columns, width, height, gutter = 4, 480, 270, 12
    rows = math.ceil(count / columns)
    sheet = Image.new('RGB', (columns * width + (columns + 1) * gutter,
                             rows * height + (rows + 1) * gutter), '#dce5ed')
    for index in range(count):
        with Image.open(output / f'slide-{index + 1:02d}.png') as slide_image:
            slide_image = slide_image.resize((width, height), Image.Resampling.LANCZOS)
            sheet.paste(slide_image, (gutter + index % columns * (width + gutter),
                                     gutter + index // columns * (height + gutter)))
    sheet.save(output / 'contact-sheet.png')
    shutil.copy2(source, output / source.name)
    overflows = [entry for entry in measurements if entry['overflow']]
    print(f'Exported {count} slides. Text boxes exceeding measured bounds: {len(overflows)}')
    for entry in overflows:
        print(f'Slide {entry["slide"]}: {entry["text"]!r}')
    if overflows:
        raise SystemExit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path, help='Non-repository export directory')
    arguments = parser.parse_args()
    render(arguments.source, arguments.output)
