import re

def basic_text_stats(text: str):
    words = re.findall(r"\b[\w']+\b", text)
    return {
        "characters": len(text),
        "words": len(words),
        "sentences": max(1, len(re.findall(r"[.!?]+", text))),
        "uppercase_ratio": round(
            sum(c.isupper() for c in text) / max(1, sum(c.isalpha() for c in text)), 3
        ),
    }
