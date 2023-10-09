import re
import os
from collections import Counter
import pandas as pd
from datetime import datetime
import json
import math
from logger_config import setup_logger
from constants import UNNECESSARY_WORDS

# Constants
BASE_DIR = 'result'
TODAY = datetime.now().strftime('%Y%m%d')
INPUT_DIR_PATH = os.path.join(BASE_DIR, TODAY)



logger = setup_logger()

def read_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    logger.info(f"3. 말버릇 분석 - {file_path} 파일을 읽었습니다.")
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
    
    # 'Needed or Not' 기준으로 행 카운트
    counts = df['Needed or Not'].value_counts().to_dict()

    # True와 False에 대한 디폴트 값을 설정
    counts.setdefault(True, 0)
    counts.setdefault(False, 0)

    return df, counts

def get_duration_from_json(json_path):
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    utterances = data.get("results", {}).get("utterances", [])
    total_duration = sum([utterance.get("duration", 0) for utterance in utterances])

    return total_duration

def get_total_unnecessary_word_count(words):
    unnecessary_word_counts = Counter(word for word in words if word in UNNECESSARY_WORDS)
    return sum(unnecessary_word_counts.values())

def split_into_sentences(text):
    """텍스트를 문장 단위로 분리합니다."""
    return re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

def categorize_sentences_by_words(text):
    """불필요한 단어가 포함된 문장과 그렇지 않은 문장을 분류합니다."""
    sentences = split_into_sentences(text)
    
    sentences_with_unnecessary_words = []
    sentences_without_unnecessary_words = []
    
    for sentence in sentences:
        if any(word in sentence for word in UNNECESSARY_WORDS):
            sentences_with_unnecessary_words.append(sentence)
            print(sentence)
        else:
            sentences_without_unnecessary_words.append(sentence)
    
    return len(sentences_with_unnecessary_words), len(sentences_without_unnecessary_words)

def get_unnecessary_words_used(words):
    """텍스트에서 사용된 불필요한 단어들의 리스트와 그 단어의 사용 횟수를 반환합니다."""
    unnecessary_word_counts = Counter(word for word in words if word in UNNECESSARY_WORDS)
    return [{"word": word, "count": count} for word, count in unnecessary_word_counts.items()]


def save_to_json(df, json_path, words, counts, total_unnecessary_word_count, num_sentences_with_unnecessary, num_sentences_without_unnecessary, used_unnecessary_words):
    # 화자 번호 추출
    spk_num = int(re.search(r'_spk(\d+)', json_path).group(1))
    spk_index = int(re.search(r'_spk(\d+)', json_path).group(1))

    # 모든 duration 값을 가져와서 합치기
    total_duration_ms = 0
    base_file_name = os.path.splitext(json_path)[0].replace(f"_spk{spk_num}_origin_result", "")
    while True:
        spk_json_path = f"{base_file_name}_spk{spk_num}_origin.json"
        if not os.path.exists(spk_json_path):
            break
        total_duration_ms += get_duration_from_json(spk_json_path)
        spk_num += 1

    # ms를 분과 초로 변환
    minutes, remainder = divmod(total_duration_ms, 60000)
    seconds = math.ceil(remainder / 1000)

    total_duration_minutes_seconds = f"{minutes}분 {seconds}초"

     # 분당 불필요하게 사용된 단어의 횟수 계산
    total_duration_minutes = total_duration_ms / 60000  # ms를 분으로 변환
    unnecessary_words_per_minute = total_unnecessary_word_count / total_duration_minutes
    unnecessary_words_per_minute = round(unnecessary_words_per_minute)
    
    # 데이터프레임에서 원하는 JSON 형식으로 데이터 변환
    data = {
        "spk": spk_index,
        "totalDuration": total_duration_minutes_seconds,
        "unnecessaryWordsSpokenPerMin" : unnecessary_words_per_minute,
        "mostUsedWords": df.apply(lambda row: {
            "word": row['Most Used Words'],
            "count": row['Count'],
            "isNeeded": row['Needed or Not']
        }, axis=1).tolist(),
        "unecessaryWordsList": used_unnecessary_words,
        "words": {
            "totalWordsCnt" : len(words),
            "totalUnnecessaryWordsCnt" : total_unnecessary_word_count,
            "totalNecessaryWordsCnt" : len(words) - total_unnecessary_word_count,
            "necessaryWordsGroupCnt" : counts.get(True, 0),
            "unnecessaryWordsGroupCnt" : counts.get(False, 0),
        },
        "sentences": {
            "withUnnecessaryWords": num_sentences_with_unnecessary,
            "withoutUnnecessaryWords": num_sentences_without_unnecessary
        }
    }
    
    # JSON 파일로 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    logger.info(f"3. 말버릇 분석 - {json_path}에 데이터를 저장했습니다.")

def was_file_processed(file_name):
    # 확장자를 제거한 파일명
    base_file_name = os.path.splitext(file_name)[0]
    
    # CSV 파일의 존재 여부로 처리 여부를 확인합니다.
    csv_file_path = os.path.join(INPUT_DIR_PATH, base_file_name + ".csv")
    
    return os.path.exists(csv_file_path)

def run():
    if not os.path.exists(INPUT_DIR_PATH):
        logger.error(f"3. 말버릇 분석 - {INPUT_DIR_PATH} 폴더가 존재하지 않습니다.")
        return

    for file_name in os.listdir(INPUT_DIR_PATH):
        if re.match(r'.*_spk\d+_origin\.txt', file_name) and not was_file_processed(file_name):
            input_file_path = os.path.join(INPUT_DIR_PATH, file_name)
            base_name = os.path.splitext(file_name)[0]
            output_json_path = os.path.join(INPUT_DIR_PATH, base_name + "_result.json")

            text = read_file(input_file_path)
            words = normalize_and_tokenize(text)
            df, counts = analyze_words(words)
            top_20_df = df.head(20)
            total_unnecessary_word_count = get_total_unnecessary_word_count(words)

            num_sentences_with_unnecessary, num_sentences_without_unnecessary = categorize_sentences_by_words(text)

            used_unnecessary_words = get_unnecessary_words_used(words)

            save_to_json(top_20_df, output_json_path, words, counts, total_unnecessary_word_count, num_sentences_with_unnecessary, num_sentences_without_unnecessary, used_unnecessary_words)

            logger.info(f"3. 말버릇 분석 - {output_json_path}에 대한 상위 20개 단어 분석을 완료했습니다.")

if __name__ == "__main__":
    run()
