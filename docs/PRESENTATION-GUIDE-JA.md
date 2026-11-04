# HTML操作ガイドの使い方と更新

**参加者へ配布するのは[参加者用HTML](workshop-presentation.html)です。** [講師用HTML](workshop-instructor.html)は別ファイルで, 参加者へ配布しません。両版の著者表示は **Jiayi Yang, Swarm Data SE** とし, [LinkedIn](https://www.linkedin.com/in/yangjiayi/)へのリンクを併記します。Microsoftの公式教材ではありません。

| 版 | ファイル | 収録内容 |
|---|---|---|
| 参加者用 / Participant edition | `docs/workshop-presentation.html` | READMEの概要, Lab00〜09の全操作 / 画像 / 確認問題 / 安全上の注意。解答と講師の進行資料は含まない |
| 講師用 / Instructor edition | `docs/workshop-instructor.html` | 同じ演習と解答, 講師の準備 / 180分の進行 / 問いかけ / 復帰 / 費用確認 |

どちらも日本語 / Englishを収録します。確認問題は参加者用にも残し, 解答は講師用に限ります。期待値, 課金 / 権限, 講師へ相談する指示, 安全な中止条件は参加者用から削除しません。これは配布内容の分離であり, リポジトリのMarkdownに対するアクセス制御ではありません。

## 開く

参加者は`docs/workshop-presentation.html`, 講師は`docs/workshop-instructor.html`をダウンロードし, Microsoft EdgeまたはGoogle Chromeで開きます。GitHubのファイル画面ではHTMLは実行されません。非公開リポジトリからの取得にはアクセス権が必要です。ファイル内のタイトル / ヘッダーに版名を表示します。

**各版はHTMLファイル1つだけで独立して閲覧できます。** 全操作画像, Fabric公式アイコン, CSS, JavaScript, Lab09のCSVダウンロードをそれぞれ内包しています。他方のHTML, フォルダーの配置, Python, Webサーバーは不要です。画像は元の画素数を保持したWebPです。正本PNGは変更していません。

閲覧時のネットワーク通信, CDN, 外部フォントはありません。外部資料へのリンク, Microsoft配布ファイルの取得, Fabricの操作にはオンライン接続が必要です。外部リンクは明示的に選択した場合だけ開きます。

## 操作

| 操作 | 方法 |
|---|---|
| 章 / 手順 | 左のラボ一覧を展開して選択。狭い画面ではナビゲーションを開きます |
| 章の絞り込み | 左のタイトルフィルター |
| 全文検索 | 上部の検索, `Ctrl+K`または`/`。複数語はすべて含む結果を表示。全角 / 半角と大文字 / 小文字を区別しません |
| 検索結果 | `↑` / `↓`で選択, `Enter`で移動, `Esc`で閉じる |
| 索引 | **索引**から用語を展開し, 出現する手順へ移動 |
| 用語注釈 | 記事内で初めて出る財務会計用語をクリック / タップすると意味と出典を表示。`Esc`または閉じるボタンで戻る |
| この記事の内容 | 右側の見出しを選択。現在位置を表示 |
| コード | **コピー**でコードをクリップボードへコピー |
| 画像 | 選択して拡大。全体 / 100% / 拡大 / 縮小, スクロール / ドラッグで細部を確認。前 / 次の画像へ移動 |
| 前 / 次 | 本文末のナビゲーション。入力中以外はキーボード操作も可能 |
| 配色 | 自動 / 明 / 暗を切り替え |
| 言語 | 上部の**言語**から日本語 / Englishを選択。同じ記事を保ったまま本文と操作部を切り替え。保存可能な環境では選択を保持 |
| 文字の表示 | Yu Gothic UIを優先。本文は表示領域に応じて17〜20px相当に自動調整。目次 / ボタン / 注釈も読みやすい大きさで表示 |
| 再訪 | `#lab…`を含むURLをブックマーク |

日本語 / 英語の本文, 検索と索引はHTMLに内包され, オンライン翻訳は使いません。画像は両言語で共有し, 画像内のFabric画面は変更せず, 説明 / 代替テキストを翻訳しています。検索対象は選択中の言語です。言語切り替え時は検索語と強調表示を解除します。既存の日本語ブックマークはそのまま使え, 英語の記事には`#en-lab…`を使います。

財務会計用語は記事ごとの初出だけを注釈ボタンにし, **用語集**では有効な記事中の用語, 定義, 出典, 初出箇所を検索 / 索引できます。用語注釈はキーボードでも開閉でき, `Esc`で閉じると起動した語へフォーカスが戻ります。印刷では初出語の直後に定義を表示します。用語データは`assets/presentation/finance-glossary.json`で管理し, 未確認の定義はHTMLへ出さず`UNCONFIRMED-ITEMS-JA.md`に分けます。

JavaScriptが無効な場合も日本語本文を縦に読めます。印刷は選択中の言語の記事だけを対象にします。Mermaid図は外部レンダラーを使わず, 折りたたみのソースで保持します。

## 正本と内容の境界

本文と操作画像の正本は[README](../README.md)と[Lab00〜09](../labs/00-prerequisites.md)です。HTMLを直接編集しません。課金 / 権限 / 承認の注意を保持し, Fabricの操作を自動実行する機能はありません。Lab07は任意演習です。Lab09のHTMLは合成CSVから始める確認済みの手順を収録します。

講師用の追加資料の正本は[講師向け進行ガイド](FACILITATOR-GUIDE.md)です。ラボの`<details><summary>解答</summary>…</details>` / 英語の`Answers`ブロックと, `<!-- presentation-instructor-start -->` / `<!-- presentation-instructor-end -->`で囲んだ講師用段落は参加者用の生成前に除去します。隠すだけの役割切り替えは使わず, 本文 / 非表示DOM / 検索 / 索引にも解答を含めません。新しい講師専用メモには両言語で同じ境界を付けてください。

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

生成元は`tools/build_presentation.py`, `assets/presentation/shell.html`, `workshop.css`, `workshop.js`, `index-terms.json`, `finance-glossary.json`です。索引は用語と別名の出現箇所をビルド時に計算します。財務用語データの定義 / 出典 / 日英両語が欠けている場合や, 記事に出現しない索引語がある場合はビルド / 回帰テストで検出します。

英語本文は`assets/presentation/locales/en/overview.json`と`lab00.json`〜`lab09.json`, 講師ガイドは`facilitator.json`, 操作部の対訳は`locales/ui-en.json`で管理します。各本文は正本の除外処理後のSHA-256と既存記事IDを持ちます。正本変更時は対応する英語本文と`source_sha256`も更新してください。全記事の翻訳, 画像の参照順序とコードブロック数を検査し, 未同期 / 欠落をビルドエラーにします。翻訳ファイルも生成元ハッシュと`--check`の対象です。確認リストの除外境界は両言語で共通です。

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
python -X utf8 tools/check_presentation_typography.py --output-dir <文字表示の出力フォルダー>
python -X utf8 tools/check_presentation_languages.py --output-dir <言語切り替えの出力フォルダー> --axe <axe.min.jsのパス>
python -X utf8 tools/check_presentation_editions.py --output-dir <版別検査の出力フォルダー> --axe <axe.min.jsのパス>
```

開発用ブラウザーチェックはインストール済みEdgeを`file://`で開きます。axe-coreのローカルファイルを指定し, 明 / 暗のアクセシビリティ, 検索, 索引, ナビゲーション, 拡大, モバイル, リンク, 画像, 通信とコンソールを検査します。スクリーンショットとJSON結果は指定先に保存し, リポジトリには追加しません。axe-coreは開発時の検査専用で, HTMLには含みません。

更新時は生成 → ブラウザーチェック → 画像の目視確認 → 独立した批評 → 修正を繰り返します。要件, 操作性, 可読性, コントラスト, ファイルサイズ, 初期表示, 内容と権利表記を確認し, 重大な指摘がなくなるまで改善します。最終差分も別途レビューします。

文字表示の検査は390 / 768 / 1280 / 1440 / 1920 CSSピクセル幅で, 算出されたフォント / 文字サイズ, 長い目次, 検索 / 索引 / 配色と折り返しを確認します。200%ズーム相当の表示領域と200%の文字設定でも横にはみ出さないことを確認します。画像とJSON結果は指定先だけに保存します。

言語の検査は日本語 → 英語 → 日本語の往復, Lab09の対応記事, 本文検索後の切り替え, 目次 / 索引 / 拡大画像 / 明暗 / モバイル, 言語の保存と履歴, 選択言語の印刷を確認します。

版別検査は両HTMLをリポジトリ外の別フォルダーへ1ファイルずつコピーし, 各版についてブラウザー / 言語 / 文字表示の全検査を実行します。版名の表示, 参加者の確認問題と解答の除外, 講師の解答 / 進行ガイド / 費用検索の範囲も確認します。通常ビルドと`--check`は2ファイルを同時に生成 / 検査し, 一方だけの更新ではCIは成功しません。個別のブラウザーツールは`--html`で対象ファイルを選べます。

動的表示も版別に検査し, シャッフル途中 / 着地後の画像, アイコンと親要素の無回転 / 無フィルター / 同率拡縮, 動きを減らす設定と印刷時の静止表示を確認します。

## デザイン / 権利

ホームと記事のグラデーションは入場後4.8秒以内に停止します。光の帯, 製品 / ラボカードのシャッフル入場, 検索ヒットのパルスと現在位置のインジケーターも短時間で終了します。本文の文字をスクランブルせず, 製品アイコンとその親要素は平行移動 / 同率拡縮 / 不透明度だけで動かします。`prefers-reduced-motion`と印刷ではアニメーションを止め, 同じ内容を静止して表示します。

Microsoft Learnの情報配置を参考にした独自デザインです。公式サイトのCSSやテンプレートを複製していません。本文 / 見出し / 目次 / ボタン / ダイアログはYu Gothic UIを優先し, 未導入の端末ではYu Gothic / Meiryo / Segoe UI等のローカルフォントを使います。実際のコードはConsolas / Cascadia Code等の等幅フォントを保持します。フォントの取得や配布は行いません。

文字サイズはブラウザーの表示領域に応じた`rem`と`clamp()`で調整します。既定の文字設定では本文17〜20px相当, 目次 / 操作部15〜16px相当, 注釈14〜15px相当を下限 / 上限とし, 日本語の行間と1行の長さも調整しています。ブラウザーのズームや既定の文字サイズは固定せず, 利用者の設定を尊重します。動きを減らすシステム設定にも対応します。

Microsoft公式Fabricアイコンは製品の説明として無改変で使います。Microsoft企業ロゴとAzureアイコンは収録していません。[取得元 / 利用条件 / 商標表記](../assets/brand/README.md)を参照してください。原典のDiego Diaz氏の著作権と[MITライセンス](../LICENSE)を保持し, 公式アイコンには別途その利用条件が適用されます。
