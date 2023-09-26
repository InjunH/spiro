# master_script.py

import download_audio_from_youtube
import media_files_make_text
import speech_analysis
import analysis_to_chart

def main():
    # 1. 유튜브에서 mp4 파일 추출
    download_audio_from_youtube.run()

    # 2. vito api를 사용하여 mp4 파일을 텍스트로 변환
    media_files_make_text.run()

    # 3. 텍스트 분석 및 csv 파일 생성
    speech_analysis.run()

    # 4. csv 파일을 사용하여 차트 생성
    analysis_to_chart.run()

if __name__ == "__main__":
    main()
