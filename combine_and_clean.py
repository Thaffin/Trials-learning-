
import json
import re
import logging
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

INPUT_DIR = ROOT_DIR / "data" / "raw"
OUTPUT_DIR = ROOT_DIR / "data" / "raw" / "cleaned"
REPORT_DIR = ROOT_DIR / "reports"
LOG_DIR = ROOT_DIR / "logs"

OUTPUT_FILE = OUTPUT_DIR / "indian_law_combined_cleaned.json"
REPORT_FILE = REPORT_DIR / "cleaning_report.json"
LOG_FILE = LOG_DIR / "lawbot.log"

INPUT_FILES = [
    "constitution_qa.json",
    "ipc_qa.json",
    "crpc_qa.json"
]


def clean_text(text):
    """Remove unnecessary whitespace."""
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def clean_record(record, source, index, review_items):
    """Validate and clean one Q&A record."""
    if not isinstance(record, dict):
        review_items.append({
            "source": source,
            "record": index,
            "reason": "Invalid record format"
        })
        return None

    question = record.get("question")
    answer = record.get("answer")

    if not isinstance(question, str) or not isinstance(answer, str):
        review_items.append({
            "source": source,
            "record": index,
            "reason": "Question or answer is not text"
        })
        return None

    question = clean_text(question)
    answer = clean_text(answer)

    if not question or not answer:
        review_items.append({
            "source": source,
            "record": index,
            "reason": "Missing question or answer"
        })
        return None

    return {
        "source": source,
        "question": question,
        "answer": answer
    }


def combine_files():
    combined_records = []
    review_items = []

    for filename in INPUT_FILES:
        file_path = INPUT_DIR / filename

        with file_path.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError(
                f"{filename} must contain a JSON list"
            )

        source = Path(filename).stem.replace("_qa", "")

        for index, record in enumerate(data):
            cleaned = clean_record(
                record, source, index, review_items
            )

            if cleaned is not None:
                combined_records.append(cleaned)

    return combined_records, review_items


def remove_duplicates(records, review_items):
    """Remove exact duplicate Q&A pairs."""
    unique_records = []
    seen = set()

    for record in records:
        key = (
            record["question"].casefold(),
            record["answer"].casefold()
        )

        if key in seen:
            review_items.append({
                "source": record["source"],
                "question": record["question"],
                "reason": "Duplicate Q&A pair"
            })
            continue

        seen.add(key)
        unique_records.append(record)

    return unique_records


def save_json(path, data):
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def main():
    for folder in [OUTPUT_DIR, REPORT_DIR, LOG_DIR]:
        folder.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8"
    )

    try:
        records, review_items = combine_files()
        original_valid_count = len(records)

        cleaned_records = remove_duplicates(
            records, review_items
        )

        save_json(OUTPUT_FILE, cleaned_records)
        save_json(REPORT_FILE, review_items)

        logging.info("Combination and cleaning completed")
        logging.info("Valid records before deduplication: %d",
                     original_valid_count)
        logging.info("Final records: %d", len(cleaned_records))
        logging.info("Records flagged for review: %d",
                     len(review_items))

    except FileNotFoundError:
        logging.exception("An input file was not found")

    except json.JSONDecodeError:
        logging.exception("An input file contains invalid JSON")

    except ValueError:
        logging.exception("Invalid JSON structure")

    except OSError:
        logging.exception("File reading or writing error")

    except Exception:
        logging.exception("Unexpected error occurred")


if __name__ == "__main__":
    main()
