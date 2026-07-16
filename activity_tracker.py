import os
import time
import csv
import threading
from pathlib import Path
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


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
# ACTIVITY OUTPUT
# --------------------------------------------------

activity_file = "file_activity.csv"


# --------------------------------------------------
# STORAGE GUARDIAN PROJECT PATH
# --------------------------------------------------

project_folder = os.path.normcase(
    os.path.abspath(os.getcwd())
)


# --------------------------------------------------
# WRITE LOCK
# --------------------------------------------------

activity_lock = threading.Lock()


# --------------------------------------------------
# EVENT DEBOUNCE
# --------------------------------------------------

DEBOUNCE_SECONDS = 2

last_events = {}


# --------------------------------------------------
# PATH NORMALIZATION
# --------------------------------------------------

def normalize_path(file_path):

    return os.path.normcase(
        os.path.abspath(file_path)
    )


# --------------------------------------------------
# CHECK PROJECT FILE
# --------------------------------------------------

def is_project_file(file_path):

    normalized_path = normalize_path(
        file_path
    )

    return (
        normalized_path == project_folder
        or normalized_path.startswith(
            project_folder + os.sep
        )
    )


# --------------------------------------------------
# ACTIVITY HANDLER
# --------------------------------------------------

class FileActivityHandler(FileSystemEventHandler):

    def save_activity(
        self,
        file_path,
        event_type
    ):

        # ------------------------------------------
        # IGNORE STORAGE GUARDIAN PROJECT FILES
        # ------------------------------------------

        if is_project_file(file_path):
            return


        # ------------------------------------------
        # NORMALIZE FILE PATH
        # ------------------------------------------

        normalized_file_path = normalize_path(
            file_path
        )


        # ------------------------------------------
        # CURRENT EVENT TIME
        # ------------------------------------------

        current_time = datetime.now()


        # ------------------------------------------
        # EVENT DEBOUNCE
        # ------------------------------------------

        event_key = (
            normalized_file_path,
            event_type
        )


        last_event_time = last_events.get(
            event_key
        )


        if last_event_time is not None:

            time_difference = (
                current_time - last_event_time
            ).total_seconds()


            if time_difference < DEBOUNCE_SECONDS:
                return


        last_events[event_key] = current_time


        # ------------------------------------------
        # ACTIVITY RECORD
        # ------------------------------------------

        activity_record = {
            "file_path": normalized_file_path,
            "event_type": event_type,
            "event_time": current_time
        }


        # ------------------------------------------
        # SAVE ACTIVITY
        # ------------------------------------------

        with activity_lock:

            file_exists = os.path.exists(
                activity_file
            )


            with open(
                activity_file,
                "a",
                newline="",
                encoding="utf-8"
            ) as file:

                fieldnames = [
                    "file_path",
                    "event_type",
                    "event_time"
                ]


                writer = csv.DictWriter(
                    file,
                    fieldnames=fieldnames
                )


                if (
                    not file_exists
                    or os.path.getsize(activity_file) == 0
                ):

                    writer.writeheader()


                writer.writerow(
                    activity_record
                )


        print(
            event_type,
            "→",
            normalized_file_path
        )


    def on_created(self, event):

        if not event.is_directory:

            self.save_activity(
                event.src_path,
                "CREATED"
            )


    def on_modified(self, event):

        if not event.is_directory:

            self.save_activity(
                event.src_path,
                "MODIFIED"
            )


    def on_deleted(self, event):

        if not event.is_directory:

            self.save_activity(
                event.src_path,
                "DELETED"
            )


    def on_moved(self, event):

        if not event.is_directory:

            self.save_activity(
                event.src_path,
                "MOVED_FROM"
            )

            self.save_activity(
                event.dest_path,
                "MOVED_TO"
            )


# --------------------------------------------------
# CREATE OBSERVER
# --------------------------------------------------

event_handler = FileActivityHandler()

observer = Observer()


# --------------------------------------------------
# WATCH APPROVED FOLDERS
# --------------------------------------------------

watched_folders = []


for folder_path in approved_folders:

    if not folder_path.exists():

        print(
            "Folder not found, skipping:",
            folder_path
        )

        continue


    observer.schedule(
        event_handler,
        str(folder_path),
        recursive=True
    )


    watched_folders.append(
        str(folder_path)
    )


# --------------------------------------------------
# START TRACKER
# --------------------------------------------------

observer.start()


print("--------------------------------")
print("STORAGE GUARDIAN ACTIVITY TRACKER")
print("--------------------------------")

print("Monitoring folders:")


for folder_path in watched_folders:

    print(
        " -",
        folder_path
    )


print("--------------------------------")
print("Press CTRL + C to stop")
print("--------------------------------")


# --------------------------------------------------
# KEEP TRACKER RUNNING
# --------------------------------------------------

try:

    while True:

        time.sleep(1)


except KeyboardInterrupt:

    print(
        "\nStopping activity tracker..."
    )

    observer.stop()


observer.join()


print(
    "Activity tracker stopped."
)