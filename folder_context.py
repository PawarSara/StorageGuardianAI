import os
import csv


input_file = "files_features.csv"
output_file = "files_context_features.csv"


KNOWN_FOLDER_TYPES = {
    "downloads": "DOWNLOADS",
    "documents": "DOCUMENTS",
    "videos": "VIDEOS",
    "desktop": "DESKTOP",
    "pictures": "PICTURES",
    "music": "MUSIC"
}


PROJECT_EXTENSIONS = {
    ".py",
    ".ipynb",
    ".js",
    ".jsx",
    ".ts",
    ".tsx",
    ".java",
    ".cpp",
    ".c"
}


PROJECT_MARKER_FILES = {
    "package.json",
    "requirements.txt",
    "pom.xml",
    "build.gradle"
}


def detect_folder_type(file_path):

    normalized_path = os.path.normpath(file_path)

    path_parts = normalized_path.split(os.sep)

    lower_parts = [
        part.lower()
        for part in path_parts
    ]


    for folder_name, folder_type in KNOWN_FOLDER_TYPES.items():

        if folder_name in lower_parts:

            return folder_type


    parent_folder = os.path.dirname(
        normalized_path
    )


    try:

        items = os.listdir(parent_folder)

        technical_file_count = 0
        marker_file_found = False


        for item in items:

            item_path = os.path.join(
                parent_folder,
                item
            )


            if os.path.isfile(item_path):

                extension = os.path.splitext(
                    item
                )[1].lower()


                if extension in PROJECT_EXTENSIONS:

                    technical_file_count += 1


                if item.lower() in PROJECT_MARKER_FILES:

                    marker_file_found = True


        if (
            marker_file_found
            or technical_file_count >= 2
        ):

            return "PROJECT_LIKE"


    except (PermissionError, OSError):

        pass


    return "GENERAL"


context_records = []


with open(
    input_file,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)


    for row in reader:

        folder_type = detect_folder_type(
            row["file_path"]
        )


        row["folder_type"] = folder_type


        context_records.append(row)


with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = list(
        context_records[0].keys()
    )


    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )


    writer.writeheader()

    writer.writerows(
        context_records
    )


for record in context_records:

    print("--------------------------------")
    print("File:", record["file_path"])
    print(
        "Folder Type:",
        record["folder_type"]
    )


print("--------------------------------")
print("FOLDER CONTEXT DETECTION COMPLETED")
print("Results saved to:", output_file)