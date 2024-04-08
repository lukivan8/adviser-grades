import time
from selenium import webdriver as drv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement


def create_instance(lang):
    options = Options()
    options.page_load_strategy = "eager"
    options.add_experimental_option("prefs", {"intl.accept_languages": lang})
    return drv.Chrome(options=options)


def close_instance(browser):
    browser.quit()


def cookie(browser, login, password):
    browser.get("https://univer.kstu.kz/user/login?ReturnUrl=/")
    login_field = browser.find_element(By.CLASS_NAME, "input-field")
    password_field = browser.find_elements(By.CLASS_NAME, "input-field")[1]
    submit = browser.find_element(By.CSS_SELECTOR, "input[type=submit]")

    login_field.send_keys(login)
    password_field.send_keys(password)
    submit.click()

    return browser.get_cookie(".ASPXAUTH")["value"]


def students(browser: WebDriver, cookie: str):
    browser.get("https://univer.kstu.kz/advicer/students/")
    browser.add_cookie({"name": ".ASPXAUTH", "value": cookie})
    browser.refresh()
    students = browser.find_elements(By.CLASS_NAME, "link")
    names = [student.find_element(By.TAG_NAME, "a").text for student in students]
    ids = [student.get_property("id") for student in students]
    students_map = {}
    for name, id in zip(names, ids):
        students_map[name] = id
    return students_map


# TODO: Распаралелить эту функцию на каждого студента
def grades(browser: WebDriver, student_id: int):
    browser.get(f"https://univer.kstu.kz/advicer/students/attendence/{student_id}/")
    timer = time.perf_counter()
    # TODO: improve bottleneck
    rows_grades = browser.find_elements(By.CLASS_NAME, "tt")
    grades = [
        [tag.text for tag in rows.find_elements(By.TAG_NAME, "td")][:-2]
        for rows in rows_grades
    ]
    print("Grades:", time.perf_counter() - timer)
    section_timer = time.perf_counter()
    sections_map = get_sections(browser)
    count = 0
    for title, sections in sections_map.items():
        sections_map[title] = {}
        for section in sections:
            sections_map[title][section] = [grades[count], grades[count + 1]]

            count += 2
    print("Sections:", time.perf_counter() - section_timer)
    return sections_map


# works only if currently on student's grades page
def get_sections(browser: WebDriver):
    browser.execute_script(
        "arguments[0].setAttribute('class', 'top')",
        browser.find_element(By.CLASS_NAME, "bot"),
    )
    top_elements = browser.find_elements(By.XPATH, '//tr[contains(@class, "top")]')
    mid_elements = browser.find_elements(By.CLASS_NAME, "mid")

    mid_elements = [
        mid for mid in mid_elements if mid.find_elements(By.CLASS_NAME, "tt")
    ]

    mid_counts = []

    for idx, elems in enumerate(top_elements):
        if idx == len(top_elements) - 1:
            break
        start_top = elems
        end_top = top_elements[idx + 1]

        # Filter mid elements between current pair of "top" elements
        mid_elements_between_top = []
        for mid in mid_elements:
            if mid.location["y"] > start_top.location["y"]:
                mid_elements.remove(mid)
            elif mid.location["y"] > end_top.location["y"]:
                break
            else:
                mid_elements_between_top.append(mid)
                mid_elements.remove(mid)

        mid_count = len(mid_elements_between_top)

        mid_counts.append(mid_count)
    class_titles = browser.find_elements(By.CLASS_NAME, "ct")
    class_titles = [
        title.text.split(" (")[0]
        for idx, title in enumerate(class_titles)
        if idx % 2 == 0 and 0 < idx < len(class_titles) - 1
    ]

    grades_types = browser.find_elements(By.CSS_SELECTOR, "a.lt")
    grades_types = [grade_type.text.split(" -")[0] for grade_type in grades_types]

    sections_map = {title: count for title, count in zip(class_titles, mid_counts)}

    # Assign grade types to sections
    last_count = 0
    for title, count in sections_map.items():
        sections_map[title] = grades_types[last_count : last_count + count // 2]
        last_count += count // 2
    return sections_map

def attestation(browser: WebDriver, student_id: int, name:str):
    browser.get(f"https://univer.kstu.kz/advicer/students/attestation/{student_id}/")
    rows_grades = browser.find_elements(By.CLASS_NAME, "link")
    grade_map = [get_row(row, name) for row in rows_grades]
    return grade_map

def get_row(row: WebElement, name: str):
    cells = row.find_elements(By.CSS_SELECTOR, "*")
    row_map = {}
    row_map["student"] = name
    row_map["title"] = cells[2].text
    row_map["rk1"] = int(cells[6].text)
    row_map["rk2"] = int(cells[7].text)
    row_map["exam"] = int(cells[8].text)
    row_map["total"] = int(cells[9].text)
    return row_map