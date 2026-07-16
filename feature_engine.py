import os
import csv
from collections import defaultdict
from datetime import datetime


# --------------------------------------------------
# INPUT / OUTPUT FILES
# --------------------------------------------------

sample_file = "sampled_files.csv"
activity_file = "file_activity.csv"
duplicate_file = "duplicate_results.csv"

output_file = "files_features.csv"


# --------------------------------------------------
# PATH NORMALIZATION
# --------------------------------------------------

def normalize_path(file_path):

    return os.path.normcase(
        os.path.abspath(file_path)
    )


# --------------------------------------------------
# CURRENT FEATURE EXTRACTION TIME
# --------------------------------------------------

current_time = datetime.now()


# --------------------------------------------------
# LOAD ACTIVITY INFORMATION
# --------------------------------------------------

modification_counts = defaultdict(int)

recent_activity_counts = defaultdict(int)

activity_rows_loaded = 0


if os.path.exists(activity_file):

    with open(
        activity_file,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)


        for row in reader:

            try:

                file_path = normalize_path(
                    row["file_path"]
                )


                event_type = row["event_type"]


                event_time = datetime.fromisoformat(
                    row["event_time"]
                )


                # ----------------------------------
                # COUNT OBSERVED MODIFICATION EVENTS
                # ----------------------------------

                if event_type == "MODIFIED":

                    modification_counts[
                        file_path
                    ] += 1


                # ----------------------------------
                # COUNT RECENT OBSERVED ACTIVITY
                # ----------------------------------

                days_since_event = (
                    current_time - event_time
                ).days


                if (
                    0 <= days_since_event <= 30
                ):

                    recent_activity_counts[
                        file_path
                    ] += 1


                activity_rows_loaded += 1


            except (
                KeyError,
                ValueError
            ):

                continue


# --------------------------------------------------
# LOAD DUPLICATE INFORMATION
# --------------------------------------------------

duplicate_groups = defaultdict(list)

duplicate_rows_loaded = 0


if os.path.exists(duplicate_file):

    with open(
        duplicate_file,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)


        for row in reader:

            try:

                group_id = row[
                    "duplicate_group_id"
                ]


                file_path = normalize_path(
                    row["file_path"]
                )


                duplicate_groups[
                    group_id
                ].append(
                    file_path
                )


                duplicate_rows_loaded += 1


            except KeyError:

                continue


# --------------------------------------------------
# BUILD DUPLICATE LOOKUP
# --------------------------------------------------

duplicate_info = {}


for group_id, file_paths in duplicate_groups.items():

    unique_file_paths = list(
        dict.fromkeys(
            file_paths
        )
    )


    duplicate_count = len(
        unique_file_paths
    )


    for file_path in unique_file_paths:

        duplicate_info[
            file_path
        ] = {
            "is_duplicate": 1,
            "duplicate_count": duplicate_count,
            "duplicate_group_id": group_id
        }


# --------------------------------------------------
# BUILD FILE FEATURES
# --------------------------------------------------

feature_records = []

invalid_sample_rows = 0


with open(
    sample_file,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)


    for row in reader:

        try:

            file_path = normalize_path(
                row["file_path"]
            )


            created_date = datetime.fromisoformat(
                row["created"]
            )


            modified_date = datetime.fromisoformat(
                row["modified"]
            )


            # --------------------------------------
            # FILE AGE
            # --------------------------------------

            file_age_days = (
                current_time - created_date
            ).days


            file_age_days = max(
                file_age_days,
                0
            )


            # --------------------------------------
            # DAYS SINCE MODIFIED
            # --------------------------------------

            days_since_modified = (
                current_time - modified_date
            ).days


            days_since_modified = max(
                days_since_modified,
                0
            )


            # --------------------------------------
            # DUPLICATE DATA
            # --------------------------------------

            duplicate_data = duplicate_info.get(
                file_path,
                {
                    "is_duplicate": 0,
                    "duplicate_count": 0,
                    "duplicate_group_id": ""
                }
            )


            # --------------------------------------
            # FEATURE RECORD
            # --------------------------------------

            feature_record = {

                "file_id": row[
                    "file_id"
                ],

                "file_name": row[
                    "file_name"
                ],

                "file_path": file_path,

                "size_bytes": int(
                    row["size_bytes"]
                ),

                "extension": row[
                    "extension"
                ],

                "file_age_days": file_age_days,

                "days_since_modified": days_since_modified,

                "modification_count": modification_counts[
                    file_path
                ],

                "recent_activity_count": recent_activity_counts[
                    file_path
                ],

                "is_duplicate": duplicate_data[
                    "is_duplicate"
                ],

                "duplicate_count": duplicate_data[
                    "duplicate_count"
                ],

                "duplicate_group_id": duplicate_data[
                    "duplicate_group_id"
                ]
            }


            feature_records.append(
                feature_record
            )


        except (
            KeyError,
            ValueError
        ):

            invalid_sample_rows += 1


# --------------------------------------------------
# SAVE FEATURES
# --------------------------------------------------

with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = [

        "file_id",
        "file_name",
        "file_path",
        "size_bytes",
        "extension",
        "file_age_days",
        "days_since_modified",
        "modification_count",
        "recent_activity_count",
        "is_duplicate",
        "duplicate_count",
        "duplicate_group_id"

    ]


    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )


    writer.writeheader()


    writer.writerows(
        feature_records
    )


# --------------------------------------------------
# FEATURE SUMMARY
# --------------------------------------------------

files_with_modifications = sum(

    1

    for record in feature_records

    if record["modification_count"] > 0

)


files_with_recent_activity = sum(

    1

    for record in feature_records

    if record["recent_activity_count"] > 0

)


duplicate_files = sum(

    1

    for record in feature_records

    if record["is_duplicate"] == 1

)


# --------------------------------------------------
# FINAL RESULT
# --------------------------------------------------

print("--------------------------------")
print("FEATURE ENGINE COMPLETED")

print(
    "Sampled files processed:",
    len(feature_records)
)

print(
    "Invalid sample rows:",
    invalid_sample_rows
)

print(
    "Activity rows loaded:",
    activity_rows_loaded
)

print(
    "Duplicate rows loaded:",
    duplicate_rows_loaded
)

print(
    "Files with observed modifications:",
    files_with_modifications
)

print(
    "Files with recent observed activity:",
    files_with_recent_activity
)

print(
    "Sampled duplicate files:",
    duplicate_files
)

print(
    "Features saved to:",
    output_file
)