import re
import datetime
import random
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from moviepy.editor import VideoClip
from moviepy.video.io.bindings import mplfig_to_npimage

import japanize_matplotlib


def parse_line_chat(file_path):
    chat_data = {}
    current_date = None
    user_pattern = re.compile(r"^(\d{1,2}:\d{2})\t(.+?)\t")

    with open(file_path, "r", encoding="utf-8") as file:
        for line in file:
            if re.match(r"^\d{4}/\d{1,2}/\d{1,2}\(.+\)$", line):
                current_date = line.strip()
                chat_data[current_date] = {}
            elif user_pattern.match(line):
                time, user = user_pattern.findall(line)[0]
                if user not in chat_data[current_date]:
                    chat_data[current_date][user] = 0
                chat_data[current_date][user] += 1

    return chat_data


def create_video(chat_data, video_path, fps=10):
    plt.style.use("fivethirtyeight")
    sorted_dates = sorted(
        chat_data.keys(),
        key=lambda x: datetime.datetime.strptime(re.sub(r"\(.+?\)", "", x), "%Y/%m/%d"),
    )
    users = set()
    for date in sorted_dates:
        users.update(chat_data[date].keys())
    users = sorted(users)

    colormap = cm.get_cmap("tab10")
    user_colors = {user: colormap(i / len(users)) for i, user in enumerate(users)}

    cumulative_counts = {user: [] for user in users}

    for date in sorted_dates:
        for user in users:
            previous_count = (
                cumulative_counts[user][-1] if cumulative_counts[user] else 0
            )
            current_count = chat_data[date].get(user, 0)
            cumulative_counts[user].append(previous_count + current_count)

    def make_frame(t):
        fig_height = len(users) * 0.5 if len(users) > 10 else 5
        fig, ax = plt.subplots(figsize=(12, fig_height))
        current_index = int(t * fps)
        if current_index < len(sorted_dates):
            current_date = sorted_dates[current_index]
            counts = [(user, cumulative_counts[user][current_index]) for user in users]
            counts.sort(key=lambda x: x[1])
            ax.clear()
            colors = [user_colors[user] for user, count in counts]
            bars = ax.barh(
                [user for user, count in counts],
                [count for user, count in counts],
                color=colors,
                height=0.8,
            )
            plt.rcParams.update({"font.size": 14})
            ax.set_title(f"{sorted_dates[0]} >>> {current_date}", fontsize=16)
            ax.set_xlabel("累積メッセージ数", fontsize=14)
            for bar, (user, count) in zip(bars, counts):
                ax.text(
                    bar.get_width(),
                    bar.get_y() + bar.get_height() / 2,
                    str(count),
                    va="center",
                )

        return mplfig_to_npimage(fig)

    duration = len(sorted_dates) / fps
    animation = VideoClip(make_frame, duration=duration)

    animation.write_videofile(video_path, fps=fps, bitrate="16000k")


line_chat_file_path = "text.txt" # ここにLINEのトーク履歴のテキストファイルを指定
output_video_path = "line_chat_video.mp4" # ここに出力する動画ファイル名を指定

chat_data = parse_line_chat(line_chat_file_path)
create_video(chat_data, output_video_path, fps=10)

print(f"{output_video_path} に保存されました")
