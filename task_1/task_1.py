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
        self.format, self.serialize = Combining.get_serialize(format.lower())
        self.students_path = Combining.check_file_path(students_path)
        self.rooms_path = Combining.check_file_path(rooms_path)

    @staticmethod
    def get_serialize(format):
        if format == "json":
            return format, Combining.serialize_to_json
        elif format == "xml":
            return format, Combining.serialize_to_xml
        else:
            raise ValueError(f"'{format} - unsupported format'")

    @staticmethod
    def serialize_to_json(combined_list: list, file) -> None:
        json.dump(combined_list, file, indent=4)
        
    @staticmethod
    def serialize_to_xml(combined_list: list, file) -> None:
        file.write(dict2xml(combined_list, wrap="room"))
   
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


def combine_lists(students_list: list, rooms_list: list) -> list:
    for student in students_list:
        room_index = student["room"]
        del student["room"]
        rooms_list[room_index].setdefault("students", []).append(student)
    return rooms_list


def create_file(combined_list: list, combined) -> None:
    with open(f"rooms_with_students.{combined.format}", "w") as file:
        combined.serialize(combined_list, file)


def main():
    combined = Combining(*parse_arguments())
    students_list = read_json(combined.students_path)
    rooms_list = read_json(combined.rooms_path)
    combined_list = combine_lists(students_list, rooms_list)
    create_file(combined_list, combined)


if __name__ == "__main__":
    main()
