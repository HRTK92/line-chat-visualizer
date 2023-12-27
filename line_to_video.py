import re
import argparse

import japanize_matplotlib
import matplotlib.pyplot as plt
from moviepy.editor import VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage


def validate_date(date):
    """日付のフォーマットが正しいかチェックする関数"""
    if re.match(r"^\d{4}/\d{1,2}/\d{1,2}", date):
        return date
    else:
        raise argparse.ArgumentTypeError(
            f"{date} is not a valid date\ne.g. 2020/1/1")


parser = argparse.ArgumentParser()
parser.add_argument("fileName", help="LINEのトーク履歴のファイル名")
parser.add_argument("-o", "--output", help="出力ファイル名")
parser.add_argument("-f", "--fps", help="FPS", default=10, type=int)
parser.add_argument("-s", "--start-date",
                    help="開始日 | 例: 2020/1/1", type=validate_date)
parser.add_argument("-dpi", "--dpi", help="解像度", default=150, type=int)
parser.add_argument("-lowest", "--lowest",
                    help="最低メッセージ数", default=0, type=int)
args = parser.parse_args()
fileName = args.fileName
output = args.output
fps = args.fps
startDate = args.start_date
dpi = args.dpi
lowest = args.lowest

# LINEのトーク履歴を分析
try:
    with open(fileName, "r", encoding="utf-8") as f:
        data = f.read()
except FileNotFoundError:
    print('\033[31m' + f'{fileName}が見つかりません。' + '\033[0m')
    exit()

print(f'{fileName}を分析を開始します。')

nowDate = None
isStart = False
user_messages = {}
for line in data.splitlines():
    try:
        if re.match(r"^\d{4}/\d{1,2}/\d{1,2}\(.+\)", line):
            if startDate:
                if line.startswith(startDate):
                    isStart = True
                if isStart:
                    nowDate = f"{line.split('/')[0]}-{line.split('/')[1].zfill(2)}-{line.split('/')[2].split('(')[0].zfill(2)}"
            else:
                nowDate = f"{line.split('/')[0]}-{line.split('/')[1].zfill(2)}-{line.split('/')[2].split('(')[0].zfill(2)}"
        if nowDate is not None and line != nowDate and line != "":
            if re.match(r"\d{1,2}:\d{1,2}", line):
                if line.endswith("が退出しました。"):
                    continue
                name = line.split()[1]
                if name not in user_messages:
                    user_messages[name] = {}
                if nowDate not in user_messages[name]:
                    user_messages[name][nowDate] = 0
                user_messages[name][nowDate] += 1
    except Exception as e:
        lineCount = len(data.splitlines())
        lineIndex = data.splitlines().index(line) + 1
        print(
            '\033[31m' + f'{lineIndex}行目のデータが正しくありません。' + '\033[0m')
        print(e)

dates = sorted(
    list(set([date for user in user_messages.values() for date in user.keys()])
         ))

if dates == []:
    print('\033[31m' + 'データが見つかりませんでした。' + '\033[0m')
    exit()

print('\033[32m' + f'{dates[0]} から {dates[-1]}のデータを読み込みました。' + '\033[0m')
print(f'ユーザー数: {len(user_messages)}')
print(f'日数: {len(user_messages[list(user_messages.keys())[0]])}')
print(
    f'メッセージ数: {sum([sum(user.values()) for user in user_messages.values()])}')
print('----------------------------------------')

# ユーザーごとに色を割り当て
userColor = {}
for i, user in enumerate(user_messages.keys()):
    userColor[user] = i

print('\033[32m' + 'グラフを作成します。' + '\033[0m')

# フレームを作成
plt.style.use("ggplot")
def make_frame(t):
    """フレームを作成する関数"""
    plt.rcParams["figure.figsize"] = (14, 10)
    plt.rcParams["figure.dpi"] = dpi
    plt.rcParams["font.size"] = 14
    plt.clf()

    fig = plt.figure()
    ax = fig.gca()
    time_index = int(t * fps)

    # ユーザーごとのメッセージ数を計算
    user_counts = {}
    for user, messages in user_messages.items():
        values = [messages.get(date, 0) for date in dates[:time_index]]
        if sum(values) > 0:
            if sum(values) > lowest:
                user_counts[user] = sum(values)

    # ユーザーごとのメッセージ数を棒グラフで表示
    sorted_users = sorted(user_counts, key=user_counts.get, reverse=False)
    y_pos = range(len(user_counts))
    for user_index, user in enumerate(sorted_users):
        ax.barh(
            y_pos[user_index],
            user_counts[user],
            color="C{}".format(userColor[user]),
            label=user,
        )
        ax.text(
            user_counts[user] + 0.2,
            y_pos[user_index],
            str(user_counts[user]),
            va="center",
        )
        values = [user_counts[user]]
        if len(values) > 0:
            ax.barh(
                y_pos[user_index],
                values[-1],
                color=f"C{userColor[user]}",
                label=user
            )
            ax.text(values[-1] + 0.2, y_pos[user_index],
                    str(values[-1]), va="center")

    # グラフの設定
    ax.set_xlabel("メッセージ数")
    ax.xaxis.set_label_position('top')
    ax.tick_params(top=True, labeltop=True, bottom=False, labelbottom=False)
    ax.text(0, len(user_counts) + 1,
            dates[time_index - 1], ha="left", va="center")
    ax.set_yticks(y_pos)
    ax.set_yticklabels(map(lambda x: x[:8], sorted_users))

    plt.gcf().tight_layout()
    return mplfig_to_npimage(plt.gcf())


# 動画を作成
if output is None:
    output = fileName.split(".")[0]
try:
    animation = VideoClip(make_frame, duration=len(dates) / fps)
    animation.write_videofile(output + ".mp4", fps=fps,
                              codec="libx264", audio=False)
except KeyboardInterrupt:
    print('\033[31m' + 'キャンセルしました。' + '\033[0m')
    exit()

print('\033[32m' + f'{output}.mp4を作成しました。' + '\033[0m')
