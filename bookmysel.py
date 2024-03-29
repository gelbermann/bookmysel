from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException 
from sys import argv
import smtplib, argparse, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os import name as osname


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--loginemail", nargs="+", required=True)
    parser.add_argument("-p", "--loginpass", nargs="+",  required=True)
    parser.add_argument("-d", "--date", nargs="+")
    parser.add_argument("-H", "--hour", nargs="+")
    parser.add_argument("-l", "--length", nargs="+")
    # parser.add_argument("--reportemail", nargs="+")
    # parser.add_argument("--reportpass", nargs="+")
    args = parser.parse_args()
    return args


def wait_for_element_by_xpath(xpath, timeout, reason, multiple=False, ec=None): 
        try:
            if ec is None:
                ec = EC.presence_of_element_located((By.XPATH, xpath)) if not multiple\
                     else EC.presence_of_all_elements_located((By.XPATH, xpath))
            element = wait(driver, timeout).until(ec)
        except TimeoutException:
            report_failure(reason, args.loginemail[0], date=date, hour=hour) 
        else:
            return element


def login(username, password):
    def fill_element(xpath, reason, value):
        elem = wait_for_element_by_xpath(xpath, 10, reason)
        elem.clear()
        elem.send_keys(value, Keys.RETURN)

    reason = "Login Failure"
    # TODO Fix StaleReference exception on RPi - wait for username/password elements
    fill_element("//input[@name='loginfmt']", reason, username)
    fill_element("//input[@name='passwd']", reason, password)
    login_btn = wait_for_element_by_xpath("", 10, reason, \
                 ec=EC.element_to_be_clickable((By.XPATH, "//input[@id='idSIButton9']")))
    login_btn.send_keys(Keys.ENTER)

    if osname == 'nt':
        confirm_btn = wait_for_element_by_xpath("//input[@type='submit']", 10, reason) # "yes" button on login check
        confirm_btn.send_keys(Keys.ENTER)
    print("Logged in")


def search_date(date, length, room):
    # time_btns = driver.find_elements_by_xpath("//label[@class='btn btn-default']")
    time_btns = wait_for_element_by_xpath("//label[@class='btn btn-default']", 10, "Site Loading Issues", multiple=True)
    time_btns[2].click() # select "date range" button

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
    input_min.send_keys(length)
    submit_btn = driver.find_element_by_name("SUBMIT")
    submit_btn.send_keys(Keys.ENTER)
    print(f"Searching date {date} for room {room}")


def verify_success():
    try:
        wait(driver, 5).until(EC.presence_of_element_located((By.XPATH, "//input[@id='btnSaveSuccessful']")))
    except TimeoutException:
        return False    
    else:
        return True


def report_failure(reason, target, date="--/--/----", hour="--:--", error=None):
    fromaddr = "bookmysel@gmail.com"
    body = f"\nUh oh!\nScheduling a reservation for {date} at {hour} failed because of {reason}.\n" 
    if error is not None:
        body = body + f"Further details:\n{str(error)}"
    body = str(body)

    if 'server' not in vars() and 'server' not in globals():
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(fromaddr.split('@')[0], "seleniumrocks")

    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = target
    msg['Subject'] = f"BookMe Reservation Failure for {date}"
    msg.attach(MIMEText(body, 'plain'))
    server.sendmail(fromaddr, target, msg.as_string())

    print(body) # TODO fix empty error message
    driver.quit()
    exit()


def main():
    driver.get("https://bookme.technion.ac.il/booked/Web/search-availability.php")
    if not "BookMe" in driver.title: 
        login(args.loginemail[0], args.loginpass[0])

    rooms = {'9': 'Ada Lovelace',
            '10': 'John Von Neumann',
            '11': 'Claude Shannon',
             '8': 'Alan Turing'}
    for room_id in rooms.keys():
        search_date(date, length, rooms[room_id])
        try:
            print("waiting for" + f"//div[@class='opening' and @data-resourceid='{room_id}' and contains(@data-startdate, '{hour}')]")
            opening = wait(driver, 20).until(EC.presence_of_element_located((By.XPATH, \
                f"//div[@class='opening' and @data-resourceid='{room_id}' and contains(@data-startdate, '{hour}')]")))
        except TimeoutException:
            print("not found")
            driver.refresh()
        else:
            print("found")
            opening.click()
            driver.find_element_by_xpath("//label[@for='startReminderEnabled']").click() 
            driver.find_elements_by_xpath("//button[contains(@class, 'save')]")[1].click() 
            if verify_success():
                print(f"Reservation made for room {rooms[room_id]} {date} at {hour}.")
                driver.quit()
                exit()
            else:
                driver.back()

    report_failure("No Reservation was Successful", args.loginemail[0], date, hour)


if __name__ == "__main__":
    args = parse_arguments()    
    date = datetime.datetime.now() + datetime.timedelta(weeks=2)
    hour = args.hour[0] if args.hour else date.strftime("%H:00") # default hour is current hour
    date = args.date[0] if args.date else date.strftime("%d/%m/%Y") # default date is 2 weeks from today
    length = args.length[0] if args.length else "180" # default length 3 hours

    if osname == 'posix':
        options = webdriver.ChromeOptions() 
        options.add_argument('headless')
        driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', options=options)
    elif osname == 'nt':
        driver = webdriver.Chrome()
    else:
        report_failure("OS Mismatch", args.loginmail[0], date, hour)

    while True:
        try:
            main()
        except StaleElementReferenceException:
            continue
        except Exception as e:
            report_failure("Unknown Exception", args.loginemail[0], error=e)
            break
        else:
            break
