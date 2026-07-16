import os
import csv
from datetime import datetime


input_file = "files_context_features.csv"
output_file = "files_project_features.csv"


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
    "build.gradle",
    "cargo.toml",
    "composer.json"
}


PROJECT_MARKER_FOLDERS = {
    ".git",
    "src",
    "models",
    "routes",
    "templates",
    "static"
}


def calculate_project_score(folder_path):

    technical_file_count = 0
    marker_file_count = 0
    marker_folder_count = 0

    try:

        items = os.listdir(folder_path)

        for item in items:

            item_path = os.path.join(
                folder_path,
                item
            )


            if os.path.isfile(item_path):

                extension = os.path.splitext(
                    item
                )[1].lower()


                if extension in PROJECT_EXTENSIONS:

                    technical_file_count += 1


                if item.lower() in PROJECT_MARKER_FILES:

                    marker_file_count += 1


            elif os.path.isdir(item_path):

                if item.lower() in PROJECT_MARKER_FOLDERS:

                    marker_folder_count += 1


    except (PermissionError, OSError):

        return 0


    project_score = (
        technical_file_count * 10
        + marker_file_count * 30
        + marker_folder_count * 20
    )


    return project_score


def find_project_root(file_path):

    current_folder = os.path.dirname(
        os.path.normpath(file_path)
    )


    while current_folder:

        project_score = calculate_project_score(
            current_folder
        )


        if project_score >= 20:

            return current_folder, project_score


        parent_folder = os.path.dirname(
            current_folder
        )


        if parent_folder == current_folder:

            break


        current_folder = parent_folder


    return "", 0


def check_project_activity(project_root):

    if not project_root:

        return 0, "NOT_PROJECT"


    recent_file_count = 0


    for root, folders, files in os.walk(
        project_root
    ):

        for file in files:

            file_path = os.path.join(
                root,
                file
            )


            try:

                modified_timestamp = os.path.getmtime(
                    file_path
                )


                modified_date = datetime.fromtimestamp(
                    modified_timestamp
                )


                days_since_modified = (
                    datetime.now() - modified_date
                ).days


                if days_since_modified <= 30:

                    recent_file_count += 1


            except (PermissionError, OSError):

                pass


    if recent_file_count > 0:

        project_status = "ACTIVE"

    else:

        project_status = "INACTIVE"


    return recent_file_count, project_status


project_records = []


with open(
    input_file,
    "r",
    encoding="utf-8"
) as file:

    reader = csv.DictReader(file)


    for row in reader:

        project_root, project_score = find_project_root(
            row["file_path"]
        )


        recent_project_files, project_status = (
            check_project_activity(project_root)
        )


        if project_status == "ACTIVE":

            is_active_project = 1

        else:

            is_active_project = 0


        row["project_root"] = project_root

        row["project_score"] = project_score

        row["recent_project_files"] = recent_project_files

        row["project_status"] = project_status

        row["is_active_project"] = is_active_project


        project_records.append(row)


with open(
    output_file,
    "w",
    newline="",
    encoding="utf-8"
) as file:

    fieldnames = list(
        project_records[0].keys()
    )


    writer = csv.DictWriter(
        file,
        fieldnames=fieldnames
    )


    writer.writeheader()

    writer.writerows(
        project_records
    )


for record in project_records:

    print("--------------------------------")
    print("File:", record["file_path"])
    print(
        "Project Root:",
        record["project_root"]
    )
    print(
        "Project Score:",
        record["project_score"]
    )
    print(
        "Recent Project Files:",
        record["recent_project_files"]
    )
    print(
        "Project Status:",
        record["project_status"]
    )
    print(
        "Active Project:",
        record["is_active_project"]
    )


print("--------------------------------")
print("PROJECT RELATIONSHIP DETECTION COMPLETED")
print("Results saved to:", output_file)