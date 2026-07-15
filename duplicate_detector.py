import os
import hashlib
import csv


folder_path = "test_storage"
duplicate_file = "duplicate_results.csv"

hash_groups = {}


def calculate_hash(file_path):

    sha256 = hashlib.sha256()

    with open(file_path, "rb") as file:

        while True:

            chunk = file.read(1024 * 1024)

            if not chunk:
                break

            sha256.update(chunk)

    return sha256.hexdigest()


for root, folders, files in os.walk(folder_path):

    for file in files:

        file_path = os.path.join(root, file)

        try:

            file_hash = calculate_hash(file_path)

            if file_hash not in hash_groups:
                hash_groups[file_hash] = []

            hash_groups[file_hash].append(file_path)

        except (PermissionError, OSError) as error:

            print("Could not process:", file_path)
            print("Error:", error)


duplicate_records = []

duplicate_group_id = 1


for file_hash, file_paths in hash_groups.items():

    if len(file_paths) > 1:

        print("--------------------------------")
        print("DUPLICATE GROUP:", duplicate_group_id)
        print("HASH:", file_hash)

        for file_path in file_paths:

            print(file_path)

            duplicate_records.append({
                "duplicate_group_id": duplicate_group_id,
                "file_path": file_path,
                "file_hash": file_hash
            })

        duplicate_group_id += 1


with open(
    duplicate_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = [
        "duplicate_group_id",
        "file_path",
        "file_hash"
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(duplicate_records)


print("--------------------------------")
print("DUPLICATE SCAN COMPLETED")
print("Duplicate groups found:", duplicate_group_id - 1)
print("Results saved to:", duplicate_file)