import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from logger_config import setup_logger

# Logger 설정
logger = setup_logger()

# Constants
BASE_DIR = 'result'
TODAY = datetime.now().strftime('%Y%m%d')
CSV_DIR_PATH = os.path.join(BASE_DIR, TODAY)

# 한글 폰트 설정
font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
font_name = fm.FontProperties(fname=font_path, size=10).get_name()
plt.rc('font', family=font_name)

def plot_chart(csv_path):
    df = pd.read_csv(csv_path)
    plt.figure(figsize=(plt.gcf().get_size_inches()[0] * 1.5, plt.gcf().get_size_inches()[1]))

    x_data = df.iloc[:, 0]
    y_data = df.iloc[:, 1]
    color_data = df.iloc[:, 2]
    colors = ['b' if value else 'r' for value in color_data]

    plt.bar(x_data, y_data, color=colors)
    plt.xlabel('가장 많이 사용된 단어')
    plt.ylabel('횟수')
    plt.title('단어 사용 빈도')
    legend_labels = ['True', 'False']
    legend_handles = [plt.Line2D([0], [0], color='b', lw=4), plt.Line2D([0], [0], color='r', lw=4)]
    plt.legend(legend_handles, legend_labels, title='Needed or Not')
    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()

    image_file_name = os.path.basename(csv_path).replace('.csv', '.png')
    image_path = os.path.join(CSV_DIR_PATH, image_file_name)
    
    plt.savefig(image_path, dpi=300)
    logger.info(f"그래프 이미지가 {image_path}에 저장되었습니다.")

def run():
    if not os.path.exists(CSV_DIR_PATH):
        logger.error(f"{CSV_DIR_PATH} 폴더가 존재하지 않습니다.")
        return

    for csv_file in os.listdir(CSV_DIR_PATH):
        if csv_file.endswith('.csv'):
            csv_path = os.path.join(CSV_DIR_PATH, csv_file)
            plot_chart(csv_path)

# if __name__ == "__main__":
#     run()
