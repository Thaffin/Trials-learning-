import json
import re
from pathlib import Path
 
# Set input and output file paths
input_file = Path("crpc_qa.json")
output_file = Path("crpc_qa_cleaned.json")
 
# Read the original JSON file
with input_file.open("r", encoding="utf-8-sig") as file:
    data = json.load(file)
 
# Check that the file contains a list
if not isinstance(data, list):
    raise ValueError("Expected a JSON list of question-answer records")
 
# Prepare result lists and duplicate tracking
cleaned_data = []
seen_pairs = set()
review_items = []
 
# Process each record
for index, item in enumerate(data):
    if not isinstance(item, dict):
        review_items.append({"record": index, "reason": "Not a JSON object"})
        continue
 
    question = item.get("question", "")
    answer = item.get("answer", "")
 
    if not isinstance(question, str) or not isinstance(answer, str):
        review_items.append({"record": index, "reason": "Question/answer is not text"})
        continue
 
    # Clean extra spaces and line breaks
    question = re.sub(r"\\s+", " ", question).strip()
    answer = re.sub(r"\\s+", " ", answer).strip()
 
    #  Flag missing questions or answers
    if not question or not answer:
        review_items.append({"record": index, "reason": "Missing question or answer"})
        continue
 
    # Skip exact duplicate Q&A pairs
    pair = (question.casefold(), answer.casefold())
    if pair in seen_pairs:
        review_items.append({"record": index, "reason": "Exact duplicate pair"})
        continue
 
    seen_pairs.add(pair)
    cleaned_data.append({"question": question, "answer": answer})
 
# Save cleaned data separately
with output_file.open("w", encoding="utf-8") as file:
    json.dump(cleaned_data, file, ensure_ascii=False, indent=2)
 
# 10. Save records that need review
report_file = Path("cleaning_report.json")
with report_file.open("w", encoding="utf-8") as file:
    json.dump(review_items, file, ensure_ascii=False, indent=2)
 
# 11. Display the results
print("Original records:", len(data))
print("Cleaned records:", len(cleaned_data))
print("Records flagged for review:", len(review_items))
print("Saved:", output_file)
print("Review report:", report_file)
