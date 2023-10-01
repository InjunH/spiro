from decouple import config
import requests
import json
import sys
import os
from datetime import datetime
import time
from logger_config import setup_logger

logger = setup_logger()

def authenticate_vito(CLIENT_ID, CLIENT_SECRET):
    try:
        resp = requests.post(
            'https://openapi.vito.ai/v1/authenticate',
            data={'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET}
        )
        resp.raise_for_status()
        response_data = resp.json()
        access_token = response_data['access_token']
        logger.info("2. 음성 파일 txt 변환 - 인증 성공! Access Token: " + access_token)
        return access_token
    except requests.HTTPError as e:
        handle_http_error(e)
        sys.exit(1)

def call_vito_api_with_token(file_path, access_token):
    config = {
        "use_diarization": True,
        "diarization": {
            "spk_count": 2
        },
        "use_multi_channel": False,
        "use_itn": False,
        "use_disfluency_filter": False,
        "use_profanity_filter": False,
        "use_paragraph_splitter": True,
        "paragraph_splitter": {
            "max": 50
        }
    }
    try:
        with open(file_path, 'rb') as file:
            resp = requests.post(
                'https://openapi.vito.ai/v1/transcribe',
                headers={'Authorization': f'Bearer {access_token}'},
                data={'config': json.dumps(config)},
                files={'file': file}
            )
        resp.raise_for_status()
        response_data = resp.json()
        if 'id' in response_data:
            transcribe_id = response_data['id']
            logger.info(f"2. 음성 파일 txt 변환 - 파일 {file_path} 처리 완료. TRANSCRIBE_ID: {transcribe_id}")
            return transcribe_id
        else:
            logger.error(f"2. 음성 파일 txt 변환 - 파일 {file_path} 처리 중 알 수 없는 응답: {response_data}")
            return None
    except requests.HTTPError as e:
        handle_http_error(e)
        sys.exit(1)

def get_transcribe_result(transcribe_id, file_name, access_token, today, retry_count=0):
    try:
        resp = requests.get(
            f'https://openapi.vito.ai/v1/transcribe/{transcribe_id}',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        resp.raise_for_status()

        # 응답 처리
        response_data = resp.json()
        print(f"TRANSCRIBE_ID {transcribe_id}")

        # status가 completed인 경우
        if response_data.get('status') == 'completed':
            # 파일명 생성 (확장자 제거하고 .json 및 .txt 추가)
            base_file_name = os.path.splitext(file_name)[0]
            json_file_path = os.path.join(f"result/{today}", base_file_name + ".json")
            txt_file_path = os.path.join(f"result/{today}", base_file_name + ".txt")

            # JSON 파일로 저장
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(response_data, json_file, ensure_ascii=False, indent=4)
            logger.info(f"2. 음성 파일 txt 변환 - 결과가 {json_file_path}에 저장되었습니다.")

            # TXT 파일로 저장
            utterances = response_data.get('results', {}).get('utterances', [])
            with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                for index, utterance in enumerate(utterances, 1):
                    msg = utterance.get('msg', '')
                    txt_file.write(f"index {index} : {msg}\n")
            logger.info(f"2. 음성 파일 txt 변환 - 텍스트 결과가 {txt_file_path}에 저장되었습니다.")


        # status가 transcribing이고 재시도 횟수가 10 미만인 경우
        elif response_data.get('status') == 'transcribing' and retry_count < 10:
            logger.info("2. 음성 파일 txt 변환 - 결과가 아직 준비되지 않았습니다. 30초 후 다시 시도합니다.")
            time.sleep(30)  # 30초 대기
            get_transcribe_result(transcribe_id, file_name, access_token, today, retry_count + 1)  # 여기에 file_name을 추가
        elif retry_count >= 10:
            logger.info("2. 음성 파일 txt 변환 - 최대 시도 횟수에 도달했습니다. 결과를 가져오지 못했습니다.")
    
    except requests.HTTPError as e:
        handle_http_error(e)
        sys.exit(1)
        
def handle_http_error(e):
    status_code = e.response.status_code
    error_messages = {
        400: "잘못된 파라미터 요청",
        401: "인증실패",
        500: "서버 오류"
    }
    error_message = error_messages.get(status_code, "알 수 없는 오류")
    logger.error(f"2. 음성 파일 txt 변환 - 오류 발생! 코드: {status_code}, 메시지: {error_message}")

def was_file_processed(file_name, today):
    # 해당 날짜의 결과 폴더에서 이미 처리된 파일들의 목록을 가져옵니다.
    result_folder = f"result/{today}"
    if not os.path.exists(result_folder):
        return False

    # 확장자를 제거한 파일명
    base_file_name = os.path.splitext(file_name)[0]
    
    # JSON 혹은 TXT 파일의 존재 여부로 처리 여부를 확인합니다.
    json_file_path = os.path.join(result_folder, base_file_name + ".json")
    txt_file_path = os.path.join(result_folder, base_file_name + ".txt")
    
    return os.path.exists(json_file_path) or os.path.exists(txt_file_path)

def process_files_in_folder(folder_path, access_token, today):
    if not os.path.exists(folder_path):
        logger.error(f"{folder_path} 2. 음성 파일 txt 변환 - 폴더가 존재하지 않습니다.")
        return

    existing_files = set(os.listdir(folder_path))

    for file_name in existing_files:
        if file_name.endswith('.mp4') and not was_file_processed(file_name, today):
            file_path = os.path.join(folder_path, file_name)
            transcribe_id = call_vito_api_with_token(file_path, access_token)
            if transcribe_id:
                logger.info("2. 음성 파일 txt 변환 - 15초 대기 후 결과를 가져옵니다.")
                time.sleep(15)
                get_transcribe_result(transcribe_id, file_name, access_token, today, retry_count=0)

def run():
    logger.info("2. 음성 파일 txt 변환 - 시작")
    CLIENT_ID = config('CLIENT_ID')
    CLIENT_SECRET = config('CLIENT_SECRET')
    access_token = authenticate_vito(CLIENT_ID, CLIENT_SECRET)

    today = datetime.now().strftime('%Y%m%d')
    folder_path = f"result/{today}"

    process_files_in_folder(folder_path, access_token, today)
    
if __name__ == "__main__":
    run()
    
