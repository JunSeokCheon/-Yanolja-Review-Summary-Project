# 나인트리 프리미어 로카우스 호텔 서울 용산 : https://www.yanolja.com/reviews/domestic/10048873?sort=HOST_CHOICE
import json
import time

from bs4 import BeautifulSoup
from selenium import webdriver


URL = 'https://www.yanolja.com/reviews/domestic/10048873?sort=HOST_CHOICE'

def crawl_yanolja_reviews():
    review_list = []
    driver = webdriver.Chrome()
    driver.get(URL)
    
    time.sleep(3)
    
    scroll_count = 20
    for i in range(scroll_count):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        time.sleep(2)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    review_containers = soup.select('#__next > section > div > div.css-1js0bc8 > div > div > div')
    review_date = soup.select('#__next > section > div > div.css-1js0bc8 > div > div > div > div.css-1toaz2b > div > div.css-1ivchjf > p')

    for i in range(len(review_containers)):
        review_texts = review_containers[i].find('p', class_='content-text').text
        review_stars = review_containers[i].find_all('path', {'fill': '#FDBD00'})
        star_cnt = len(review_stars)
        date = review_date[i].text
        
        review_dict = {
            'review': review_texts,
            'stars': star_cnt,
            'date': date
        }
        
        review_list.append(review_dict)
    
    with open('./res/reviews.json', 'w', encoding='utf-8') as f:
        json.dump(review_list, f, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    crawl_yanolja_reviews()


