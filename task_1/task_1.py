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


def read_json(path) -> list:
    with open(path, "r") as file:
        data = json.load(file)
    return data


def combine_lists(format: str, students_list: list, rooms_list: list) -> list:
    dictionary_key = "student" if format == "xml" else "students"
    for student in students_list:
        try:
            room_index = student["room"]
            del student["room"]
            rooms_list[room_index][dictionary_key].append(student)
        except KeyError:
            rooms_list[room_index][dictionary_key] = [student]
    return rooms_list


def create_file(format: str, combined_list: list) -> None:
    with open(f"rooms_with_students.{format}", "w") as file:
        if format == "json":
            json.dump(combined_list, file, indent=4)
        elif format == "xml":
            file.write(dict2xml(combined_list, wrap="room"))


def main():
    combined = Combining(*parse_arguments())
    students_list = read_json(combined.students_path)
    rooms_list = read_json(combined.rooms_path)
    combined_list = combine_lists(combined.format, students_list, rooms_list)
    create_file(combined.format, combined_list)


if __name__ == "__main__":
    main()
