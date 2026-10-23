import json
import re
import logging
from pathlib import Path

# File paths
INPUT_FILE = Path("crpc_qa.json")
OUTPUT_FILE = Path("crpc_qa_cleaned.json")
REPORT_FILE = Path("cleaning_report.json")
LOG_FILE = Path("cleaning.log")


def clean_text(text):
    """Remove extra whitespace."""
    if not isinstance(text, str):
        return ""

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def validate_record(record, index, review_items):
    """Check and clean each question-answer record."""
    if not isinstance(record, dict):
        review_items.append({
            "record": index,
            "reason": "Invalid record format"
        })
        return None

    question = record.get("question", "")
    answer = record.get("answer", "")

    if not isinstance(question, str) or not isinstance(answer, str):
        review_items.append({
            "record": index,
            "reason": "Question or answer is not text"
        })
        return None

    question = clean_text(question)
    answer = clean_text(answer)

    if not question or not answer:
        review_items.append({
            "record": index,
            "reason": "Missing question or answer"
        })
        return None

    return {"question": question, "answer": answer}


def remove_duplicates(records, review_items):
    """Remove exact duplicate Q&A pairs."""
    unique_records = []
    seen = set()

    for index, record in enumerate(records):
        pair = (
            record["question"].casefold(),
            record["answer"].casefold()
        )

        if pair in seen:
            review_items.append({
                "record": index,
                "reason": "Duplicate Q&A pair"
            })
            continue

        seen.add(pair)
        unique_records.append(record)

    return unique_records


def clean_records(data):
    """Run validation, cleaning, and duplicate removal."""
    valid_records = []
    review_items = []

    for index, record in enumerate(data):
        cleaned = validate_record(record, index, review_items)

        if cleaned is not None:
            valid_records.append(cleaned)

    cleaned_records = remove_duplicates(
        valid_records, review_items
    )

    return cleaned_records, review_items


def save_json(path, data):
    """Save data to a JSON file."""
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)


def main():
    # Create the log file
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        encoding="utf-8,
    )

    try:
        # Read input file
        with INPUT_FILE.open("r", encoding="utf-8-sig") as file:
            data = json.load(file)

        if not isinstance(data, list):
            raise ValueError("JSON must contain a list of records")

        # Call cleaning functions
        cleaned_records, review_items = clean_records(data)

        # Save results
        save_json(OUTPUT_FILE, cleaned_records)
        save_json(REPORT_FILE, review_items)

        # Log summary at the end
        logging.info("Cleaning completed successfully")
        logging.info("Original records: %d", len(data))
        logging.info("Cleaned records: %d", len(cleaned_records))
        logging.info("Records requiring review: %d", len(review_items))

    except FileNotFoundError:
        logging.exception("Input file not found")

    except json.JSONDecodeError:
        logging.exception("Invalid JSON format")

    except ValueError:
        logging.exception("Invalid JSON structure")

    except OSError:
        logging.exception("File reading or writing error")

    except Exception:
        logging.exception("Unexpected error occurred")


if __name__ == "__main__":
    main()
