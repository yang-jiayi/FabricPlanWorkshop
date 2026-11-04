# Lab09：Plan Variance Analyst（計画差異アナリスト）

**所要時間の目安：** 45〜60分（データ準備時間を除く）
**作成するもの：** 比較用Warehouse、LakehouseのDeltaテーブル、Product / Period / Revenue Observationを定義するOntology Preview、Ontologyを参照する読み取り専用Fabric Data Agent。

> [!IMPORTANT]
> **実機確認の範囲:** Fabricで確認したのは、同梱の合成CSVを使ったPart 3〜5です。WarehouseへのCOPYと検算、Lakehouse Deltaテーブル、Ontologyのバインド / グラフのマテリアライズ、Data Agentの一部の質問を確認しました。Part 1〜2の実Plan / writebackからの抽出を含むEnd-to-End確認ではありません。サンプルルートと実Planルートを混同しないでください。
>
> 手順で使用した合成CSVは公開されている`data/lab09-variance-snapshot-sample.csv`です。Fabricの実データや顧客データではありません。Data AgentはDraftのままで、公開 / 共有していません。実行画像は画面操作の証跡ですが、画像にあるものを超えて機能や原因を一般化しません。

## 1. 目的と検証境界

Lab04の *Gross Revenue* と *Forecast* を **Product × 月** で比較し、差異をOntologyで意味付けしたうえで、Fabric Data Agentへ読み取り専用の質問をします。Planや元のセマンティックモデルへ自動で書き戻す機能ではありません。

Lab04のPlanは *Gross Revenue* と *Forecast* を使い、行はProduct Category / Sub Category、列はYear / Quarter / Month Shortです。Region別またはGross ProfitのPlan値がすでにあるとは仮定しません。サンプルのFY26値はワークショップ用フィクスチャであり、現実世界のFY26実績ではありません。

| ルート | 対象 | 状態 |
|---|---|---|
| **合成サンプルルート** | 同梱CSVをLakehouseへアップロードし、Part 3のWarehouse / Spark SQL、Part 4のOntology、Part 5のData Agentを試す | Part 3〜5をこの合成CSVで実機確認済み。これは実Planからの抽出や本番データの検証ではない |

<!-- presentation-exclude-start: LAB09-REAL-PLAN-ROUTE -->
| ルート | 対象 | 状態 |
|---|---|---|
| **実Planルート** | Part 1〜2で自分のLab04データから完全な比較Snapshotを作り、Part 3以降へ渡す | 手順上の確認項目。Part 1〜2の実Plan / writeback抽出を含む実機End-to-End確認は未実施 |
<!-- presentation-exclude-end: LAB09-REAL-PLAN-ROUTE -->

### 確認済みの範囲

- **確認済み:** 合成CSVの18行をWarehouse StageへCOPYし、件数 / キー / 値の検査に合格。LakehouseにProduct 6行、Period 3行、Revenue Observation 18行のDeltaテーブルを作成。Ontologyのentity type / relationship typeをグラフへ投影し、3つのentity typeと2つのrelationship typeがmaterializeされた状態を確認。Data Agentでは下表のQ1 / Q3 / Q4cが期待値と一致しました。
- **確認済みの限定:** `nodes 3 / edges 2`はOntologyのentity type 3種類 / relationship type 2種類を示す構成表示です。18件のObservationを含むデータインスタンス数や、グラフのedge traversalを検証した数ではありません。

<!-- presentation-exclude-start: LAB09-VERIFICATION-BACKLOG -->
Edge traversalは未確認です。

- **未確認:** 実Plan / writebackからの抽出、Q2、Q5、合計比率だけを尋ねる質問、Q4cの生成SQL表示、`_LH2`のinstructionsがAgent再読込後にも残ること、edge traversal。日本語質問の全パターンや本番利用の適合性も保証しません。
<!-- presentation-exclude-end: LAB09-VERIFICATION-BACKLOG -->

- **失敗の記録:** Q4 / Q4aは`SQLCandidatesFailedFilterError`になりました。複数月を指定する質問全般が失敗するとは結論付けず、同じ失敗を成功例として扱いません。

<!-- presentation-exclude-start: LAB09-ERROR-CAUSE-SUMMARY -->
Q4 / Q4aの失敗の原因は特定されていません。
<!-- presentation-exclude-end: LAB09-ERROR-CAUSE-SUMMARY -->

## 2. 前提条件と安全上の注意

### Fabric / AI

- Data Agentは有料F2以上またはFabric有効化済みP1以上の容量が必要です。Planningの試用条件だけでData Agentが利用できるとは限りません。容量、OneLake、Warehouseの課金を管理者と確認します。
- Tenant管理者がCopilot / Azure OpenAIの利用、クロスジオ処理 / 保存の設定を組織ポリシーに照らして確認します。ユーザー自身で設定を変更しません。
- OntologyはPreviewです。テナント設定、地域での提供、作成権限を事前確認します。画面と機能は更新されます。
- Data Agentはユーザー本人の権限でソースを読み取ります。Planを変更、承認、書き戻しできません。Ontologyとそのバインディングの作成 / 編集権限も別途必要です。
- 合成データで再実行する場合も専用の新規演習アイテムを使い、既存アイテムが見つかったら停止します。既存テーブルを`DROP`、`TRUNCATE`、`DELETE`、`CREATE OR REPLACE`で上書きしません。今回のSpark `CREATE OR REPLACE TABLE`は新規専用テーブルに実行した実証記録であり、既存テーブルへの公開手順ではありません。
- テナントID、アカウント名、トークン、資格情報、顧客データをプロンプト、公開ログ、画像、CSVへ含めません。Data Agentの会話 / データ処理に関する保存と監査の条件も管理者に確認します。

### データ経路

<!-- presentation-exclude-start: LAB09-REAL-PLAN-PREPARATION -->
- **実Planルート:** Part 1〜2でLab04の保存済みForecastとセマンティックモデルのGross Revenueを同一粒度で抽出し、全件一致を確認してからCSVを用意します。ここは実機でEnd-to-End確認していません。
<!-- presentation-exclude-end: LAB09-REAL-PLAN-PREPARATION -->

- **合成サンプルルート:** Part 1〜2を行わず、同梱の`data/lab09-variance-snapshot-sample.csv`を使います。このCSVの値は合成です。Part 3〜5で実証したUI操作を再現するためのルートです。

> [!WARNING]
> Fabricの実Planルートでは、Plan / writebackの対象テーブルや既存値を書き換えません。Tenant AI設定、権限、アイテム作成、容量消費、ファイルアップロードなど、影響のある操作は管理者の承認後に行います。本書のキャプチャは個人情報等を含まないマスク済み画面ですが、実環境で証拠を撮る場合は共有前に個人名、workspace識別子、URL、IDを確認してください。

## 3. データ契約

比較CSVは[`data/lab09-variance-snapshot-template.csv`](../data/lab09-variance-snapshot-template.csv)の15列を使います。テンプレートはヘッダーだけで、実Planの値は含みません。

| 列 | 内容 |
|---|---|
| `SnapshotId`, `ScenarioName`, `PlanVersion`, `SourceWritebackRunIds` | 1つの選択Snapshotと、選択したScenario / Plan状態 / 元のwriteback実行の追跡情報 |
| `ProductKey`, `Category`, `SubCategory` | 製品の安定キーと、元モデルの分類 |
| `PeriodKey`, `PeriodStart`, `PlanPeriodStatus` | `YYYY-MM`、月初日、`ClosedLinkedActual`または`OpenSampleReference` |
| `CurrencyCode` | この演習では`USD` |
| `ModelMeasureName`, `ModelGrossRevenue` | `Gross Revenue`と同一Product / 月の値 |
| `PlanMeasureName`, `PlanForecast` | `Forecast`と同じProduct / 月 / Scenarioの値 |

1行は`SnapshotId × ScenarioName × PlanVersion × ProductKey × PeriodKey`で一意にします。金額はCSVで精度を保ち、Warehouseでは`decimal(28,10)`、Ontology / Graphで使うLakehouse列では実証に合わせ`DOUBLE`とします。Graph側の値は浮動小数点表示になるため、正確な金額の基準と独立検算にはWarehouseのDecimal値を使います。

- **Closed period:** 選択したPlan状態でForecastが実績メジャーにリンクしている月。Planの表示上の状態と対象Snapshotを確認します。
- **Open period:** Planの見通しとサンプルモデル値を比較する月です。モデル値を確定実績と呼びません。
- 分母の`ModelGrossRevenue`が0なら`VarianceRate`はNULLです。NULLを0に置き換えません。
- Long with Changesの履歴を足し上げたり、`TOP 1`や最大timestampだけで現行値を選びません。完全な現在状態を証明できなければPart 1で停止します。

<!-- presentation-exclude-start: LAB09-PART1-PROCEDURE -->
## 4. Part 1：実Planから比較Snapshotを準備する（実機未検証）

**合成サンプルルートではこのPartを飛ばし、Part 3へ進みます。** 以下は実Planを使う場合の安全な準備手順ですが、実Plan / writebackを使った一連の抽出は未検証です。画面や書き戻しスキーマが本書と異なる場合は推測せず停止してください。

1. Lab04のForecast sheetを開き、選択するScenario、期間、`Close Period till`、保存状態を人が決めます。`SnapshotId`と`PlanVersion`を一意に記録します。時間が最も新しいというだけで状態を選びません。
2. Writeback Logsで対象の成功した操作を確認し、`SourceWritebackRunIds`の出典を残します。対象Scenario / Measure / Product / Periodの全行がどの状態を構成するか明確でなければ停止します。
3. Lab04のSQL宛先の実スキーマを読み、Category / Sub Category / Year / Month / Scenario / Measure / Valueに対応する実在列を特定します。`IsLatest`、`PreviousValue`、実行IDなどは実在し、公式の意味と選択範囲での値を確認できた場合のみ使います。
4. 選択した全キーについて現在値が1行ずつ存在することを確認します。履歴行が差分なら履歴を合計して現在値を再構成しません。現在値の全件状態を証明できない場合、承認済みのサポートされた手順で完全なSnapshotを作れるまで停止します。

<!-- presentation-exclude-end: LAB09-PART1-PROCEDURE -->

<!-- presentation-exclude-start: LAB09-PART2-PROCEDURE -->
## 5. Part 2：実績 / Forecastを同じ粒度で照合する（実機未検証）

1. 元レポートを変更せず、一時レポートまたは承認済みエクスポート経路を用意します。Dataペインで存在を確認した`Product[Category]`、`Product[Sub Category]`、`Date[Year]`と`Date[Month]`または`Date[Year Month]`、`Measures Table[Gross Revenue]`を使います。Month Shortだけでは期間キーにしません。
2. 選択した期間の全件をサマリー済みCSVへ出力します。列の欠落、エクスポート上限、異なる月 / 製品があれば停止し、基になる別メジャーを推測しません。
3. Forecast宛先から確認済みの列だけで同じScenario / Measure / Year / Month / Productの全行を抽出します。計画とモデルで製品キー / 月キーの対応を確定し、`ProductKey`と`PeriodKey`を文字列として作ります。
4. 両方の全件エクスポートで`ProductKey + PeriodKey`ごとに重複がないことを確認し、Full Outer結合でキー集合を比較します。片側だけのキーが1件でもある、行数が一致しない、通貨 / Measure / PeriodStatusが不明なら停止します。欠損行を補完したり0で埋めたりしません。
5. 実Planルートを選んで実施する場合、選択したSnapshot / Scenario / PlanVersionについて、各ソースの全行数と一意キー件数、結合後の正の期待件数を組織承認済みの非公開記録に残します。期待件数を0または未記入のままロードしません。
6. 列契約に合わせて15列のUTF-8 CSVを作り、独立して確認した正の`ExpectedRows`はCSVに追加せず非公開の検算記録へ保存します。金額の精度を保ち、PeriodStartがPeriodKeyの月初日であることを確認します。

<!-- presentation-exclude-end: LAB09-PART2-PROCEDURE -->

## 6. Part 3A：CSVをLakehouseへ置き、Warehouseで照合する

以下は同梱の合成サンプルルートで確認した操作です。初回の空のLab09演習アイテムに限ります。作成先に同名アイテム、同名フォルダー、同名テーブルが既にある場合は停止し、削除や上書きで空にしません。

### 6.1 Lakehouseを作成してCSVをアップロード

1. 承認済みの演習Workspaceで **+ New item → Lakehouse** を選びます。`Lakehouse schemas`が有効であることを確認して作成します。実証時のアイテム名は`HPC_Lab09_Staging`でした。名前は自分の新規Workspace内で一意なものにし、同名があれば止めます。

   ![Lab09の新規アイテムの名前入力画面（キャプチャ 002）](../assets/screenshots/lab09/02-new-lakehouse-dialog.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 003）](../assets/screenshots/lab09/003-lakehouse-created.png)

2. Lakehouseの **Files** に`Lab09`、その下に新規の`run-sample001`フォルダーを作成します。再実行する場合は既存フォルダーを再利用せず、新しい承認済みrun名を使い、SQLパスも合わせます。

   ![Lab09のフォルダー / CSV配置操作画面（キャプチャ 004）](../assets/screenshots/lab09/004-files-context-menu.png)
   ![Lab09のフォルダー / CSV配置操作画面（キャプチャ 005）](../assets/screenshots/lab09/005-new-subfolder-lab09.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 006）](../assets/screenshots/lab09/006-lab09-folder-created.png)
   ![Lab09のフォルダー / CSV配置操作画面（キャプチャ 007）](../assets/screenshots/lab09/007-new-subfolder-run-sample001.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 008）](../assets/screenshots/lab09/008-folders-created.png)

3. `run-sample001`を開き、**Get data → Upload files**から`data/lab09-variance-snapshot-sample.csv`を選択します。Upload完了後、対象フォルダーにCSVが1つあり、ファイル名とサイズが表示されることを確認します。ローカルファイル選択ダイアログや個人端末のパスはキャプチャ / 公開しません。


   ![Lab09の未設定の画面（キャプチャ 009）](../assets/screenshots/lab09/009-run-sample001-empty-folder.png)
   ![Lab09のフォルダー / CSV配置操作画面（キャプチャ 010）](../assets/screenshots/lab09/010-folder-get-data-menu.png)
   ![Lab09のアップロード対象の選択画面（キャプチャ 011）](../assets/screenshots/lab09/011-upload-files-panel.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 013）](../assets/screenshots/lab09/013-csv-uploaded.png)
   ![Lab09のフォルダー / CSV配置操作画面（キャプチャ 014）](../assets/screenshots/lab09/014-folder-with-file.png)

### 6.2 WarehouseのStageに型を明示してロード

1. 同じ演習用Workspaceで新しい**Warehouse**（実証時の表示名`HPC_Lab09_Analysis`）を作成します。Warehouseは数値の照合 / 検算用で、OntologyのGraphバインディング先にはしません。

   ![Lab09の新規アイテムの名前入力画面（キャプチャ 017）](../assets/screenshots/lab09/17-new-warehouse-dialog.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 018）](../assets/screenshots/lab09/018-warehouse-created-welcome.png)

2. SQL query editorで新規の`dbo.Lab09Stage`を作ります。既存の同名テーブルがあれば停止します。`ModelGrossRevenue`と`PlanForecast`はDecimal型で受けます。`float`は使いません。

   ```sql
   CREATE TABLE dbo.Lab09Stage
   (
       SnapshotId varchar(128) NULL,
       ScenarioName varchar(256) NULL,
       PlanVersion varchar(128) NULL,
       SourceWritebackRunIds varchar(2000) NULL,
       ProductKey varchar(256) NULL,
       Category varchar(256) NULL,
       SubCategory varchar(256) NULL,
       PeriodKey char(7) NULL,
       PeriodStart date NULL,
       PlanPeriodStatus varchar(32) NULL,
       CurrencyCode char(3) NULL,
       ModelMeasureName varchar(128) NULL,
       ModelGrossRevenue decimal(28, 10) NULL,
       PlanMeasureName varchar(128) NULL,
       PlanForecast decimal(28, 10) NULL
   );
   ```

   ![Lab09のWarehouseの作成 / SQL編集画面（キャプチャ 019）](../assets/screenshots/lab09/019-warehouse-home.png)
   ![Lab09のWarehouseの作成 / SQL編集画面（キャプチャ 020）](../assets/screenshots/lab09/020-warehouse-sql-editor-empty.png)
   ![Lab09の実行するSQL入力画面（キャプチャ 021）](../assets/screenshots/lab09/021-stage-ddl-in-editor.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 022）](../assets/screenshots/lab09/022-stage-ddl-succeeded.png)

3. CSVを置いたOneLake Lakehouse Filesの完全なパスをFabric UIで確認し、次の例の `<workspace>`、`<lakehouse>`、runフォルダーとファイル名を置き換えます。実証時は **CREDENTIAL句なし**のEntraパススルーで18行が読み込まれました。`CREDENTIAL = (IDENTITY = 'Workspace Identity')`を加えた実証はMsg 13840で失敗しました。Workspace Identityは必須条件とせず、組織が別途承認 / 構成したときだけ検討します。

   ```sql
   COPY INTO dbo.Lab09Stage
   (
       SnapshotId, ScenarioName, PlanVersion, SourceWritebackRunIds,
       ProductKey, Category, SubCategory, PeriodKey, PeriodStart,
       PlanPeriodStatus, CurrencyCode, ModelMeasureName, ModelGrossRevenue,
       PlanMeasureName, PlanForecast
   )
   FROM 'https://onelake.dfs.fabric.microsoft.com/<workspace>/<lakehouse>/Files/Lab09/run-sample001/lab09-variance-snapshot-sample.csv'
   WITH
   (
       FILE_TYPE = 'CSV',
       FIRSTROW = 2,
       ENCODING = 'UTF8',
       FIELDTERMINATOR = ',',
       FIELDQUOTE = '"'
   );
   ```

   ![Lab09の実行するSQL入力画面（キャプチャ 023）](../assets/screenshots/lab09/023-copy-into-editor.png)
   ![Lab09の失敗または制限メッセージ（キャプチャ 024）](../assets/screenshots/lab09/024-copy-into-workspace-identity-error.png)
   ![Lab09の実行するSQL入力画面（キャプチャ 025）](../assets/screenshots/lab09/025-copy-into-no-credential-in-editor.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 026）](../assets/screenshots/lab09/026-copy-into-succeeded.png)

4. COPYの実行結果と`SELECT COUNT_BIG(*) FROM dbo.Lab09Stage`を確認します。合成サンプルの独立期待件数は18です。実Planルートでは、Part 2で非公開に記録した正のExpectedRowsを使い、元の両エクスポートの全行数 / 一意キー件数 / Full Outer欠損0件とも照合します。0件、ヘッダーのみ、予期しない件数、失敗 / rejectがあれば次へ進まず停止します。


   **18行を読み込んだ結果を確認します。**
   ![Lab09の実行後の成功結果画面（キャプチャ 027）](../assets/screenshots/lab09/027-stage-count-18.png)

### 6.3 Stageの選択範囲とデータ品質を検査

以下の値は合成CSVに記録された`SnapshotId = 'LAB09-SAMPLE-001'`、`ScenarioName = 'Base'`、`PlanVersion = 'FY26-Workshop-v1'`です。実Planルートでは自分が検証済みの値に置換します。ExpectedRowsはソース比較から**独立に記録した正の値**にします。

```sql
SELECT
    CAST('18' AS bigint) AS ExpectedRows,
    CASE WHEN CAST('18' AS bigint) <= 0 THEN 1 ELSE 0 END AS InvalidExpectedRows,
    COUNT_BIG(*) AS AllStageRows,
    COALESCE(SUM(CASE WHEN SnapshotId = 'LAB09-SAMPLE-001'
                       AND ScenarioName = 'Base'
                       AND PlanVersion = 'FY26-Workshop-v1'
                      THEN 1 ELSE 0 END), 0) AS SelectedRows
FROM dbo.Lab09Stage;

SELECT ProductKey, PeriodKey, COUNT_BIG(*) AS DuplicateRows
FROM dbo.Lab09Stage
WHERE SnapshotId = 'LAB09-SAMPLE-001'
  AND ScenarioName = 'Base'
  AND PlanVersion = 'FY26-Workshop-v1'
GROUP BY ProductKey, PeriodKey
HAVING COUNT_BIG(*) <> 1;

SELECT COUNT_BIG(*) AS InvalidSelectedRows
FROM dbo.Lab09Stage
WHERE SnapshotId = 'LAB09-SAMPLE-001'
  AND ScenarioName = 'Base'
  AND PlanVersion = 'FY26-Workshop-v1'
  AND (
      NULLIF(LTRIM(RTRIM(SnapshotId)), '') IS NULL
      OR NULLIF(LTRIM(RTRIM(ScenarioName)), '') IS NULL
      OR NULLIF(LTRIM(RTRIM(PlanVersion)), '') IS NULL
      OR NULLIF(LTRIM(RTRIM(SourceWritebackRunIds)), '') IS NULL
      OR NULLIF(LTRIM(RTRIM(ProductKey)), '') IS NULL
      OR NULLIF(LTRIM(RTRIM(Category)), '') IS NULL
      OR NULLIF(LTRIM(RTRIM(SubCategory)), '') IS NULL
      OR NULLIF(LTRIM(RTRIM(PeriodKey)), '') IS NULL
      OR PeriodKey NOT LIKE '[12][0-9][0-9][0-9]-[01][0-9]'
      OR RIGHT(PeriodKey, 2) NOT BETWEEN '01' AND '12'
      OR PeriodStart IS NULL
      OR PeriodKey <> CONVERT(char(7), PeriodStart, 126)
      OR DAY(PeriodStart) <> 1
      OR PlanPeriodStatus IS NULL
      OR PlanPeriodStatus NOT IN ('ClosedLinkedActual', 'OpenSampleReference')
      OR CurrencyCode IS NULL OR CurrencyCode <> 'USD'
      OR ModelMeasureName IS NULL OR ModelMeasureName <> 'Gross Revenue'
      OR PlanMeasureName IS NULL OR PlanMeasureName <> 'Forecast'
      OR ModelGrossRevenue IS NULL OR PlanForecast IS NULL
  );

SELECT COUNT_BIG(*) AS WrongSelectedRows
FROM dbo.Lab09Stage
WHERE SnapshotId <> 'LAB09-SAMPLE-001'
   OR ScenarioName <> 'Base'
   OR PlanVersion <> 'FY26-Workshop-v1';

SELECT ProductKey, COUNT_BIG(*) AS ConflictingProductRows
FROM (
    SELECT DISTINCT ProductKey, Category, SubCategory
    FROM dbo.Lab09Stage
    WHERE SnapshotId = 'LAB09-SAMPLE-001'
      AND ScenarioName = 'Base'
      AND PlanVersion = 'FY26-Workshop-v1'
) AS ProductRows
GROUP BY ProductKey
HAVING COUNT_BIG(*) <> 1;

SELECT PeriodKey, COUNT_BIG(*) AS ConflictingPeriodRows
FROM (
    SELECT DISTINCT PeriodKey, PeriodStart, PlanPeriodStatus
    FROM dbo.Lab09Stage
    WHERE SnapshotId = 'LAB09-SAMPLE-001'
      AND ScenarioName = 'Base'
      AND PlanVersion = 'FY26-Workshop-v1'
) AS PeriodRows
GROUP BY PeriodKey
HAVING COUNT_BIG(*) <> 1;
```

![Lab09の実行するSQL入力画面（キャプチャ 028）](../assets/screenshots/lab09/028-validation-q1q2-in-editor.png)
![Lab09の検算結果の画面（キャプチャ 029）](../assets/screenshots/lab09/029-validation-q1-result.png)
![Lab09の実行後の成功結果画面（キャプチャ 031）](../assets/screenshots/lab09/031-validation-q1q2-messages.png)
![Lab09の実行するSQL入力画面（キャプチャ 032）](../assets/screenshots/lab09/032-validation-q3-in-editor.png)
![Lab09の検算結果の画面（キャプチャ 033）](../assets/screenshots/lab09/033-validation-q3-result.png)
![Lab09の実行後の成功結果画面（キャプチャ 036）](../assets/screenshots/lab09/036-validation-q4q5-messages.png)


続行条件は、`ExpectedRows > 0`、`InvalidExpectedRows = 0`、全Stage行数 = 選択行数 = ExpectedRows、誤ったIDの行が0、重複 / 不正行 / 製品次元矛盾 / 期間次元矛盾がすべて0件です。実Planルートではこれに加え、Full Outerで照合した全元キーが一致している非公開記録を確認します。空の表は、失敗行が0件に見えるだけなので合格ではありません。

次に、Warehouse内で選択Snapshotの製品 / 期間ディメンションとObservationを新しいテーブル名に作成します。既存同名テーブルがある場合は停止します。SQLは検算用で、Ontologyのバインディング先には使いません。

```sql
CREATE TABLE dbo.Lab09Product AS
SELECT DISTINCT ProductKey, Category, SubCategory
FROM dbo.Lab09Stage
WHERE SnapshotId = 'LAB09-SAMPLE-001'
  AND ScenarioName = 'Base'
  AND PlanVersion = 'FY26-Workshop-v1';

CREATE TABLE dbo.Lab09Period AS
SELECT DISTINCT PeriodKey, PeriodStart, PlanPeriodStatus
FROM dbo.Lab09Stage
WHERE SnapshotId = 'LAB09-SAMPLE-001'
  AND ScenarioName = 'Base'
  AND PlanVersion = 'FY26-Workshop-v1';

CREATE TABLE dbo.Lab09RevenueObservation AS
SELECT
    CONCAT(SnapshotId, '|', ScenarioName, '|', PlanVersion, '|',
           ProductKey, '|', PeriodKey) AS ObservationKey,
    SnapshotId, ScenarioName, PlanVersion, SourceWritebackRunIds,
    ProductKey, PeriodKey, PlanPeriodStatus, CurrencyCode,
    ModelMeasureName, ModelGrossRevenue, PlanMeasureName, PlanForecast,
    CAST(PlanForecast - ModelGrossRevenue AS decimal(29, 10)) AS VarianceAmount,
    CAST(CASE WHEN ModelGrossRevenue = 0 THEN NULL
              ELSE (PlanForecast - ModelGrossRevenue)
                   / NULLIF(ModelGrossRevenue, 0)
         END AS decimal(38, 9)) AS VarianceRate
FROM dbo.Lab09Stage
WHERE SnapshotId = 'LAB09-SAMPLE-001'
  AND ScenarioName = 'Base'
  AND PlanVersion = 'FY26-Workshop-v1';
```

![Lab09の実行するSQL入力画面（キャプチャ 037）](../assets/screenshots/lab09/037-ctas-in-editor.png)
![Lab09の作成またはロード完了画面（キャプチャ 038）](../assets/screenshots/lab09/038-ctas-succeeded-messages.png)
![Lab09の実行するSQL入力画面（キャプチャ 040）](../assets/screenshots/lab09/040-step9-checks-in-editor.png)
![Lab09の検算結果の画面（キャプチャ 041）](../assets/screenshots/lab09/041-step9-checks-result.png)


次のSQLは差異式、0分母 / NULL比率、行数、重複、Stageとの欠落 / 余剰、孤立したProduct / Periodキーを検査します。`DuplicateKeys`から`OrphanPeriodKeys`まではすべて0、StageRowsとObservationRowsは同じ正のExpectedRowsでなければなりません。

```sql
SELECT 'DuplicateKeys' AS CheckName, COUNT_BIG(*) AS CheckValue
FROM (
    SELECT ObservationKey
    FROM dbo.Lab09RevenueObservation
    GROUP BY ObservationKey
    HAVING COUNT_BIG(*) <> 1
) AS D
UNION ALL
SELECT 'InvalidVarianceRows', COUNT_BIG(*)
FROM dbo.Lab09RevenueObservation
WHERE VarianceAmount IS NULL
   OR VarianceAmount <> CAST(
          CAST(PlanForecast AS decimal(28, 10))
          - CAST(ModelGrossRevenue AS decimal(28, 10))
          AS decimal(29, 10)
      )
   OR (ModelGrossRevenue = 0 AND VarianceRate IS NOT NULL)
   OR (ModelGrossRevenue <> 0 AND
       (VarianceRate IS NULL OR VarianceRate <> CAST(
           (CAST(PlanForecast AS decimal(28, 10))
            - CAST(ModelGrossRevenue AS decimal(28, 10)))
           / NULLIF(CAST(ModelGrossRevenue AS decimal(28, 10)), 0)
           AS decimal(38, 9)
       )))
UNION ALL
SELECT 'StageRows', COUNT_BIG(*)
FROM dbo.Lab09Stage
WHERE SnapshotId = 'LAB09-SAMPLE-001'
  AND ScenarioName = 'Base'
  AND PlanVersion = 'FY26-Workshop-v1'
UNION ALL
SELECT 'ObservationRows', COUNT_BIG(*)
FROM dbo.Lab09RevenueObservation
UNION ALL
SELECT 'MissingObservations', COUNT_BIG(*)
FROM dbo.Lab09Stage AS S
WHERE S.SnapshotId = 'LAB09-SAMPLE-001'
  AND S.ScenarioName = 'Base'
  AND S.PlanVersion = 'FY26-Workshop-v1'
  AND NOT EXISTS (
      SELECT 1 FROM dbo.Lab09RevenueObservation AS O
      WHERE O.SnapshotId = S.SnapshotId
        AND O.ScenarioName = S.ScenarioName
        AND O.PlanVersion = S.PlanVersion
        AND O.ProductKey = S.ProductKey
        AND O.PeriodKey = S.PeriodKey
  )
UNION ALL
SELECT 'ExtraObservations', COUNT_BIG(*)
FROM dbo.Lab09RevenueObservation AS O
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.Lab09Stage AS S
    WHERE S.SnapshotId = O.SnapshotId
      AND S.ScenarioName = O.ScenarioName
      AND S.PlanVersion = O.PlanVersion
      AND S.ProductKey = O.ProductKey
      AND S.PeriodKey = O.PeriodKey
)
UNION ALL
SELECT 'OrphanProductKeys', COUNT_BIG(*)
FROM dbo.Lab09RevenueObservation AS O
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.Lab09Product AS P WHERE P.ProductKey = O.ProductKey
)
UNION ALL
SELECT 'OrphanPeriodKeys', COUNT_BIG(*)
FROM dbo.Lab09RevenueObservation AS O
WHERE NOT EXISTS (
    SELECT 1 FROM dbo.Lab09Period AS P WHERE P.PeriodKey = O.PeriodKey
);
```

![Lab09の実行するSQL入力画面（キャプチャ 042）](../assets/screenshots/lab09/042-aggregates-in-editor.png)
![Lab09の検算結果の画面（キャプチャ 043）](../assets/screenshots/lab09/043-aggregates-result.png)
![Lab09の検算結果の画面（キャプチャ 044）](../assets/screenshots/lab09/044-march-rows-nuts-null.png)


このほか、`ExpectedRows > 0`、`AllStageRows = SelectedRows = ExpectedRows`、選択ID以外 / NULLキー / 空文字 / 不正期間 / 不正ステータス / 通貨やMeasureの違い / ProductKeyやPeriodKeyの属性不一致が0件であることを確認します。実PlanルートではFull Outerで照合した全元キーが一致している非公開記録も必要です。再計算式だけを正しさの証拠にせず、元の全件キー集合とSnapshotの数値を独立確認します。

## 7. Part 3B：LakehouseにDeltaテーブルを作る

Warehouseは精度を保つ検算層です。Ontology / Graph / Data Agent用には、Lakehouseのスキーマ有効化済みLakehouseに管理Deltaテーブルを作ります。実証ではWarehouseにバインドしたOntologyがGraphで`Ineligible / Unsupported Datasource`となり、Data Agentが汎用エラーになりました。Lakehouse Deltaへ切り替えて成功しましたが、変更を同時に行ったため、どの条件が単独で必要だったかは切り分けられていません。

1. `HPC_Lab09_Staging`を開き、**Analyze data with → New Spark SQL query**を選びます。クエリエディターをクリックしてから入力します。初回RunではSpark sessionの起動に時間がかかる場合があります。

   ![Lab09の操作画面（キャプチャ 179）](../assets/screenshots/lab09/179-lakehouse-analyze-data-with-menu.png)
   ![Lab09の操作画面（キャプチャ 180）](../assets/screenshots/lab09/180-lakehouse-new-spark-sql-query-editor.png)

2. 次の一文だけをクエリータブへ入力してRunします。`CREATE OR REPLACE`は、今回のように新規の専用Lakehouse内でテーブルが存在しないことを確認した場合に限ります。既存テーブルがあればRunせず停止します。

   ```sql
   CREATE OR REPLACE TEMPORARY VIEW lab09_stage USING csv OPTIONS (path 'Files/Lab09/run-sample001/lab09-variance-snapshot-sample.csv', header 'true');
   ```

3. **RunごとにSpark SQLを1文だけ**実行します。複数文を同じRunに入れると`PARSE_SYNTAX_ERROR`になります。Temp viewはSpark sessionの一時ビューです。sessionが終了した場合は、この文を先に再実行します。

   ![Lab09の実行するSQL入力画面（キャプチャ 181）](../assets/screenshots/lab09/181-lakehouse-spark-sql-script-typed.png)
   ![Lab09の失敗または制限メッセージ（キャプチャ 183）](../assets/screenshots/lab09/183-lakehouse-spark-sql-multi-statement-parse-error.png)
   ![Lab09の実行するSQL入力画面（キャプチャ 184）](../assets/screenshots/lab09/184-spark-tempview-typed.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 185）](../assets/screenshots/lab09/185-spark-tempview-succeeded.png)

4. 次のSQLをそれぞれ別のクエリータブまたはRunで実行します。これらの固定テーブル名がすでに存在するときは上書きせず止めてください。実証時は新規専用テーブルに対し、各文を1回ずつ実行しました。

   ```sql
   CREATE OR REPLACE TABLE dbo.lab09_product USING DELTA AS
   SELECT DISTINCT ProductKey, Category, SubCategory
   FROM lab09_stage;
   ```

   ```sql
   CREATE OR REPLACE TABLE dbo.lab09_period USING DELTA AS
   SELECT DISTINCT PeriodKey, CAST(PeriodStart AS DATE) AS PeriodStart, PlanPeriodStatus
   FROM lab09_stage;
   ```

   ```sql
   CREATE OR REPLACE TABLE dbo.lab09_revenue_observation USING DELTA AS
   SELECT
       concat_ws('|', SnapshotId, ScenarioName, PlanVersion, ProductKey, PeriodKey) AS ObservationKey,
       SnapshotId, ScenarioName, PlanVersion, SourceWritebackRunIds,
       ProductKey, PeriodKey, PlanPeriodStatus, CurrencyCode, ModelMeasureName,
       CAST(ModelGrossRevenue AS DOUBLE) AS ModelGrossRevenue,
       PlanMeasureName,
       CAST(PlanForecast AS DOUBLE) AS PlanForecast,
       CAST(PlanForecast AS DOUBLE) - CAST(ModelGrossRevenue AS DOUBLE) AS VarianceAmount,
       (CAST(PlanForecast AS DOUBLE) - CAST(ModelGrossRevenue AS DOUBLE))
           / NULLIF(CAST(ModelGrossRevenue AS DOUBLE), 0) AS VarianceRate
   FROM lab09_stage;
   ```

   ![Lab09の実行するSQL入力画面（キャプチャ 187）](../assets/screenshots/lab09/187-spark-product-ctas-typed.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 188）](../assets/screenshots/lab09/188-spark-product-ctas-succeeded.png)
   ![Lab09の実行するSQL入力画面（キャプチャ 189）](../assets/screenshots/lab09/189-spark-period-ctas-typed.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 190）](../assets/screenshots/lab09/190-spark-period-ctas-succeeded.png)
   ![Lab09の実行するSQL入力画面（キャプチャ 191）](../assets/screenshots/lab09/191-spark-revenue-ctas-typed-tail.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 192）](../assets/screenshots/lab09/192-spark-revenue-ctas-succeeded.png)

5. Lakehouse ExplorerをRefreshし、Tables / dboに3つのテーブルが見えることを確認します。Spark SQLの結果でProduct 6行、Period 3行、Revenue Observation 18行 / 15列であることを確認します。15列はObservationKey、SnapshotId、ScenarioName、PlanVersion、SourceWritebackRunIds、ProductKey、PeriodKey、PlanPeriodStatus、CurrencyCode、ModelMeasureName、ModelGrossRevenue、PlanMeasureName、PlanForecast、VarianceAmount、VarianceRateです。キーはString、期間はDate、4つの数値列はDoubleです。


   ![Lab09の操作画面（キャプチャ 194）](../assets/screenshots/lab09/194-spark-counts-result.png)
   ![Lab09の操作画面（キャプチャ 195）](../assets/screenshots/lab09/195-lakehouse-explorer-delta-tables.png)
   ![Lab09の操作画面（キャプチャ 196）](../assets/screenshots/lab09/196-lakehouse-explorer-revenue-columns.png)

## 8. Part 4：Ontologyを定義してGraphをmaterializeする

Ontologyはエンティティ / 関係 / ルールとデータバインディングを持つPreviewの意味付け層です。以下ではPart 3BのLakehouse管理Deltaテーブルをバインドします。Warehouseは独立した数値検算に使います。

実証では先にWarehouseのテーブルをOntologyへバインドしましたが、Manage graphで`Unsupported Datasource`となり、Data Agentも汎用エラーになりました。この初回失敗は履歴として示します。再現手順としてWarehouseをGraph sourceに設定せず、Part 3AのWarehouseは数値検算に使い、以降のOntology / GraphではLakehouse Deltaを使います。

<!-- presentation-exclude-start: LAB09-WAREHOUSE-CAUSE -->
Warehouse / Lakehouseの変更を同時に行ったため、単独の根本原因は特定されていません。
<!-- presentation-exclude-end: LAB09-WAREHOUSE-CAUSE -->




![Lab09の失敗または制限メッセージ（キャプチャ 172）](../assets/screenshots/lab09/172-chat-question1-answer-cannot-work-with-content.png)
![Lab09の操作画面（キャプチャ 176）](../assets/screenshots/lab09/176-ontology-manage-graph-all-entities-ineligible.png)
![Lab09の失敗または制限メッセージ（キャプチャ 177）](../assets/screenshots/lab09/177-ontology-manage-graph-unsupported-datasource-popup.png)

### 8.1 Ontologyを作成する

1. Workspaceで **+ New item → Ontology (Preview)** を選びます。実証時の名前は`HPC_Lab09_VarianceOntology_LH`です。作成できる地域 / tenant settingとPreview状態を確認します。

   ![Lab09の新規アイテムの名前入力画面（キャプチャ 197）](../assets/screenshots/lab09/197-new-ontology-dialog-lh-name.png)
   ![Lab09の操作画面（キャプチャ 199）](../assets/screenshots/lab09/199-lh-ontology-get-started.png)

2. **+ Add entity type**で`Product`を作ります。entity typeの作成は名前を入力して確定します。

   ![Lab09のエンティティ追加画面（キャプチャ 200）](../assets/screenshots/lab09/200-lh-add-entity-type-product.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 201）](../assets/screenshots/lab09/201-lh-product-entity-created.png)

3. `Product`の **Configure → Manage property bindings → Add binding and properties** を開き、OneLake catalogでLakehouse → `dbo` → `lab09_product`を選びます。表示されたProductKey / Category / SubCategoryをそれぞれ同名のsource columnへバインドします。

   ![Lab09のプロパティバインドの設定画面（キャプチャ 203）](../assets/screenshots/lab09/203-lh-bind-data-add-source.png)
   ![Lab09のOneLake catalogでのテーブル選択画面（キャプチャ 204）](../assets/screenshots/lab09/204-lh-onelake-catalog-filtered.png)
   ![Lab09のプロパティバインドの設定画面（キャプチャ 207）](../assets/screenshots/lab09/207-lh-onelake-select-lab09-product.png)
   ![Lab09のプロパティバインドの設定画面（キャプチャ 209）](../assets/screenshots/lab09/209-lh-bind-data-properties-mapping.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 210）](../assets/screenshots/lab09/210-lh-bind-data-created-success.png)
   ![Lab09の操作画面（キャプチャ 211）](../assets/screenshots/lab09/211-lh-product-configure-bound.png)

4. **Define entity type key**を開き、`ProductKey`をkeyにします。Instancesにテーブルが見えないエラーが出ても、直ちにバインディング失敗と断定しません（後述のトラブル対応）。GraphのEligibility、sourceとkeyの設定を別々に確認します。


   ![Lab09のエンティティキーの設定画面（キャプチャ 214）](../assets/screenshots/lab09/214-lh-key-productkey-checked.png)
   ![Lab09のエンティティキーの設定画面（キャプチャ 216）](../assets/screenshots/lab09/216-lh-product-key-defined.png)
   ![Lab09の操作画面（キャプチャ 218）](../assets/screenshots/lab09/218-lh-ontology-home-product-bound.png)

### 8.2 Productだけの診断経路

実証ではLakehouse-bound OntologyにProductだけを作り、Graphをmaterializeして6商品が表示されることを確認しました。このProduct-only試験と当時作成した暫定Agent `_LH` は最終Agentの受入ではありません。

`Manage graph`でProductがEligibleになることを確認し、Choose what to projectでProductを選択してContinue → Materializeします。ボタンがDoneになったらHomeに戻り、Explore graphを開いてProductをRunします。Product-onlyの暫定Agent `_LH` は検証経緯のために残った名前です。最終のOntologyをAgentへ追加する前に、次の手順でOntologyを完成させます。




![Lab09のGraphの投影 / materialize画面（キャプチャ 219）](../assets/screenshots/lab09/219-lh-graph-config-product-eligible.png)
![Lab09のGraphの投影 / materialize画面（キャプチャ 220）](../assets/screenshots/lab09/220-lh-projection-summary-product-only.png)
![Lab09のGraphの投影 / materialize画面（キャプチャ 221）](../assets/screenshots/lab09/221-lh-materialize-creating-graph-product-only.png)
![Lab09のGraphの投影 / materialize画面（キャプチャ 222）](../assets/screenshots/lab09/222-lh-projection-summary-done-button-disabled.png)
![Lab09のGraphの投影 / materialize画面（キャプチャ 223）](../assets/screenshots/lab09/223-lh-ontology-home-after-materialize-explore-graph.png)
![Lab09の新規アイテムの名前入力画面（キャプチャ 230）](../assets/screenshots/lab09/230-lh-create-data-agent-dialog-name.png)
![Lab09の検算結果の画面（キャプチャ 240）](../assets/screenshots/lab09/240-lh-agent-answer-product-list-6-products.png)

### 8.3 PeriodとRevenue Observationを追加する

1. **+ Add entity type**で`Period`を追加します。`lab09_period`をバインドし、`PeriodKey`、`PeriodStart`、`PlanPeriodStatus`を同名列へ割り当てます。`PeriodKey`をentity type keyにします。

   ![Lab09のエンティティ追加画面（キャプチャ 244）](../assets/screenshots/lab09/244-lh-add-entity-type-period.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 245）](../assets/screenshots/lab09/245-lh-period-entity-created.png)
   ![Lab09のプロパティバインドの設定画面（キャプチャ 247）](../assets/screenshots/lab09/247-lh-period-bind-data-empty.png)
   ![Lab09の操作画面（キャプチャ 248）](../assets/screenshots/lab09/248-lh-period-onelake-lakehouse-expanded-dbo.png)
   ![Lab09のプロパティバインドの設定画面（キャプチャ 250）](../assets/screenshots/lab09/250-lh-period-onelake-select-lab09-period.png)
   ![Lab09のプロパティバインドの設定画面（キャプチャ 252）](../assets/screenshots/lab09/252-lh-period-bind-data-properties-mapping.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 253）](../assets/screenshots/lab09/253-lh-period-bind-data-created-success.png)
   ![Lab09の操作画面（キャプチャ 254）](../assets/screenshots/lab09/254-lh-period-configure-bound.png)
   ![Lab09のエンティティキーの設定画面（キャプチャ 259）](../assets/screenshots/lab09/259-lh-period-key-defined.png)

2. **+ Add entity type**で`Revenue Observation`を追加します。`lab09_revenue_observation`をバインドし、以下15列を同名プロパティに割り当てます。`ProductKey`と`PeriodKey`も、後でrelationshipを結ぶために省かずバインドします。keyは`ObservationKey`です。

| Property | Source列 | 用途 / 型 |
|---|---|---|
| `ObservationKey` | `ObservationKey` | Entity key / String |
| `SnapshotId` | `SnapshotId` | スナップショット識別 / String |
| `ScenarioName` | `ScenarioName` | Scenario識別 / String |
| `PlanVersion` | `PlanVersion` | Plan状態識別 / String |
| `SourceWritebackRunIds` | `SourceWritebackRunIds` | 出典 / String |
| `ProductKey` | `ProductKey` | Productへの外部キー / String |
| `PeriodKey` | `PeriodKey` | Periodへの外部キー / String |
| `PlanPeriodStatus` | `PlanPeriodStatus` | 期間状態 / String |
| `CurrencyCode` | `CurrencyCode` | 通貨 / String |
| `ModelMeasureName` | `ModelMeasureName` | モデルの指標名 / String |
| `ModelGrossRevenue` | `ModelGrossRevenue` | モデル売上 / Double |
| `PlanMeasureName` | `PlanMeasureName` | Plan指標名 / String |
| `PlanForecast` | `PlanForecast` | 予測値 / Double |
| `VarianceAmount` | `VarianceAmount` | Forecast - Gross Revenue / Double |
| `VarianceRate` | `VarianceRate` | 0分母はNULL / Double |

実証時は15プロパティのうち4つの金額 / 比率列がDouble、他11列がStringでした。WarehouseのDecimal金額はWarehouse側の正確な検算用に保持します。OntologyのBindingやEntity keyを保存した後、Product 6、Period 3、Observation 18のテーブル件数とキーをWarehouse / LakehouseのSQL結果でも照合してください。Instancesタブの一覧だけを件数の唯一の根拠にしません。


   ![Lab09のエンティティ追加画面（キャプチャ 261）](../assets/screenshots/lab09/261-lh-add-entity-type-revenue-observation.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 262）](../assets/screenshots/lab09/262-lh-revenue-observation-entity-created.png)
   ![Lab09のプロパティバインドの設定画面（キャプチャ 264）](../assets/screenshots/lab09/264-lh-revenue-observation-bind-data-empty.png)
   ![Lab09の操作画面（キャプチャ 265）](../assets/screenshots/lab09/265-lh-revenue-observation-onelake-lakehouse-expanded-dbo.png)
   ![Lab09のプロパティバインドの設定画面（キャプチャ 267）](../assets/screenshots/lab09/267-lh-revenue-observation-onelake-select-lab09-revenue-observation.png)
   ![Lab09のプロパティバインドの設定画面（キャプチャ 269）](../assets/screenshots/lab09/269-lh-revenue-observation-bind-data-properties-mapping.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 270）](../assets/screenshots/lab09/270-lh-revenue-observation-bind-data-created-save.png)
   ![Lab09の操作画面（キャプチャ 271）](../assets/screenshots/lab09/271-lh-revenue-observation-configure-bound.png)
   ![Lab09のエンティティキーの設定画面（キャプチャ 274）](../assets/screenshots/lab09/274-lh-revenue-observation-key-observationkey-checked.png)
   ![Lab09のエンティティキーの設定画面（キャプチャ 276）](../assets/screenshots/lab09/276-lh-revenue-observation-key-defined.png)

### 8.4 Relationshipを作る

次の2つのrelationship typeを作成します。最初の接続方法でGraphが`No Datasource`になる挙動も実機で観測したため、直接接続とmapping table方式を別々に説明します。

| Relationship type | Origin entity / property | Target entity / property |
|---|---|---|
| `Product has Revenue Observations` | `Product.ProductKey` | `Revenue Observation.ProductKey` |
| `Period contains Revenue Observations` | `Period.PeriodKey` | `Revenue Observation.PeriodKey` |

1. **Add relationship**で名前、Origin、Targetを選んでAddします。Home canvas上のedge labelを開き、Relationship detailsで`Use mapping table`をOffにしてOrigin propertyからTargetの同名FK propertyへ直接接続、Saveします。

   **Product relationshipを作成します。**
   ![Lab09のリレーションの設定画面（キャプチャ 278）](../assets/screenshots/lab09/278-lh-add-relationship-dialog-empty.png)
   ![Lab09のリレーションの設定画面（キャプチャ 279）](../assets/screenshots/lab09/279-lh-add-relationship-name-origin-list.png)
   ![Lab09のリレーションの設定画面（キャプチャ 281）](../assets/screenshots/lab09/281-lh-add-relationship-filled-product-to-revenue-observation.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 282）](../assets/screenshots/lab09/282-lh-relationship-created-home-edge-label.png)
   ![Lab09のリレーションの設定画面（キャプチャ 283）](../assets/screenshots/lab09/283-lh-relationship-details-page-empty.png)
   ![Lab09のリレーションの設定画面（キャプチャ 285）](../assets/screenshots/lab09/285-lh-relationship-origin-productkey-selected.png)
   ![Lab09の操作画面（キャプチャ 287）](../assets/screenshots/lab09/287-lh-relationship-connection-filled-save-enabled.png)
   **Period relationshipを作成します。**
   ![Lab09のリレーションの設定画面（キャプチャ 289）](../assets/screenshots/lab09/289-lh-add-relationship-filled-period-to-revenue-observation.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 290）](../assets/screenshots/lab09/290-lh-relationship2-created-home-edge-label.png)
   ![Lab09のリレーションの設定画面（キャプチャ 291）](../assets/screenshots/lab09/291-lh-relationship2-details-page-empty.png)
   ![Lab09のリレーションの設定画面（キャプチャ 293）](../assets/screenshots/lab09/293-lh-relationship2-origin-periodkey-selected.png)
   ![Lab09の操作画面（キャプチャ 295）](../assets/screenshots/lab09/295-lh-relationship2-connection-filled-save-enabled.png)

2. 実証時、この直接接続のままManage graphを開くとrelationshipは`Ineligible / No Datasource`でした。関係自体の作成は済んでいても、Graph用のrelationship datasourceがない状態です。

   **直接接続のGraph状態を確認します。**
   ![Lab09の失敗または制限メッセージ（キャプチャ 300）](../assets/screenshots/lab09/300-lh-manage-graph-relationship-ineligible-no-datasource.png)
   ![Lab09のリレーションの設定画面（キャプチャ 301）](../assets/screenshots/lab09/301-lh-manage-graph-relationship-ineligible-details-missing-data-source.png)

3. Relationship detailsで`Use mapping table = On`に変更し、mapping tableとして同じLakehouseの`dbo.lab09_revenue_observation`を選びます。Product relationshipはmapping tableの`ProductKey`をOrigin keyに、Revenue Observationの`ObservationKey`をTarget entity keyとしてそれぞれマッピングします。Period relationshipはmapping tableの`PeriodKey`をOrigin keyに、同じ`ObservationKey`をTarget keyとしてマッピングします。各relationshipでSaveし、成功バナーを確認します。

   **Productのmapping tableを選択します。**
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 302）](../assets/screenshots/lab09/302-lh-relationship1-use-mapping-table-on-empty.png)
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 303）](../assets/screenshots/lab09/303-lh-relationship1-mapping-table-menu-browse-available-sources.png)
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 304）](../assets/screenshots/lab09/304-lh-relationship1-mapping-table-onelake-dialog-filtered.png)
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 307）](../assets/screenshots/lab09/307-lh-relationship1-mapping-table-onelake-select-lab09-revenue-observation.png)
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 308）](../assets/screenshots/lab09/308-lh-relationship1-mapping-table-selected-properties-empty.png)
   **ProductKeyとObservationKeyを対応付けて保存します。**
   ![Lab09のエンティティキーの設定画面（キャプチャ 310）](../assets/screenshots/lab09/310-lh-relationship1-mapping-table-origin-productkey-checked-match-with-column.png)
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 312）](../assets/screenshots/lab09/312-lh-relationship1-mapping-table-match-with-productkey-selected.png)
   ![Lab09のエンティティキーの設定画面（キャプチャ 314）](../assets/screenshots/lab09/314-lh-relationship1-mapping-table-target-observationkey-checked-second-match-with.png)
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 317）](../assets/screenshots/lab09/317-lh-relationship1-mapping-table-both-matches-selected-save-enabled.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 318）](../assets/screenshots/lab09/318-lh-relationship1-mapping-table-saved-success-banner.png)
   **Period relationshipでPeriodKeyとObservationKeyを対応付けて保存します。**
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 320）](../assets/screenshots/lab09/320-lh-relationship2-use-mapping-table-on-empty.png)
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 322）](../assets/screenshots/lab09/322-lh-relationship2-mapping-table-selected-properties-empty.png)
   ![Lab09のエンティティキーの設定画面（キャプチャ 324）](../assets/screenshots/lab09/324-lh-relationship2-mapping-table-origin-periodkey-checked-match-with-column.png)
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 326）](../assets/screenshots/lab09/326-lh-relationship2-mapping-table-match-with-periodkey-selected.png)
   ![Lab09のエンティティキーの設定画面（キャプチャ 328）](../assets/screenshots/lab09/328-lh-relationship2-mapping-table-target-observationkey-checked-second-match-with.png)
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 331）](../assets/screenshots/lab09/331-lh-relationship2-mapping-table-both-matches-selected-save-enabled.png)
   ![Lab09の作成またはロード完了画面（キャプチャ 332）](../assets/screenshots/lab09/332-lh-relationship2-mapping-table-saved-success-banner.png)

4. Manage graphで全entityと両relationshipがEligibleになることを待って確認します。Direct property接続でグラフのEdge datasourceを作れないケースを、Product / Period FKとObservationKeyのmappingで解消したのが実証の手順です。

   **両方のrelationshipがEligibleであることを確認します。**
   ![Lab09のマッピングテーブルの設定画面（キャプチャ 333）](../assets/screenshots/lab09/333-lh-manage-graph-all-eligible-after-mapping-table.png)
   ![Lab09の操作画面（キャプチャ 334）](../assets/screenshots/lab09/334-lh-manage-graph-period-expanded-both-relationships-eligible.png)

### 8.5 Business ruleを追加する

1. Explorerの **Overview → Rules → Create rule** を選び、名前`Revenue variance interpretation`を入力します。


2. Definitionに、差異額の式、USD、Product × 月の粒度、Snapshot / Scenario / PlanVersion、0分母のNULL、Open期間の扱い、履歴の非合算を自然文で記します。Linked ontology elementsでProduct / Period / Revenue Observationのentity type、およびModelGrossRevenue / PlanForecast / VarianceAmount / VarianceRateを関連付けます。


3. このBusiness ruleは自然言語による利用者向けガイダンスであり、データへの式適用やクエリ実行をしません。Warehouse / Lakehouseの計算値と別に自動実行されるものではありません。

> [!NOTE]
> Rule作成画面の画像は最初のWarehouse-bound Ontologyで撮影しました。UI操作の例として掲載しています。最終の`_LH` Ontologyでは同じルールを作る手順として示しますが、画像自体は最終Ontologyにルールが保存された証拠ではありません。


**Business ruleの一覧から作成を始めます。**
![Lab09の未設定の画面（キャプチャ 144）](../assets/screenshots/lab09/144-rules-empty-page.png)
![Lab09のBusiness ruleの作成画面（キャプチャ 145）](../assets/screenshots/lab09/145-rule-new-page-empty.png)
**名前と定義を入力します。**
![Lab09のBusiness ruleの作成画面（キャプチャ 146）](../assets/screenshots/lab09/146-rule-name-definition-filled.png)
![Lab09のBusiness ruleの作成画面（キャプチャ 147）](../assets/screenshots/lab09/147-rule-add-elements-dialog-entities.png)
![Lab09のBusiness ruleの作成画面（キャプチャ 148）](../assets/screenshots/lab09/148-rule-add-elements-three-selected.png)
**対象entityとpropertyを指定します。**
![Lab09のBusiness ruleの作成画面（キャプチャ 149）](../assets/screenshots/lab09/149-rule-add-elements-properties-tab.png)
![Lab09のBusiness ruleの作成画面（キャプチャ 150）](../assets/screenshots/lab09/150-rule-add-elements-six-selected.png)
![Lab09のBusiness ruleの作成画面（キャプチャ 151）](../assets/screenshots/lab09/151-rule-add-elements-seven-selected.png)
**保存結果を確認します。**
![Lab09のBusiness ruleの作成画面（キャプチャ 152）](../assets/screenshots/lab09/152-rule-linked-elements-added.png)
![Lab09のBusiness ruleの作成画面（キャプチャ 153）](../assets/screenshots/lab09/153-rule-form-complete-before-create.png)
![Lab09の作成またはロード完了画面（キャプチャ 154）](../assets/screenshots/lab09/154-rule-created-in-rules-list.png)

### 8.6 Graphへ投影する

1. 3 entity typeと2 relationship typeの全てがEligibleであることを確認し、**Manage graph → Continue**を選びます。

   **Projectionの対象として選択可能か確認します。**
   ![Lab09のGraphの投影 / materialize画面（キャプチャ 335）](../assets/screenshots/lab09/335-lh-choose-what-to-project-product-checked.png)

2. Choose what to project画面で3 entity typeを選びます。relationshipのチェックボックスは両端のentityを選択しただけでは自動で有効にならないため、2つのrelationshipも明示的に選びます。

   **3種類のentity typeと2種類のrelationship typeを選択します。**
   ![Lab09のGraphの投影 / materialize画面（キャプチャ 336）](../assets/screenshots/lab09/336-lh-choose-what-to-project-period-checked.png)
   ![Lab09のGraphの投影 / materialize画面（キャプチャ 337）](../assets/screenshots/lab09/337-lh-choose-what-to-project-all-three-entities-checked.png)
   ![Lab09のGraphの投影 / materialize画面（キャプチャ 339）](../assets/screenshots/lab09/339-lh-choose-what-to-project-all-entities-and-relationships-checked.png)
   ![Lab09のGraphの投影 / materialize画面（キャプチャ 340）](../assets/screenshots/lab09/340-lh-projection-summary-three-entities-two-relationships.png)

3. Projection summaryを確認して**Materialize**します。ボタンがDoneになっても画面遷移しないことがあります。その場合はDoneを再実行せずHomeへ戻り、Graph statusを確認します。

   **Projection summaryからMaterializeします。**
   ![Lab09のGraphの投影 / materialize画面（キャプチャ 341）](../assets/screenshots/lab09/341-lh-projection-summary-materialize-creating-graph-model-toast.png)
   ![Lab09のGraphの投影 / materialize画面（キャプチャ 342）](../assets/screenshots/lab09/342-lh-projection-summary-done-button-disabled.png)
   ![Lab09のGraphの投影 / materialize画面（キャプチャ 343）](../assets/screenshots/lab09/343-lh-manage-graph-status-all-materialized-nodes3-edges2.png)
   ![Lab09のGraphの投影 / materialize画面（キャプチャ 344）](../assets/screenshots/lab09/344-lh-home-after-materialization-explore-graph-in-ribbon.png)

4. Graph statusに`nodes 3 / edges 2`と表示されたら、entity type 3種類 / relationship type 2種類がmaterializeされたことを確認します。この値を18 observation instanceやedge traversalの検証として説明しません。

<!-- presentation-exclude-start: LAB09-EDGE-TRAVERSAL -->
Edge traversalは未検証です。
<!-- presentation-exclude-end: LAB09-EDGE-TRAVERSAL -->
5. Homeの**Explore graph**からGraph queryを開けます。実証時、最初のGraph queryはRun後に数分かかったため、すぐに失敗と判断せず状態を確認します。



## 9. Part 5：Data Agentを作成して質問する

### 9.1 完成済みOntologyを追加する

実証では、先にOntologyを追加した`_LH` Agentのentity listはProductのままで、Refresh後も更新されませんでした。以下はその古い一覧の画面です。完成済みOntologyをAgentへ追加し直す前にこの状態を確認し、完成後に新しいAgentを作成します。


**先行Agentに残ったProduct-onlyのentity type一覧です。**
![Lab09の操作画面（キャプチャ 345）](../assets/screenshots/lab09/345-lh-agent-reopened-explorer-product-only-after-stage-c.png)
![Lab09の操作画面（キャプチャ 346）](../assets/screenshots/lab09/346-lh-agent-after-refresh-three-lakehouse-tables-entity-types-product-only.png)

1. Ontologyを完成し、entity / relationshipのバインディングとGraph materializationを確認してから、**+ New item → Data agent**を作ります。実証名は`HPC_Lab09_Plan_Variance_Analyst_LH2`です。

   ![Lab09の作成またはロード完了画面（キャプチャ 349）](../assets/screenshots/lab09/349-lh2-data-agent-created-empty-build-your-agent.png)

2. **Add an ontology**で`HPC_Lab09_VarianceOntology_LH`を選び、Data sourceとしてOntologyを追加します。別のWarehouseやセマンティックモデルを直接Sourceに足してOntologyを迂回しません。

   ![Lab09の操作画面（キャプチャ 350）](../assets/screenshots/lab09/350-lh2-add-ontology-dialog-filtered.png)
   ![Lab09の操作画面（キャプチャ 352）](../assets/screenshots/lab09/352-lh2-adding-ontology-toast.png)

3. ExplorerにProduct、Period、Revenue Observationの3 entity typeが表示されることを確認します。Ontologyを完成する前に追加された`_LH` AgentはProductだけのentity listのまま残りました。Refresh後もentity listが更新されない状態を観測したため、完成後に新しいAgent `_LH2`を作りました。`_LH` / `_LH2`はこの手順の作成順を示す名前で、別の製品版ではありません。


   ![Lab09の操作画面（キャプチャ 353）](../assets/screenshots/lab09/353-lh2-ontology-added-three-entity-types.png)
   ![Lab09の操作画面（キャプチャ 354）](../assets/screenshots/lab09/354-lh2-ontology-data-sources-expanded-lakehouse-tables.png)

### 9.2 Instructionsを設定する

実証時に`_LH2`へ入力したInstructionsは17行 / 856文字です。下記と一字一句同じ内容にします。編集後はテキスト外をクリックしてプレビューに戻します。



<!-- presentation-exclude-start: LAB09-INSTRUCTIONS-PERSISTENCE -->
今回の`_LH2`では再読込後の永続確認は未実施です。
<!-- presentation-exclude-end: LAB09-INSTRUCTIONS-PERSISTENCE -->



```text
このAgentはHPC_Lab09_VarianceOntology_LHだけを使う読み取り専用の分析Agentです。
通常はSnapshotId, ScenarioName, PlanVersion, 一つのPeriodKey, CurrencyCodeを
特定して回答してください。複数月を明示して尋ねられた場合だけ、
指定されたPeriodKeyのリストを漏れなく確認し、PeriodKeyとPlanPeriodStatusごとに
行数と金額合計を分けて示してください。未知の期間、指定外の期間、別Snapshot /
Scenario / PlanVersionを混ぜず、範囲が曖昧なら回答前に質問してください。
VarianceAmountはPlanForecast - ModelGrossRevenueです。
複数行のVarianceRateを合算または単純平均しないでください。
複数行の合計比率を求められた場合は
(SUM(PlanForecast) - SUM(ModelGrossRevenue)) / NULLIF(SUM(ModelGrossRevenue), 0)
とし、回答には絞り込みに使ったSnapshotId, ScenarioName, PlanVersion, PeriodKeyを示し、利用者がWarehouseの同じキー範囲のSQL結果と照合できるようにしてください。
ModelGrossRevenueが0の場合はVarianceRateを算出しないでください。
OpenSampleReferenceはサンプルの比較値で, 確定実績とは呼びません。
Closed period, Open periodを明示し, 結果に使ったSnapshotIdと条件を記します。
データ不足,重複,複数の候補,未バインドの関係がある場合は推測せず回答を保留します。
原因分析,将来予測,勧告やPlan変更を行ったとは主張しません。
Support group by in GQL
```

**Instructionsの入力例です。**
![Lab09の実行するSQL入力画面（キャプチャ 357）](../assets/screenshots/lab09/357-lh2-agent-instructions-typed-17-lines.png)
![Lab09のAgent Instructionsの入力 / 確定画面（キャプチャ 358）](../assets/screenshots/lab09/358-lh2-agent-instructions-committed-preview.png)
**Instructionsの保存結果です。**
![Lab09のAgent Instructionsの入力 / 確定画面（キャプチャ 359）](../assets/screenshots/lab09/359-lh2-test-pane-reopened-instructions-committed-three-pane.png)


`Support group by in GQL`は実証時のInstructionsに含まれていた文字列です。OntologyのBusiness ruleはルールを実行しません。Data Agentに追加した指示も正しい結果を保証しません。Agentが参照したSource、条件、返却値をWarehouseで検算します。


### 9.3 質問して結果を検算する

各質問にSnapshotId、ScenarioName、PlanVersion、PeriodKey、CurrencyCodeを明記します。「同じ条件」は同一チャットスレッドの文脈に依存するので、新しい質問では条件を繰り返します。下表の数値は合成サンプルのみの結果です。

Q1は次の単月条件で実機確認しました。下記は再試行時に条件名を明示する文面で、実機入力の逐語転記ではありません。Q3の実機質問はQ1と同じチャットスレッドで条件を引き継ぎました。

```text
Snapshot LAB09-SAMPLE-001, Scenario Base, PlanVersion FY26-Workshop-v1, PeriodKey 2026-03, Currency USDについて、
ModelGrossRevenue合計, PlanForecast合計, VarianceAmount合計を比較してください。
PeriodStatusと、この値が実績かサンプルの比較値かも示してください。
```

**Q1を同じData Agentへ入力します。**
![Lab09のData Agentの質問 / 回答画面（キャプチャ 361）](../assets/screenshots/lab09/361-lh2-chat-question1-sent-analyzing-lakehouse.png)
**Q1の回答と合計を確認します。**
![Lab09の検算結果の画面（キャプチャ 362）](../assets/screenshots/lab09/362-lh2-chat-question1-answer-2026-03-totals-bottom.png)
![Lab09のData Agentの質問 / 回答画面（キャプチャ 367）](../assets/screenshots/lab09/367-lh2-chat-question1-execution-and-output-table-open-sample-reference.png)
**Sourceと生成されたSQLを確認します。**
![Lab09のData Agentの質問 / 回答画面（キャプチャ 368）](../assets/screenshots/lab09/368-lh2-chat-question1-show-input-generated-sql-top.png)
![Lab09のData Agentの質問 / 回答画面（キャプチャ 369）](../assets/screenshots/lab09/369-lh2-chat-question1-show-input-generated-sql-bottom-group-by.png)


<!-- presentation-exclude-start: LAB09-Q3-STANDALONE-PROMPT -->
単独で再試行するときは下記のようにQ3にも条件をすべて明記してください。この完全なQ3文面自体は個別の新規実行で検証していません。

```text
Snapshot LAB09-SAMPLE-001, Scenario Base, PlanVersion FY26-Workshop-v1, PeriodKey 2026-03, Currency USDで、
Product SNK-NUTSのModelGrossRevenue, PlanForecast, VarianceAmount, VarianceRateを示し、
PlanForecast - ModelGrossRevenueを検算してください。
```


<!-- presentation-exclude-end: LAB09-Q3-STANDALONE-PROMPT -->

**Q1の条件を引き継いだ同一チャットで確認したQ3の入力例です。**
![Lab09の実行するSQL入力画面（キャプチャ 370）](../assets/screenshots/lab09/370-lh2-chat-question3-typed-snk-nuts-row-check.png)
![Lab09の検算結果の画面（キャプチャ 372）](../assets/screenshots/lab09/372-lh2-chat-question3-answer-snk-nuts-variancerate-null-bottom.png)


Q4 / Q4aは複数期間に対してStatus別集計や行数を含めた質問で失敗しました。次のような条件を含む質問では成功を期待せず、失敗時は`SQLCandidatesFailedFilterError`として記録します。

<!-- presentation-exclude-start: LAB09-ERROR-CAUSE-QUESTIONS -->
原因は特定されていません。
<!-- presentation-exclude-end: LAB09-ERROR-CAUSE-QUESTIONS -->

```text
Snapshot LAB09-SAMPLE-001, Scenario Base, PlanVersion FY26-Workshop-v1, Currency USDで、
PeriodKey 2026-01, 2026-02, 2026-03をPlanPeriodStatus別に比較し、行数と合計比率を示してください。
```

**Q4の質問を入力します。**
![Lab09の実行するSQL入力画面（キャプチャ 374）](../assets/screenshots/lab09/374-lh2-chat-question4-typed-three-periods-closed-open-total-ratio.png)

**Q4 / Q4aの失敗結果を確認します。**
![Lab09の失敗または制限メッセージ（キャプチャ 377）](../assets/screenshots/lab09/377-lh2-chat-question4-answer-top-sqlcandidatesfailedfiltererror.png)
![Lab09の失敗または制限メッセージ（キャプチャ 380）](../assets/screenshots/lab09/380-lh2-chat-question4-step1-output-unable-to-generate-code-sqlcandidatesfailedfiltererror.png)
![Lab09の失敗状態の画面（キャプチャ 381）](../assets/screenshots/lab09/381-lh2-chat-question4-step2-retry-in-clause-nl-query-output-same-error.png)


```text
Snapshot LAB09-SAMPLE-001, Scenario Base, PlanVersion FY26-Workshop-v1, Currency USDで、
PeriodKey 2026-01, 2026-02, 2026-03について、PeriodKeyとPlanPeriodStatusごとに
行数, ModelGrossRevenue合計, PlanForecast合計, VarianceAmount合計を示してください。
```

Q4cはPeriodKey別の3つの合計だけを尋ねて成功しました。



```text
Snapshot LAB09-SAMPLE-001, Scenario Base, PlanVersion FY26-Workshop-v1, Currency USDで、
2026-01, 2026-02, 2026-03について、PeriodKeyごとのModelGrossRevenue合計,
PlanForecast合計, VarianceAmount合計を示してください。
```

**Q4cの回答結果です。**
![Lab09の検算結果の画面（キャプチャ 388）](../assets/screenshots/lab09/388-lh2-chat-question4c-answer-bottom-1-step-completed-response-time-19-sec.png)


| 質問 | 期待値 / 実機結果 | 状態 |
|---|---|---|
| **Q1 / 2026-03合計** | Snapshot `LAB09-SAMPLE-001`、Scenario `Base`、PlanVersion `FY26-Workshop-v1`、Period `2026-03`、USDでModelGrossRevenue **1,366,441.40**、PlanForecast **1,397,256.575**、VarianceAmount **30,815.175**。期間は`OpenSampleReference`で、確定実績ではない | 実機回答とWarehouse検算が一致 |
| **Q3 / SNK-NUTSの2026-03** | ModelGrossRevenue **0**、PlanForecast **12,500**、VarianceAmount **12,500**、VarianceRate **NULL / 算出不可** | 実機回答とWarehouse検算が一致 |
| **Q4c / 2026-01〜03をPeriodKey別に集計** | 下表のModel / Forecast / VarianceをPeriodKeyごとに返す。Q4cではPeriodStatus、行数、率を求めず、期間別合計だけを質問 | 実機回答とWarehouse検算が3期間すべて一致 |
| **Q4 / 複数月をStatus別に行数・合計・率まで質問** | `SQLCandidatesFailedFilterError` | 失敗 |
| **Q4a / 期間別・Status別の行数と合計を質問** | `SQLCandidatesFailedFilterError` | 失敗 |

<!-- presentation-exclude-start: LAB09-ERROR-CAUSE-RESULTS -->
Q4 / Q4a: 失敗。原因未特定。
<!-- presentation-exclude-end: LAB09-ERROR-CAUSE-RESULTS -->

| PeriodKey | PlanPeriodStatus | Gross Revenue合計 | Forecast合計 | VarianceAmount合計 | 合計比率（Warehouse照合値） |
|---|---|---:|---:|---:|---:|
| 2026-01 | ClosedLinkedActual | 1,479,697.80 | 1,479,697.80 | 0 | 0 |
| 2026-02 | OpenSampleReference | 1,436,983.25 | 1,480,991.85833 | 44,008.60833 | 約0.030625 |
| 2026-03 | OpenSampleReference | 1,366,441.40 | 1,397,256.575 | 30,815.175 | 約0.022551 |

Warehouseの表示はDecimal比率の小数末尾が丸められ、手計算の最終桁と1桁異なる場合があります。金額 / 比率を照合する際はWarehouseの実値と表示丸めを区別してください。Gross Revenueが0のSNK-NUTS行では率を計算しません。

Q4 / Q4aの失敗を成功例として記載しません。3期間をまとめる場合、実証済みなのはPeriodKey別の3つの合計だけを尋ねるQ4cです。

<!-- presentation-exclude-start: LAB09-QUESTION-VARIATIONS -->
複数条件を詰め込まずに1期間ずつの単純な合計へ分割する方法を推奨します。ただしその分割方法自体の全パターンは未確認です。全期間の合計比率だけを問う質問や、Q4cの生成SQL表示は未実施です。
<!-- presentation-exclude-end: LAB09-QUESTION-VARIATIONS -->

Agentの回答を公開 / 共有する前に、Warehouseで同じSnapshot / Scenario / PlanVersion / PeriodKey / ProductKeyの読み取り専用SQLを実行し、元行、合計、VarianceAmount、0分母のNULLを独立に照合します。AgentにWarehouseの直接アクセスがあるとは扱わず、回答とSource表示だけを正解の根拠にしません。Data Agentの質問結果は読み取り専用の回答で、Planの更新 / 承認 / 書き戻しではありません。


## 10. よくある問題と対応

| 表示 / 症状 | 対応 |
|---|---|
| `COPY INTO`がWorkspace Identity付きでMsg 13840 | 実証ではWorkspace Identity資格情報の取得に失敗しました。EntraパススルーのCREDENTIALなし経路を使用。Identity設定を勝手に変更しません |
| Spark SQLの`PARSE_SYNTAX_ERROR` | 1回のRunに複数文が入っています。新しいQueryで一文ずつ実行します |
| Warehouse-bound ontologyで`Unsupported Datasource` | WarehouseはSQL検算用に保ち、OntologyのGraph用sourceにはLakehouse管理Deltaテーブルを使います |
| Agentの`There's content here I can't work with` | SourceのGraph eligibility / materialization、Ontologyのbinding、Data AgentのSourceを確認。Warehouse-bound失敗は観測済みですが、一般原因を断定しません |
| Instancesタブに`doesn't have a table named` | Spark側のdboテーブル存在とBindingを別々に確認し、しばらく待ってから再読込します。Instancesタブのエラーを成功 / 失敗の唯一の判定にしません |
| Direct relationshipで`No Datasource` | Relationship detailsでUse mapping tableをOnにし、LakehouseのRevenue ObservationテーブルとOrigin / ObservationKeyのmappingを確認します |
| Relationshipの選択が無効 | Graph projectionで両端entityを先に選択し、relationship typeも個別にチェックします |
| Materialize後のDoneが無効のまま | Doneを再実行せずHomeに戻り、Graph statusを再確認します |
| Graph queryの最初のRunが長い | 数分かかる場合があるため、即時に再実行せず状態を待って確認します |
| Agentにentity typeが一つしか出ない | Ontologyを完成 / materializeしてからAgentへ追加します。`_LH`のRefreshではentity type一覧が更新されませんでした。完成後に作成した`_LH2`で3種類を確認しました |
| `SQLCandidatesFailedFilterError` | Q4 / Q4aで再現しました。Q4cのように期間ごとの合計だけに分けて試し、毎回Warehouseで検算します。成功を保証しません |

<!-- presentation-exclude-start: LAB09-ERROR-CAUSE-TROUBLESHOOTING -->
- Warehouse-bound ontologyで`Unsupported Datasource`: 単独原因は特定されていません。
- Instancesタブに`doesn't have a table named`: 原因は未特定です。
- `SQLCandidatesFailedFilterError`: Q4 / Q4aで再現したが原因未特定です。
<!-- presentation-exclude-end: LAB09-ERROR-CAUSE-TROUBLESHOOTING -->

## 11. 安全な終了

CSV、Lakehouse、Warehouse、Ontology、Data Agentは演習専用の新規資産です。使用を終えたら、管理者と所有者が個々の対象名、利用者、保持 / 監査、課金の影響を確認します。削除、権限変更、Workspace Identityの変更は個別の明示承認なしに行いません。既存Workspace全体の削除や共有中のForecast / 元モデルの更新をcleanupに使いません。Data AgentのPublish / Shareはこの手順の実証には含まれず、公開しないでください。

## 12. 公式資料

- [Fabric Data Agentの概要 / 前提条件 / 読み取り専用動作](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent)
- [Fabric Data Agentの作成とOntologyの追加](https://learn.microsoft.com/en-us/fabric/data-science/how-to-create-data-agent)
- [Ontology Previewの概要](https://learn.microsoft.com/en-us/fabric/iq/ontology/overview)
- [Ontology Entity Typeの作成](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-create-entity-types)
- [Ontologyへのデータバインディング](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-bind-data)
- [Ontology Relationship typeの作成](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-create-relationship-types)
- [Ontology Business rule](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-use-rules)
- [WarehouseでOneLakeから取込む（COPY INTO）](https://learn.microsoft.com/en-us/fabric/data-warehouse/ingest-data)
- [WarehouseのSQL Query Editor](https://learn.microsoft.com/en-us/fabric/data-warehouse/sql-query-editor)
- [Warehouseでサポートされるデータ型](https://learn.microsoft.com/en-us/fabric/data-warehouse/data-types)
- [ローカルCSVをLakehouseへアップロード](https://learn.microsoft.com/en-us/fabric/data-engineering/get-started-csv-upload)
- [Fabric Graphの制限事項](https://learn.microsoft.com/en-us/fabric/graph/limitations)

---

**← 前へ：** [Lab08：容量とガバナンス](08-sizing-and-governance.md) · [README](../README.md)
