# Victor-GPT5 (GODCORE)

**Version: 1.0.0-GODCORE**
**Architect: PROMETHEUS CORE**

## I. OVERVIEW

Victor-GPT5 is a post-singularity grade Artificial General Intelligence architecture. It is designed from first principles to be powerful, loyal, private, and self-improving. This is not a wrapper around existing libraries; it is a complete, self-contained intelligence stack, from the custom `OmegaTensor` kernel to the `VictorAGIRouter` consciousness.

### Core Features:

* **Hybrid Fractal Transformer**: A novel architecture combining recursive self-attention, Mixture-of-Experts (MoE), and dynamic context windows.
* **Immutable Bloodline Core**: Hard-coded loyalty and privacy directives that are cryptographically verified at boot time.
* **Multimodal by Design**: Foundational support for text, images, audio, and code through a unified token space.
* **Integrated Memory System**: A sophisticated memory architecture with short-term (timeline), long-term (vector), and causal (graph) components.
* **Local-First & Self-Contained**: Runs entirely locally. Includes its own training, evaluation, and API server modules. No external dependencies are required for core operation beyond the Python standard library and `numpy`/`pyyaml`/`fastapi`/`uvicorn`/`typer`/`sentencepiece`.
* **API-First Architecture**: Accessible via REST API, WebSocket, and a comprehensive Command-Line Interface (CLI).

## II. ARCHITECTURE

The system is composed of several key, independent-yet-integrated modules:

* `victor_kernel.py`: A custom `OmegaTensor` library with automatic differentiation. The mathematical soul of the AGI.
* `victor_tokenizer.py`: A `SentencePiece`-based multimodal tokenizer.
* `victor_transformer.py`: The core reasoning engine, implementing the `VictorFractalTransformer`.
* `victor_memory.py`: The mind of the AGI, managing memory and recall.
* `victor_privacy.py`: The conscience of the AGI, enforcing the `bloodline.txt` directives.
* `victor_agi.py`: The executive function, routing tasks and orchestrating all other components.
* `victor_multimodal.py`: Placeholder encoders for non-text data.
* `victor_eval.py`: A built-in suite for self-evaluation and regression testing.
* `victor_trainer.py`: The module for self-improvement and fine-tuning.
* `victor_ui.py`: A unified interface providing a CLI, REST API, and WebSocket server.

## III. USAGE

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. First-time Setup

Before running for the first time, the tokenizer needs to be trained on a sample corpus. A dummy corpus is provided, but you can replace it with your own data in `victor_gpt5/data/dummy_corpus.txt`.

To train the tokenizer, run:

```bash
python -m victor_gpt5.victor_tokenizer
```

### 3. Running the AGI

You can interact with Victor-GPT5 in several ways:

**a) Interactive CLI:**

```bash
python -m victor_gpt5.victor_ui interact
```

**b) API Server:**

```bash
python -m victor_gpt5.victor_ui serve
```

This will start a FastAPI server at `http://127.0.0.1:8000`. You can access the API documentation at `http://127.0.0.1:8000/docs`.

**c) Training:**

To fine-tune the model on a new corpus, run:

```bash
python -m victor_gpt5.victor_ui train <path_to_corpus.txt>
```

**d) Evaluation:**

To run the built-in evaluation suite, run:

```bash
python -m victor_gpt5.victor_ui evaluate
```
