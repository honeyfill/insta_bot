from selenium import webdriver
from bs4 import BeautifulSoup
import time
import random
from data import driverway, img, anonymous, myself, trainer
from selenium.webdriver.chrome.options import Options
import csv


def del_sym(candidate):
    ans = ""
    for sym in candidate:
        if ord(sym) > ord('9') or ord(sym) < ord('0'):
            continue
        ans += sym
    return ans


def open_driver():
    options = Options()
    options.add_argument("user-data-dir=C:\\Users\\Sema\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2")
    return webdriver.Chrome(executable_path=driverway, chrome_options=options)


def get_followers(name):
    driver = open_driver()
    driver.get(f"https://www.instagram.com/{name}")
    followers = []
    url = '/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span'
    followers_button = driver.find_element_by_xpath(url)
    followers_count = followers_button.get_attribute("title")
    
    if " " in followers_count:
        followers_count = "".join(followers_count.split())

    followers_count = int(followers_count)
    scrolls = followers_count // 12
    followers_button.click()
    time.sleep(3)
    followers_window = driver.find_element_by_xpath("/html/body/div[6]/div/div/div[2]")

    for i in range(scrolls):
        driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_window)
        time.sleep(random.randrange(2, 4))
    all_urls_div = followers_window.find_elements_by_tag_name("li")

    for url in all_urls_div:
        followers.append(url.find_element_by_tag_name("a").get_attribute("href"))

    with open(f"C:\\Users\\Sema\\Documents\\{name}.txt", 'w') as file:
        for url in followers:
            file.write(url + '\n')
    driver.quit()


def write_to_csv(name):
    driver = open_driver()
    with open(f"C:\\Users\\Sema\\Documents\\{name}.txt") as file:
        to_write = []
        for line in file.readlines():
            account = line.split("\n")[0]
            driver.get(account)

            if account == myself or driver.find_elements_by_xpath(img) == []:
                continue

            time.sleep(random.randrange(2, 4))

            soup = BeautifulSoup(driver.page_source, 'lxml')
            quotes = soup.find('meta', {'name': 'description'})['content'].split('п')
            followers, following, posts = int(del_sym(quotes[0])), int(del_sym(quotes[2])), int(del_sym(quotes[4]))

            avatar = driver.find_element_by_xpath('/html/body/div[1]/section/main/div/header/div/div/span/img')
            driver.get(avatar.get_attribute('src'))
            soup = BeautifulSoup(driver.page_source, 'lxml')
            head = soup.find('title')
            head = str(head).split('>')[1].split('<')[0]

            if head == anonymous:
                ava = 0
            else:
                ava = 1
            to_write.append({'url': line, 'followers': followers, 'following': following, 'posts': posts, 'ava': ava})

    with open(f"C:\\Users\\Sema\\Documents\\{name}.csv", "w") as file:
        fieldnames = ['url', 'followers', 'following', 'posts', 'ava']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(to_write)

    return "Data is ready."


if __name__ == '__main__':
    print(get_followers(trainer))
