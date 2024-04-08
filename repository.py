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
        StudentID INTEGER PRIMARY KEY AUTOINCREMENT,
        StudentName TEXT NOT NULL
    );
    """
    )

    db.execute(
    """
    CREATE TABLE Courses (
    CourseID INTEGER PRIMARY KEY AUTOINCREMENT,
    CourseTitle TEXT NOT NULL
    );
    """
    )

    db.execute(
    """
    CREATE TABLE Marks (
        MarkID INTEGER PRIMARY KEY AUTOINCREMENT,
        StudentID INTEGER NOT NULL,
        CourseID INTEGER NOT NULL,
        Round1Coursework INTEGER,
        Round2Coursework INTEGER,
        ExamMark INTEGER,
        TotalMark INTEGER,
        FOREIGN KEY(StudentID) REFERENCES Students(StudentID),
        FOREIGN KEY(CourseID) REFERENCES Courses(CourseID)
    );
    """
    )

    db.commit()


def store_parsed(db: instance, grades: list[dict]):
    # grade_map = {student: str, title: str, rk1: int, rk2: int, exam: int, total: int}
    for grade_map in grades:
        print(grade_map)
        db.execute(
            """
        INSERT INTO Students (StudentName) VALUES (?);
        """,
            (grade_map["student"],),
        )
        db.commit()

        db.execute(
            """
        INSERT INTO Courses (CourseTitle) VALUES (?);
        """,
            (grade_map["title"],),
        )
        db.commit()

        db.execute(
            """
        INSERT INTO Marks (StudentID, CourseID, Round1Coursework, Round2Coursework, ExamMark, TotalMark) VALUES (
            (SELECT StudentID FROM Students WHERE StudentName = ?),
            (SELECT CourseID FROM Courses WHERE CourseTitle = ?),
            ?, ?, ?, ?
        );
        """,
            (
                grade_map["student"],
                grade_map["title"],
                grade_map["rk1"],
                grade_map["rk2"],
                grade_map["exam"],
                grade_map["total"],
            ),
        )
        db.commit()

