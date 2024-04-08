import time
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
grades:list[dict] = []
t1 = time.perf_counter()
for name, id in students.items():
    grades.extend(extract.attestation(browser, id, name))
print(grades)
print(time.perf_counter() - t1)

extract.close_instance(browser)

repository.wipe()
db = repository.create_instance()
repository.setup_tables(db)
repository.store_parsed(db, grades)
repository.close_instance(db)
