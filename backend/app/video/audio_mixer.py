from __future__ import annotations

import random
from pathlib import Path

from loguru import logger


# Default BGM tracks (placeholder paths)
DEFAULT_BGM_TRACKS = [
    "upbeat_tech.mp3",
    "calm_knowledge.mp3",
    "inspiring_story.mp3",
]

# Category to mood mapping
CATEGORY_MOODS = {
    "tech_trends": "upbeat",
    "科技前沿": "upbeat",
    "history": "epic",
    "历史人文": "epic",
    "economics": "serious",
    "经济投资": "serious",
    "automotive": "energetic",
    "汽车评测": "energetic",
}


def select_bgm(category: str, assets_dir: Path) -> str | None:
    """Select a background music track based on content category.

    Returns the path to the BGM file, or None if not available.
    """
    music_dir = assets_dir / "music"
    if not music_dir.exists():
        logger.warning(f"Music directory not found: {music_dir}")
        return None

    # Look for any .mp3 or .wav files
    tracks = list(music_dir.glob("*.mp3")) + list(music_dir.glob("*.wav"))
    if not tracks:
        logger.warning("No music tracks found")
        return None

    # Try to match by mood/category
    mood = CATEGORY_MOODS.get(category, "calm")
    matching = [t for t in tracks if mood in t.stem.lower()]
    if matching:
        selected = random.choice(matching)
    else:
        selected = random.choice(tracks)

    logger.info(f"[audio] Selected BGM: {selected.name}")
    return str(selected)
