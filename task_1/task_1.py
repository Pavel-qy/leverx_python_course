import json
from dict2xml import dict2xml


def open_json(path: str) -> list:
    with open(path, "r") as file:
        data = json.load(file)
    return data


def combine_lists(students_list: list, rooms_list: list, dictionary_key: str) -> list:
    for student in students_list:
        try:
            room_index = student["room"]
            del student["room"]
            rooms_list[room_index][dictionary_key].append(student)
        except KeyError:
            rooms_list[room_index][dictionary_key] = [student]
    return rooms_list


def create_json(combined_list: list):
    with open("rooms_with_students.json", "w") as file:
        json.dump(combined_list, file, indent=4)


def create_xml(combined_list: list):
    with open("rooms_with_students.xml", "w") as file:
        file.write(dict2xml(combined_list, wrap="room"))


def main():
    students_list = open_json(input("Enter a relative path to a 'students' json file: "))
    rooms_list = open_json(input("Enter a relative path to a 'rooms' json file: "))
    format = input("Specify the output format, 'json' or 'xml': ").lower()
    if format == "json":
        dictionary_key = "students"
        combined_list = combine_lists(students_list, rooms_list, dictionary_key)
        create_json(combined_list)
    elif format == "xml":
        dictionary_key = "student"
        combined_list = combine_lists(students_list, rooms_list, dictionary_key)
        create_xml(combined_list)


if __name__ == "__main__":
    main()
