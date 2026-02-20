from gliner_pipeline.io.loader import load_pages
from gliner_pipeline.io.writer import save_json
from gliner_pipeline.preprocessing.blocks import extract_valid_blocks
from gliner_pipeline.ner.gliner_model import GLiNERService
from gliner_pipeline.rendering.html_builder import build_html
from gliner_pipeline.config import INPUT_DIR, OUTPUT_FILE, LABELS


def run_pipeline():

    pages = load_pages(INPUT_DIR)

    blocks = extract_valid_blocks(pages)

    ner = GLiNERService()

    for block in blocks:
        spans = ner.predict(block.text, LABELS)
        pages[block.page_idx]["blocks"][block.block_idx]["concept_spans"] = spans

    filtered_pages = [build_html(page) for page in pages]

    save_json(filtered_pages, OUTPUT_FILE)