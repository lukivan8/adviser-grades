import repository
import extract
import os
from dotenv import load_dotenv

# TODO: Поместить этот код за http сервер
load_dotenv()
browser = extract.create_instance("ru")
cookie = extract.cookie(
    browser, os.getenv("KURATOR_LOGIN"), os.getenv("KURATOR_PASSWORD")
)
students = extract.students(browser, cookie)
for name, id in students.items():
    students[name] = extract.grades(browser, cookie, id)
extract.close_instance(browser)

repository.wipe()
db = repository.create_instance()
repository.setup_tables(db)
repository.store_parsed(db, students)
repository.close_instance(db)
