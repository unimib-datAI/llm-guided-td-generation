from dataclasses import dataclass
from typing import List

BLOCK_TYPES = {
    "paragraph",
    "list_item",
    "inline_note",
    "table_block"
}

@dataclass
class BlockInput:
    page_idx: int
    block_idx: int
    block_id: str
    text: str

def extract_valid_blocks(pages) -> List[BlockInput]:
    blocks = []

    for page_idx, page in enumerate(pages):
        for block_idx, block in enumerate(page["blocks"]):
            if block["block_type"] not in BLOCK_TYPES:
                continue

            blocks.append(
                BlockInput(
                    page_idx=page_idx,
                    block_idx=block_idx,
                    block_id=block["block_id"],
                    text=block["text"]
                )
            )

    return blocks