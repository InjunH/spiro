from decouple import config
import requests
import json
import sys
import os
from datetime import datetime
import time


CLIENT_ID = config('CLIENT_ID')
CLIENT_SECRET = config('CLIENT_SECRET')

# 전역 변수로 access_token 저장 (인증 로직에서 값을 할당)
access_token = None

# vito 인증
try:
    resp = requests.post(
        'https://openapi.vito.ai/v1/authenticate',
        data={'client_id': CLIENT_ID,'client_secret': CLIENT_SECRET}
    )
    resp.raise_for_status()
    response_data = resp.json()
    access_token = response_data['access_token']
    print("인증 성공! Access Token:", access_token)

except requests.HTTPError as e:
    status_code = e.response.status_code
    error_messages = {
        400: "잘못된 파라미터 요청",
        401: "인증실패",
        500: "서버 오류"
    }
    error_message = error_messages.get(status_code, "알 수 없는 오류")
    print(f"오류 발생! 코드: {status_code}, 메시지: {error_message}")
    sys.exit(1)


def call_vito_api_with_token(file_path):
    if not access_token:
        print("Access Token이 없습니다. 먼저 인증을 진행해주세요.")
        sys.exit(1)

    config = {}
    try:
        with open(file_path, 'rb') as file:
            resp = requests.post(
                'https://openapi.vito.ai/v1/transcribe',
                headers={'Authorization': f'Bearer {access_token}'},
                data={'config': json.dumps(config)},
                files={'file': file}
            )
        resp.raise_for_status()

        # 응답 처리
        response_data = resp.json()
        if 'id' in response_data:
            transcribe_id = response_data['id']
            print(f"파일 {file_path} 처리 완료. TRANSCRIBE_ID: {transcribe_id}")
            return transcribe_id  # TRANSCRIBE_ID 값을 반환
        else:
            print(f"파일 {file_path} 처리 중 알 수 없는 응답: {response_data}")
            return None

    except requests.HTTPError as e:
        error_messages = {
            400: {
                "H0001": "잘못된 파라미터 요청",
                "H0010": "지원하지 않는 파일 포맷"
            },
            401: {"H0002": "유효하지 않은 토큰"},
            413: {
                "H0005": "파일 사이즈 초과",
                "H0006": "파일 길이 초과"
            },
            429: {"A0001": "사용량 초과"},
            500: {"E500": "서버 오류"}
        }

        error_code = e.response.json().get('code', None)
        status_code = e.response.status_code
        error_message = error_messages.get(status_code, {}).get(error_code, "알 수 없는 오류")
        print(f"API 호출 중 오류 발생! 파일: {file_path}, 코드: {status_code}, 메시지: {error_message}")
        sys.exit(1)

def get_transcribe_result(transcribe_id, retry_count=0):
    try:
        resp = requests.get(
            f'https://openapi.vito.ai/v1/transcribe/{transcribe_id}',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        resp.raise_for_status()

        # 응답 처리
        response_data = resp.json()
        print(f"TRANSCRIBE_ID {transcribe_id}의 결과:", response_data)

        # status가 completed인 경우
        if response_data.get('status') == 'completed':
            # 파일명 생성 (확장자 제거하고 .json 및 .txt 추가)
            base_file_name = os.path.splitext(file_name)[0]
            json_file_path = os.path.join(f"result/{today}", base_file_name + ".json")
            txt_file_path = os.path.join(f"result/{today}", base_file_name + ".txt")

            # JSON 파일로 저장
            with open(json_file_path, 'w', encoding='utf-8') as json_file:
                json.dump(response_data, json_file, ensure_ascii=False, indent=4)
            print(f"결과가 {json_file_path}에 저장되었습니다.")

                # TXT 파일로 저장
            utterances = response_data.get('results', {}).get('utterances', [])
            with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
                for index, utterance in enumerate(utterances, 1):
                    msg = utterance.get('msg', '')
                    txt_file.write(f"index {index} : {msg}\n")
            print(f"텍스트 결과가 {txt_file_path}에 저장되었습니다.")


        # status가 transcribing이고 재시도 횟수가 10 미만인 경우
        elif response_data.get('status') == 'transcribing' and retry_count < 10:
            print("결과가 아직 준비되지 않았습니다. 1분 후 다시 시도합니다.")
            time.sleep(60)  # 1분 대기
            get_transcribe_result(transcribe_id, retry_count + 1)
        elif retry_count >= 10:
            print("최대 시도 횟수에 도달했습니다. 결과를 가져오지 못했습니다.")

    except requests.HTTPError as e:
        error_messages = {
            400: "잘못된 파라미터 요청",
            401: "유효하지 않은 토큰",
            500: "서버 오류"
        }
        status_code = e.response.status_code
        error_message = error_messages.get(status_code, "알 수 없는 오류")
        print(f"API 호출 중 오류 발생! TRANSCRIBE_ID: {transcribe_id}, 코드: {status_code}, 메시지: {error_message}")
        sys.exit(1)

# 오늘 날짜로 폴더 경로 생성
today = datetime.now().strftime('%Y%m%d')
folder_path = f"result/{today}"

# 해당 폴더 내의 모든 mp3 파일을 순회하면서 API 호출
if os.path.exists(folder_path):
    for file_name in os.listdir(folder_path):
        if file_name.endswith('.mp3'):
            file_path = os.path.join(folder_path, file_name)
            transcribe_id = call_vito_api_with_token(file_path)
            if transcribe_id:
                print("30초 대기 후 결과를 가져옵니다.")
                time.sleep(30)  # 30초 대기
                get_transcribe_result(transcribe_id)
else:
    print(f"{folder_path} 폴더가 존재하지 않습니다.")