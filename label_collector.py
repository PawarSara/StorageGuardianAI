import csv
import os


input_file = "files_project_features.csv"
output_file = "ml_training_dataset.csv"


FEATURE_COLUMNS = [
    "size_bytes",
    "extension",
    "file_age_days",
    "days_since_modified",
    "modification_count",
    "recent_activity_count",
    "is_duplicate",
    "duplicate_count",
    "folder_type",
    "project_score",
    "recent_project_files",
    "is_active_project"
]


OUTPUT_COLUMNS = (
    ["file_id"]
    + FEATURE_COLUMNS
    + ["local_relevance_label"]
)


def load_existing_labels():

    existing_labels = {}

    if not os.path.exists(output_file):

        return existing_labels


    with open(
        output_file,
        "r",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)


        for row in reader:

            existing_labels[
                row["file_id"]
            ] = row


    return existing_labels


def save_dataset(records):

    with open(
        output_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=OUTPUT_COLUMNS
        )


        writer.writeheader()

        writer.writerows(records)


existing_labels = load_existing_labels()

training_records = list(
    existing_labels.values()
)


with open(
    input_file,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)


    for row in reader:

        file_id = row["file_id"]


        if file_id in existing_labels:

            continue


        print("\n--------------------------------")

        print(
            "File:",
            row["file_name"]
        )

        print(
            "Path:",
            row["file_path"]
        )

        print(
            "Extension:",
            row["extension"]
        )

        print(
            "Days Since Modified:",
            row["days_since_modified"]
        )

        print(
            "Recent Activity:",
            row["recent_activity_count"]
        )

        print(
            "Duplicate:",
            row["is_duplicate"]
        )

        print(
            "Folder Type:",
            row["folder_type"]
        )

        print(
            "Active Project:",
            row["is_active_project"]
        )


        print("\nLOCAL RELEVANCE")

        print(
            "1 → HIGH"
        )

        print(
            "2 → MEDIUM"
        )

        print(
            "3 → LOW"
        )

        print(
            "Q → Stop labelling"
        )


        while True:

            choice = input(
                "\nYour label: "
            ).strip().lower()


            if choice == "1":

                label = "HIGH"

                break


            elif choice == "2":

                label = "MEDIUM"

                break


            elif choice == "3":

                label = "LOW"

                break


            elif choice == "q":

                print(
                    "\nLabelling stopped."
                )

                save_dataset(
                    training_records
                )

                print(
                    "Current dataset saved to:",
                    output_file
                )

                exit()


            else:

                print(
                    "Invalid choice."
                )

                print(
                    "Enter 1, 2, 3, or Q."
                )


        training_record = {
            "file_id": file_id
        }


        for feature in FEATURE_COLUMNS:

            training_record[feature] = row[
                feature
            ]


        training_record[
            "local_relevance_label"
        ] = label


        training_records.append(
            training_record
        )


        existing_labels[
            file_id
        ] = training_record


        save_dataset(
            training_records
        )


        print(
            "Label saved:",
            label
        )


print("\n--------------------------------")

print(
    "ALL AVAILABLE FILES LABELLED"
)

print(
    "Training samples:",
    len(training_records)
)

print(
    "Dataset saved to:",
    output_file
)