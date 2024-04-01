# TODO: Использовать postgresql вместо sqlite3
import sqlite3
import os
from sqlite3 import Connection as instance


def create_instance():
    return sqlite3.connect("grades.db")


def close_instance(db: instance):
    db.close()


def wipe():
    if os.path.exists("grades.db"):
        os.remove("grades.db")


def setup_tables(db: instance):
    db.execute(
        """
    CREATE TABLE Students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_name TEXT
    );
    """
    )

    db.execute(
        """
    CREATE TABLE Classes (
        class_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        class_name TEXT,
        FOREIGN KEY (student_id) REFERENCES Students(student_id)
    );
    """
    )

    db.execute(
        """
    CREATE TABLE LessonTypes (
        type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT
    );
    """
    )

    db.execute(
        """
    CREATE TABLE Grades (
        grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        type_id INTEGER,
        semester_part INTEGER,
        grades TEXT,
        FOREIGN KEY (class_id) REFERENCES Classes(class_id),
        FOREIGN KEY (type_id) REFERENCES LessonTypes(type_id)
    );
    """
    )
    db.commit()


def store_parsed(db: instance, grade_map: dict):
    for key in grade_map.keys():
        db.execute(
            """
        INSERT INTO Students (student_name) VALUES (?);
        """,
            (key,),
        )
        db.commit()
        student_id = db.execute(
            """
        SELECT student_id FROM Students WHERE student_name = ?;
        """,
            (key,),
        ).fetchone()[0]

        for class_name, grades in grade_map[key].items():
            db.execute(
                """
            INSERT INTO Classes (student_id, class_name) VALUES (?, ?);
            """,
                (student_id, class_name),
            )
            db.commit()
            class_id = db.execute(
                """
            SELECT class_id FROM Classes WHERE student_id = ? AND class_name = ?;
            """,
                (student_id, class_name),
            ).fetchone()[0]

            for lesson_type, grade in grades.items():
                db.execute(
                    """
                INSERT INTO LessonTypes (type_name) VALUES (?);
                """,
                    (lesson_type,),
                )
                db.commit()
                type_id = db.execute(
                    """
                SELECT type_id FROM LessonTypes WHERE type_name = ?;
                """,
                    (lesson_type,),
                ).fetchone()[0]

                for semester_part, grade in enumerate(grade):
                    db.execute(
                        """
                    INSERT INTO Grades (class_id, type_id, semester_part, grades) VALUES (?, ?, ?, ?);
                    """,
                        (class_id, type_id, semester_part, ",".join(grade)),
                    )
                    db.commit()
