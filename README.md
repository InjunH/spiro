# SPIRO - Speech Pattern Analysis Tool
> YouTube 동영상의 음성을 분석하여 말버릇 패턴을 시각화하는 도구

## 📌 개요
SPIRO는 YouTube 동영상에서 음성을 추출하고, STT(Speech-to-Text) 기술을 활용하여 텍스트로 변환한 후, 말버릇 패턴을 분석하여 시각화하는 파이썬 기반 도구입니다. 발표나 스피치 능력 향상을 위해 불필요한 말버릇을 객관적으로 파악하고 개선할 수 있도록 돕습니다.

## 🚀 주요 기능
- **YouTube 음성 추출**: YouTube URL로부터 음성(MP4) 파일 자동 다운로드
- **음성-텍스트 변환**: VITO API를 활용한 고품질 STT 변환
- **말버릇 분석**: 한국어 불필요 단어 및 말버릇 패턴 감지
- **데이터 시각화**: 분석 결과를 차트로 시각화하여 직관적 파악
- **배치 처리**: CSV 파일을 통한 다중 영상 일괄 처리

## 📁 프로젝트 구조
```
spiro/
├── master_script.py              # 메인 실행 스크립트
├── download_audio_from_youtube.py # YouTube 음성 다운로드
├── media_files_make_text.py      # STT 변환 처리
├── speech_analysis.py            # 말버릇 패턴 분석
├── analysis_to_chart.py          # 차트 생성
├── constants.py                  # 불필요 단어 사전
├── logger_config.py              # 로깅 설정
├── youtube_task_list.csv         # 처리할 YouTube URL 목록
└── result/                       # 결과 파일 저장 디렉토리
    └── YYYYMMDD/                 # 날짜별 결과 폴더
```

## 🛠️ 설치 및 환경 설정

### 필수 요구사항
- Python 3.7 이상
- VITO API 인증 정보

### 의존성 패키지
```bash
pip install pytube pandas matplotlib
```

### VITO API 설정
VITO API 사용을 위해 인증 정보가 필요합니다. 
[VITO API](https://developers.vito.ai) 에서 API 키를 발급받으세요.

## 📖 사용 방법

### 1. 전체 파이프라인 실행
모든 과정을 한 번에 실행하려면:
```bash
python master_script.py
```

### 2. 개별 모듈 실행

#### 1단계: YouTube 음성 다운로드
```bash
python download_audio_from_youtube.py
```
- `youtube_task_list.csv` 파일에서 URL을 읽어 음성 파일 다운로드
- 다운로드 완료된 항목은 자동으로 마킹
- 결과: `result/YYYYMMDD/` 폴더에 MP4 파일 저장

#### 2단계: 음성을 텍스트로 변환
```bash
python media_files_make_text.py
```
- VITO API를 통해 MP4 파일을 텍스트로 변환
- 실패 시 최대 10회 재시도 (1분 간격)
- 결과: JSON 및 TXT 형식으로 저장

#### 3단계: 말버릇 분석
```bash
python speech_analysis.py
```
- 텍스트 파일 분석 및 불필요 단어 검출
- 단어 빈도수 계산 및 분류
- 결과: CSV 파일로 분석 결과 저장

#### 4단계: 시각화 차트 생성
```bash
python analysis_to_chart.py
```
- CSV 데이터를 기반으로 2D 막대 차트 생성
- 결과: PNG 이미지 파일로 저장

## 📝 CSV 파일 형식

### youtube_task_list.csv
```csv
작업일,유튜브 주소,채널명,타이틀,비고
20230927,https://www.youtube.com/watch?v=...,채널명,동영상 제목,다운로드 완료
```

## 📊 출력 결과
- **MP4 파일**: 추출된 오디오 파일
- **TXT 파일**: STT 변환된 텍스트
- **JSON 파일**: 상세 STT 결과 (타임스탬프 포함)
- **CSV 파일**: 단어 빈도 분석 결과
- **PNG 파일**: 시각화 차트

## ⚙️ 설정 및 커스터마이징

### 불필요 단어 사전 수정
`constants.py` 파일에서 `UNNECESSARY_WORDS` 리스트를 수정하여 분석할 말버릇을 커스터마이징할 수 있습니다.

### 로깅 설정
`logger_config.py`를 통해 로깅 레벨 및 형식을 조정할 수 있습니다.

## 🔄 업데이트 내역
- **2023.09.27**
  - 파일명 변경: `mp3_files_make_text.py` → `media_files_make_text.py`
  - 전체 모듈 리팩토링 및 로거 기능 추가
  - CSV 비고란 기반 다운로드 로직 개선

## 📄 라이선스
이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🤝 기여
버그 리포트, 기능 제안, 풀 리퀘스트를 환영합니다!
