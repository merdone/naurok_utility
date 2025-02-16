import os
import time
import json
import random
import telebot
from dotenv import load_dotenv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from collections import deque
import threading
import re

load_dotenv("config.env")

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CACHE_FILE = os.getenv("CACHE_FILE")

bot = telebot.TeleBot(TOKEN)

task_queue = deque()
processing = False
cleaning = False
last_task_time = time.time()
cleaning_event = threading.Event()


try:
    with open(CACHE_FILE, "r", encoding="utf-8") as f:
        cache = json.load(f)
except FileNotFoundError:
    cache = {}

options = webdriver.ChromeOptions()
options.add_argument(
    "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
)
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("--ignore-certificate-errors")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--headless")
options.add_argument("--window-size=1920,1080")
options.add_argument("--disable-gpu")

browser = webdriver.Chrome(options=options)
wait = WebDriverWait(browser, 3)

auth_link = "https://naurok.com.ua/login"
browser.get(auth_link)
email_field = browser.find_element(By.ID, "loginform-login")
password_field = browser.find_element(By.ID, "loginform-password")
email_field.send_keys(EMAIL)
password_field.send_keys(PASSWORD)
logged_in = False
while not logged_in:
    try:
        button2 = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Увійти')]")))
        button2.click()
        time.sleep(random.uniform(2, 4))
    except:
        print("Logging was successful")
        logged_in = True


def save_cache():
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)


def process_queue():
    global processing
    if processing:
        return
    if not task_queue:
        return
    if cleaning:
        cleaning_event.set()
        while cleaning:
            time.sleep(0.5)
    processing = True

    chat_id, test_link = task_queue.popleft()
    bot.send_message(chat_id, "⏳ Починаю твій тест, почекай трошки, будь ласка.")
    test_id = get_test_id(test_link)

    if test_id in cache:
        answers_text = cache[test_id]["answers_text"]
        result_link = cache[test_id]["result_link"]
        bot.send_message(chat_id, answers_text)
        bot.send_message(chat_id, f"🔗 Посилання на відповіді: {result_link}")
    else:
        result_link = process_naurok_test(test_link)
        if result_link.startswith("❌"):
            bot.send_message(chat_id, result_link)
        else:
            answers_text = getting_text_answers(result_link)
            bot.send_message(chat_id, answers_text)
            bot.send_message(chat_id, f"🔗 Посилання на відповіді: {result_link}")
            cache[test_id] = {
                "answers_text": answers_text,
                "result_link": result_link
            }
            save_cache()
    processing = False
    process_queue()


def get_test_id(test_link: str) -> str:
    match = re.search(r"-(\d+)\.html", test_link)
    if match:
        return match.group(1)
    return test_link


def process_naurok_test(link):
    try:
        link = link[:len(link) - 5] + "/set"
        browser.get(link)
        for _ in range(2):
            try:
                date_set_button = wait.until(EC.presence_of_element_located((By.ID, "homework-deadline_day")))
                browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight;", date_set_button)
                select = Select(date_set_button)
                select.select_by_index(len(select.options) - 1)
                submit_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "btn.btn-orange.btn-block")))
                submit_button.click()
                break
            except:
                print("Mistake in first part")
        time.sleep(3)
        for _ in range(2):
            try:
                soup = BeautifulSoup(browser.page_source, 'html.parser')
                new_link = soup.find("input", {"class": "form-control input-xs"})["value"]
                browser.get(new_link)
                break
            except:
                print("Mistake in code funding")
        time.sleep(random.uniform(1, 3))
        for _ in range(2):
            try:
                name_field = browser.find_element(By.ID, "joinform-name")
                name_field.send_keys("created by merdone")
                break
            except:
                print("Mistake in name")
        for _ in range(2):
            try:
                join_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, "//button[contains(text(),'Приєднатись')]")))
                join_button.click()
                break
            except:
                print("Mistake in connecting to test")
        for _ in range(2):
            time.sleep(3)
            try:
                time.sleep(3)
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "test-option0")))
                random_option = browser.find_element(By.CLASS_NAME, "test-option0")
                random_option.click()
                break
            except:
                print("Mistake in changing option")
        try:
            answer_button = browser.find_element(By.CLASS_NAME, "test-multiquiz-save-button")
            answer_button.click()
            time.sleep(3)
        except:
            pass

        end_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "endSessionButton")))
        end_button.click()
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        result_url = browser.current_url
        return result_url

    except Exception as e:
        return "❌An error occurred"


def getting_text_answers(link):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    correct_answer = ""
    response = requests.get(link, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    answers = soup.find_all("div", {"class": "homework-stat-question-line"})

    for i in range(len(answers)):
        correct_answer += f"🔹{i + 1} питання: {answers[i].find('p').text.strip()}\n"
        right_answers = answers[i].find_all("div", {"class": "correct"})
        for right_answer in right_answers:
            temp = right_answer.text.strip()
            correct_answer += f"✅{temp[0]}" + " варіант: " + temp[1:].strip() + "\n"
        correct_answer += "\n"
    return correct_answer.strip()


def clear_tests():
    global cleaning
    cleaning = True
    cleaning_event.clear()
    try:
        browser.get("https://naurok.com.ua/test/homework/list")
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        links = soup.find_all("a", {"class": "homework-name"})
        for temp in links:
            if cleaning_event.is_set():
                print("Cleaning interrupted - new tasks in queue")
                break
            temp_link = "https://naurok.com.ua" + temp.get("href")
            browser.get(temp_link)
            for _ in range(2):
                try:
                    for _ in range(2):
                        if cleaning_event.is_set():
                            break
                        time.sleep(2)
                        stop_button = browser.find_element(By.CLASS_NAME, "btn-danger")
                        stop_button.click()
                        alert = browser.switch_to.alert
                        alert.accept()
                        time.sleep(2)
                    if cleaning_event.is_set():
                        break
                    break
                except:
                    print("Cleaning mistake")
    finally:
        cleaning = False
        cleaning_event.clear()


def clean_cache():
    global cache
    keys_to_delete = [test_id for test_id, data in cache.items()]
    for key in keys_to_delete:
        del cache[key]
    if keys_to_delete:
        save_cache()
        print(f"🗑️ Cleaned {len(keys_to_delete)} old cache entries.")


def monitor_queue():
    global last_task_time
    while True:
        time.sleep(60)
        if time.time() - last_task_time >= 300 and not task_queue:
            print("Queue idle for 5 minutes. Running clear_tests...")
            clear_tests()
            clean_cache()


def get_first_url(response):
    link = "https://www.google.com.ua/search?q=naurok.com.ua: " + response
    browser.get(link)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    try:
        result = soup.find("div", {"class": "MjjYud"}).find("a", {"jsname": "UWckNb"}).get("href")
        return result
    except:
        return "Капча не дає життя("


threading.Thread(target=monitor_queue, daemon=True).start()


@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(message.chat.id,
                     "👋 Привіт. \n ✅Надсилай мені посилання наурок і я дам тобі відповіді. \n ❌Або можеш спробувати почати повідомлення з крапки, тоді спробую пошукати це в інтернеті. \nАле маловирогідно що вийде, не знаю як боротись з капчею(")


@bot.message_handler(func=lambda message: "naurok.com.ua/test/" in message.text)
def handle_naurok_test(message):
    global last_task_time
    task_queue.append((message.chat.id, message.text))
    last_task_time = time.time()
    bot.send_message(message.chat.id,
                     f"✅ Твій запит додано до черги. Твоя позиція в ній: {len(task_queue)}")
    process_queue()


@bot.message_handler(func=lambda message: message.text.startswith('.'))
def handle_dot_query(message):
    global last_task_time
    query = message.text[1:].strip()

    if not query:
        bot.send_message(message.chat.id, "❌ Нема запиту")
        return

    test_link = get_first_url(query)
    if test_link == "Капча не дає життя(":
        bot.send_message(message.chat.id, "❌ Капча не дає життя(")
        return

    task_queue.append((message.chat.id, test_link))
    last_task_time = time.time()
    bot.send_message(message.chat.id,
                     f"✅ Знайшов посилання: {test_link}\n"
                     f"Твій запит додано до черги. Твоя позиція в ній: {len(task_queue)}")
    process_queue()


bot.polling()
