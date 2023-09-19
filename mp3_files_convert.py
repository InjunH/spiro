import requests
import json
import sys
import os
from datetime import datetime
import time
from decouple import config

# 상수
CLIENT_ID = config('CLIENT_ID')
CLIENT_SECRET = config('CLIENT_SECRET')

# 전역 변수
access_token = None

def authenticate_vito():
    """Vito API 인증 및 Access Token 획득"""
    global access_token
    try:
        resp = requests.post(
            'https://openapi.vito.ai/v1/authenticate',
            data={'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET}
        )
        resp.raise_for_status()
        access_token = resp.json().get('access_token')
        print("인증 성공! Access Token:")
    except requests.HTTPError:
        handle_http_error(resp)

def handle_http_error(response):
    """HTTP 오류 처리"""
    error_messages = {
        400: "잘못된 파라미터 요청",
        401: "인증실패",
        500: "서버 오류"
    }
    status_code = response.status_code
    error_message = error_messages.get(status_code, "알 수 없는 오류")
    print(f"오류 발생! 코드: {status_code}, 메시지: {error_message}")
    sys.exit(1)

def call_vito_api_with_token(file_path):
    """Vito API 호출 및 TRANSCRIBE_ID 반환"""
    if not access_token:
        print("Access Token이 없습니다. 먼저 인증을 진행해주세요.")
        sys.exit(1)

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
        return resp.json().get('id')
    except requests.HTTPError:
        handle_http_error(resp)

def get_transcribe_result(transcribe_id, file_name, retry_count=0):
    """결과 조회 및 파일 저장"""
    try:
        resp = requests.get(
            f'https://openapi.vito.ai/v1/transcribe/{transcribe_id}',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        resp.raise_for_status()
        response_data = resp.json()

        if response_data.get('status') == 'completed':
            save_results(response_data, file_name)
        elif response_data.get('status') == 'transcribing' and retry_count < 10:
            time.sleep(60)
            get_transcribe_result(transcribe_id, file_name, retry_count + 1)
    except requests.HTTPError:
        handle_http_error(resp)

def save_results(data, file_name):
    """결과를 JSON 및 TXT 파일로 저장"""
    today = datetime.now().strftime('%Y%m%d')
    base_file_name = os.path.splitext(file_name)[0]
    
    # JSON 저장
    json_path = os.path.join(f"result/{today}", base_file_name + ".json")
    with open(json_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

    # TXT 저장
    txt_path = os.path.join(f"result/{today}", base_file_name + ".txt")
    utterances = data.get('results', {}).get('utterances', [])
    with open(txt_path, 'w', encoding='utf-8') as txt_file:
        for index, utterance in enumerate(utterances, 1):
            msg = utterance.get('msg', '')
            txt_file.write(f"index {index} : {msg}\n")

if __name__ == "__main__":
    authenticate_vito()

    today = datetime.now().strftime('%Y%m%d')
    folder_path = f"result/{today}"

    if os.path.exists(folder_path):
        for file_name in os.listdir(folder_path):
            if file_name.endswith('.mp3'):
                file_path = os.path.join(folder_path, file_name)
                transcribe_id = call_vito_api_with_token(file_path)
                if transcribe_id:
                    time.sleep(30)
                    get_transcribe_result(transcribe_id, file_name)
    else:
        print(f"{folder_path} 폴더가 존재하지 않습니다.")
