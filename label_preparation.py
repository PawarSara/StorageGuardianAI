import csv


input_file = "files_context_features.csv"
output_file = "final_ml_dataset.csv"


dataset_rows = []


with open(
    input_file,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)

    fieldnames = reader.fieldnames.copy()

    if "importance_label" not in fieldnames:

        fieldnames.append(
            "importance_label"
        )


    for row in reader:

        row["importance_label"] = ""

        dataset_rows.append(row)


with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )

    writer.writeheader()

    writer.writerows(
        dataset_rows
    )


print("--------------------------------")
print("LABEL DATASET CREATED")
print("Total files:", len(dataset_rows))
print("Output file:", output_file)
print("--------------------------------")
print("Open final_ml_dataset.csv")
print("Fill the importance_label column manually.")