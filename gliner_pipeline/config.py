from pathlib import Path
import torch

INPUT_DIR = Path("../block_data")
OUTPUT_FILE = Path("../ner_output/TV.json")

NER_MODEL_NAME = "urchade/gliner_base"
CONF_THRESHOLD = 0.6

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

VALID_BLOCK_TYPES = {
    "paragraph",
    "list_item",
    "inline_note",
    "table_block"
}

LABELS = ["service purpose",
    "service domain",
    "target user",
    "transport capability",
    "route or navigation function",
    "booking and reservation function",
    "real time information function",
    "payment function",
    "user account function",
    "API interaction pattern",
    "API method definition (action, properties, event, GET/POST/PUT/DELETE/)",
    "geographical coverage",
    "operational limitations",
    "unit of measurement of data",
    "regulatory constraints",
    "dependency on external context",
    "performance characteristics",
    "reliability and availability characteristics",
    "scalability characteristics",
    "security and privacy aspects",
    "cost model",
    "accessibility feauture",
    "user physical constraints supports",
    "language and localization",
    "environmental impact",
    "sustainability features",
    "energy source or fuel characteristics",
    "ecological regulation compliance",
    "third part services dependency",
    "multi modal support"]