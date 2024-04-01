import time
from selenium import webdriver as drv
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote.webdriver import WebDriver


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
def grades(browser: WebDriver, cookie: str, student_id: int):
    browser.get(f"https://univer.kstu.kz/advicer/students/attendence/{student_id}/")
    browser.add_cookie({"name": ".ASPXAUTH", "value": cookie})
    browser.refresh()
    rows_grades = browser.find_elements(By.CLASS_NAME, "tt")

    grades = [
        list(map(lambda tag: tag.text, rows.find_elements(By.TAG_NAME, "td")))
        for rows in rows_grades
    ]
    grades = list(map(lambda grade: grade[0:-2], grades))
    sections_map = get_sections(browser)
    count = 0
    for title, sections in sections_map.items():
        sections_map[title] = {}
        for section in sections:
            sections_map[title][section] = [grades[count], grades[count + 1]]

            count += 2
    return sections_map


# works only if currently on student's grades page
def get_sections(browser: WebDriver):
    t1 = time.perf_counter()
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

    time1 = time.perf_counter()
    for idx, elems in enumerate(top_elements):
        if idx == len(top_elements) - 1:
            break
        start_top = elems
        end_top = top_elements[idx + 1]

        # Filter mid elements between current pair of "top" elements
        # TODO: improve this bottleneck
        mid_elements_between_top = [
            mid
            for mid in mid_elements
            if start_top.location["y"] < mid.location["y"] < end_top.location["y"]
        ]

        mid_count = len(mid_elements_between_top)

        mid_counts.append(mid_count)
    print(f"Time elements: {time.perf_counter() - time1}")
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
    print(time.perf_counter() - t1)
    return sections_map
