import re
import os
from collections import Counter
import pandas as pd
from datetime import datetime
from logger_config import setup_logger

# Constants
BASE_DIR = 'result'
TODAY = datetime.now().strftime('%Y%m%d')
INPUT_DIR_PATH = os.path.join(BASE_DIR, TODAY)

# List of unnecessary words
UNNECESSARY_WORDS = [
    "가지고", "거", "거는", "거든", "거든요", "게", "그", "그거", "그게", "그냥", "그래도", "그래서", "그러고 나서", 
    "그러고 보니", "그러고는", "그러니까", "그러다가", "그러다보니", "그러면", "그런 거야", "그런 거지", "그런 건", 
    "그런 것", "그런 것 같아", "그런 것만", "그런 것보다", "그런 것에", "그런 것으로", "그런 것은", "그런 것을", "그런 것이", 
    "그런 것이다", "그런 것이라", "그런 것이라고", "그런 것이라면", "그런 것이라서", "그런 것이면", "그런 것이었다", "그런 것인", 
    "그런 것인가", "그런 것인데", "그런 것일", "그런 것일까", "그런 것임", "그런 것처럼", "그런데", "그럼", "그럼에도 불구하고", 
    "그렇게", "그렇게 됐어", "그렇지 않아?", "그렇지만", "그리고", "근데", "기로", "기에", "나", "네요", "니까", "다", 
    "더니", "더라", "더라고요", "데요", "되게", "든요", "또", "막", "뭐", "뭐랄까", "뭐지", "뭔가", "별로", "서요", "아", 
    "아니야", "아마", "아마도", "아무래도", "아무튼", "아서", "아이구", "아이쿠", "안", "약간", "얘기를 좀", "어", "어느", 
    "어디", "어디까지", "어디로", "어디서", "어디에", "어때", "어땠어", "어떡해", "어떤", "어떻게", "어떻게 보면", "어떻게든", 
    "어쨌든", "어쩌다가", "어쩌면", "어쩜", "어찌나", "에요", "예요", "왜냐하면", "요", "음", "이", "이거", "이게", "이런", 
    "이런 식으로", "이런저런", "이렇게", "이렇게저렇게", "이상하게", "이제", "자", "저", "저거", "저게", "저렇게", "좀", "죠", 
    "지요", "진짜", "헐", "확실히"
]

logger = setup_logger()

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    logger.info(f"{file_path} 파일을 읽었습니다.")
    return content

def normalize_and_tokenize(text):
    normalized_text = re.sub(r'[^가-힣\s]', '', text)
    return normalized_text.split()

def analyze_words(words):
    word_count = Counter(words)
    df = pd.DataFrame(list(word_count.items()), columns=['Most Used Words', 'Count'])
    df['Needed or Not'] = ~df['Most Used Words'].isin(UNNECESSARY_WORDS)
    df.sort_values(by='Count', ascending=False, inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

def save_to_csv(df, csv_path):
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    logger.info(f"{csv_path}에 데이터를 저장했습니다.")

def run():
    if not os.path.exists(INPUT_DIR_PATH):
        logger.error(f"{INPUT_DIR_PATH} 폴더가 존재하지 않습니다.")
        return

    for file_name in os.listdir(INPUT_DIR_PATH):
        if file_name.endswith('.txt'):
            input_file_path = os.path.join(INPUT_DIR_PATH, file_name)
            output_csv_path = os.path.join(INPUT_DIR_PATH, file_name.replace('.txt', '.csv'))

            text = read_file(input_file_path)
            words = normalize_and_tokenize(text)
            df = analyze_words(words)
            top_20_df = df.head(20)
            save_to_csv(top_20_df, output_csv_path)
            logger.info(f"{output_csv_path}에 대한 상위 20개 단어 분석을 완료했습니다.")

# if __name__ == "__main__":
#     run()





