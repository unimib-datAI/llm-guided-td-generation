# llm-guided-td-generation

This repository implements a pipeline for **semantic extraction and Thing Description (TD) generation** from services documentation pages.

The project combines:

* structured block extraction
* NER-based concept detection (GLiNER)
* prompt construction
* LLM-based TD generation

It is designed as a **research prototype** for studying automated semantic API understanding and Web of Things description synthesis.

---

## Project Structure

```
.
├── gliner_pipeline/        # semantic extraction pipeline
│
├── prompts/
│   ├── baseline_prompt.txt
│   └── guided_prompt.txt
│
├── td_generation/          # LLM backends and prompt builder
│   ├── azure.py
│   ├── groq.py
│   ├── openrouter.py
│   └── prompt_creation.py
│
└── scraper.py              # documentation scraping
```

---

## Pipeline Overview

The workflow is divided into four stages:

1. **Scraping**

   * Collect documentation pages and convert them to structured JSON blocks

2. **Semantic Annotation (GLiNER)**

   * Filter relevant textual blocks
   * Detect domain concepts using a Named Entity Recognition model
   * Produce annotated HTML

3. **Prompt Construction**

   * Build LLM prompts from extracted semantics
   * Two modes available:

     * baseline prompt
     * guided prompt

4. **Thing Description Generation**

   * Send prompts to LLM providers
   * Generate candidate TDs

---

## Requirements

Python ≥ 3.10

Install dependencies:

```
pip install -r requirements.txt
```

GLiNER requires PyTorch.
GPU is optional but recommended.

---

## Prompts

* `baseline_prompt.txt`
  Minimal instruction to the model

* `guided_prompt.txt`
  Structured instruction leveraging extracted entities

The comparison between them is part of the experimental evaluation.

---

## Notes

This repository is intended for experimentation and reproducible evaluation, not production deployment.

LLM outputs are not validated automatically and may require post-processing.
