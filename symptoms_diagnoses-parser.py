import requests
from bs4 import BeautifulSoup
import json
import codecs

diagnoses_url = 'https://fnkc-fmba.ru/zabolevaniya/'
page = requests.get(diagnoses_url)

diagnoses = {}

soup = BeautifulSoup(page.text, "html.parser")

for letter in soup.find_all('div', class_='letter_list_v2__wrap js-filter-container'):
    for diagnose in letter.find_all('a', href=True):
        diagnose_href = 'https://fnkc-fmba.ru' + diagnose['href']
        diagnoses[diagnose.text] = None  # инициализация ключа в словаре для каждого заболевания
        print(diagnose_href)

        diagnose_page = requests.get(diagnose_href)  # парсинг страницы с заболеванием(диагнозом)
        diagnose_soup = BeautifulSoup(diagnose_page.text, 'html.parser')

        for all_wp_tags in diagnose_soup.find_all("div", class_='col-md-8 offset-md-2'):
            if all_wp_tags.find('ul'):
                litags_list = []
                for litag in all_wp_tags.find('ul'):
                    litags_list.append(litag.text.strip())
                diagnoses[diagnose.text] = litags_list
                diagnoses[diagnose.text] = [item for item in diagnoses[diagnose.text] if item != ""]

print(diagnoses)
with codecs.open('diagnoses.txt', 'w', 'utf-8') as f:
    f.write(json.dumps(diagnoses, ensure_ascii=False))
