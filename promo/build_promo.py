import base64
import math
from array import array
from pathlib import Path
import subprocess
import sys
import wave

from fontTools.ttLib import TTFont
from fontTools.pens.svgPathPen import SVGPathPen
import imageio_ffmpeg
import pyttsx3
import resvg_py
from PIL import Image, ImageColor, ImageDraw

ROOT = Path(__file__).resolve().parent
BUILD = ROOT / ".build"
OUTPUT = ROOT / "the-lms-as-a-build-target.mp4"
MUSIC_BED = BUILD / "music_bed.wav"
WIDTH, HEIGHT, FPS = 1920, 1080, 24
BG = "#F3E4F0"
PANEL = "#FFFFFF"
WHITE = "#111111"
MUTED = "#630460"
LIME = "#EF5BA1"
CYAN = "#630460"
CORAL = "#EF5BA1"
FONT_REGULAR = str(ROOT / "fonts" / "inter-500.woff2")
FONT_BOLD = str(ROOT / "fonts" / "poppins-800.woff2")
FONT_MONO = str(ROOT / "fonts" / "poppins-600.woff2")
LOGO_DATA = base64.b64encode((ROOT / "edutech_logo.png").read_bytes()).decode("ascii")
VECTOR_DIR = ROOT / "vector"
FONT_CACHE = {}

SCENES = [
    {
        "audio": "Hi, I'm Tristan Bunn, and I'm excited to be speaking at EDUtech AU.",
        "caption": "Hi, I’m Tristan Bunn, and I’m excited to be speaking at EDUtech AU.",
    },
    {
        "audio": "My session, The LMS as a Build Target, explores a better way to create course content.",
        "caption": "My session, The LMS as a Build Target, explores a better way to create course content.",
    },
    {
        "audio": "Discover how a plain-text pipeline can turn Markdown into LMS pages, PDFs, and course packages,",
        "caption": "Discover how a plain-text pipeline can turn Markdown into LMS pages, PDFs, and course packages,",
    },
    {
        "audio": "reducing content drift, improving version control, and cutting updates from days to minutes.",
        "caption": "Reducing content drift, improving version control, and cutting updates from days to minutes.",
    },
    {
        "audio": "I'll share what worked, what broke, and where AI fits.",
        "caption": "I’ll share what worked, what broke, and where AI fits.",
    },
    {
        "audio": "See you at EDUtech AU!",
        "caption": "See you at EDUtech AU!",
    },
]


def number(value):
    return f"{value:.3f}".rstrip("0").rstrip(".")


def paint(value):
    if isinstance(value, str):
        return value, 1.0
    if len(value) == 4:
        return f"#{value[0]:02x}{value[1]:02x}{value[2]:02x}", value[3] / 255
    return f"#{value[0]:02x}{value[1]:02x}{value[2]:02x}", 1.0


class VectorFont:
    def __init__(self, path, size):
        self.path = path
        self.size = size
        if path not in FONT_CACHE:
            data = TTFont(path)
            FONT_CACHE[path] = (data, data.getGlyphSet(), data.getBestCmap(), data["hmtx"], data["head"].unitsPerEm, data["hhea"].ascent)
        self.data, self.glyphs, self.cmap, self.metrics, self.units, self.ascent = FONT_CACHE[path]
        self.scale = size / self.units

    def glyph_name(self, character):
        return self.cmap.get(ord(character), ".notdef")

    def advance(self, character):
        return self.metrics[self.glyph_name(character)][0] * self.scale

    def width(self, text):
        return sum(self.advance(character) for character in text)


class VectorDraw:
    def __init__(self):
        self.elements = []
        self.defs = []

    def textlength(self, text, font):
        return font.width(text)

    def textbbox(self, origin, text, font):
        return (0, 0, font.width(text), font.size)

    def text(self, xy, text, font, fill):
        color, opacity = paint(fill)
        x, y = xy
        baseline = y + font.ascent * font.scale
        paths = []
        advance = 0.0
        for character in text:
            name = font.glyph_name(character)
            pen = SVGPathPen(font.glyphs)
            font.glyphs[name].draw(pen)
            paths.append(f'<path d="{pen.getCommands()}" transform="translate({number(advance)} 0)"/>')
            advance += font.advance(character) / font.scale
        self.elements.append(f'<g fill="{color}" fill-opacity="{number(opacity)}" transform="translate({number(x)} {number(baseline)}) scale({number(font.scale)} {number(-font.scale)})">{"".join(paths)}</g>')

    def multiline_text(self, xy, text, font, fill, spacing=4):
        x, y = xy
        for line in text.split("\n"):
            self.text((x, y), line, font, fill)
            y += font.size + spacing

    def rounded_rectangle(self, box, radius, fill, outline=None, width=1):
        x1, y1, x2, y2 = box
        color, opacity = paint(fill)
        stroke = ""
        if outline:
            stroke_color, stroke_opacity = paint(outline)
            stroke = f' stroke="{stroke_color}" stroke-opacity="{number(stroke_opacity)}" stroke-width="{number(width)}"'
        self.elements.append(f'<rect x="{number(x1)}" y="{number(y1)}" width="{number(x2-x1)}" height="{number(y2-y1)}" rx="{number(radius)}" fill="{color}" fill-opacity="{number(opacity)}"{stroke}/>')

    def rectangle(self, box, fill):
        self.rounded_rectangle(box, 0, fill)

    def ellipse(self, box, fill=None, outline=None, width=1):
        x1, y1, x2, y2 = box
        color, opacity = paint(fill or "none")
        stroke = ""
        if outline:
            stroke_color, stroke_opacity = paint(outline)
            stroke = f' stroke="{stroke_color}" stroke-opacity="{number(stroke_opacity)}" stroke-width="{number(width)}"'
        self.elements.append(f'<ellipse cx="{number((x1+x2)/2)}" cy="{number((y1+y2)/2)}" rx="{number((x2-x1)/2)}" ry="{number((y2-y1)/2)}" fill="{color}" fill-opacity="{number(opacity)}"{stroke}/>')

    def line(self, xy, fill, width=1):
        x1, y1, x2, y2 = xy
        color, opacity = paint(fill)
        self.elements.append(f'<line x1="{number(x1)}" y1="{number(y1)}" x2="{number(x2)}" y2="{number(y2)}" stroke="{color}" stroke-opacity="{number(opacity)}" stroke-width="{number(width)}" stroke-linecap="round"/>')

    def polygon(self, points, fill):
        color, opacity = paint(fill)
        pairs = zip(points[::2], points[1::2]) if points and isinstance(points[0], (int, float)) else points
        coordinates = " ".join(f"{number(x)},{number(y)}" for x, y in pairs)
        self.elements.append(f'<polygon points="{coordinates}" fill="{color}" fill-opacity="{number(opacity)}"/>')

    def image(self, xy, width, height, data):
        x, y = xy
        self.elements.append(f'<image x="{number(x)}" y="{number(y)}" width="{number(width)}" height="{number(height)}" preserveAspectRatio="xMidYMid meet" href="data:image/png;base64,{data}"/>')

    def render(self, name):
        VECTOR_DIR.mkdir(exist_ok=True)
        svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}"><defs>{"".join(self.defs)}</defs>{"".join(self.elements)}</svg>'
        svg_path = VECTOR_DIR / f"{name}.svg"
        png_path = BUILD / f"{name}_2x.png"
        if not svg_path.exists():
            svg_path.write_text(svg, encoding="utf-8")
        png_path.write_bytes(resvg_py.svg_to_bytes(svg_path=str(svg_path), width=WIDTH * 2, height=HEIGHT * 2))
        image = Image.open(png_path).convert("RGBA")
        return image.resize((WIDTH, HEIGHT), Image.Resampling.LANCZOS)


def font(size, bold=False, mono=False):
    path = FONT_MONO if mono else FONT_BOLD if bold else FONT_REGULAR
    return VectorFont(path, size)


def clamp(value):
    return max(0.0, min(1.0, value))


def ease(value):
    value = clamp(value)
    return 1 - (1 - value) ** 3


def wrapped_lines(draw, text, text_font, max_width):
    lines, current = [], ""
    for word in text.split():
        trial = f"{current} {word}".strip()
        if current and draw.textlength(trial, font=text_font) > max_width:
            lines.append(current)
            current = word
        else:
            current = trial
    if current:
        lines.append(current)
    return lines


def text_at(draw, text, center_x, y, text_font, fill=WHITE, max_width=1600, spacing=12):
    lines = wrapped_lines(draw, text, text_font, max_width)
    for line in lines:
        box = draw.textbbox((0, 0), line, font=text_font)
        height = box[3] - box[1]
        draw.text((center_x - draw.textlength(line, font=text_font) / 2, y), line, font=text_font, fill=fill)
        y += height + spacing
    return y


def centered_text(draw, text, y, text_font, fill=WHITE, max_width=1600, spacing=12):
    return text_at(draw, text, WIDTH / 2, y, text_font, fill, max_width, spacing)


def rounded(draw, box, fill=PANEL, outline=None, width=2, radius=28):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def background():
    draw = VectorDraw()
    draw.rectangle((0, 0, WIDTH, HEIGHT), BG)
    pink = ImageColor.getrgb(LIME)
    purple = ImageColor.getrgb(MUTED)
    for cx, cy, radius, color in [
        (WIDTH * 0.925, -HEIGHT * 0.05, WIDTH * 0.21, (*pink, 40)),
        (WIDTH * 0.99, HEIGHT * 1.02, WIDTH * 0.14, (*purple, 20)),
        (-WIDTH * 0.033, HEIGHT * 0.96, WIDTH * 0.10, (*pink, 30)),
    ]:
        draw.ellipse((cx - radius, cy - radius, cx + radius, cy + radius), fill=color)
    draw.defs.append(f'<linearGradient id="footerGradient" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="{MUTED}"/><stop offset="1" stop-color="{LIME}"/></linearGradient>')
    draw.rectangle((0, HEIGHT - 22, WIDTH, HEIGHT), "url(#footerGradient)")
    return draw.render("background")


def header_and_footer():
    draw = VectorDraw()
    draw.image((60, 42), 360, 58, LOGO_DATA)
    draw.text((1650, 974), "#EDUtechAU", font=font(22, bold=True), fill=MUTED)
    return draw.render("header")


def scene_content(scene_index):
    draw = VectorDraw()
    if scene_index == 0:
        draw.text((120, 225), "I’M SPEAKING AT", font=font(32, bold=True), fill=LIME)
        draw.text((120, 295), "EDUtech AU 2027", font=font(64, bold=True), fill=MUTED)
        draw.text((120, 450), "TRISTAN BUNN", font=font(82, bold=True), fill=WHITE)
        draw.multiline_text((120, 610), "THE LMS AS A\nBUILD TARGET", font=font(38, bold=True), fill=WHITE, spacing=14)
        draw.text((120, 845), "9 & 10 June 2027  •  ICC Sydney", font=font(25), fill=WHITE)
    elif scene_index == 1:
        centered_text(draw, "SESSION REVEAL", 180, font(29, bold=True), CYAN)
        centered_text(draw, "THE LMS AS A", 290, font(86, bold=True), WHITE)
        centered_text(draw, "BUILD TARGET", 410, font(110, bold=True), LIME)
        draw.rounded_rectangle((400, 585, 1520, 589), radius=2, fill=(99, 4, 96, 45))
        centered_text(draw, "A publishing-pipeline approach to course content", 655, font(43), WHITE)
        rounded(draw, (660, 795, 1260, 870), fill=(239, 91, 161, 22), outline=(239, 91, 161, 100), radius=37)
        centered_text(draw, "SOURCE  /  BUILD  /  LMS", 815, font(29, mono=True), LIME)
    elif scene_index == 2:
        centered_text(draw, "ONE SOURCE.  MANY OUTPUTS.", 190, font(66, bold=True), LIME)
        rounded(draw, (100, 400, 600, 690), fill=(255, 255, 255, 245), outline=(98, 217, 255, 110))
        text_at(draw, "course.md", 350, 465, font(56, mono=True), CYAN)
        text_at(draw, "MARKDOWN + METADATA + CITATIONS", 350, 575, font(24, bold=True), MUTED, max_width=440)
        draw.line((615, 545, 705, 545), fill=LIME, width=5)
        draw.polygon((690, 531, 690, 559, 714, 545), fill=LIME)
        rounded(draw, (735, 460, 1080, 630), fill=(239, 91, 161, 30), outline=(239, 91, 161, 140), radius=35)
        text_at(draw, "BUILD\nPIPELINE", 907, 500, font(36, bold=True), LIME, spacing=14)
        draw.line((1095, 545, 1185, 545), fill=LIME, width=5)
        draw.polygon((1170, 531, 1170, 559, 1194, 545), fill=LIME)
        labels = [("LMS PAGES", CYAN), ("PDF BRIEFS", LIME), ("COURSE PACKAGES", CORAL)]
        for index, (label, color) in enumerate(labels):
            y = 330 + index * 190
            rounded(draw, (1220, y, 1820, y + 135), fill=(255, 255, 255, 245), outline=color, radius=25)
            draw.rounded_rectangle((1255, y + 35, 1310, y + 42), radius=3, fill=color)
            draw.text((1350, y + 47), label, font=font(30, bold=True), fill=WHITE)
    elif scene_index == 3:
        centered_text(draw, "UPDATE YOUR COURSE", 190, font(36, bold=True), CYAN)
        text_at(draw, "DAYS", 440, 365, font(135, bold=True), MUTED)
        draw.line((870, 455, 1025, 455), fill=LIME, width=8)
        draw.polygon((1010, 433, 1010, 477, 1045, 455), fill=LIME)
        text_at(draw, "MINUTES", 1450, 365, font(128, bold=True), LIME)
        chips = ["LESS CONTENT DRIFT", "MEANINGFUL VERSION HISTORY", "SINGLE-SOURCE PUBLISHING"]
        for index, label in enumerate(chips):
            x1 = 80 + index * 600
            rounded(draw, (x1, 715, x1 + 560, 825), fill=(255, 255, 255, 230), radius=38)
            draw.ellipse((x1 + 35, 760, x1 + 55, 780), fill=LIME)
            text_at(draw, label, x1 + 310, 755, font(25, bold=True), WHITE, max_width=450)
    elif scene_index == 4:
        centered_text(draw, "NO SILVER BULLET.", 190, font(72, bold=True), WHITE)
        centered_text(draw, "JUST A BETTER WORKFLOW.", 305, font(35, bold=True), CORAL)
        cards = [("01", "WHAT WORKED", CYAN), ("02", "WHAT BROKE", CORAL), ("03", "WHERE AI FITS", LIME)]
        for index, (number, label, color) in enumerate(cards):
            x1 = 80 + index * 600
            rounded(draw, (x1, 500, x1 + 560, 790), fill=(255, 255, 255, 240), outline=(*ImageColor.getrgb(color), 90), radius=30)
            text_at(draw, number, x1 + 280, 565, font(58, mono=True), color)
            text_at(draw, label, x1 + 280, 685, font(34, bold=True), WHITE)
    else:
        centered_text(draw, "SEE YOU AT", 180, font(40, bold=True), MUTED)
        centered_text(draw, "EDUtech AU", 295, font(144, bold=True), LIME)
        rounded(draw, (650, 540, 1270, 655), fill=(239, 91, 161, 28), outline=(239, 91, 161, 130), radius=50)
        centered_text(draw, "#EDUtechAU", 565, font(58, bold=True), LIME)
        centered_text(draw, "THE LMS AS A BUILD TARGET", 755, font(34, bold=True), WHITE)
        centered_text(draw, "TRISTAN BUNN", 835, font(28), MUTED)
        centered_text(draw, "9 & 10 June 2027  •  ICC Sydney", 920, font(24), MUTED)
    return draw.render(f"scene_{scene_index}")


def run(command):
    subprocess.run([str(part) for part in command], check=True)


def make_narration():
    narration = BUILD / "narration.wav"
    starts, durations = [], []
    pcm = array("h")
    sample_rate = 22050
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    engine = pyttsx3.init()
    engine.setProperty("rate", 195)
    voices = engine.getProperty("voices")
    preferred_voice = next((voice for voice in voices if "karen" in voice.name.lower() or "en_au" in voice.id.lower()), None)
    if preferred_voice:
        engine.setProperty("voice", preferred_voice.id)
    for index, scene in enumerate(SCENES):
        engine.save_to_file(scene["audio"], str(BUILD / f"voice_{index}_render"))
    engine.runAndWait()
    for index, scene in enumerate(SCENES):
        source = BUILD / f"voice_{index}_render"
        path = BUILD / f"voice_{index}.wav"
        run([ffmpeg, "-y", "-i", source, "-ar", "22050", "-ac", "1", "-c:a", "pcm_s16le", path])
        with wave.open(str(path), "rb") as audio:
            sample_rate = audio.getframerate()
            frames = audio.getnframes()
            if not frames:
                raise RuntimeError(f"Narration generation failed for scene {index}")
            data = array("h")
            data.frombytes(audio.readframes(frames))
        lead = int(sample_rate * (0.20 if index == 0 else 0.10))
        tail = int(sample_rate * (0.25 if index < len(SCENES) - 1 else 0.65))
        starts.append((len(pcm) + lead) / sample_rate)
        durations.append(frames / sample_rate)
        pcm.extend([0] * lead)
        pcm.extend(data)
        pcm.extend([0] * tail)
    with wave.open(str(narration), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        if sys.byteorder != "little":
            pcm.byteswap()
        audio.writeframes(pcm.tobytes())
    return narration, sample_rate, starts, durations, len(pcm) / sample_rate


def make_music(path, sample_rate, duration):
    samples = array("h")
    chords = [(110.0, 164.81, 220.0), (130.81, 196.0, 261.63), (98.0, 146.83, 196.0), (110.0, 164.81, 220.0)]
    total = int(duration * sample_rate)
    for index in range(total):
        t = index / sample_rate
        chord = chords[int(t / 4) % len(chords)]
        fade = min(1.0, t / 1.5, (duration - t) / 2.0)
        pad = sum(math.sin(2 * math.pi * frequency * t) for frequency in chord) / 3
        pulse = math.sin(2 * math.pi * chord[0] * 2 * t) * (0.5 + 0.5 * math.sin(2 * math.pi * 0.5 * t)) ** 6
        shimmer = math.sin(2 * math.pi * chord[2] * 2 * t) * (0.5 + 0.5 * math.sin(2 * math.pi * 0.25 * t)) ** 10
        value = int(32767 * 0.20 * fade * (0.55 * pad + 0.18 * pulse + 0.10 * shimmer))
        samples.append(value)
    with wave.open(str(path), "wb") as audio:
        audio.setnchannels(1)
        audio.setsampwidth(2)
        audio.setframerate(sample_rate)
        if sys.byteorder != "little":
            samples.byteswap()
        audio.writeframes(samples.tobytes())


def write_script():
    script = "\n".join(scene["audio"] for scene in SCENES)
    (ROOT / "script.txt").write_text(script + "\n", encoding="utf-8")


def render_video(total_duration, scene_starts):
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    silent = BUILD / "silent_landscape.mp4"
    shared_background = background()
    shared_header = header_and_footer()
    contents = [scene_content(index) for index in range(6)]
    scene_durations = []
    for index, start in enumerate(scene_starts):
        end = scene_starts[index + 1] if index + 1 < len(SCENES) else total_duration
        scene_durations.append(end - start)
    frame_count = math.ceil(total_duration * FPS)
    command = [ffmpeg, "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{WIDTH}x{HEIGHT}", "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-preset", "medium", "-tune", "animation", "-crf", "12", "-pix_fmt", "yuv420p", "-movflags", "+faststart", silent]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    scene_index = 0
    elapsed = 0.0
    for frame_index in range(frame_count):
        t = frame_index / FPS
        while scene_index + 1 < len(scene_durations) and t >= elapsed + scene_durations[scene_index]:
            elapsed += scene_durations[scene_index]
            scene_index += 1
        local_t = t - elapsed
        frame = Image.alpha_composite(shared_background, shared_header)
        enter = ease((local_t - 0.03) / 0.48)
        shifted = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        shifted.alpha_composite(contents[scene_index], (0, int(34 * (1 - enter))))
        shifted.putalpha(shifted.getchannel("A").point(lambda alpha: int(alpha * enter)))
        frame = Image.alpha_composite(frame, shifted)
        if scene_index == 2:
            draw = ImageDraw.Draw(frame, "RGBA")
            for dot in range(3):
                dot_x = 620 + ((local_t * 90 + dot * 34) % 80)
                draw.ellipse((dot_x, 539, dot_x + 12, 551), fill=(239, 91, 161, 170))
        if t > total_duration - 0.55:
            opacity = clamp((total_duration - t) / 0.55)
            black = Image.new("RGBA", (WIDTH, HEIGHT), (*ImageColor.getrgb(BG), int(255 * (1 - opacity))))
            frame = Image.alpha_composite(frame, black)
        process.stdin.write(frame.convert("RGB").tobytes())
    process.stdin.close()
    if process.wait() != 0:
        raise RuntimeError("Video encoding failed")
    return ffmpeg, silent


def main():
    BUILD.mkdir(exist_ok=True)
    narration, sample_rate, starts, durations, total_duration = make_narration()
    scene_starts = [start - (0.20 if index == 0 else 0.10) for index, start in enumerate(starts)]
    write_script()
    ffmpeg, silent = render_video(total_duration, scene_starts)
    raw_music = BUILD / "music.wav"
    processed_voiceover = BUILD / "voiceover_processed.wav"
    make_music(raw_music, sample_rate, total_duration)
    run([ffmpeg, "-y", "-i", narration, "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-ac", "2", processed_voiceover])
    run([ffmpeg, "-y", "-i", raw_music, "-af", "volume=0.28", "-ar", "48000", "-ac", "2", MUSIC_BED])
    run([
        ffmpeg, "-y", "-i", silent, "-i", processed_voiceover, "-i", MUSIC_BED,
        "-filter_complex", "[1:a][2:a]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.95[a]",
        "-map", "0:v:0", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-metadata", "title=The LMS as a Build Target — EDUtech AU", "-movflags", "+faststart", "-shortest", OUTPUT,
    ])
    print(f"Created {OUTPUT}")
    print(f"Duration: {total_duration:.2f} seconds")


if __name__ == "__main__":
    main()
