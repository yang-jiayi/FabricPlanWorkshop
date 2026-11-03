# 教材への貢献

手順,説明,翻訳の改善を歓迎します。変更では、参加者が再現できる内容と、開催環境で個別に確認する必要がある内容を区別してください。

## 執筆方針

- 自然で具体的な日本語を使い、区切りにはASCIIの `,` と ` / ` を使います。
- ボタン名,フィールド名,モデル識別子,数式,SQLは、画面やサンプルと照合できるよう原語を保持します。
- 原版から引き継いだ内容と、日本語版で追加,改訂した内容を区別し、[LOCALIZATION.md](LOCALIZATION.md)の用語方針に従います。
- 手順,期待値,画面ラベル,製品仕様の意味を変えないでください。環境依存の挙動は、前提や注意点を添えてください。
- スクリーンショットには参加者が画面を理解できる代替テキストを付け、個人情報,顧客名,テナント固有の識別子を含めないでください。
- サンプルの `.pbix` / `.xlsx` はコミットせず、Microsoftの配布元へリンクしてください。

## 変更前の確認

文書を変更したら、リポジトリのルートから次のチェックを実行してください。

```powershell
python -m pip install -r requirements-docs.txt
python -X utf8 tools/build_presentation.py
python -X utf8 tools/build_presentation.py --check
python tools/validate_docs.py
python -m unittest discover -s tools -p "test_*.py"
python tools/check_public_hygiene.py
```

画像を追加,削除した場合は、Markdownから参照されていることと、代替テキストが内容を説明していることを確認してください。モジュールの追加や番号変更では、READMEの一覧,隣接モジュールのナビゲーション,演習フロー図も更新してください。

HTML操作ガイドは生成物です。`docs/workshop-presentation.html`を直接編集せず, 正本Markdownまたは`assets/presentation`を変更して再生成し, HTMLも同じ変更に含めてください。更新漏れはCIの同期チェックで失敗します。[利用 / 更新方法](docs/PRESENTATION-GUIDE-JA.md)
