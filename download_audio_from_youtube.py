import os
import csv
from datetime import datetime
from pytube import YouTube
from logger_config import setup_logger



def authenticate_youtube_video(row, today, download_path, logger):
    try:
        yt = YouTube(row[1])
        video_id = row[1].split("v=")[1].split("&")[0]
        filename = f"{video_id}_{today}.mp4"  # 확장자 .mp4 추가
        logger.info(f"1. 음성 파일 다운로드 - 다운로드 진행 중: {filename}")
        stream = yt.streams.filter(only_audio=True, file_extension="mp4").first()
        stream.download(output_path=download_path, filename=filename)
        row[0] = today  # 현재 날짜로 업데이트
        row[2] = yt.author
        row[3] = yt.title
        row[4] = "다운로드 완료"
        logger.info(f"Download completed for video: {filename}")
    except Exception as e:
        logger.error(f"{row[1]} 1. 음성 파일 다운로드 - 다운로드 중 오류 발생: {e}")
        row[4] = "다운로드 실패"


def update_csv_file(csv_path, updated_rows):
    with open(csv_path, 'w', encoding='utf-8-sig', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(updated_rows)

def run():
    logger = setup_logger()
    logger.info("1. 음성 파일 다운로드 - 시작")

    csv_path = "youtube_task_list.csv"
    today = datetime.now().strftime('%Y%m%d')
    download_path = f"result/{today}"

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    updated_rows = []

    logger.info("Reading CSV file.")
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as file:
        reader = csv.reader(file)
        headers = next(reader)
        updated_rows.append(headers)

        for row in reader:
            if row[4] != "다운로드 완료":
                authenticate_youtube_video(row, today, download_path, logger)
            updated_rows.append(row)

    update_csv_file(csv_path, updated_rows)
    logger.info("1. 음성 파일 다운로드 - 완료")

if __name__ == "__main__":
    run()
    
