"""
LAWBOT: Generate embeddings for chunked Indian legal data.

Input:
    data/chunked/indian_law_chunks.json

Output:
    data/embedded/indian_law_embeddings.json

Logs:
    logs/embedding.log
    logs/lawbot.log
"""

import json
import logging
import time
from pathlib import Path

from sentence_transformers import SentenceTransformer


ROOT_DIR = Path(__file__).resolve().parent
INPUT_FILE = ROOT_DIR / "data" / "chunked" / "indian_law_chunks.json"
OUTPUT_DIR = ROOT_DIR / "data" / "embedded"
OUTPUT_FILE = OUTPUT_DIR / "indian_law_embeddings.json"
LOG_DIR = ROOT_DIR / "logs"
LOG_FILE = LOG_DIR / "embedding.log"

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
BATCH_SIZE = 32


def setup_logging():
    """Configure logging to both the terminal and a log file."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(LOG_FILE, encoding="utf-8"),
        ],
        force=True,
    )


def load_chunks():
    """Load chunk records from the input JSON file."""
    try:
        with INPUT_FILE.open("r", encoding="utf-8") as file:
            data = json.load(file)
    except FileNotFoundError:
        logging.error("Input JSON file not found: %s", INPUT_FILE)
        raise
    except json.JSONDecodeError:
        logging.exception("Input file is not valid JSON: %s", INPUT_FILE)
        raise
    except OSError:
        logging.exception("Could not read input file: %s", INPUT_FILE)
        raise

    if isinstance(data, dict):
        if isinstance(data.get("chunks"), list):
            data = data["chunks"]
        elif isinstance(data.get("records"), list):
            data = data["records"]
        else:
            raise ValueError(
                "Input JSON object must contain a list under 'chunks' or 'records'."
            )

    if not isinstance(data, list):
        raise ValueError("Expected the input JSON to contain a list of chunks.")

    return data


def get_text_for_embedding(chunk):
    """Combine question and answer/text into one string for embedding."""
    if not isinstance(chunk, dict):
        raise ValueError("Each chunk record must be a JSON object.")

    question = str(chunk.get("question", "")).strip()
    answer = str(chunk.get("answer", chunk.get("text", ""))).strip()

    if not question and not answer:
        return ""

    return f"Question: {question}\nAnswer: {answer}"


def main():
    total_start = time.perf_counter()

    try:
        setup_logging()
        logging.info("Embedding pipeline started.")
        logging.info("Input file: %s", INPUT_FILE)
        logging.info("Selected model: %s", MODEL_NAME)

        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        chunks = load_chunks()
        if not chunks:
            raise ValueError("The input file contains no chunks.")

        texts = [get_text_for_embedding(chunk) for chunk in chunks]
        empty_indices = [index for index, text in enumerate(texts) if not text]
        if empty_indices:
            raise ValueError(
                "Empty text found at record positions: %s",
                empty_indices[:10],
            )

        logging.info("Loaded %d chunks.", len(chunks))

        model_start = time.perf_counter()
        try:
            model = SentenceTransformer(MODEL_NAME)
        except Exception:
            logging.exception("Failed to load embedding model: %s", MODEL_NAME)
            raise
        model_load_seconds = time.perf_counter() - model_start
        logging.info("Model loaded in %.3f seconds.", model_load_seconds)

        embedding_start = time.perf_counter()
        try:
            vectors = model.encode(
                texts,
                batch_size=BATCH_SIZE,
                show_progress_bar=False,
                normalize_embeddings=True,
                convert_to_numpy=True,
            )
        except Exception:
            logging.exception("Failed while generating embeddings.")
            raise
        embedding_seconds = time.perf_counter() - embedding_start

        output_records = []
        for chunk, vector in zip(chunks, vectors):
            output_records.append({
                "chunk_id": chunk.get("chunk_id"),
                "source": chunk.get("source"),
                "question": chunk.get("question"),
                "text": get_text_for_embedding(chunk),
                "embedding_model": MODEL_NAME,
                "embedding_dimensions": int(len(vector)),
                "embedding": vector.tolist(),
            })

        try:
            with OUTPUT_FILE.open("w", encoding="utf-8") as file:
                json.dump(output_records, file, ensure_ascii=False, indent=2)
        except OSError:
            logging.exception("Could not write embedding output: %s", OUTPUT_FILE)
            raise

        total_seconds = time.perf_counter() - total_start
        first_record = output_records[0]
        first_vector = vectors[0]

        logging.info("Embedding preview chunk_id=%s source=%s",
                     first_record.get("chunk_id"), first_record.get("source"))
        logging.info("Vector dimensions: %d", len(first_vector))
        logging.info("First 10 vector values: %s", first_vector[:10].tolist())
        logging.info("Chunks embedded: %d", len(output_records))
        logging.info("Embedding time for all chunks: %.3f seconds", embedding_seconds)
        logging.info("Average time per chunk: %.6f seconds",
                     embedding_seconds / len(chunks))
        logging.info("Throughput: %.2f chunks/second",
                     len(chunks) / embedding_seconds if embedding_seconds else 0.0)
        logging.info("Total execution time: %.3f seconds", total_seconds)
        logging.info("Embedding output saved to: %s", OUTPUT_FILE)
        logging.info("Embedding pipeline completed successfully.")

    except FileNotFoundError:
        logging.error("Pipeline stopped because a required file was not found.")
    except json.JSONDecodeError:
        logging.error("Pipeline stopped because the input JSON could not be parsed.")
    except (ValueError, OSError):
        logging.exception("Pipeline stopped due to an input, validation, or file error.")
    except Exception:
        logging.exception("Unexpected error occurred in the embedding pipeline.")


if __name__ == "__main__":
    # Configure logging before main so startup errors can also be recorded.
    try:
        setup_logging()
        main()
    except Exception:
        logging.exception("Unable to initialize or run the embedding pipeline.")
