import re
from pathlib import Path
from .ollama import OllamaClient

PROMPTS = Path(__file__).parent.parent.parent / "prompts"


def _load_prompt(name: str) -> str:
    return (PROMPTS / name).read_text(encoding="utf-8")


def generate_outline(client: OllamaClient, topic: str, references: list[dict], template: str = "tutorial") -> dict:
    refs = "\n".join(
        f"- {r['title']} (👍{r['liked_count']})" for r in references[:5]
    )
    prompt_file = f"{template}_outline.txt"
    prompt = _load_prompt(prompt_file).format(topic=topic, references=refs)

    print(f"  [outline] generating for topic={topic}...")
    raw = client.generate(prompt)

    title = ""
    emoji = "📝"
    sections = []

    for line in raw.splitlines():
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.startswith("EMOJI:"):
            emoji = line.replace("EMOJI:", "").strip()
        elif re.match(r"^\d+\.", line):
            sections.append(line.strip())

    return {"title": title, "emoji": emoji, "sections": sections, "raw": raw}


def generate_body(client: OllamaClient, title: str, outline: dict, template: str = "tutorial") -> str:
    outline_text = "\n".join(outline["sections"])
    prompt_file = f"{template}_body.txt"
    prompt = _load_prompt(prompt_file).format(
        title=title, outline=outline_text
    )

    print(f"  [body] generating '{title}'...")
    return client.generate(prompt)
