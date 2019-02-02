from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
# from selenium.webdriver import ActionChains
# import time
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


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
    except TimeoutException as e:
        report_failure("Login Failure", error=e)
    else:
        login_btn.send_keys(Keys.ENTER)
    driver.find_element_by_class_name("btn-primary").click() # "yes" button on login check


def search_date(date, length):
    time_btns = driver.find_elements_by_xpath("//label[@class='btn btn-default']")
    time_btns[2].click() # select "thisweek" button

    begin_date = driver.find_element_by_xpath("//input[@type='text' and @id='beginDate']")
    begin_date.clear()
    begin_date.send_keys(date)
    end_date = driver.find_element_by_xpath("//input[@type='text' and @id='endDate']")
    end_date.clear()
    end_date.send_keys(date)
    
    footer = driver.find_element_by_xpath("//footer")
    footer.click()

    input_min = driver.find_element_by_xpath("//input[@class='form-control hours-minutes' and @id='minutes']")
    input_min.clear()
    input_min.send_keys(length) # TODO change to arg
    submit_btn = driver.find_element_by_name("SUBMIT")
    submit_btn.send_keys(Keys.ENTER)


def verify_success():
    try:
        wait(driver, 20).until(EC.presence_of_element_located(By.XPATH, "//input[@id='btnSaveSuccessful']"))
    except TimeoutException as e:
        return False    
    else:
        return True


def report_failure(reason, date="--/--/----", hour="--:--", error=None):
    if 'server' not in vars() and 'server' not in globals():
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login("bookmysel", "seleniumrocks") # TODO change to args

    fromaddr = "bookmysel@gmail.com" # TODO change to arg
    toaddr = "gelbermann@campus.technion.ac.il" # TODO change to arg
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = f"BookMe Reservation Failure for {date}"
    body = f"Uh oh!\n\nScheduling a reservation for {date} at {hour} failed because of {reason}.\n\n" 
    if not error is None:
        body = body + f"Further details:\n{str(error)}"
    body = str(body)
    msg.attach(MIMEText(body, 'plain'))

    server.sendmail(fromaddr, toaddr, msg.as_string())
    print(f"Failed to make reservation because: \n{str(error)}") # TODO fix empty error message
    driver.quit()
    exit()


if __name__ == "__main__":
    driver = webdriver.Chrome()
    driver.get("https://bookme.technion.ac.il/booked/Web/search-availability.php")
    if not "BookMe" in driver.title: 
        login("gelbermann@campus.technion.ac.il", "Fk1jhhk1") # TODO change to args

    hour = '13:00' # TODO change to arg

    rooms = {'9': 'Ada Lovelace',
            '10': 'John Von Neumann',
            '11': 'Claude Shannon',
             '8': 'Alan Turing'}
    for room_id in rooms.keys():
        search_date("17/02/2019", "180") # TODO change to args
        try:
            opening = wait(driver, 30).until(EC.presence_of_element_located((By.XPATH, \
                f"//div[@class='opening' and @data-resourceid='{room_id}' and contains(@data-startdate, '{beginning}')]")))
        except TimeoutException as e:
            pass
        else:
            opening.click()
            driver.find_element_by_xpath("//label[@for='startReminderEnabled']").click() 
            driver.find_elements_by_xpath("//button[contains(@class, 'save')]")[1].click() 
            if verify_success():
                print(f"Reservation made for room {rooms[room_id]} {date} at {hour}.")
                driver.quit()
                exit()
            else:
                driver.back()

    report_failure("No Successful Reservation")
