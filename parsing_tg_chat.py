import time
from datetime import datetime, timedelta
from fake_useragent import UserAgent

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


class TgChat:

    def remake_time(self, time: str):

        dict_time = {
            'days': ['дня', 'дней', 'день'],
            'hours': ['часов', 'час', 'часа', 'час назад'],
            'yesterday': ['вчера'],
            'minutes': ['минут', 'минуты', 'минуту']
        }

        time_split = time.split(' ')

        try:
            if len(time_split) > 1:
                if time_split[1] in dict_time['days']:
                    time = (datetime.today() - timedelta(days=int(time_split[0]))).strftime('%d.%m.%y')
                elif time_split[1] in dict_time['hours']:
                    time = (datetime.today() - timedelta(hours=int(time_split[0]))).strftime('%d.%m.%y %H:%M')
                elif time_split[1] in dict_time['minutes']:
                    time = (datetime.today() - timedelta(minutes=int(time_split[0]))).strftime('%d.%m.%y %H:%M')

            else:
                if time in dict_time['yesterday']:
                    time = (datetime.today() - timedelta(days=1)).strftime('%d.%m.%y')
                elif time in dict_time['minutes']:
                    time = (datetime.today() - timedelta(minutes=1)).strftime('%d.%m.%y %H:%M')
                elif time in dict_time['hours']:
                    time = (datetime.today() - timedelta(hours=1)).strftime('%d.%m.%y %H:%M')

        except:
            time = time

        return time

    def get_content(self, number_of_page: int):

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")

        link = f'https://tlgrm.ru/channels/@ostorozhno_novosti'
        browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=options)
        browser.get(link)
        time.sleep(2)

        for i in range(1, number_of_page):
            browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            button = browser.find_element(By.XPATH, '//button[text()="Загрузить ещё"]')
            button.click()
            time.sleep(2)

        content = self.parseTG(browser.page_source)
        browser.quit()

        return content

    def parseTG(self, page_source):
        soup = BeautifulSoup(page_source, 'lxml')
        list_items = soup.find_all('div', class_='channel-feed__brick')

        items = []
        for i in list_items:

            if i.find('time', class_='cfeed-card-header__datetime').text != 'Рекламный пост':

                try:
                    title = i.find('article', class_='cpost-wt-text').find('b').get_text().replace(f'\n\n', '').replace(
                        f'\n', '')
                except Exception:
                    title = ''

                article = i.find('article', class_='cpost-wt-text').text.replace(f'\n\n', '').replace(title,
                                                                                                      '').replace(f'\n',
                                                                                                                  '')
                time_of_public = self.remake_time(i.find('time', class_='cfeed-card-header__datetime').text)

                if title == '':
                    title = article
                    article = ''

                # print(f'title = {title}\narticle = {article}\n\n')

                if time_of_public == 'неделю назад':
                    break

                topic = {
                    'title': title.strip(),
                    'article': article.strip(),
                    'time_of_public': time_of_public
                }

                items.append(topic)

        return items
