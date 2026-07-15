import os
import time
import csv
from datetime import datetime

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


folder_path = "test_storage"
activity_file = "file_activity.csv"


class FileActivityHandler(FileSystemEventHandler):

    def save_activity(self, file_path, event_type):

        activity_record = {
            "file_path": file_path,
            "event_type": event_type,
            "event_time": datetime.now()
        }

        file_exists = os.path.exists(activity_file)

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

            if not file_exists:
                writer.writeheader()

            writer.writerow(activity_record)

        print(
            event_type,
            "→",
            file_path
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


event_handler = FileActivityHandler()

observer = Observer()

observer.schedule(
    event_handler,
    folder_path,
    recursive=True
)

observer.start()


print("--------------------------------")
print("STORAGE GUARDIAN ACTIVITY TRACKER")
print("Monitoring:", folder_path)
print("Press CTRL + C to stop")
print("--------------------------------")


try:

    while True:
        time.sleep(1)

except KeyboardInterrupt:

    observer.stop()


observer.join()

print("Activity tracker stopped.")