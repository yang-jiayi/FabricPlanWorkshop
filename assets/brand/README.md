# Microsoft Fabric公式アイコンの出典と利用条件

Microsoft製品を説明する教材 / ドキュメントとして使用します。このリポジトリ自体のロゴや, 独自の製品 / サービスを表すものとしては使用しません。Microsoftの承認や提携を示すものではありません。

## 出典

配布元はMicrosoft Learnの[Microsoft Fabric product, experience, and item icons](https://learn.microsoft.com/en-us/fabric/fundamentals/icons)です。同ページが案内するMicrosoft公式の[Icons.zip](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/Icons.zip)を2026-11-02に取得しました。取得したアーカイブのパッケージ版は **v6.1.0** です。

各ファイルはアーカイブ内の `v6.1.0/package/dist/svg/` から同名のままコピーしました。色, パス, 形状, 余白, 向きは変更していません。表示時のサイズだけを縦横同じ比率で指定します。SVG内に独自の文字や図形を追加していません。

| ファイル | 表す製品 / アイテム | 取得日 | 配布元 / 適用条件 |
|---|---|---|---|
| [fabric_48_color.svg](fabric_48_color.svg) | Microsoft Fabric製品アイコン / 公式ロゴ図形 | 2026-11-02 | [公式アーカイブ](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/Icons.zip) / 下記Fabricアイコン利用条件 |
| [report_48_item.svg](report_48_item.svg) | Fabricワークスペースのレポートアイテム | 2026-11-02 | [公式アーカイブ](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/Icons.zip) / 下記Fabricアイコン利用条件 |
| [planning_48_item.svg](planning_48_item.svg) | Fabric Planアイテム | 2026-11-02 | [公式アーカイブ](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/Icons.zip) / 下記Fabricアイコン利用条件 |
| [sql_database_48_item.svg](sql_database_48_item.svg) | Fabric SQLデータベース | 2026-11-02 | [公式アーカイブ](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/Icons.zip) / 下記Fabricアイコン利用条件 |
| [semantic_model_48_item.svg](semantic_model_48_item.svg) | Fabricセマンティックモデル | 2026-11-02 | [公式アーカイブ](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/Icons.zip) / 下記Fabricアイコン利用条件 |
| [data_warehouse_48_item.svg](data_warehouse_48_item.svg) | Fabric Warehouse | 2026-11-02 | [公式アーカイブ](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/Icons.zip) / 下記Fabricアイコン利用条件 |
| [data_agent_48_item.svg](data_agent_48_item.svg) | Fabric Data Agent | 2026-11-02 | [公式アーカイブ](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/Icons.zip) / 下記Fabricアイコン利用条件 |
| [lakehouse_48_item.svg](lakehouse_48_item.svg) | Lakehouse | 2026-11-03 | 同上 / v6.1.0 |
| [notebook_48_item.svg](notebook_48_item.svg) | Notebook | 2026-11-03 | 同上 / v6.1.0 |
| [power_bi_48_color.svg](power_bi_48_color.svg) | Power BI | 2026-11-03 | 同上 / v6.1.0 |
| [one_lake_48_color.svg](one_lake_48_color.svg) | OneLake | 2026-11-03 | 同上 / v6.1.0 |
| [graph_intelligence_48_color.svg](graph_intelligence_48_color.svg) | Graph intelligence | 2026-11-03 | 同上 / v6.1.0 |
| [group_workspace_48_non-item.svg](group_workspace_48_non-item.svg) | Workspace | 2026-11-03 | 同上 / v6.1.0 |
| [copilot_48_color.svg](copilot_48_color.svg) | Copilot | 2026-11-03 | 同上 / v6.1.0 |

## 利用条件

Microsoft Learnの[FabricアイコンのTerms](https://learn.microsoft.com/en-us/fabric/fundamentals/icons#terms)は次の使用を明示的に許可しています (2026-11-02確認)。

> Microsoft permits the use of these icons in architectural diagrams, training materials, or documentation. You can copy, distribute, and display the icons only for the permitted use unless granted explicit permission by Microsoft. Microsoft reserves all other rights.

同ページのDo's / Don'tsに従い, 製品内の見た目を保持し, 切り抜き, 反転, 回転, 変形を行いません。アイコンの近くに製品名 / アイテム名を記載します。

[Microsoft Trademark and Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks)も2026-11-02に確認しました。一般のブランドガイドラインだけを無制限なロゴ利用許諾とは解釈せず, 本教材では上記のFabricアイコン用の明示的な利用許諾に限定しています。Microsoftの企業ロゴ / ワードマークは収録していません。

[Azure Architecture Centerのアイコン利用条件](https://learn.microsoft.com/en-us/azure/architecture/icons/#icon-terms)にも教材 / ドキュメント向けの同様の許諾がありますが, Azureアイコンのファイルは追加していません。

## HTML操作ガイドでの使用

2026-11-03に上記の[Fabricアイコン利用条件](https://learn.microsoft.com/en-us/fabric/fundamentals/icons#terms), [Azureアイコン利用条件](https://learn.microsoft.com/en-us/azure/architecture/icons/#icon-terms), [Microsoft Trademark and Brand Guidelines](https://www.microsoft.com/en-us/legal/intellectualproperty/trademarks)を再確認しました。Fabric公式ページはtraining materials / slide decks / documentationでの利用を案内しています。

[HTML操作ガイド](../../docs/workshop-presentation.html)では, 上表の公式ファイルをデータURIとして埋め込みます。2026-11-03追加分も同じv6.1.0アーカイブの原本とバイト単位で一致します。製品の説明に使い, 近くにFabric / 各アイテムの名前を添えます。アイコンの回転 / 反転 / 歪曲 / CSSフィルター / 再配色は行いません。Microsoft企業ロゴの利用はこの教材向けに別途許諾されたとは判断できないため収録せず, Fabric製品アイコンと通常のテキスト表記を使います。Azureアイコンも使用しません。

HTMLの面 / 余白 / ナビゲーション / 緑系アクセントは独自のFluent風デザインで, Microsoftの公式デザインテンプレートや公式サイトの複製ではありません。Segoe UIは利用者のシステムにある場合のみ表示し, フォントファイルを配布しません。作者名Jiayi Yangは教材の制作クレジットであり, Microsoftとの関係を示しません。

## ライセンスとソーシャルプレビュー

これらの公式アイコンに教材のMITライセンスを適用しません。Microsoftが留保する権利と上記の用途制限が優先します。

[ソーシャルプレビュー](../social/social-preview.png)はこの教材の学習経路を紹介する1280×640の画像です。Microsoft Fabric製品アイコンを変更せず, 縦横同率で表示して撮影しています。背景と説明文は日本語版で作成しました。公式アイコンの権利と利用条件は同画像内でも保持されます。

Microsoft Fabric and the Microsoft logo are trademarks of Microsoft Corporation.
