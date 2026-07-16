import os
import csv
import uuid
from pathlib import Path
from datetime import datetime


# --------------------------------------------------
# USER FOLDERS
# --------------------------------------------------

user_home = Path.home()
onedrive_home = user_home / "OneDrive"


def get_personal_folder(folder_name):

    normal_folder = user_home / folder_name
    onedrive_folder = onedrive_home / folder_name

    if normal_folder.exists():
        return normal_folder

    if onedrive_folder.exists():
        return onedrive_folder

    return normal_folder


approved_folders = [
    get_personal_folder("Desktop"),
    get_personal_folder("Documents"),
    get_personal_folder("Downloads"),
    get_personal_folder("Videos"),
    get_personal_folder("Pictures"),
    get_personal_folder("Music"),
]


# --------------------------------------------------
# OUTPUT FILE
# --------------------------------------------------

csv_file = "files_metadata.csv"


# --------------------------------------------------
# CURRENT STORAGE GUARDIAN PROJECT
# --------------------------------------------------

project_folder = os.path.normcase(
    os.path.abspath(os.getcwd())
)


# --------------------------------------------------
# FOLDERS TO SKIP
# --------------------------------------------------

excluded_folder_names = {
    ".git",
    "__pycache__",
    ".ipynb_checkpoints",
    "venv",
    ".venv",
    "env"
}


# --------------------------------------------------
# FILE COLLECTION
# --------------------------------------------------

file_records = []

skipped_files = 0


# --------------------------------------------------
# SCAN APPROVED FOLDERS
# --------------------------------------------------

for folder_path in approved_folders:

    if not folder_path.exists():

        print("Folder not found, skipping:", folder_path)

        continue


    print("Scanning:", folder_path)


    for root, folders, files in os.walk(folder_path):

        normalized_root = os.path.normcase(
            os.path.abspath(root)
        )


        # --------------------------------------------------
        # SKIP STORAGE GUARDIAN PROJECT
        # --------------------------------------------------

        if (
            normalized_root == project_folder
            or normalized_root.startswith(
                project_folder + os.sep
            )
        ):

            folders[:] = []

            continue


        # --------------------------------------------------
        # REMOVE EXCLUDED DIRECTORIES
        # --------------------------------------------------

        folders[:] = [
            folder
            for folder in folders
            if folder.lower() not in excluded_folder_names
        ]


        for file in files:

            file_path = os.path.join(root, file)


            try:

                absolute_file_path = os.path.abspath(file_path)

                file_size = os.path.getsize(
                    absolute_file_path
                )


                # --------------------------------------------------
                # FILE EXTENSION
                # --------------------------------------------------

                extension = os.path.splitext(
                    file
                )[1].lower()


                # --------------------------------------------------
                # FILE TIMESTAMPS
                # --------------------------------------------------

                created_time = os.path.getctime(
                    absolute_file_path
                )

                modified_time = os.path.getmtime(
                    absolute_file_path
                )

                accessed_time = os.path.getatime(
                    absolute_file_path
                )


                created_date = datetime.fromtimestamp(
                    created_time
                )

                modified_date = datetime.fromtimestamp(
                    modified_time
                )

                accessed_date = datetime.fromtimestamp(
                    accessed_time
                )


                # --------------------------------------------------
                # STABLE FILE ID
                # --------------------------------------------------

                file_id = str(
                    uuid.uuid5(
                        uuid.NAMESPACE_URL,
                        absolute_file_path
                    )
                )


                # --------------------------------------------------
                # FILE RECORD
                # --------------------------------------------------

                file_record = {
                    "file_id": file_id,
                    "file_name": file,
                    "file_path": absolute_file_path,
                    "size_bytes": file_size,
                    "extension": extension,
                    "created": created_date,
                    "modified": modified_date,
                    "last_accessed": accessed_date
                }


                file_records.append(file_record)


            except (
                PermissionError,
                OSError,
                ValueError
            ) as error:

                skipped_files += 1

                print(
                    "Could not scan:",
                    file_path
                )

                print(
                    "Error:",
                    error
                )


# --------------------------------------------------
# SAVE METADATA
# --------------------------------------------------

with open(
    csv_file,
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
        "created",
        "modified",
        "last_accessed"
    ]


    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )


    writer.writeheader()

    writer.writerows(
        file_records
    )


# --------------------------------------------------
# FINAL RESULT
# --------------------------------------------------

print("--------------------------------")

print("REAL FILE SCAN COMPLETED")

print(
    "Total files scanned:",
    len(file_records)
)

print(
    "Files skipped:",
    skipped_files
)

print(
    "Metadata saved to:",
    csv_file
)