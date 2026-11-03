# ワークショップ概要 PowerPoint

[参加者向けPowerPointをダウンロード](workshop-overview-ja.pptx)

Microsoft Fabric Plan Workshop の目的, データの流れ, Lab00〜09 の学習経路, 前提条件と参加方法を説明する日本語の概要資料です。23 枚 / 16:9 で, 全フォントを **Yu Gothic UI** に指定しています。操作手順の正本は [README](../README.md) と各 Lab の Markdown です。[参加者向け HTML 操作ガイド](workshop-presentation.html)も利用できます。PowerPoint は全手順や解答を収録した資料ではありません。表示クレジットは **Jiayi Yang, Swarm Data SE** です。

## 表示とデザイン

Yu Gothic UIがインストールされたWindows版PowerPointを推奨します。フォントファイルは配布・埋め込みしません。別の環境では代替フォントになり, 改行や配置が変わる場合があります。

Microsoft Learn / Docs風のヘッダー, パンくず, カード, 手順ブロック, 補足 / ヒント / 重要 / 注意の枠を, 鮮やかなグラデーションと組み合わせた独自デザインです。Microsoft公式テンプレートや公式認定教材ではありません。

公式Fabric製品 / アイテムアイコンは[利用条件と出典](../assets/brand/README.md)に従い使用しています。元SVGを変更せず同率でPNG化し, 製品名を近くに置いています。Microsoft企業ロゴ / ワードマークとAzureアイコンは収録していません。教材のMITライセンスを公式アイコンに適用しません。

## 再生成と確認

リポジトリルートで実行します。生成時にネットワーク接続やFabric操作は行いません。

```powershell
python -m pip install -r requirements-powerpoint.txt
python -X utf8 tools\build_workshop_powerpoint.py
python -X utf8 tools\build_workshop_powerpoint.py --check
python -X utf8 tools\build_workshop_powerpoint.py --audit-fonts
python -X utf8 -m unittest discover -s tools -p "test_*.py"
python -X utf8 tools\validate_docs.py
python -X utf8 tools\check_public_hygiene.py
git diff --check
```

フォント検査は標準ライブラリだけで実行でき, 全テーマの major / minor の latin / ea / cs, テキスト run, ノート, マスター, レイアウトのフォント指定を検査します。既存 CI の unittest でも, チェックインされた PowerPoint のフォント, 日本語と英数字の半角スペース, 指定クレジット, 図形の範囲, アイコンの同率配置, 出典と公開情報の衛生を確認します。スペース規則はタイトル / 本文 / 図のラベル / 注意書き / ノートにも適用し, URL とコードの綴りを保持します。

出典は参加者向けのREADME / Lab00〜09に限定します。`presentation-exclude`で囲んだ範囲, 解答, 講師用資料は使いません。Lab09は合成CSVによるPart 3〜5の確認範囲だけを紹介し, 実Plan抽出の経路は説明しません。各スライドのノートに正本へのリンクと参加者向け出典のSHA256を記録します。出典の更新でハッシュが変わった場合は, 概要の説明も照合して再生成してください。

## Windows PowerPointでの表示確認

Windows版PowerPointとPythonの`pywin32`がある環境では, 次を実行すると全スライドのPNG, コンタクトシート, PowerPointのコピー, テキストの表示領域測定JSONを作成します。出力先はリポジトリ外の専用フォルダーを指定してください。

```powershell
python -X utf8 tools\render_workshop_powerpoint.py docs\workshop-overview-ja.pptx <output-directory>
```

スクリプトは対象資料を読み取り専用で開き, その資料だけを閉じます。利用者のPowerPointアプリは終了しません。文字の実測領域が枠を超える場合は失敗します。PNGも目視し, 改行, 余白, 文字の欠け, コントラスト, アイコンの形状を確認してください。静的検査や表示確認は, Fabricでの演習完了や本番適合を保証するものではありません。

## 原典と日本語版

Lab00〜08はDiego Diaz氏の[Fabric Planning Lab](https://github.com/Diaz506/fabric-planning-lab)に基づき, 原典のMITライセンスと著作権表示を保持します。日本語の説明, 操作画像, このPowerPointとLab09は日本語版の追加 / 修正です。制作: Jiayi Yang。[翻訳と用語の方針](../LOCALIZATION.md)
