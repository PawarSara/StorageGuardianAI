import csv


input_file = "files_project_features.csv"
output_file = "file_value_results.csv"


def calculate_value_score(row):

    score = 50

    reasons = []


    days_since_modified = int(
        row["days_since_modified"]
    )

    modification_count = int(
        row["modification_count"]
    )

    recent_activity_count = int(
        row["recent_activity_count"]
    )

    is_duplicate = int(
        row["is_duplicate"]
    )

    duplicate_count = int(
        row["duplicate_count"]
    )

    is_active_project = int(
        row["is_active_project"]
    )

    folder_type = row["folder_type"]

    size_bytes = int(
        row["size_bytes"]
    )


    # --------------------------------
    # RECENCY
    # --------------------------------

    if days_since_modified <= 7:

        score += 20

        reasons.append(
            "recently_modified"
        )


    elif days_since_modified <= 30:

        score += 10

        reasons.append(
            "modified_within_30_days"
        )


    elif days_since_modified >= 365:

        score -= 20

        reasons.append(
            "not_modified_for_over_1_year"
        )


    elif days_since_modified >= 180:

        score -= 10

        reasons.append(
            "long_time_since_modification"
        )


    # --------------------------------
    # MODIFICATION ACTIVITY
    # --------------------------------

    if modification_count >= 5:

        score += 15

        reasons.append(
            "high_modification_activity"
        )


    elif modification_count >= 1:

        score += 5

        reasons.append(
            "some_modification_activity"
        )


    # --------------------------------
    # RECENT ACTIVITY
    # --------------------------------

    if recent_activity_count >= 5:

        score += 15

        reasons.append(
            "high_recent_activity"
        )


    elif recent_activity_count >= 1:

        score += 5

        reasons.append(
            "some_recent_activity"
        )


    # --------------------------------
    # ACTIVE PROJECT RELATIONSHIP
    # --------------------------------

    if is_active_project == 1:

        score += 25

        reasons.append(
            "active_project_relationship"
        )


    # --------------------------------
    # DUPLICATE EVIDENCE
    # --------------------------------

    if is_duplicate == 1:

        score -= 15

        reasons.append(
            "exact_duplicate_exists"
        )


    if duplicate_count >= 3:

        score -= 5

        reasons.append(
            "multiple_duplicate_copies"
        )


    # --------------------------------
    # FOLDER CONTEXT
    # --------------------------------

    if folder_type == "DOCUMENTS":

        score += 5

        reasons.append(
            "document_folder_context"
        )


    elif folder_type == "DOWNLOADS":

        score -= 5

        reasons.append(
            "downloads_folder_context"
        )


    # --------------------------------
    # STORAGE COST
    # --------------------------------

    size_mb = size_bytes / (
        1024 * 1024
    )


    if size_mb >= 10:

        score -= 10

        reasons.append(
            "high_local_storage_cost"
        )


    # --------------------------------
    # SCORE LIMIT
    # --------------------------------

    score = max(
        0,
        min(100, score)
    )


    # --------------------------------
    # VALUE CLASS
    # --------------------------------

    if score >= 80:

        value_class = "VERY_HIGH"


    elif score >= 60:

        value_class = "HIGH"


    elif score >= 40:

        value_class = "MEDIUM"


    else:

        value_class = "LOW"


    return score, value_class, reasons


value_records = []


with open(
    input_file,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)


    for row in reader:

        value_score, value_class, reasons = (
            calculate_value_score(row)
        )


        row["value_score"] = value_score

        row["value_class"] = value_class

        row["value_reasons"] = "|".join(
            reasons
        )


        value_records.append(row)


with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = list(
        value_records[0].keys()
    )


    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )


    writer.writeheader()

    writer.writerows(
        value_records
    )


for record in value_records:

    print("--------------------------------")

    print(
        "File:",
        record["file_path"]
    )

    print(
        "Value Score:",
        record["value_score"]
    )

    print(
        "Value Class:",
        record["value_class"]
    )

    print(
        "Reasons:",
        record["value_reasons"]
    )


print("--------------------------------")
print("FILE VALUE ANALYSIS COMPLETED")
print("Results saved to:", output_file)