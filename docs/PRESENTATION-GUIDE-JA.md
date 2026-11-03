# HTML操作ガイドの使い方と更新

[HTML操作ガイド](workshop-presentation.html)はREADMEの概要とLab00〜09から生成します。日本語版の作者は **Jiayi Yang** です。Microsoftの公式教材ではありません。

## 開く

`docs/workshop-presentation.html`をダウンロードし, Microsoft EdgeまたはGoogle Chromeで開きます。GitHubのファイル画面ではHTMLは実行されません。非公開リポジトリからの取得にはアクセス権が必要です。

**HTMLファイル1つだけで閲覧できます。** 全操作画像, Fabric公式アイコン, CSS, JavaScript, Lab09のCSVダウンロードを内包しています。フォルダーの配置, Python, Webサーバーは不要です。画像は元の画素数を保持したWebPです。正本PNGは変更していません。

閲覧時のネットワーク通信, CDN, 外部フォントはありません。外部資料へのリンク, Microsoft配布ファイルの取得, Fabricの操作にはオンライン接続が必要です。外部リンクは明示的に選択した場合だけ開きます。

## 操作

| 操作 | 方法 |
|---|---|
| 章 / 手順 | 左のラボ一覧を展開して選択。狭い画面ではナビゲーションを開きます |
| 章の絞り込み | 左のタイトルフィルター |
| 全文検索 | 上部の検索, `Ctrl+K`または`/`。複数語はすべて含む結果を表示。全角 / 半角と大文字 / 小文字を区別しません |
| 検索結果 | `↑` / `↓`で選択, `Enter`で移動, `Esc`で閉じる |
| 索引 | **索引**から用語を展開し, 出現する手順へ移動 |
| この記事の内容 | 右側の見出しを選択。現在位置を表示 |
| コード | **コピー**でコードをクリップボードへコピー |
| 画像 | 選択して拡大。全体 / 100% / 拡大 / 縮小, スクロール / ドラッグで細部を確認。前 / 次の画像へ移動 |
| 前 / 次 | 本文末のナビゲーション。入力中以外はキーボード操作も可能 |
| 配色 | 自動 / 明 / 暗を切り替え |
| 再訪 | `#lab…`を含むURLをブックマーク |

JavaScriptが無効な場合も本文を縦に読めます。Mermaid図は外部レンダラーを使わず, 折りたたみのソースで保持します。

## 正本と内容の境界

本文と操作画像の正本は[README](../README.md)と[Lab00〜09](../labs/00-prerequisites.md)です。HTMLを直接編集しません。課金 / 権限 / 承認の注意を保持し, Fabricの操作を自動実行する機能はありません。Lab07は任意演習です。Lab09のHTMLは合成CSVから始める確認済みの手順を収録します。

確認が必要な事項は[Agent向け確認事項リスト](UNCONFIRMED-ITEMS-JA.md)で別管理し, HTMLには載せません。正本の該当箇所を次の対で囲みます。IDはリストの見出しと1対1です。正本の記述を消すための仕組みではありません。

```html
<!-- presentation-exclude-start: LAB09-EXAMPLE -->
確認が必要な正本の記述
<!-- presentation-exclude-end: LAB09-EXAMPLE -->
```

画像を除外範囲に入れないでください。全578画像の順序と代替テキストをテストで確認します。確認完了後は正本, リスト, マーカーを一緒に更新します。HTMLには確認リストへのリンクを追加しません。

## 再生成 / 同期チェック

ビルドにはPython 3.12以降を使います。

```powershell
python -m pip install -r requirements-docs.txt
python -X utf8 tools/build_presentation.py
python -X utf8 tools/build_presentation.py --check
python -X utf8 -m unittest discover -s tools -v
python -X utf8 tools/validate_docs.py
python -X utf8 tools/check_public_hygiene.py
git diff --check
```

生成元は`tools/build_presentation.py`, `assets/presentation/shell.html`, `workshop.css`, `workshop.js`, `index-terms.json`です。索引は用語と別名の出現箇所をビルド時に計算します。内容に出現しない用語はビルドエラーになります。

`section-ids.json`は既存記事のブックマークIDを保持します。見出しの改題時は同じIDのタイトルを更新してください。除外する手順のIDを別の記事へ使い回しません。

画像の変換結果は`assets/presentation/screenshots.zip`に固定し, 元PNGと変換結果のSHA-256, 画素数, 変換設定を内包します。通常ビルドとCIは画像を再変換せず, ハッシュを照合します。OSによるエンコーダー差や繰り返し変換を避けるためです。PNG追加 / 変更時のみ次を実行し, パックと生成HTMLもコミットします。

```powershell
python -m pip install -r requirements-presentation-dev.txt
python -X utf8 tools/build_presentation.py --encode-images
```

`--check`は正本とUIから再生成したHTMLをコミット対象と比較します。ビルドにネットワークやFabric認証は使いません。外部画像はエラーになります。

## 品質ループ

```powershell
python -m pip install -r requirements-presentation-dev.txt
python -X utf8 tools/check_presentation_browser.py --output-dir <出力フォルダー> --axe <axe.min.jsのパス>
```

開発用ブラウザーチェックはインストール済みEdgeを`file://`で開きます。axe-coreのローカルファイルを指定し, 明 / 暗のアクセシビリティ, 検索, 索引, ナビゲーション, 拡大, モバイル, リンク, 画像, 通信とコンソールを検査します。スクリーンショットとJSON結果は指定先に保存し, リポジトリには追加しません。axe-coreは開発時の検査専用で, HTMLには含みません。

更新時は生成 → ブラウザーチェック → 画像の目視確認 → 独立した批評 → 修正を繰り返します。要件, 操作性, 可読性, コントラスト, ファイルサイズ, 初期表示, 内容と権利表記を確認し, 重大な指摘がなくなるまで改善します。最終差分も別途レビューします。

## デザイン / 権利

Microsoft Learnの情報配置を参考にした独自デザインです。公式サイトのCSSやテンプレートを複製していません。Segoe UI / Yu Gothic UI等はシステムフォントを使い, フォントを配布しません。動きを減らすシステム設定に対応します。

Microsoft公式Fabricアイコンは製品の説明として無改変で使います。Microsoft企業ロゴとAzureアイコンは収録していません。[取得元 / 利用条件 / 商標表記](../assets/brand/README.md)を参照してください。原典のDiego Diaz氏の著作権と[MITライセンス](../LICENSE)を保持し, 公式アイコンには別途その利用条件が適用されます。
