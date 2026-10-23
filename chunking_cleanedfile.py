        )

    chunks = []
    step = chunk_size - overlap

    for start in range(0, len(words), step):
        chunk_words = words[start:start + chunk_size]
        if not chunk_words:
            break

        chunks.append(" ".join(chunk_words))

        if start + chunk_size >= len(words):
            break

    return chunks


def chunk_record(record, review_items, index):
    """Keep short Q&A records whole; split long answers."""
    if not isinstance(record, dict):
        review_items.append({
            "record": index,
            "reason": "Invalid record format"
        })
        return []

    question = record.get("question")
    answer = record.get("answer")
    source = record.get("source", "unknown")

    if not isinstance(question, str) or not isinstance(answer, str):
        review_items.append({
            "record": index,
            "reason": "Question or answer is not text"
        })
        return []

    question = question.strip()
    answer = answer.strip()

    if not question or not answer:
        review_items.append({
            "record": index,
            "reason": "Missing question or answer"
        })
        return []

    answer_chunks = split_into_chunks(answer)
    output_records = []

    for chunk_index, answer_chunk in enumerate(answer_chunks):
        output_records.append({
            "source": source,
            "question": question,
            "answer": answer_chunk,
            "chunk_id": f"{source}_{index}_{chunk_index}"
        })

    return output_records


def chunk_records(records):
    """Chunk all records and collect invalid records for review."""
    all_chunks = []
    review_items = []

    for index, record in enumerate(records):
        all_chunks.extend(chunk_record(record, review_items, index))

    return all_chunks, review_items


def save_json(path, data):
    """Save data as UTF-8 JSON."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    LOG_DIR.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    try:
        with INPUT_FILE.open("r", encoding="utf-8-sig") as file:
            records = json.load(file)

        if not isinstance(records, list):
            raise ValueError("Input JSON must contain a list of records")

        chunks, review_items = chunk_records(records)
        save_json(OUTPUT_FILE, chunks)

        if review_items:
            review_file = OUTPUT_DIR / "chunking_review.json"
            save_json(review_file, review_items)

        logging.info("Chunking completed successfully")
        logging.info("Input records: %d", len(records))
        logging.info("Output chunks: %d", len(chunks))
        logging.info("Records flagged for review: %d", len(review_items))
        logging.info("Chunk output: %s", OUTPUT_FILE)

    except FileNotFoundError:
        logging.exception("Input JSON file was not found")
    except json.JSONDecodeError:
        logging.exception("Input file contains invalid JSON")
    except ValueError:
        logging.exception("Invalid input JSON structure or chunk settings")
    except OSError:
        logging.exception("File reading or writing error")
    except Exception:
        logging.exception("Unexpected error occurred")


if __name__ == "__main__":
    main()
