# LINE to Video

LINE のトーク履歴をユーザー別の発言数をグラフにまとめるやつです。

## Requirements

- matplotlib
- moviepy
- Pillow
- japanize_matplotlib (日本語のフォントを使用する場合)

```
pip install matplotlib moviepy Pillow japanize_matplotlib
```

## 使い方

### 1. LINE のトークファイルをエクスポートする

LINE のトーク画面からメニューを開き、その他 > トーク履歴の送信 からテキストファイルを作成します。
作成が完了したら、一度 Keep に保存してからダウンロードします。

### 2. トーク履歴を解析する

```
python3 line_to_video.py LINEのトークファイル.txt
```
