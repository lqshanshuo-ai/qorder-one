from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from loguru import logger


# Default font settings
DEFAULT_FONT_SIZE = 60
OVERLAY_FONT_SIZE = 80
TITLE_FONT_SIZE = 100
SUBTITLE_FONT_SIZE = 48

# Video dimensions (9:16 vertical)
WIDTH = 1080
HEIGHT = 1920


def _get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    """Get a font, falling back to default if custom fonts unavailable."""
    font_candidates = [
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    if bold:
        font_candidates = [
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        ] + font_candidates

    for font_path in font_candidates:
        if Path(font_path).exists():
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                continue

    logger.warning("No TrueType fonts found, using default bitmap font")
    return ImageFont.load_default()


def create_text_frame(
    text: str,
    overlay_text: str = "",
    bg_color: tuple[int, int, int] = (15, 15, 25),
    text_color: tuple[int, int, int] = (255, 255, 255),
    accent_color: tuple[int, int, int] = (0, 200, 255),
    width: int = WIDTH,
    height: int = HEIGHT,
) -> Image.Image:
    """Create a single video frame with text overlay.

    Args:
        text: Main narration text (smaller, at bottom)
        overlay_text: Key text displayed prominently (center)
        bg_color: Background color RGB
        text_color: Text color RGB
        accent_color: Accent color for overlay text
    """
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw overlay text (prominent, centered)
    if overlay_text:
        font_overlay = _get_font(OVERLAY_FONT_SIZE, bold=True)
        _draw_wrapped_text(
            draw, overlay_text, font_overlay, accent_color,
            x=width // 2, y=height // 2 - 100,
            max_width=width - 120, align="center",
        )

    # Draw narration text (smaller, at bottom)
    if text:
        font_text = _get_font(DEFAULT_FONT_SIZE)
        _draw_wrapped_text(
            draw, text, font_text, text_color,
            x=width // 2, y=height - 400,
            max_width=width - 100, align="center",
        )

    return img


def create_title_frame(
    title: str,
    subtitle: str = "",
    bg_color: tuple[int, int, int] = (15, 15, 25),
    title_color: tuple[int, int, int] = (255, 255, 255),
    accent_color: tuple[int, int, int] = (0, 200, 255),
    width: int = WIDTH,
    height: int = HEIGHT,
) -> Image.Image:
    """Create a title/intro frame."""
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Draw decorative line
    line_y = height // 2 - 150
    draw.rectangle(
        [(width // 2 - 200, line_y), (width // 2 + 200, line_y + 4)],
        fill=accent_color,
    )

    # Title
    font_title = _get_font(TITLE_FONT_SIZE, bold=True)
    _draw_wrapped_text(
        draw, title, font_title, title_color,
        x=width // 2, y=height // 2,
        max_width=width - 120, align="center",
    )

    # Subtitle
    if subtitle:
        font_sub = _get_font(SUBTITLE_FONT_SIZE)
        _draw_wrapped_text(
            draw, subtitle, font_sub, accent_color,
            x=width // 2, y=height // 2 + 200,
            max_width=width - 120, align="center",
        )

    return img


def create_cover_image(
    title: str,
    category: str = "",
    bg_color: tuple[int, int, int] = (25, 25, 40),
    width: int = WIDTH,
    height: int = HEIGHT,
) -> Image.Image:
    """Create a cover image for the video."""
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Category badge
    if category:
        font_cat = _get_font(40)
        badge_text = f"[ {category} ]"
        bbox = draw.textbbox((0, 0), badge_text, font=font_cat)
        tw = bbox[2] - bbox[0]
        draw.text(
            ((width - tw) // 2, height // 2 - 250),
            badge_text, fill=(0, 200, 255), font=font_cat,
        )

    # Title
    font_title = _get_font(90, bold=True)
    _draw_wrapped_text(
        draw, title, font_title, (255, 255, 255),
        x=width // 2, y=height // 2,
        max_width=width - 140, align="center",
    )

    # Bottom decoration
    draw.rectangle(
        [(100, height - 200), (width - 100, height - 196)],
        fill=(0, 200, 255),
    )

    return img


def _draw_wrapped_text(
    draw: ImageDraw.ImageDraw,
    text: str,
    font: ImageFont.FreeTypeFont,
    color: tuple[int, int, int],
    x: int,
    y: int,
    max_width: int,
    align: str = "center",
    line_spacing: int = 20,
) -> None:
    """Draw text with word wrapping."""
    lines: list[str] = []
    current_line = ""

    for char in text:
        test_line = current_line + char
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > max_width and current_line:
            lines.append(current_line)
            current_line = char
        else:
            current_line = test_line

    if current_line:
        lines.append(current_line)

    # Calculate total height
    line_height = font.size + line_spacing
    total_height = line_height * len(lines)
    start_y = y - total_height // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        tw = bbox[2] - bbox[0]
        if align == "center":
            lx = x - tw // 2
        else:
            lx = x
        draw.text((lx, start_y + i * line_height), line, fill=color, font=font)
