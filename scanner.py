import os
import csv
import uuid
from pathlib import Path
from datetime import datetime

folder_path = "test_storage"
csv_file = "files_metadata.csv"

file_records = []

for root, folders, files in os.walk(folder_path):

    for file in files:

        file_path = os.path.join(root, file)

        try:
            file_size = os.path.getsize(file_path)

            extension = Path(file_path).suffix

            created_time = os.path.getctime(file_path)
            modified_time = os.path.getmtime(file_path)
            accessed_time = os.path.getatime(file_path)

            created_date = datetime.fromtimestamp(created_time)
            modified_date = datetime.fromtimestamp(modified_time)
            accessed_date = datetime.fromtimestamp(accessed_time)

            file_id = str(
                uuid.uuid5(
                    uuid.NAMESPACE_URL,
                    os.path.abspath(file_path)
                )
            )

            file_record = {
                "file_id": file_id,
                "file_name": file,
                "file_path": file_path,
                "size_bytes": file_size,
                "extension": extension,
                "created": created_date,
                "modified": modified_date,
                "last_accessed": accessed_date
            }

            file_records.append(file_record)

        except (PermissionError, OSError) as error:
            print("Could not scan:", file_path)
            print("Error:", error)


with open(csv_file, "w", newline="", encoding="utf-8") as file:

    fieldnames = [
        "file_id",
        "file_name",
        "file_path",
        "size_bytes",
        "extension",
        "created",
        "modified",
        "last_accessed"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    writer.writeheader()
    writer.writerows(file_records)


print("--------------------------------")
print("SCAN COMPLETED")
print("Total files scanned:", len(file_records))
print("Metadata saved to:", csv_file)