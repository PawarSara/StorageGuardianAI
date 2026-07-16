import os
import csv
import hashlib
from collections import defaultdict


# --------------------------------------------------
# INPUT / OUTPUT FILES
# --------------------------------------------------

metadata_file = "files_metadata.csv"
sample_file = "sampled_files.csv"
duplicate_file = "duplicate_results.csv"


# --------------------------------------------------
# HASH CACHE
# --------------------------------------------------

hash_cache = {}


# --------------------------------------------------
# PATH NORMALIZATION
# --------------------------------------------------

def normalize_path(file_path):

    return os.path.normcase(
        os.path.abspath(file_path)
    )


# --------------------------------------------------
# HASH FUNCTION
# --------------------------------------------------

def calculate_hash(file_path):

    normalized_path = normalize_path(
        file_path
    )


    if normalized_path in hash_cache:

        return hash_cache[
            normalized_path
        ]


    sha256 = hashlib.sha256()


    with open(
        normalized_path,
        "rb"
    ) as file:

        while True:

            chunk = file.read(
                1024 * 1024
            )


            if not chunk:
                break


            sha256.update(
                chunk
            )


    file_hash = sha256.hexdigest()


    hash_cache[
        normalized_path
    ] = file_hash


    return file_hash


# --------------------------------------------------
# LOAD FULL FILE METADATA
# --------------------------------------------------

size_groups = defaultdict(list)

total_metadata_files = 0


with open(
    metadata_file,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(
        file
    )


    for row in reader:

        try:

            file_path = normalize_path(
                row["file_path"]
            )

            file_size = int(
                row["size_bytes"]
            )


            size_groups[
                file_size
            ].append(
                file_path
            )


            total_metadata_files += 1


        except (
            ValueError,
            KeyError
        ):

            continue


print("--------------------------------")

print(
    "FULL METADATA FILES LOADED:",
    total_metadata_files
)


# --------------------------------------------------
# LOAD SAMPLED FILES
# --------------------------------------------------

sampled_files = []


with open(
    sample_file,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(
        file
    )


    for row in reader:

        try:

            sampled_files.append({
                "file_path": normalize_path(
                    row["file_path"]
                ),
                "size_bytes": int(
                    row["size_bytes"]
                )
            })


        except (
            ValueError,
            KeyError
        ):

            continue


print(
    "SAMPLED FILES LOADED:",
    len(sampled_files)
)


# --------------------------------------------------
# CHECK SAMPLED FILES FOR EXACT DUPLICATES
# --------------------------------------------------

duplicate_records = []

duplicate_group_lookup = {}

next_duplicate_group_id = 1

processed_samples = 0
skipped_files = 0


for sampled_record in sampled_files:

    sampled_path = sampled_record[
        "file_path"
    ]

    sampled_size = sampled_record[
        "size_bytes"
    ]


    try:

        if not os.path.isfile(
            sampled_path
        ):

            skipped_files += 1

            continue


        candidate_paths = size_groups.get(
            sampled_size,
            []
        )


        candidate_paths = [
            candidate_path
            for candidate_path in candidate_paths
            if (
                candidate_path != sampled_path
                and os.path.isfile(
                    candidate_path
                )
            )
        ]


        if not candidate_paths:

            processed_samples += 1

            continue


        sampled_hash = calculate_hash(
            sampled_path
        )


        matching_paths = []


        for candidate_path in candidate_paths:

            try:

                candidate_hash = calculate_hash(
                    candidate_path
                )


                if candidate_hash == sampled_hash:

                    matching_paths.append(
                        candidate_path
                    )


            except (
                PermissionError,
                OSError
            ):

                skipped_files += 1


        if matching_paths:

            if sampled_hash not in duplicate_group_lookup:

                duplicate_group_lookup[
                    sampled_hash
                ] = next_duplicate_group_id

                next_duplicate_group_id += 1


            duplicate_group_id = (
                duplicate_group_lookup[
                    sampled_hash
                ]
            )


            duplicate_records.append({
                "duplicate_group_id": duplicate_group_id,
                "file_path": sampled_path,
                "file_hash": sampled_hash
            })


            for matching_path in matching_paths:

                duplicate_records.append({
                    "duplicate_group_id": duplicate_group_id,
                    "file_path": matching_path,
                    "file_hash": sampled_hash
                })


        processed_samples += 1


        if processed_samples % 50 == 0:

            print(
                "Sampled files processed:",
                processed_samples,
                "/",
                len(sampled_files)
            )


    except (
        PermissionError,
        OSError
    ):

        skipped_files += 1


# --------------------------------------------------
# REMOVE DUPLICATE OUTPUT ROWS
# --------------------------------------------------

unique_duplicate_records = {}

for record in duplicate_records:

    record_key = (
        record["duplicate_group_id"],
        record["file_path"],
        record["file_hash"]
    )


    unique_duplicate_records[
        record_key
    ] = record


duplicate_records = list(
    unique_duplicate_records.values()
)


# --------------------------------------------------
# SAVE DUPLICATE RESULTS
# --------------------------------------------------

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


    writer.writerows(
        duplicate_records
    )


# --------------------------------------------------
# FINAL SUMMARY
# --------------------------------------------------

print("--------------------------------")

print(
    "SAMPLE-AWARE DUPLICATE SCAN COMPLETED"
)

print(
    "Sampled files processed:",
    processed_samples
)

print(
    "Unique files hashed:",
    len(hash_cache)
)

print(
    "Files skipped:",
    skipped_files
)

print(
    "Duplicate groups found:",
    len(duplicate_group_lookup)
)

print(
    "Duplicate file records:",
    len(duplicate_records)
)

print(
    "Results saved to:",
    duplicate_file
)