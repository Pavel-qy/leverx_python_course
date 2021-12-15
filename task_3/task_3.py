import argparse
import json
import os
from dict2xml import dict2xml
from mysql.connector import connect, Error


def parse_arguments():
    parser = argparse.ArgumentParser(description="MySQL Query Script")
    parser.add_argument(
        "format",
        help="Output format: 'json' or 'xml'",
    )
    parser.add_argument(
        "-u",
        "--user",
        "--username",
        required=True,
        help="Username to connect to MySQL server",
        dest="username",
    )
    parser.add_argument(
        "-p",
        "--pass",
        "--password",
        required=True,
        help="Password to connect to MySQL server",
        dest="password",
    )
    parser.add_argument(
        "--rooms",
        default="data/rooms.json",
        help="Path to 'rooms.json' file",
        dest="rooms_path",
    )
    parser.add_argument(
        "--students",
        default="data/students.json",
        help="Path to 'students.json' file",
        dest="students_path",
    )
    args = parser.parse_args()
    return args.format, args.username, args.password, args.rooms_path, args.students_path


class Table:
    def __init__(self, path: str):
        self.path = Table.check_file_path(path)
        self.name = os.path.basename(self.path).split(".")[0].lower()
        self.table_creation, self.table_filling, self.index = Table.define_query(self.name)

    @staticmethod
    def check_file_path(path: str) -> str or ValueError:
        if os.path.isfile(path):
            return path
        else:
            raise ValueError("invalid file path")
    
    @staticmethod
    def define_query(name: str) -> tuple[str, str, str]:
        if name == "rooms":
            table_creation = (
                """
                CREATE TABLE rooms(
                    id SMALLINT UNSIGNED PRIMARY KEY,
                    name VARCHAR(20)
                    )
                """
            )
            table_filling = (
                """
                INSERT INTO rooms
                (id, name)
                VALUES ( %(id)s, %(name)s )
                """
            )
            index = "CREATE INDEX name_id ON rooms(id, name)"
            return table_creation, table_filling, index
        elif name == "students":
            table_creation = (
                """
                CREATE TABLE students(
                    birthday DATE,
                    id SMALLINT UNSIGNED PRIMARY KEY,
                    name VARCHAR(50),
                    room SMALLINT UNSIGNED,
                    sex CHAR(1),
                    FOREIGN KEY(room) REFERENCES rooms(id)
                    )
                """
            )
            table_filling = (
                """
                INSERT INTO students
                (birthday, id, name, room, sex)
                VALUES ( %(birthday)s, %(id)s, %(name)s, %(room)s, %(sex)s )
                """
            )
            index = "CREATE INDEX sex ON students(sex)"
            return table_creation, table_filling, index
    

def db_connection(user:str, password:str, host:str, database:str=None) -> None:
    def decorator(func):
        def wrapper(db_name, *args):
            try:
                with connect(
                    host=host, 
                    user=user, 
                    password=password, 
                    database=database
                    ) as connection:
                    with connection.cursor() as cursor:
                        return func(connection, cursor, db_name, *args)
            except Error as exc:
                print(exc)
        return wrapper
    return decorator


def create_db(username: str, password: str, host:str, db_name: str, *args) -> None:
    @db_connection(username, password, host)
    def wrapped(connection, cursor, db_name, *args):
        cursor.execute("SHOW DATABASES")
        for row in cursor.fetchall():
            if db_name in row:
                return
        cursor.execute(f"CREATE DATABASE {db_name}")
        connection.database = db_name
        for table in args:
            cursor.execute(table.table_creation)
            with open(table.path, "r") as file:
                json_file = json.load(file)
            cursor.executemany(table.table_filling, json_file)
            cursor.execute(table.index)
            connection.commit()
    wrapped(db_name, *args)


class Query:
    def __init__(self, format: str):
        self.format, self.serialize = Query.get_serialize(format.lower())
        self.queries = {
            "students_count": """
            SELECT rooms.name, COUNT(students.name)
            FROM rooms
            JOIN students
            ON students.room = rooms.id
            GROUP BY rooms.name
            """,
            "smallest_average_age": """
            SELECT rooms.name
            FROM rooms
            JOIN students
            ON students.room = rooms.id
            GROUP BY rooms.name
            ORDER BY AVG(students.birthday) DESC
            LIMIT 5
            """,
            "biggest_age_diffrence": """
            SELECT rooms.name
            FROM rooms
            JOIN students
            ON students.room = rooms.id
            GROUP BY rooms.name
            ORDER BY MAX(students.birthday) - MIN(students.birthday) DESC
            LIMIT 5
            """,
            "defferent_sex_students": """
            SELECT rooms.name
            FROM rooms
            JOIN students
            ON students.room = rooms.id
            WHERE rooms.name IN (
                SELECT rooms.name
                FROM rooms
                JOIN students
                ON students.room = rooms.id
                WHERE students.sex = 'M'
                GROUP BY rooms.name
                HAVING COUNT(students.sex) > 0
                ) AND students.sex = 'F'
            GROUP BY rooms.name
            HAVING COUNT(students.sex) > 0
            """
        }

    @staticmethod
    def get_serialize(format: str):
        if format == "json":
            return format, Query.serialize_to_json
        elif format == "xml":
            return format, Query.serialize_to_xml
        else:
            raise ValueError(f"'{format}' - invalid output format")

    @staticmethod
    def serialize_to_json(combined_list: list, file) -> None:
        json.dump(combined_list, file, indent=4)
        
    @staticmethod
    def serialize_to_xml(combined_list: list, file) -> None:
        file.write(dict2xml(combined_list, wrap="room"))
   
    
def unload_selection(username: str, password: str, host: str, db_name: str, query):
    @db_connection(username, password, host, db_name)
    def wrapped(connection, cursor, query):
        for filename, query_content in query.queries.items():
            cursor.execute(query_content)
            selection = cursor.fetchall()
            result_list = [{i[0]: i[1]} if len(i) == 2 else i[0] for i in selection]
            with open(f"{filename}.{query.format}", "w") as file:
                query.serialize(result_list, file)
    wrapped(query)


def main():
    format, username, password, rooms_path, students_path = parse_arguments()
    host = "localhost"
    db_name = "task_3"
    rooms_table = Table(rooms_path)
    students_table = Table(students_path)
    create_db(username, password, host, db_name, rooms_table, students_table)
    query = Query(format)
    unload_selection(username, password, host, db_name, query)


if __name__ == "__main__":
    main()
