import os
import csv
from collections import defaultdict


duplicate_file = "duplicate_results.csv"
activity_file = "file_activity.csv"
output_file = "duplicate_context_results.csv"


activity_counts = defaultdict(int)


if os.path.exists(activity_file):

    with open(
        activity_file,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            normalized_path = os.path.normpath(
                row["file_path"]
            )

            if row["event_type"] == "MODIFIED":
                activity_counts[normalized_path] += 1


duplicate_groups = defaultdict(list)


with open(
    duplicate_file,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    for row in reader:

        duplicate_groups[
            row["duplicate_group_id"]
        ].append(
            os.path.normpath(row["file_path"])
        )


def calculate_context_score(file_path):

    score = 0

    path_lower = file_path.lower()

    modification_count = activity_counts[file_path]

    score += modification_count * 5

    project_extensions = [
        ".py",
        ".ipynb",
        ".js",
        ".java",
        ".cpp"
    ]

    parent_folder = os.path.dirname(file_path)

    project_files_found = 0

    try:

        for item in os.listdir(parent_folder):

            item_extension = os.path.splitext(item)[1].lower()

            if item_extension in project_extensions:
                project_files_found += 1

    except OSError:
        pass

    score += project_files_found * 10

    if "project" in path_lower:
        score += 20

    return score, modification_count, project_files_found


context_records = []


for group_id, file_paths in duplicate_groups.items():

    scored_files = []

    for file_path in file_paths:

        (
            context_score,
            modification_count,
            project_files_found
        ) = calculate_context_score(file_path)

        scored_files.append({
            "file_path": file_path,
            "context_score": context_score,
            "modification_count": modification_count,
            "project_files_found": project_files_found
        })


    scored_files.sort(
        key=lambda record: record["context_score"],
        reverse=True
    )


    for index, record in enumerate(scored_files):

        if index == 0:
            decision = "KEEP"
        else:
            decision = "REDUNDANT_CANDIDATE"

        record["duplicate_group_id"] = group_id
        record["decision"] = decision

        context_records.append(record)


with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = [
        "duplicate_group_id",
        "file_path",
        "context_score",
        "modification_count",
        "project_files_found",
        "decision"
    ]

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()
    writer.writerows(context_records)


for record in context_records:

    print("--------------------------------")
    print("File:", record["file_path"])
    print("Context Score:", record["context_score"])
    print(
        "Modification Count:",
        record["modification_count"]
    )
    print(
        "Project Files Found:",
        record["project_files_found"]
    )
    print("Decision:", record["decision"])


print("--------------------------------")
print("CONTEXT ANALYSIS COMPLETED")
print("Results saved to:", output_file)