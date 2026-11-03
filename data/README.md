# サンプルデータ

Lab01〜08の主なデータはMicrosoft公式のNorthwind FMCGサンプルです。Lab09には、この教材用に作成した**合成の比較データ**もあります。合成CSVはMicrosoft公式データではなく、実Plan / writebackから抽出した実績でもありません。

## ダウンロード

2つのファイルは、Microsoftの [`fabric-samples`](https://github.com/microsoft/fabric-samples/tree/main/docs-samples/iq/plan) リポジトリの `docs-samples/iq/plan/` にあります。

| ファイル | サイズ | 使用するモジュール |
|---|---|---|
| [`Northwind_FMCG.pbix`](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/iq/plan/Northwind_FMCG.pbix) | 9.3 MB | モジュール01〜06,09 |
| [`Northwind-FMCG-assets-powertable-tutorial.xlsx`](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/iq/plan/Northwind-FMCG-assets-powertable-tutorial.xlsx) | 36 KB | モジュール07（任意） |
| [`lab09-variance-snapshot-sample.csv`](lab09-variance-snapshot-sample.csv) | 18行 / 15列 | Lab09のPart 3〜5（合成データによる実機手順の再現） |

`fabric-samples` は大きなリポジトリです。必要な `.pbix` ファイルをGitHubから直接ダウンロードすれば、リポジトリ全体をクローンする必要はありません。

`.pbix` は[モジュール01](../labs/01-environment-and-first-sheet.md)でFabricワークスペースにインポートします。事前にモデルの中身を確認する場合を除き、Power BI Desktopは不要です。

---

## サンプルモデル：Northwind FMCG

`.pbix` をインポートすると、**レポートとセマンティックモデルの2つのアイテム**が作成されます。

この演習の基盤となるのは、**セマンティックモデル**です。Plan アイテムはこのモデルに接続し、接続後に別のモデルへ変更することはできません。各モジュールは、このモデルをHarborlight Provisionsの既存のレポート基盤、つまり財務部門が共通で使う信頼できる数値の基盤として扱います。

**レポート**は、Harborlightがすでに使っている業績レポートに相当します。[モジュール01](../labs/01-environment-and-first-sheet.md)で現在の姿を確認し、[モジュール06](../labs/06-intelligence-canvas.md)で計画作成後にもう一度開きます。本演習では計画データを別のFabric SQLデータベースに書き戻し、元のセマンティックモデルを変更しない構成を使います。そのため、この構成では既存のレポートは変更されません。

> [!NOTE]
> **標準のSQL書き戻しと、モデルへの追加操作を区別してください。** 最新の公式資料には、SQLに書き戻したテーブルを **Add table to semantic model** でセマンティックモデルに追加する手順もあります。本演習ではこの操作は行いません。「Planningはセマンティックモデルを一切変更できない」という意味ではありません。追加する場合は、対象モデル、リレーションシップ、権限、制約を[公式のセマンティックモデルへの書き戻し手順](https://learn.microsoft.com/fabric/iq/plan/planning-writeback/planning-how-to-write-back-semantic-model)で別途確認してください。

実際の導入では、サンプルをインポートする代わりに、お客様がすでにレポートで使っているセマンティックモデルにPlan アイテムを接続します。

## モデルに含まれる内容

セマンティックモデルに接続すると、**Data** ペインにはテーブルごとにフィールドが表示されます。目的のフィールドがどのテーブルにあるかを把握しておくと、操作がスムーズになります。

> [!NOTE]
> サンプルのフィールド構成,表示名,リレーションシップは、配布ファイルの版によって異なる場合があります。手順を進める前に、インポートしたモデルの **Data** ペインで使用するテーブルとフィールドを確認してください。

| テーブル | 種類 | 主な内容 | 使用するモジュール |
|---|---|---|---|
| **Measures Table** | メジャー | *Gross Revenue*、*2025 Gross Revenue*、*COGS*、*2025 COGS* | モジュール01,03,04,06,09 |
| **Date** | ディメンション | *Date Hierarchy*、*Date Key*、*Half Year*、*Month*、*Month Name*、*Month Short*、*Quarter*、*Year*、*Year Month*、*Year Quarter* | 各モジュールで使用 |
| **Fact Transactions** | ファクト | 地域別,製品別の売上実績と原価実績 | Measures Table の基になるデータ |
| **Geography** | ディメンション | *Region*、*Sub Region*、*City* | モジュール01,03,05 |
| **P&L Measures** | ファクト | 販売数量、平均販売価格、売上原価の構成要素、営業費用などのドライバー。**テーブル内に独自の Region Hierarchy と Date Hierarchy を持ちます** | モジュール05のメジャーモデル |
| **P&L Rows** | ファクト | 損益項目を行として保持。*Account* 列と *Value* 列があります | モジュール05の行モデル |
| **Product** | ディメンション | *Category*、*Sub Category* | モジュール01,03,04,06,09 |

日付を扱うディメンションや階層は、テーブルによって使い分けます。特に **P&L Measures** では、下記のとおり、テーブル内の階層を使う点に注意してください。

> [!IMPORTANT]
> **Measures Table には、年度を限定したメジャーと、限定していないメジャーがあります。**
>
> | メジャー | 対象期間 | 表示される内容 |
> |---|---|---|
> | *Gross Revenue* | 全年度 | 2023,2024,2025,2026の各年の列 |
> | *2025 Gross Revenue* | FY25のみ | 1年分、**$25.87M** |
> | *COGS* | 全年度 | 全年度 |
> | *2025 COGS* | FY25のみ | FY25のみ |
>
> この演習ではMicrosoftのチュートリアルに合わせ、**2025年に限定したメジャー**を使います。年度を限定していないメジャーを選んでもエラーにはなりませんが、意図した列構成になりません。

> [!NOTE]
> **Microsoftのチュートリアルに書かれた名称と、サンプルモデルの名称が異なる場合があります。** 翻訳元では、次の違いが報告されています。この演習の操作手順では、モデル側で報告された名称を使っています。
>
> | Learnのチュートリアル上の名称 | 翻訳元で報告されたモデル,画面上の名称 |
> |---|---|
> | Sales Transactions | **Fact Transactions** |
> | Region Name | **Region** |
> | Quarter Name | **Quarter** |
> | Sub-Category | **Sub Category** |
> | Predict ペインの Select Measure | **Measure Selected** |
>
> また、チュートリアルでは *Category* と *Sub Category* を格納するテーブル名が明記されていない場合があります。翻訳元で報告されているテーブル名は **Product** です。Learnと本演習を並行して進める場合は、名称の違いも考慮して Data ペインを探してください。

---

## ファクトテーブルの詳細

### Fact Transactions

地域別,製品別の売上実績と原価実績です。FY26の販売計画の基礎データとなります。トップダウン目標を配賦するときに使う前年の構成比も、このデータに基づきます。

主要なメジャーは **2025 Gross Revenue** です。FY25通年の売上実績で、合計は約**2,590万ドル**です。これを基準にFY26の成長目標を設定します。メジャー自体は、このテーブルではなく **Measures Table** にあります。

### P&L Measures

損益のドライバーとなる10個のメジャーと、独自のディメンションを持ちます。

| 区分 | メジャー |
|---|---|
| 売上 | Sales Volume、Avg Selling Price、Discounts and Returns |
| 売上原価 | Raw Material Cost、Labor Cost、Other Direct Exp |
| 営業費用 | Admin Expenses、Employee Expenses、R&D、Selling and Marketing Expenses |

このほか、**Region Hierarchy**、**Date Hierarchy**、*Invoice ID* フィールド、ネイティブの *COGS*、*Gross revenue*、*net revenue* メジャーを持ちます。

> [!IMPORTANT]
> **翻訳元の報告では、P&L Measures は Geography および Date のディメンションテーブルとリレーションシップを持ちません。** テーブル内の Region Hierarchy と Date Hierarchy を使って集計します。
>
> P&L Measures を使うシートで、Geography の行や Date の列を設定すると、各セルに同じ総計値が繰り返し表示されると報告されています。この場合もエラーは表示されません。モジュール01,03,04,06では、Geography、Date、Product に関連付けられた Measures Table を使います。この違いが特に問題になるのは、モジュール05です。実環境で同じ症状が出た場合は、まず使用する階層とモデルのリレーションシップを確認してください。

[モジュール05](../labs/05-pl-models-and-scenarios.md)では、これらのドライバーをメジャーモデルで組み合わせ、損益計算書を構成します。

### モジュール09の比較データ（発展編）

Lab09の実機確認は、**同梱の合成CSVを使ったPart 3〜5に限定**されています。Warehouseへのコピーと検算、Lakehouse Deltaテーブル、OntologyとData Agentの一部の操作を確認しました。Part 1〜2の実Plan / writeback抽出を含むEnd-to-End確認ではありません。サンプル経路のUI確認を、顧客データや実Planの検証結果として扱わないでください。

[`lab09-variance-snapshot-sample.csv`](lab09-variance-snapshot-sample.csv)はこの教材用の合成データです。SnapshotIdは`LAB09-SAMPLE-001`、Scenarioは`Base`、PlanVersionは`FY26-Workshop-v1`で、3期間 / 6製品の18行を含みます。これらの値は実Planや現実のFY26実績を表しません。WarehouseのDecimal列で数値を検算し、Ontology / Graphで使うLakehouse Delta側では金額と比率をDoubleとして扱います。

実Planルートでは、モデルの*Measures Table[Gross Revenue]*とLab04のPlan内*Forecast*を同じProduct / 月の粒度で照合します。Gross RevenueはDAXメジャーなので、実在するProduct / Dateフィールドから同じ期間の値を出し、Planの保存済みForecastと対応付けます。地域別やGross ProfitのPlan値をこのデータに含まれるものとして扱いません。実Plan / writeback抽出の一連の操作は未検証です。

Long with Changesの履歴を合計したり、`TOP 1`や最大timestampだけで現在値を選んだりしません。完全な選択状態、行数、全キー集合を確認できなければ停止します。比較CSVの列契約は[Lab09 Snapshotテンプレート](lab09-variance-snapshot-template.csv)を参照してください。こちらはヘッダーだけで、実値は含みません。

Lab09では合成CSVをLakehouse Filesへ置き、Warehouse `COPY INTO`を資格情報句なしのEntraパススルーで実証しました。Workspace Identityは必須ではありません。利用可能な認証経路は実行者の権限 / 組織ポリシーで確認してください。取込、全件 / キー検査、Lakehouse Delta作成、Ontology bindingの手順は[Lab09](../labs/09-variance-analyst.md)に記載しています。実Planの書き戻し履歴、顧客データ、テナント情報を公開場所へアップロードしないでください。

### P&L Rows

損益項目が行として格納され、費用データも項目ごとの明細で保持されています。*Account* と *Value* を使い、モジュール05の行モデルビルダーで Net Profit を起点とする損益階層を作成します。

---

## 資産台帳（任意モジュール）

`Northwind-FMCG-assets-powertable-tutorial.xlsx` は、IT資産の台帳です。共有スプレッドシートで管理され、責任者が曖昧になりがちな参照データを想定しています。モジュール07ではPowerTableに取り込み、承認やアクセス制御を設定します。

---

## 名前の扱いについて

サンプルの名前は *Northwind FMCG* のまま使います。Plan アイテムに接続したセマンティックモデルの名前を変更すると、**接続が切れ、Plan アイテムが動作しなくなります**。名前を変えずに使うほうが、操作も簡単で安全です。この制約は[公式の既知の制限事項](https://learn.microsoft.com/fabric/iq/plan/overview-limitations)も確認してください。

演習中は、*Northwind FMCG* を *Harborlight Provisions* のデータとして読み替えてください。地域、カテゴリ、メジャーの名前を編集しなくても、演習のシナリオに沿って使えます。

---

## インポート時に報告されている事象

翻訳元では、`.pbix` のインポート後にFabricで次のメッセージが表示される場合があると報告されています。

> Refresh failed due to missing data source credentials

これは「データソースの資格情報がないため、更新に失敗した」という意味です。翻訳元では、モデルに埋め込まれたデータが利用でき、計画シートにも接続できたとされています。ただし、今回の作業でこの事象を再現,検証したわけではありません。

**メッセージを無条件に無視せず**、レポートに期待するサンプルデータが表示されること、計画シートからセマンティックモデルに接続できること、演習で使う値が取得できることを確認してから進んでください。利用できない場合は、更新履歴、データソース,資格情報,モデルの設定を管理者と調査してください。この演習のために、資格情報を推測して入力する必要はありません。
