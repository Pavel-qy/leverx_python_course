import argparse
import json
import os
from dict2xml import dict2xml


def parse_arguments():
    parser = argparse.ArgumentParser(description="Script for combining two json files")
    parser.add_argument(
        "format",
        help="Output format: 'json' or 'xml'",
    )
    parser.add_argument(
        "--students",
        default="data/students.json",
        help="Path to 'students.json' file",
        dest="students_path",
    )
    parser.add_argument(
        "--rooms",
        default="data/rooms.json",
        help="Path to 'rooms.json' file",
        dest="rooms_path",
    )
    args = parser.parse_args()
    return args.format, args.students_path, args.rooms_path


class Combining:
    def __init__(self, format: str, students_path: str, rooms_path: str):
        self.format = Combining.check_format(format)
        self.students_path = Combining.check_file_path(students_path)
        self.rooms_path = Combining.check_file_path(rooms_path)
        self.students_list = Combining.read_json(self.students_path)
        self.rooms_list = Combining.read_json(self.rooms_path)

    @staticmethod
    def check_format(format: str) -> str or ValueError:
        supported_formats = ["json", "xml"]
        if format.lower() in supported_formats:
            return format.lower()
        else:
            raise ValueError(f"'{format} - unsupported format'")
    
    @staticmethod
    def check_file_path(path: str) -> str or ValueError:
        if os.path.isfile(path):
            return path
        else:
            raise ValueError("invalid file path")

    @staticmethod
    def read_json(path) -> list:
        with open(path, "r") as file:
            data = json.load(file)
        return data

    def combine_lists(self) -> None:
        dictionary_key = "student" if self.format == "xml" else "students"
        for student in self.students_list:
            try:
                room_index = student["room"]
                del student["room"]
                self.rooms_list[room_index][dictionary_key].append(student)
            except KeyError:
                self.rooms_list[room_index][dictionary_key] = [student]

    def create_file(self) -> None:
        with open(f"rooms_with_students.{self.format}", "w") as file:
            if self.format == "json":
                json.dump(self.rooms_list, file, indent=4)
            elif self.format == "xml":
                file.write(dict2xml(self.rooms_list, wrap="room"))


def main():
    combined = Combining(*parse_arguments())
    combined.combine_lists()
    combined.create_file()


if __name__ == "__main__":
    main()
