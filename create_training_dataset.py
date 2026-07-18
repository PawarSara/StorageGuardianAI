import csv

input_file = "files_project_features.csv"
output_file = "ml_training_dataset.csv"

training_records = []

with open(
    input_file,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        training_record = {

            "size_bytes": row["size_bytes"],

            "extension": row["extension"],

            "file_age_days": row["file_age_days"],

            "days_since_modified": row["days_since_modified"],

            "modification_count": row["modification_count"],

            "recent_activity_count": row["recent_activity_count"],

            "is_duplicate": row["is_duplicate"],

            "duplicate_count": row["duplicate_count"],

            "folder_type": row["folder_type"],

            "importance_label": row["importance_label"]

        }

        training_records.append(training_record)

with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = list(training_records[0].keys())

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(training_records)

print("--------------------------------")
print("TRAINING DATASET CREATED")
print("Total samples:", len(training_records))
print("Saved to:", output_file)