from gliner_pipeline.config import CONF_THRESHOLD

def annotate_text(text, spans):
    spans = [s for s in spans if s.get("score", 1.0) >= CONF_THRESHOLD]
    spans = sorted(spans, key=lambda s: s["start"], reverse=True)

    for s in spans:
        entity = text[s["start"]:s["end"]]
        wrapped = f'<span class="{s["label"]}">{entity}</span>'
        text = text[:s["start"]] + wrapped + text[s["end"]:]
    return text


def build_html(page):
    html_parts = []
    removed = []

    for block in sorted(page["blocks"], key=lambda b: b["order"]):

        tag = block.get("tag_name") or "p"
        spans = block.get("concept_spans", [])

        if not spans:
            removed.append(block["block_id"])
            continue

        if removed:
            html_parts.append(f"<!-- BLOCKS_REMOVED {','.join(removed)} -->")
            removed = []

        annotated = annotate_text(block["text"], spans)
        html_parts.append(f"<{tag}>{annotated}</{tag}>")

    return {"url": page["url"], "html": "".join(html_parts)}