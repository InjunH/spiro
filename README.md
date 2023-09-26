### spiro

### 1. download_audio_from_youtube

유튜브에서 mp4 파일을 추출합니다.

- 기존에는 csv 파일 0번째 column 을 읽어서 현재 날짜인 행만 읽어와서 다운로드 했던 것을 수정했습니다.
- 23.09.27 비고란에 다운로드 완료가 아니라면 다운로드 처리

- 명령어
  python download_audio_from_youtube.py
- 실행
  youtube_task_list.csv 파일을 읽어서 순차적으로 유튜브 파일을 MP4 형태로 다운로드 합니다.
- 결과
  result 폴더 안에 현재일 기준으로 mp4 파일이 생성됩니다.

### 2.0 media_files_make_text.py

vito api 인증 후 mp4 파일로 추출된 결과 파일을 json , txt 형태로 저장합니다.
입니다.

- 23.09.27 파일명을 mp3_files_make_text.py -> media_files_make_text.py 로 변경 했습니다.
- 23.09.27 리팩토링 및 로거 추가

- 명령어
  python media_files_make_text.py
- 실행
  1. vitoAPi 인증
  2. result/현재날짜/ 경로에 있는 mp4 읽어오기
  3. 순서대로 stt 요청
     3.1 요청 결과 실패시 1분 후 재요청 (최대 10번 실행)
  4. 요청된 파일 결과 result/현재날짜 에 저장
- 결과
  result 폴더 안에 현재일 기준으로 mp4 파일이 생성됩니다.

### 3.0 speech_analysis.py

분석된 텍스트 파일을 통해 불필요한 말버릇을 체크하여 csv 형태로 만들어줍니다.
2에서 생성된 txt 파일을 찾아서 csv 파일로 만들어줍니다.

- 23.09.27 리팩토링 및 로거 추가

- 명령어
  python speech_analysis.py
- 실행
  txt 파일을 읽어 csv 파일을 만들어 줍니다.
- 결과
  result 폴더 안에 현재일 기준으로 csv 파일이 생성됩니다.

### 4.0 analysis_to_chart.py

추출된 csv 파일을 통해 2D Bar chart를 만들어줍니다.

- 23.09.27 리팩토링 및 로거 추가

- 명령어
  python analysis_to_chart.py
- 실행
  csv 파일을 읽어 차트를 만들어 줍니다.
- 결과
  result 폴더 안에 현재일 기준으로 png 파일이 생성됩니다.
