from __future__ import annotations

from pathlib import Path
from functools import lru_cache

import yaml
from loguru import logger

from app.config import get_settings


@lru_cache
def load_prompts() -> dict:
    """Load prompt templates from YAML config."""
    config_path = get_settings().config_dir / "prompts.yaml"
    if not config_path.exists():
        logger.warning(f"Prompts config not found at {config_path}, using defaults")
        return _default_prompts()

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_prompt(name: str) -> dict[str, str]:
    """Get a specific prompt template (system + template)."""
    prompts = load_prompts()
    if name not in prompts:
        raise KeyError(f"Prompt '{name}' not found. Available: {list(prompts.keys())}")
    return prompts[name]


def render_prompt(name: str, **kwargs: str) -> tuple[str, str]:
    """Render a prompt template with variables. Returns (system_prompt, user_prompt)."""
    prompt_config = get_prompt(name)
    system = prompt_config.get("system", "")
    template = prompt_config.get("template", "")
    user_prompt = template.format(**kwargs)
    return system, user_prompt


def _default_prompts() -> dict:
    return {
        "topic_selection": {
            "system": "You are a content planning expert.",
            "template": "Select topics from: {crawled_items}\nCategories: {categories}",
        },
        "research": {
            "system": "You are a professional content researcher.",
            "template": "Research topic: {topic_title}\n{topic_description}\nCategory: {topic_category}",
        },
        "outline": {
            "system": "You are a short video content planner.",
            "template": "Create outline from: {research_summary}",
        },
        "script": {
            "system": "You are a short video script writer.",
            "template": "Write a {duration}s script from: {outline}",
        },
        "hashtags": {
            "system": "You are a social media expert.",
            "template": "Generate tags for: {title}\n{summary}\nPlatform: {platform}",
        },
    }
