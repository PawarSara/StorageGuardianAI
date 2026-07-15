import os
from datetime import datetime, timedelta


TEST_FILES = {
    "test_storage/Downloads/dataset.csv": {
        "days_old": 300,
        "size_mb": 2
    },

    "test_storage/Downloads/dataset_copy.csv": {
        "days_old": 250,
        "size_mb": 2
    },

    "test_storage/Documents/resume_old.pdf": {
        "days_old": 180,
        "size_mb": 1
    },

    "test_storage/Videos/old_movie.mp4": {
        "days_old": 500,
        "size_mb": 20
    },

    "test_storage/Desktop/old_project.zip": {
        "days_old": 240,
        "size_mb": 10
    },

    "test_storage/ML_Project/app.py": {
        "days_old": 2,
        "size_mb": 1
    },

    "test_storage/ML_Project/dataset.csv": {
        "days_old": 3,
        "size_mb": 2
    },

    "test_storage/ML_Project/model.ipynb": {
        "days_old": 0,
        "size_mb": 1
    },

    "test_storage/ML_Project/College/final_report.docx": {
        "days_old": 5,
        "size_mb": 1
    },

    "test_storage/ML_Project/College/notes.txt": {
        "days_old": 7,
        "size_mb": 1
    }
}


for file_path, settings in TEST_FILES.items():

    if not os.path.exists(file_path):

        print("File not found:", file_path)
        continue


    size_bytes = settings["size_mb"] * 1024 * 1024


    with open(file_path, "r+b") as file:

        file.truncate(size_bytes)


    modified_date = (
        datetime.now()
        - timedelta(days=settings["days_old"])
    )


    timestamp = modified_date.timestamp()


    os.utime(
        file_path,
        (timestamp, timestamp)
    )


    print("--------------------------------")
    print("File:", file_path)
    print("Size:", settings["size_mb"], "MB")
    print(
        "Days Since Modified:",
        settings["days_old"]
    )


print("--------------------------------")
print("TEST DATA PREPARATION COMPLETED")