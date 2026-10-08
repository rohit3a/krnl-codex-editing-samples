"""Render an original illustrated editing demonstration; no client assets."""
from pathlib import Path
import json
import math
import os
import subprocess

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parent
WIDTH, HEIGHT, FPS, SECONDS = 720, 1280, 24, 18
FONT = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
BOLD = Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
INK, CREAM, TEAL, CLAY = '#1E2431', '#F4F0E8', '#234C4C', '#D46547'
fonts = {
    'label': ImageFont.truetype(FONT, 22),
    'small': ImageFont.truetype(FONT, 27),
    'body': ImageFont.truetype(FONT, 32),
    'subtitle': ImageFont.truetype(FONT, 38),
    'title': ImageFont.truetype(BOLD, 72),
    'number': ImageFont.truetype(BOLD, 50),
}


def centred(draw, text, y, font, colour=INK):
    box = draw.textbbox((0, 0), text, font=font)
    x = (WIDTH - (box[2] - box[0])) / 2
    draw.text((x, y), text, font=font, fill=colour)


def frame_at(t):
    scene = min(int(t // 6), 2)
    local = t - scene * 6
    image = Image.new('RGB', (WIDTH, HEIGHT), CREAM)
    d = ImageDraw.Draw(image)
    drift = 5 * math.sin(local * 0.7)
    d.rounded_rectangle((45, 55, 675, 1225), 34, outline='#D9D4CA', width=2)
    d.text((78, 85), 'KRNL / ORIGINAL EDITING DEMO', font=fonts['label'], fill=TEAL)
    d.text((78, 167), f'0{scene + 1}', font=fonts['number'], fill=CLAY)
    title, subtitle = [('PLAN', 'Pick one small task.'),
                       ('FOCUS', 'Give it your full attention.'),
                       ('REVIEW', 'Write down what you learned.')][scene]
    d.text((78, 234), title, font=fonts['title'], fill=INK)

    if scene == 0:
        y = 417 + drift
        d.rounded_rectangle((94, y, 626, y + 425), 20, fill='white')
        d.text((125, y + 29), 'TODAY', font=fonts['body'], fill=TEAL)
        for row, text in enumerate(['Read five pages', 'Make three notes', 'Check one example']):
            yy = y + 120 + row * 85
            d.rounded_rectangle((126, yy, 166, yy + 40), 6, outline=TEAL, width=3)
            d.text((189, yy + 2), text, font=fonts['small'], fill=INK)
        if local >= 1.2:
            d.line([(132, y + 139), (142, y + 148), (161, y + 126)], fill=CLAY, width=5)
    elif scene == 1:
        centre_y = 650 + drift
        box = (172, centre_y - 188, 548, centre_y + 188)
        d.arc(box, 0, 360, fill='#D9D4CA', width=19)
        d.arc(box, -90, -90 + min(local / 6, 1) * 300, fill=TEAL, width=19)
        centred(d, '5 MIN', centre_y - 43, fonts['number'])
        centred(d, 'ONE TASK', centre_y + 32, fonts['small'], TEAL)
    else:
        y = 423 + drift
        d.rounded_rectangle((93, y, 627, y + 427), 20, fill='white')
        d.text((126, y + 33), 'KEEP THE USEFUL PART', font=fonts['label'], fill=TEAL)
        for row, text in enumerate(['One new idea.', 'One clear question.', 'One next step.']):
            yy = y + 121 + row * 86
            d.ellipse((127, yy + 11, 139, yy + 23), fill=CLAY)
            d.text((164, yy), text, font=fonts['body'], fill=INK)

    # Readable on-screen text, deliberately not speech-transcription claims.
    alpha = min(1, max(0, (local - 0.15) / 0.6))
    caption = Image.new('RGBA', (WIDTH, HEIGHT), (0, 0, 0, 0))
    cd = ImageDraw.Draw(caption)
    centred(cd, subtitle, 957 + 9 * (1 - alpha), fonts['subtitle'],
            (30, 36, 49, round(255 * alpha)))
    image = Image.alpha_composite(image.convert('RGBA'), caption).convert('RGB')
    d = ImageDraw.Draw(image)
    for index in range(3):
        x = 303 + index * 47
        d.ellipse((x, 1074, x + 19, 1093), fill=CLAY if index == scene else '#D9D4CA')
    centred(d, 'NEW SAMPLE / ILLUSTRATED FOOTAGE', 1143, fonts['label'], TEAL)
    d.rounded_rectangle((78, 1193, 642, 1199), 3, fill='#D9D4CA')
    progress = min(t / SECONDS, 1)
    if progress > 0:
        d.rounded_rectangle((78, 1193, 78 + 564 * progress, 1199), 3, fill=TEAL)
    return image


def main():
    output = OUT / 'study-edit-demo.mp4'
    if output.exists():
        raise FileExistsError(output)
    command = ['ffmpeg', '-hide_banner', '-loglevel', 'error', '-n',
               '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{WIDTH}x{HEIGHT}',
               '-r', str(FPS), '-i', 'pipe:0', '-an', '-c:v', 'libx264',
               '-threads', '2', '-preset', 'veryfast', '-crf', '23',
               '-pix_fmt', 'yuv420p', '-movflags', '+faststart', str(output)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        for n in range(FPS * SECONDS):
            process.stdin.write(frame_at(n / FPS).tobytes())
        process.stdin.close()
        rc = process.wait()
        if rc:
            raise RuntimeError(f'ffmpeg failed: {rc}')
    except BaseException:
        process.terminate()
        process.wait()
        raise
    frame_at(2).save(OUT / 'preview.jpg', quality=90)
    review = Image.new('RGB', (WIDTH, HEIGHT * 3), CREAM)
    for index, t in enumerate([2, 8, 14]):
        review.paste(frame_at(t), (0, index * HEIGHT))
    review.resize((360, 1920)).save(OUT / 'review-frames.jpg', quality=90)
    metadata = {
        'created': '2026-10-08', 'creator': 'Codex for Rohit / KRNL Studio',
        'purpose': 'New original editing demonstration, not a past client commission',
        'dimensions': [WIDTH, HEIGHT], 'fps': FPS, 'seconds': SECONDS,
        'audio': 'None; deliberately silent',
        'assets': 'Original vector geometry and fictional study-planning text',
        'font': 'Installed DejaVu Sans; font files are not redistributed',
        'technique': 'Pillow illustrations, hard cuts at 6/12 seconds, animated captions/progress, FFmpeg H.264',
        'personal_or_client_material': False,
    }
    (OUT / 'metadata.json').write_text(json.dumps(metadata, indent=2) + '\n')
    for path in OUT.iterdir():
        if path.is_file():
            os.chmod(path, 0o600)
    print(json.dumps({'rendered': str(output), 'bytes': output.stat().st_size,
                      'frames': FPS * SECONDS}))


if __name__ == '__main__':
    main()
