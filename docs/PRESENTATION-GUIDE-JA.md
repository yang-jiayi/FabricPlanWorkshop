# HTML操作ガイドの使い方と更新

[HTMLプレゼンテーション](workshop-presentation.html)は, READMEの概要とLab00〜09のMarkdownから生成するオフライン用の操作ガイドです。作者 / 日本語版の制作者は **Jiayi Yang** です。Microsoftの公式教材ではありません。

## 開く

1. リポジトリをcloneするか, GitHubの **Code → Download ZIP** から取得します。非公開リポジトリではアクセス権が必要です。
2. ZIPの場合は**すべて展開**します。`docs`と`assets`の位置関係を変えず, フォルダー全体を保持してください。HTMLファイルだけを保存しても画像は表示されません。
3. `docs/workshop-presentation.html`をMicrosoft EdgeまたはGoogle Chromeで開きます。HTMLの閲覧にPythonやWebサーバーは不要です。GitHubのファイル画面はHTMLを実行しないため, ローカルへ取得して開きます。

表示に使うCSS / JavaScriptはHTML内に含め, 画像と公式アイコンは同梱の相対パスで参照します。CDN, 外部フォント, 分析用通信はありません。外部の公式資料, Microsoft配布のPBIX / XLSX取得, Fabricの操作には別途オンライン接続が必要です。外部リンクは明示的に選択した場合だけ開きます。

## 操作

| 操作 | 方法 |
|---|---|
| 章を選択 | 左のLab一覧, または上部の**目次**。狭い画面では目次を使います |
| 手順を選択 | **この章の手順**または目次の**手順を選ぶ** |
| 前 / 次の手順 | 下部の矢印, キーボードの`←` / `→` |
| 最初 / 最後の手順 | `Home` / `End` |
| 目次 / 操作方法 | `T` / `?`。検索欄の入力中は文字入力を優先します |
| 長い手順 | 本文を縦にスクロール。表とコードは必要に応じて横スクロール |
| 画像を読む | 画像集の見出しを開き, 画像を選択して拡大。**100%**で元の画素サイズ, **+ / −**で倍率を調整し, 縦横にスクロールして細部を確認。**全体**で画面に収める。拡大中の矢印で同じ手順の画像を切り替え（画像領域にフォーカスがある100%表示ではスクロール） |
| ダイアログを閉じる | `Esc`または`×` |
| 配色 / 集中表示 | 上部の**テーマ**は自動 → 明 → 暗。**集中表示**は左の一覧を隠します |
| 手順への再訪 | URL末尾の`#lab…`を含めてブックマーク。同じローカル配置で使います |

進捗バーは**教材内の表示位置**であり, Fabricでの操作完了や検証合格を表すものではありません。完了チェックや回答の保存 / 送信は行いません。JavaScriptが無効な場合は全手順を縦に表示します。

Mermaid図は外部ライブラリを使わず, 折りたたみのソースとして保持します。READMEの構成説明 / 表と併せて読んでください。図としての表示は, Mermaid対応の正本Markdownで確認できます。

## 内容と検証境界

本文と操作画像の正本は[README](../README.md)と[Lab00〜09](../labs/00-prerequisites.md)です。HTMLを直接編集せず, Markdownを修正して再生成します。OverviewはREADMEの学習内容 / 目的 / アーキテクチャ / ラボ一覧 / 注意点 / 原典・ライセンスを収録し, AI向け配備プロンプト等は正本へリンクします。

HTMLを読んでもFabricの操作は実行されません。元の課金 / 権限 / 承認 / 検証範囲の注意を保持しています。Lab07は任意演習です。Lab09は追加の発展編で, 実機確認は合成CSVから始めたPart 3〜5のみです。実Planからの抽出を含むEnd-to-End確認ではありません。失敗 / 未確認事項も[Lab09](../labs/09-variance-analyst.md)の記載どおり収録します。既存の操作PNGは変更していません。

## 再生成 / 同期チェック

ビルド時だけPython 3.12以降とMarkdownレンダラーを使います。リポジトリのルートで実行します。

```powershell
python -m pip install -r requirements-docs.txt
python -X utf8 tools/build_presentation.py
python -X utf8 tools/build_presentation.py --check
python -X utf8 tools/validate_docs.py
python -X utf8 tools/check_public_hygiene.py
python -X utf8 -m unittest discover -s tools -v
git diff --check
```

`--check`はREADME, 全Lab, 生成コード, ローカルUIテンプレートから再生成した内容とコミット対象のHTMLを比較し, 差があれば終了コード1にします。CIでも同じチェックを実行します。ビルドはネットワークやFabric認証を使用せず, 日時を埋め込まないため同じ入力から同じHTMLを生成します。

生成元は`tools/build_presentation.py`, `assets/presentation/shell.html`, `assets/presentation/workshop.css`, `assets/presentation/workshop.js`です。依存バージョンは`requirements-docs.txt`に固定しています。新しい手順見出しを追加すると目次とスライドへ反映されます。外部画像を追加した場合はオフライン要件に違反するためビルドが失敗します。

## デザイン / 権利

Segoe UI系のシステムフォント, ニュートラルな面, Fabricの緑系アクセントを使った独自のFluent風デザインです。Microsoftの公式UI / 公式テンプレートそのものではなく, ブランドの承認や提携を示しません。フォントファイルは配布していません。

製品の説明には, 同梱のMicrosoft公式Fabric製品 / アイテムアイコン7種類を無改変で使います。Microsoft企業ロゴ / 企業ワードマークとAzureアイコンは追加していません。[取得元 / 教材への利用許諾 / 商標表記](../assets/brand/README.md)を参照してください。原典のDiego Diaz氏の著作権と[MITライセンス](../LICENSE)を保持し, Microsoftのアイコンには別途その利用条件が適用されます。
