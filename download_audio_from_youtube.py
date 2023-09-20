import os
import csv
import logging
from datetime import datetime
from pytube import YouTube


# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# CSV 파일 경로
csv_path = "youtube_task_list.csv"

# 현재 날짜 가져오기
today = datetime.now().strftime('%Y%m%d')

# 다운로드 경로 설정
download_path = f"result/{today}"

# 다운로드 경로가 없으면 생성
if not os.path.exists(download_path):
    os.makedirs(download_path)

updated_rows = []  # 수정된 행들을 저장할 리스트

# CSV 파일 읽기
with open(csv_path, 'r', encoding='utf-8-sig', newline='') as file:
    reader = csv.reader(file)
    headers = next(reader)  # 첫 번째 행은 헤더
    updated_rows.append(headers)  # 헤더 추가

    # 각 행을 순회하며 작업
    for row in reader:
        if row[0] == today and row[4] != "다운로드 완료":
            try:
                yt = YouTube(row[1])
                video_id = row[1].split("v=")[1].split("&")[0]  # video ID 추출
                filename = f"{video_id}_{today}"  # 파일 이름 생성
                stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
                stream.download(output_path=download_path, filename=filename)  # 파일 이름 지정하여 다운로드
                # 채널명과 타이틀 업데이트
                row[2] = yt.author
                row[3] = yt.title
                row[4] = "다운로드 완료"
                logging.info(f"{yt.title} 다운로드 완료!")
            except Exception as e:
                logging.error(f"{row[1]} 다운로드 중 오류 발생: {e}")
        updated_rows.append(row)  # 수정된 행 추가

# CSV 파일 업데이트
with open(csv_path, 'w', encoding='utf-8-sig', newline='') as file:
    writer = csv.writer(file)
    writer.writerows(updated_rows)


logging.info("모든 작업 완료")
