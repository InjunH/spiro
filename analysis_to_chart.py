import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# 한글 폰트를 설정합니다.
font_path = "/System/Library/Fonts/AppleSDGothicNeo.ttc"  # 실제 Nanum 폰트의 위치에 맞게 변경해 주세요.
font_name = fm.FontProperties(fname=font_path, size=10).get_name()
plt.rc('font', family=font_name)

# CSV 파일을 읽어옵니다.
csv_path = '/Users/hwang-injun/Downloads/sample.csv'  # 앞서 저장한 CSV 파일 경로를 여기에 입력해주세요.
df = pd.read_csv(csv_path)

# 첫 번째 열을 x축으로, 두 번째 열을 y축으로, 세 번째 열은 색상을 결정하는데 사용합니다.
x_data = df.iloc[:, 0]  # 첫 번째 열
y_data = df.iloc[:, 1]  # 두 번째 열
color_data = df.iloc[:, 2]  # 세 번째 열

# 색상을 설정합니다.
colors = ['b' if value else 'r' for value in color_data]

# 막대 그래프를 그립니다.
bars = plt.bar(x_data, y_data, color=colors)

# 레이블과 타이틀을 추가합니다.
plt.xlabel('가장 많이 사용된 단어')
plt.ylabel('횟수')
plt.title('단어 사용 빈도')

# 범례를 추가합니다.
plt.legend([bars[0], bars[-1]], ['True', 'False'], title='Needed or Not')

# 그래프를 보여줍니다.
plt.show()
