"""One prompt section; no tool registrations, hooks or network calls."""
from pathlib import Path

STYLE_PATH = Path(__file__).resolve().parents[3] / "prompts" / "conversation.md"
MAX_CHARS = 4000


def render_style(session_info):
    text = STYLE_PATH.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("Shared conversation prompt is empty")
    if len(text) > MAX_CHARS:
        raise ValueError("Shared conversation prompt exceeds the 4000-character cap")
    return text


def register(ctx):
    ctx.register_system_prompt_section(
        "shared-response-style.communication", render_style,
        position="after_memory", max_chars=MAX_CHARS,
    )
