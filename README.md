# LINE to Video

LINE のトーク履歴を解析して、matplotlib でグラフを作成し、moviepy で動画に変換します。

## Requirements

- matplotlib
- moviepy
- Pillow
- japanize_matplotlib (日本語のフォントを使用する場合)

```
pip install matplotlib moviepy Pillow japanize_matplotlib
```

## How to use

### 1. LINE のトークファイルをエクスポートする

LINE のトーク画面からメニューを開き、その他 > トーク履歴の送信 からテキストファイルを作成します。
作成が完了したら、一度 Keep に保存してからダウンロードします。

### 2. トーク履歴を解析する

```
python3 line_to_video.py LINEのトークファイル.txt
```

#### オプション

- `-o` `--output` : 出力ファイル名を指定します。デフォルトは `output.mp4` です。
- `-f` `--fps` : 動画のフレームレートを指定します。デフォルトは `10` です。
- `-s` `--start-date` : 開始日を指定します。指定しない場合はトーク履歴の最初の日になります。
- `-dpi` `--dpi` : 解像度を指定します。デフォルトは `150` です。
- `-lowest` `--lowest` : 最低メッセージ数を指定します。この数以下のメッセージ数のユーザーはグラフに表示されません。デフォルトは `0` です。
