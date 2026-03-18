from __future__ import annotations

"""Video style templates for different content categories."""


TEMPLATES = {
    "text_montage": {
        "name": "Text + Image Montage",
        "bg_color": (15, 15, 25),
        "text_color": (255, 255, 255),
        "accent_color": (0, 200, 255),
        "fps": 30,
        "transition": "fade",
        "transition_duration": 0.5,
    },
    "tech": {
        "name": "Tech Blue",
        "bg_color": (10, 15, 30),
        "text_color": (220, 240, 255),
        "accent_color": (0, 150, 255),
        "fps": 30,
        "transition": "fade",
        "transition_duration": 0.3,
    },
    "history": {
        "name": "History Gold",
        "bg_color": (30, 20, 10),
        "text_color": (255, 245, 220),
        "accent_color": (218, 165, 32),
        "fps": 30,
        "transition": "fade",
        "transition_duration": 0.8,
    },
    "economics": {
        "name": "Finance Green",
        "bg_color": (10, 20, 15),
        "text_color": (240, 255, 240),
        "accent_color": (0, 200, 100),
        "fps": 30,
        "transition": "fade",
        "transition_duration": 0.5,
    },
    "automotive": {
        "name": "Auto Red",
        "bg_color": (25, 10, 10),
        "text_color": (255, 240, 240),
        "accent_color": (255, 60, 60),
        "fps": 30,
        "transition": "fade",
        "transition_duration": 0.4,
    },
}

# Category to template mapping
CATEGORY_TEMPLATE_MAP = {
    "tech_trends": "tech",
    "科技前沿": "tech",
    "history": "history",
    "历史人文": "history",
    "economics": "economics",
    "经济投资": "economics",
    "automotive": "automotive",
    "汽车评测": "automotive",
}


def get_template(category: str) -> dict:
    """Get the video style template for a given category."""
    template_name = CATEGORY_TEMPLATE_MAP.get(category, "text_montage")
    return TEMPLATES.get(template_name, TEMPLATES["text_montage"])
