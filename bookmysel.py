from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import ActionChains
import time


def login(username, password):

    def fill_element(name, value): 
        elem = driver.find_element_by_name(name)
        elem.clear()
        elem.send_keys(value, Keys.RETURN)

    fill_element("loginfmt", username) 
    fill_element("passwd", password) 
    try:
        login_btn = wait(driver, 10) \
                    .until(EC.element_to_be_clickable((By.XPATH, "//input[@id='idSIButton9']")))
    except Exception as e:
        handle_errors(e)
    else:
        login_btn.send_keys(Keys.ENTER)
    driver.find_element_by_class_name("btn-primary").click() # "yes" button on login check


def search_this_week():
    time_btns = driver.find_elements_by_xpath("//label[@class='btn btn-default']")
    time_btns[1].click() # select "thisweek" button
    input_min = driver.find_element_by_xpath("//input[@class='form-control hours-minutes' and @id='minutes']")
    input_min.clear()
    input_min.send_keys("180") # TODO change to arg
    submit_btn = driver.find_element_by_name("SUBMIT")
    submit_btn.click()  


def search_dates():
    time_btns = driver.find_elements_by_xpath("//label[@class='btn btn-default']")
    time_btns[2].click() # select "thisweek" button

    begin_date = driver.find_element_by_xpath("//input[@type='text' and @id='beginDate']")
    begin_date.clear()
    begin_date.send_keys("17/02/2019")
    end_date = driver.find_element_by_xpath("//input[@type='text' and @id='endDate']")
    end_date.clear()
    end_date.send_keys("23/02/2019")
    
    footer = driver.find_element_by_xpath("//footer")
    footer.click()

    input_min = driver.find_element_by_xpath("//input[@class='form-control hours-minutes' and @id='minutes']")
    input_min.clear()
    input_min.send_keys("180") # TODO change to arg
    submit_btn = driver.find_element_by_name("SUBMIT")
    submit_btn.send_keys(Keys.ENTER)


def handle_errors(e):
    # TODO send mail about error 
    # TODO terminate browser and script
    pass


if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get("https://bookme.technion.ac.il/booked/Web/search-availability.php")
    if not "BookMe" in driver.title: # login required
        login("gelbermann@campus.technion.ac.il", "Fk1jhhk1") # TODO change to args
        assert "BookMe" in driver.title

    # # search_this_week()
    # search_dates()

    # beginning = '13:00' # TODO change to arg
    # try:
    #     # room ids:
    #     # resourceid='8' - Alan Turing
    #     # resourceid='9' - Ada Lovalace
    #     # resourceid='10' - John Von Neumann
    #     # resourceid='11' - Claude Shannon
    #     openings = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, \
    #         "//div[@class='opening' and @data-resourceid='9' and contains(@data-startdate, '13:00')]")))
    # except Exception as e:
    #     handle_errors(e)
    # else:
    #     actions = ActionChains(driver)
    #     for opening in openings:
    #         # opening.click()
    #         actions.key_down(Keys.CONTROL).click(opening).key_up(Keys.CONTROL).perform()
    #         driver.switch_to.window(driver.window_handles[1])

    #         before_checkbox = driver.find_element_by_xpath("//label[@for='startReminderEnabled']")
    #         before_checkbox.click()
    #         driver.find_elements_by_xpath("//button[contains(@class, 'save')]")[1].click()

    #         driver.back()
    #         time.sleep(5)
    
    actions = ActionChains(driver)
    for i in range(0,6):
        # search_this_week()
        search_dates()

        beginning = '13:00' # TODO change to arg
        try:
            # room ids:
            # resourceid='8' - Alan Turing
            # resourceid='9' - Ada Lovalace
            # resourceid='10' - John Von Neumann
            # resourceid='11' - Claude Shannon
            openings = wait(driver, 30).until(EC.presence_of_all_elements_located((By.XPATH, \
                "//div[@class='opening' and @data-resourceid='9' and contains(@data-startdate, '13:00')]")))
        except Exception as e:
            handle_errors(e)
        else:
            openings[i].click()

            before_checkbox = driver.find_element_by_xpath("//label[@for='startReminderEnabled']")
            before_checkbox.click()
            driver.find_elements_by_xpath("//button[contains(@class, 'save')]")[1].click()

            driver.back()
            time.sleep(5)
        break # TODO remove