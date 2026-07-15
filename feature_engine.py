import os
import csv
from collections import defaultdict
from datetime import datetime


metadata_file = "files_metadata.csv"
activity_file = "file_activity.csv"
duplicate_file = "duplicate_results.csv"

output_file = "files_features.csv"


# --------------------------------
# LOAD ACTIVITY INFORMATION
# --------------------------------

modification_counts = defaultdict(int)
recent_activity_counts = defaultdict(int)


if os.path.exists(activity_file):

    with open(
        activity_file,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            file_path = os.path.normpath(
                row["file_path"]
            )

            event_type = row["event_type"]

            event_time = datetime.fromisoformat(
                row["event_time"]
            )


            if event_type == "MODIFIED":

                modification_counts[file_path] += 1


            days_since_event = (
                datetime.now() - event_time
            ).days


            if days_since_event <= 30:

                recent_activity_counts[file_path] += 1


# --------------------------------
# LOAD DUPLICATE INFORMATION
# --------------------------------

duplicate_groups = defaultdict(list)


if os.path.exists(duplicate_file):

    with open(
        duplicate_file,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            group_id = row["duplicate_group_id"]

            file_path = os.path.normpath(
                row["file_path"]
            )

            duplicate_groups[group_id].append(
                file_path
            )


duplicate_info = {}


for group_id, file_paths in duplicate_groups.items():

    duplicate_count = len(file_paths)

    for file_path in file_paths:

        duplicate_info[file_path] = {
            "is_duplicate": 1,
            "duplicate_count": duplicate_count,
            "duplicate_group_id": group_id
        }


# --------------------------------
# BUILD FILE FEATURES
# --------------------------------

feature_records = []


with open(
    metadata_file,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)


    for row in reader:

        file_path = os.path.normpath(
            row["file_path"]
        )


        created_date = datetime.fromisoformat(
            row["created"]
        )

        modified_date = datetime.fromisoformat(
            row["modified"]
        )


        file_age_days = (
            datetime.now() - created_date
        ).days


        days_since_modified = (
            datetime.now() - modified_date
        ).days


        duplicate_data = duplicate_info.get(
            file_path,
            {
                "is_duplicate": 0,
                "duplicate_count": 0,
                "duplicate_group_id": ""
            }
        )


        feature_record = {

            "file_id": row["file_id"],

            "file_name": row["file_name"],

            "file_path": file_path,

            "size_bytes": int(
                row["size_bytes"]
            ),

            "extension": row["extension"],

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


# --------------------------------
# SAVE FEATURES
# --------------------------------

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


print("--------------------------------")
print("FEATURE ENGINE COMPLETED")
print("Total files:", len(feature_records))
print("Features saved to:", output_file)