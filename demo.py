import json, os
import datetime
import pickle
from dateutil import parser

import gradio as gr
from openai import OpenAI

OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

# 숙소와 그에 맞는 리뷰 데이터 매핑 맵
MAPPING = {
    '나이트리 용산' : './res/reviews.json',
    '글래드 마포' : './res/glad_mapo.json',
    '글래드 여의도' : './res/glad_yeouido.json'
}

# prompt 로드
with open('./res/prompt_1shot.pickle', 'rb') as f:
    PROMPT = pickle.load(f)

# 데이터 전처리
def preprocess_reviews(path='./res/reviews.json'):
    with open(path, 'r', encoding='utf-8') as f:
        review_list = json.load(f)
        
    reviews_good, reviews_bad = [], []
    
    current_date = datetime.datetime.now()
    date_boundary = current_date - datetime.timedelta(days=6*30)
    
    filtered_cnt = 0
    for r in review_list:
        review_date_str = r['date']
        # 몇 일전, 몇 시간전 등의 예외 케이스를 대응하기 위한 try~excpet
        try:
            review_date = parser.parse(review_date_str)
        except (ValueError, TypeError):
            # 최대 일주일간은 현재 날짜로 대체
            review_date = current_date
        
        if review_date < date_boundary:
            continue
        
        # 단순 길이 제한 
        if len(r['review']) < 30:
            filtered_cnt += 1
            continue
        
        if r['stars'] == 5:
            reviews_good.append('[REVIEW_START]' + r['review'] + '[REVIEW_END]')
        else:
            reviews_bad.append('[REVIEW_START]' + r['review'] + '[REVIEW_END]')
    
    ## api input token 제한이 발생한다면, 애라와 같이 입력값 제한이 필요(50개)
    # reviews_good = reviews_good[:min(len(reviews_good), 50)]
    # reviews_bad = reviews_bad[:min(len(reviews_bad), 50)]
    
    reviews_good_text = '\n'.join(reviews_good)
    reviews_bad_text = '\n'.join(reviews_bad)
    
    return reviews_good_text, reviews_bad_text

def summarize(reviews):
    prompt = PROMPT + '\n\n' + reviews
    
    client = OpenAI(
        api_key=OPENAI_API_KEY
    )
    completion = client.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=[{'role':'user', 'content':prompt}],
        temperature=0.0
    )
    
    return completion
    

def fn(accom_name):
    path = MAPPING[accom_name]
    reviews_good, reviews_bad = preprocess_reviews(path)
    
    summary_good = summarize(reviews_good).choices[0].message.content
    summary_bad = summarize(reviews_bad).choices[0].message.content
    
    return summary_good, summary_bad

def run_demo():
    demo = gr.Interface(
        fn=fn,
        inputs=[gr.Radio(['나이트리 용산', '글래드 마포', '글래드 여의도'], label='숙소')],
        outputs=[gr.Textbox(label='높은 평점 요약'), gr.Textbox(label='낮은 평점 요약')]
    )
    demo.launch()


if __name__ == '__main__':
    run_demo()