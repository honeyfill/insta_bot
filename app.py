from flask import Flask, request
import requests
from selenium import webdriver
import time
import random
from bs4 import BeautifulSoup
from data import hello_message, params, driverway, token
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)


def get_weather():
    api_result = requests.get('http://api.weatherstack.com/current', params)
    api_response = api_result.json()
    print(api_response)
    return f"Сейчас в Санкт-Петербурге {api_response['current']['temperature']} градусов. Скорость ветра " \
           f"{round(api_response['current']['wind_speed'] / 3.6, 2)} метров в секунду. Давление" \
           f"{round(api_response['current']['pressure'] * 0.74)} мм ртутного столба. Видимость могу оценить на "\
           f"{api_response['current']['visibility']}. \nСостояние указано на: {api_response['location']['localtime']}."


class InstRequest:
    def __init__(self):
        options = Options()
        options.add_argument("user-data-dir=C:\\Users\\Sema\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")
        self.driver = webdriver.Chrome(executable_path=driverway, chrome_options=options)

    def close_driver(self):
        self.driver.close()
        self.driver.quit()

    def count_subs(self, name) -> str:
        self.driver.get(f"https://www.instagram.com/{name}")
        time.sleep(random.randrange(3, 5))
        soup = BeautifulSoup(self.driver.page_source, 'lxml')
        quotes = soup.find('meta', {'name': 'description'})['content']
        return quotes.split()[0]

    def all_posts(self, name) -> list:
        self.driver.get(f"https://www.instagram.com/{name}")
        time.sleep(random.randrange(3, 5))
        posts_count = int(self.driver.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li["
                                                            "1]/span/span").text)
        loops_count = int(posts_count / 12)
        urls = []
        for i in range(loops_count):

            hrefs = self.driver.find_elements_by_tag_name('a')
            hrefs = [item.get_attribute('href') for item in hrefs if "/p/" in item.get_attribute('href')]

            for href in hrefs:
                urls.append(href+'\n')

            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.randrange(2, 4))

        set_urls = set(urls)
        urls = list(set_urls)
        return urls

    def likes_on_posts(self, name) -> list:
        likes = []
        posts = InstRequest.all_posts(self, name)
        for post in posts:
            self.driver.get(post)
            time.sleep(random.randrange(3, 5))

            likes_path = self.driver.find_element_by_xpath('/html/body/div[1]/section/main/div/div[1]/article/div['
                                                           '3]/section[2]/div/div[2]/a/span').text
            likes.append(int(likes_path.split()[0]) + 1)

        return likes


def send_message(chat_id, text):
    method = "sendMessage"
    url = f"https://api.telegram.org/bot{token}/{method}"
    data = {"chat_id": chat_id, "text": text}
    requests.post(url, data=data)


def make_text(text) -> str:
    if text == '/start':
        return hello_message

    if text == '/weatherSPb':
        return get_weather()

    if text.split(':')[0] == '/howmuch':
        name = text.split(':')[1]
        finder = InstRequest()
        try:
            count = finder.count_subs(name)
        except ValueError:
            finder.close_driver()
            return f"I could not find user /{name}."
        finder.close_driver()
        return f"User /{name} has {count} subscribers at the moment."

    if text.split(':')[0] == '/maxlikes':
        finder = InstRequest()
        name = text.split(':')[1]
        try:
            likes = finder.likes_on_posts(name)
        except ValueError:
            finder.close_driver()
            return f"I could not find a user /{name}."
        likes = sorted(likes)
        finder.close_driver()
        return f"The maximum number of likes on an account /{name} is {str(likes[-1])}."

    if text.split(':')[0] == '/sumoflikes':
        finder = InstRequest()
        name = text.split(':')[1]
        try:
            likes = finder.likes_on_posts(name)
        except ValueError:
            finder.close_driver()
            return f"I could not find a user /{name}."
        finder.close_driver()
        return f"The sum of likes on an account /{name} is {sum(likes)}."

    if text.split(':')[0] == '/urls':
        finder = InstRequest()
        name = text.split(':')[1]
        try:
            urls = finder.all_posts(name)
        except ValueError:
            finder.close_driver()
            return f"I could not find a user /{name}"
        finder.close_driver()
        return f"An account {name} has {len(urls)} posts:\n" + sum(urls)


@app.route("/", methods=["GET", "POST"])
def receive_update():
    if request.method == "POST":
        edit = ""
        if 'edited_message' in request.json:
            edit = "edited_"
        chat_id = request.json[edit + "message"]["chat"]["id"]
        try:
            mess = make_text(request.json[edit + "message"]["text"])
            send_message(chat_id, mess)
        except ValueError:
            send_message(chat_id, "I do not understand you.")
            request.json.clear()
    return {"ok": True}
