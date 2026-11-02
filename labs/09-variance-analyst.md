# モジュール09：Plan Variance Analyst（計画差異アナリスト）

**所要時間の目安：** 45〜60分（Lab09用データの準備時間を除く）<br>
**このモジュールで作成するもの：** Lab04の売上実績 / 見通しを照合した比較スナップショット, 一時Lakehouse FilesからWarehouseへ取り込む専用データ領域, Product / Period / Revenue Observationを結ぶOntology（Preview）, そのOntologyだけを参照する読み取り専用Fabric Data Agent。

> [!IMPORTANT]
> **ライブ実行とLab09画面キャプチャは未完了です。** この手順はMicrosoft公式資料に基づく実装ガイドで, 実際のFabricテナントで一連のLakehouse upload / Warehouse取込 / Ontology binding / Data Agent回答まで通した検証ではありません。Lab09固有のFabric画面キャプチャは未収録です。画面, テナント設定, Previewの提供状況は実施時に確認し, 手順どおりの実行ができない場合は成功扱いにせず講師 / 管理者へ相談してください。

---

## 目的と対象範囲

Harborlightの担当者として, **Product Category / Sub Category × 月**の粒度で *Gross Revenue* と *Forecast* を同じ期間で比較し, 差異を数値で説明します。Fabric Data Agentに質問する前に, 元データの意味, 粒度, 期間状態, PlanのScenario / version, 書き戻し履歴を人が確定します。AIの回答を正解データの代用にせず, Warehouseの照合結果と突き合わせます。

このラボは[Lab04](04-forecast-and-writeback.md)で作成した実績 / 見通しを使います。Northwindサンプルの *Gross Revenue* はLab04で使ったセマンティックモデルのDAXメジャーです。FY26のサンプル値は演習用フィクスチャであり, 現実世界のFY26実績や将来予測ではありません。範囲を確認できない場合は, 期間を実績として扱わず停止します。

**このラボではRegion別 / Gross Profit分析を作りません。** Lab04の *Forecast* は *Gross Revenue* を使い, 行は *Product Category / Sub Category*, 列は *Year / Quarter / Month Short* です。地域別や売上総利益のPlanデータが既にあるとは仮定しません。分析粒度を変更する場合は, 元モデルと書き戻しの両方に同じ検証済みキーがあることを別途確認してください。

## 完了条件

| 確認対象 | 受入条件 |
|---|---|
| 比較範囲 | Lab04のGross Revenue / ForecastをProduct Category / Sub Category × 月, 同一Scenario / Plan version / USDで照合する。Region別 / Gross Profit別のPlan値を想定しない |
| 比較Snapshot | 1行は1つの`SnapshotId × Scenario × Plan version × ProductKey × PeriodKey`。欠損 / 重複キーがなく, 元数値の精度を保つ。Closed / Openを区別し, Open periodのサンプルモデル値は確定実績と呼ばない |
| CSV取込 | 両方の全エクスポートの一意キー集合をFull Outerで照合し, 正のExpectedRowsを非公開記録。UTF-8 CSVをLakehouse Filesへ承認済み経路でアップロードし, 明示型StageへOneLake COPY後の全件数を照合する |
| 履歴と保存 | 選択したPlan状態を全件照合し, Long with Changes履歴を加算したり, `TOP 1` / 最大timestampで現行値と推測したりしない。Warehouseの一意キー / 件数 / 差異算式を独立検証する |
| Ontology | Product / Period / Revenue Observationのキーと関係を定義し, 全EntityのProperty bindingsが専用Warehouseを指す。必要ならOntologyを手動Refreshし, Previewに表示されるデータ版を確認する |
| Data Agent | 比較用OntologyのみをSourceに使う読み取り専用Agent。質問にSnapshotId / Scenario / Plan versionを含め, 回答の値 / 期間状態をWarehouseの全精度値と照合する。日本語の質問も実際に試し, 適用可能な言語品質を確認する |
| 権限とプライバシー | 対象ユーザー本人のWarehouse / Ontologyアクセスで確認する。公開リポジトリ / スクリーンショット / プロンプトにTenant ID, token, credentials, 参加者データを残さない |

## 前提条件と承認

### Fabric / AIの前提条件

- Data Agentの公式要件は**有料F2以上またはFabric有効化済みP1以上**です。Lab00のPlanning試用条件だけでData Agentが使えるとは限りません。容量の利用可否と請求範囲を管理者に確認します。
- Tenant管理者が, 組織のポリシーに従ってCopilot / Azure OpenAIの利用, 必要なクロスジオ処理 / 保存設定を確認します。設定変更は管理者の承認が必要です。地域 / コンプライアンス境界によっては有効化できない場合があります。
- Ontologyは**Preview**です。テナントの「Users can create ontology items」「Users can create Fabric items」設定, 対象地域での提供状況, Previewの利用可否を事前に確認します。
- データAgent作成者にはAgent / Ontology / Warehouseの作成・編集権限が必要です。OntologyへのSemantic modelバインドを追加する場合は対象モデルのRead **とBuild**が必要ですが, 本ラボは比較済みWarehouseをOntologyにバインドする方式です。Data AgentのWarehouseデータに対する読取権限も確認します。
- Data Agentはユーザー本人の権限を使い, ソースへの問い合わせを**読み取り専用**で実行します。Planの変更, 承認, 書き戻しはできません。Agentで読める範囲と, Ontologyのバインドを作る権限を混同しません。

### データと費用の前提条件

- Lab04の*Forecast* SQL書き戻し, 元モデルの*Gross Revenue*へのアクセス, CSVを安全に扱う承認済み端末 / 場所が必要です。実データは持ち込まず, MicrosoftのNorthwindサンプルだけを使います。
- 比較用WarehouseとCSVを一時保管する専用Lakehouseは新しい演習アイテムとして作成します。Capacity / Warehouse / OneLake / Data Agentの消費を確認してから作成します。共有中のForecastや元モデルを置き換えません。
- 手順は画面に出ている値を確認して進めます。想定した列 / キーが見つからない, Scenario / versionが判別できない, 同じキーに複数の現在値がある, 全ページを確認できない場合は停止し, 推測で補完しません。

> [!WARNING]
> Data Agentは質問,回答,データをAzure OpenAIへ処理目的で送る機能です。Tenant設定によるクロスジオ処理 / 保存,会話履歴,監査,組織ポリシーを管理者と確認してください。トークン,資格情報,テナント固有情報,参加者データをプロンプト,公開ログ,画面共有,この教材のCSVへ記録しません。

## アーキテクチャとデータ契約

詳細図は[Lab09の構成図](../assets/diagrams/lab09-variance-analyst.md)を参照してください。

| データ | 出所と意味 |
|---|---|
| `ModelGrossRevenue` | `Northwind_FMCG`セマンティックモデルの *Measures Table[Gross Revenue]* をProduct / 月で集計。DAXメジャーが元値 |
| `PlanForecast` | Lab04のPlan内 *Forecast* を同じProduct / 月 / Scenarioで取得した値 |
| `PlanPeriodStatus` | Planで対象期間がClosedかOpenか。Plan設定 / 画面で確認し, 取得できない場合は不明として比較を止める |
| `SnapshotId` / `ScenarioName` / `PlanVersion` / `SourceWritebackRunIds` | 作成者が選択した一つの比較用スナップショットと, その元になるPlan状態 / 書き戻しログを識別する情報。時刻順の推測に使わない |
| `VarianceAmount` | `PlanForecast - ModelGrossRevenue` |
| `VarianceRate` | `VarianceAmount / ModelGrossRevenue`。分母が0ならNULL / 算出不可 |

`ModelGrossRevenue`と`PlanForecast`は両方ともUSD,全精度で保持します。月キーは`YYYY-MM`に統一し, Category / Sub Categoryは元のフィールド値で突合します。表示用の丸め値や`Month Short`だけでは照合しません。`ProductKey`と`PeriodKey`は各CSV内で再現可能なキーにし, 元列との対応表を残します。キー衝突,曖昧な製品名,月の取り違えを検出できない場合はデータをロードしません。

### 期間の解釈

- **Closed period:** PlanのForecastが実績メジャーにリンクする期間です。ForecastとGross Revenueが一致することを確認するチェックに使います。差があれば, Scenario / 月 / 製品 / 書き戻し状態を調査します。
- **Open period:** Planの入力 / 予測期間です。NorthwindのGross Revenueが同じ月にあっても, それはサンプルモデル内の比較値です。**確定済みの実績として呼ばず**, 「Open periodのPlan Forecast対サンプルモデル値」と明示します。
- Lab04の例ではJan 2026がClosed, Feb-Dec 2026がOpenです。自分のPlanでClose Period設定が異なる場合, 実際の表示を優先します。
- Jan 2026のLab04全体例ではForecast 2,091,951.33343, Gross Revenue 1,919,542.65が**期間を閉じる前**に表示されています。その後, Jan 2026をClosedにするとForecastはGross Revenueを参照する設定です。前後の値を同じPlan状態として混ぜません。
- 算術式だけの確認例では, このJan 2026 All行の`Forecast - Gross Revenue`は172,408.68343, 比率は0.0898175841（約8.98175841%）です。これはLab04の期間全体の例であり, Product × 月の比較SnapshotへAll行を混ぜる値ではありません。

## パート1：比較対象を固定する

1. Lab04でPlanを開き, Forecastシート, Scenario, Forecast期間, `Close Period till`,保存済みの内容を確認します。比較する**一つのScenarioと一つのPlan状態**を選び, `PlanVersion`に人が分かる版名を付けます。Data Agentの質問に使う`SnapshotId`も一意に決めます。時刻が最新という理由だけでデータを選ばないでください。
2. Writeback **Logs**から対象となる成功操作を確認し, ログ上のID / 実行情報を`SourceWritebackRunIds`として記録します。Long with Changesから集約された状態が複数回の書き戻しにまたがる場合は, 関係する実行を漏れなく記録します。一回の操作で全履歴が置き換わったとは仮定しません。
3. Fabric SQLでLab04の宛先テーブルの実スキーマを確認します。Lab04の`INFORMATION_SCHEMA.COLUMNS`照会を使い, Category / Sub Category / Year / Month / Scenario / Measure / Valueに対応する**実在列**を特定します。`IsLatest`, `PreviousValue`,実行IDなどは, スキーマに存在し, 公式の書き戻し意味と対象テーブルの実値を確認できた列だけ使います。
4. `IsLatest = 1`がある場合でも, 選択Scenario / Measure / Period / Productの全キーごとに現在行が**1行だけ**かを検査します。`IsLatest`がない / 複数行 / 欠落行の場合に, `TOP 1`,最大タイムスタンプ,行順で代替してはいけません。
5. **Long with Changesは変更履歴形式です。** 履歴を合計して現在Forecastを再構成しません。データが差分で完全な現行状態を証明できない場合は, 対象Planの現在のForecastを使った管理された全件スナップショットを作成してください。Lab04の宛先 / 履歴を上書きしたり, Planの設定を黙って変更したりしません。現行UIでサポートされた方法で全件取得できない場合は, Lab09を停止して講師 / 管理者へ相談します。

## パート2：実績 / 見通しを同じ粒度で抽出する

1. 元レポートを変更しないよう, `Northwind_FMCG`セマンティックモデルから新しい一時レポートを作成するか, 管理者が承認したエクスポート用レポートを使います。テーブルビジュアルに以下を配置します。

   | 用途 | モデルのフィールド |
   |---|---|
   | 行キー | *Product[Category]*, *Product[Sub Category]* |
   | 月キー | *Date[Year]* と *Date[Month]* または *Date[Year Month]*。Dataペインに存在する正確な列を確認 |
   | 数値 | *Measures Table[Gross Revenue]* |

2. Planと同じ対象月 / Category / Sub Categoryを含むことを確認します。レポートの **More options → Export data** からサマリー済みデータをCSVで出力します。画面が許可しない,列が省略される,エクスポート制限に達する場合は管理者に確認し, 基になるデータや別のメジャーを推測で出力しません。
3. SQLのForecast宛先から, パート1で確認した列を使って同じScenario / Measure / Year / Month / Productの行を読み出します。キーが完全に確認できた**全精度**の値をCSVへ出力します。出力列にない書き戻しIDや履歴列を付け足しません。必要なログIDは別の出典メモに残します。
4. 承認済みのExcelで **Data → Get Data → From Text/CSV** から2つの全件CSVをPower Queryへ読み込み, `ProductKey` / `PeriodKey`はText, 金額は精度を落とさない10進数として設定します。各クエリを`ProductKey + PeriodKey`で **Group By → Count Rows** し, 件数が1以外のキーがあれば停止します。**Merge Queries as New**で同じ2キーを選び, Join kindを**Full Outer (all rows from both)**にします。Forecast側のキーを展開し, いずれかの側のキーがnullの行がないことを確認します。両方の全件エクスポートの一意キー件数が一致し, Full Outer結合の欠損が0件, 結合後の行数も双方の一意キー件数と一致することを確認します。結果を[比較スナップショットの列テンプレート](../data/lab09-variance-snapshot-template.csv)に合わせ, `ExpectedRows`（結合済み件数 > 0）, 両エクスポートの総行数 / 一意キー件数, SnapshotId / Scenario / PlanVersionを組織承認済みの**非公開な検算記録**へ残します。未一致,重複,欠損,通貨違いは根拠を特定して直すまでロードしません。Excelの自動型変換でProductKey / PeriodKeyが変わらないよう文字列として扱い, 金額は全精度の10進値を保持します。
5. 1行につき一つの`SnapshotId × ScenarioName × PlanVersion × ProductKey × PeriodKey`にします。`SourceWritebackRunIds`には現在値を構成する対象ログIDを識別できるよう記録します。全行で同一の単独Writeback IDが確認できないなら, その事実を隠さず複数IDまたは集約状態として残します。
6. Warehouseへロードする前に, CurrencyCodeが`USD`, Measure名が正確に`Gross Revenue` / `Forecast`,行の一意性,全精度の数値,対象期間状態を検査します。Closed / Openの各月の実際の状態を確認し, `ClosedLinkedActual`または`OpenSampleReference`のどちらかを記録します。データのない値を0で埋めず, 固定の商品数や行数に合わせて欠損を補完しません。

## パート3：専用Warehouseに比較スナップショットを作る

1. 事前承認した演習Workspaceに, 比較用Warehouse（例：`HPC_Lab09_Analysis`）と一時ファイル保管用Lakehouse（例：`HPC_Lab09_Staging`）を新規作成します。Capacity / Warehouse / OneLakeの課金と, 必要ならWorkspace IdentityをLakehouse側へ追加する権限変更を管理者と確認します。CSVの内容と保管先を組織ポリシーで承認し, 公開リンク / 個人用共有領域 / 実データは使いません。
2. Lab09 CSVをUTF-8で保存し, 15列の順序とヘッダーが[テンプレート](../data/lab09-variance-snapshot-template.csv)と完全一致することを確認します。金額は10進数文字列を10桁以内の小数精度で保持し, Excelの数値丸め / 指数表記 / ロケール変換を行いません。`ExpectedRows`と双方のソース件数 / 一意キー件数はCSVへ加えず, 組織承認済みの非公開検算記録へ保存します。
3. FabricでLakehouseを開き, **Files** に今回の取込専用の新しい子フォルダー（例：`Lab09/run-<safe-id>`）を作成します。フォルダーの **... → Upload → Upload files** を選び, CSVをローカル端末からアップロードします。フォルダーに今回のファイルが1つだけあること, ファイル名と内容がSnapshotのものと一致することをUIで確認します。これはLakehouseを一時置場にする経路です。詳しくは[公式CSVアップロード手順](https://learn.microsoft.com/en-us/fabric/data-engineering/get-started-csv-upload)を参照してください。
4. WarehouseのSQL query editorで新規の `dbo.Lab09Stage` を**明示的な型**で作成します。同名テーブルが既にある場合は上書き / 再利用せず停止します。再試行用の別名を選ぶ場合は, 後続SQLのStage参照もすべてその新しい名前へ置き換えます。数値はfloatへ推論させません。

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

5. 管理者が事前に承認した構成でWorkspace IdentityがソースLakehouseのWorkspaceへContributorとして追加され, 実行者にWarehouseの必要なSQL権限があることを確認します。このIdentity設定 / 権限付与自体は本ラボのSQLで自動作成せず, 組織の承認手順に従います。Warehouse SQL query editorで次の`COPY INTO`を実行し, パス中のWorkspace / Lakehouse Item ID / run folder / ファイル名だけを実際のUI値に置き換えます。ソースはOneLake Lakehouse FilesのURLで, ローカルパスや公開ストレージURLではありません。

   ```sql
   COPY INTO dbo.Lab09Stage
   (
       SnapshotId, ScenarioName, PlanVersion, SourceWritebackRunIds,
       ProductKey, Category, SubCategory, PeriodKey, PeriodStart,
       PlanPeriodStatus, CurrencyCode, ModelMeasureName, ModelGrossRevenue,
       PlanMeasureName, PlanForecast
   )
   FROM 'https://onelake.dfs.fabric.microsoft.com/<workspace-id>/<lakehouse-item-id>/Files/Lab09/<safe-id>/<snapshot-file>.csv'
   WITH
   (
       FILE_TYPE = 'CSV',
       FIRSTROW = 2,
       ENCODING = 'UTF8',
       FIELDTERMINATOR = ',',
       FIELDQUOTE = '"',
       CREDENTIAL = (IDENTITY = 'Workspace Identity')
   );
   ```

   `COPY INTO`は[WarehouseのOneLakeソース取込](https://learn.microsoft.com/en-us/fabric/data-warehouse/ingest-data)で文書化された経路です。ヘッダーを飛ばし, CSVのカンマ区切り / 二重引用符を解釈します。Workspace IdentityやソースWorkspace権限を組織で許可できない場合は, 認証を迂回したり非公開データを外部へ移したりせず, 管理者が承認した同等のOneLake経路が整うまで停止します。
6. アップロード完了と`COPY INTO`のSQL実行完了を確認後, `COUNT_BIG(*)`でStageのロード件数を読み返します。ロード件数が非公開検算記録の`ExpectedRows`と一致しない, 0件, COPYのエラー / rejectがある場合は先へ進まず, 原因を直して新しい空のStage名でやり直します。既存データの`DROP`, `TRUNCATE`, `DELETE`で再実行を通しません。新しいStage名へ切り替える場合は, 続くすべてのSQLの参照名も合わせます。
7. 対象Snapshot / Scenario / PlanVersionに限定した次の検査を実行します。**全て0件かつ正の期待件数との一致が必要**です。`<...>`をCSV内の値に置き換え, 文字列値はSQL文字列中でシングルクォートを二重化するかパラメーターを使用します。検査用SQLは**この新しいLab09専用Warehouseだけ**で実行します。

   ```sql
   -- SQL検査はこの新しいLab09専用Warehouseだけで実行する。
   SELECT
       CAST('<expected-row-count>' AS bigint) AS ExpectedRows,
       CASE WHEN CAST('<expected-row-count>' AS bigint) <= 0
            THEN 1 ELSE 0 END AS InvalidExpectedRows,
       COUNT_BIG(*) AS AllStageRows,
       COALESCE(SUM(CASE WHEN SnapshotId = '<snapshot-id>'
                          AND ScenarioName = '<scenario-name>'
                          AND PlanVersion = '<plan-version>'
                         THEN 1 ELSE 0 END), 0) AS SelectedRows
   FROM dbo.Lab09Stage;

   SELECT ProductKey, PeriodKey, COUNT_BIG(*) AS DuplicateRows
   FROM dbo.Lab09Stage
   WHERE SnapshotId = '<snapshot-id>'
     AND ScenarioName = '<scenario-name>'
     AND PlanVersion = '<plan-version>'
   GROUP BY ProductKey, PeriodKey
   HAVING COUNT_BIG(*) <> 1;

   SELECT COUNT_BIG(*) AS InvalidSelectedRows
   FROM dbo.Lab09Stage
   WHERE SnapshotId = '<snapshot-id>'
     AND ScenarioName = '<scenario-name>'
     AND PlanVersion = '<plan-version>'
     AND (
         NULLIF(LTRIM(RTRIM(SnapshotId)), '') IS NULL
         OR NULLIF(LTRIM(RTRIM(ScenarioName)), '') IS NULL
         OR NULLIF(LTRIM(RTRIM(PlanVersion)), '') IS NULL
         OR NULLIF(LTRIM(RTRIM(SourceWritebackRunIds)), '') IS NULL
         OR NULLIF(LTRIM(RTRIM(ProductKey)), '') IS NULL
         OR NULLIF(LTRIM(RTRIM(Category)), '') IS NULL
         OR NULLIF(LTRIM(RTRIM(SubCategory)), '') IS NULL
         OR CHARINDEX('|', SnapshotId) > 0
         OR CHARINDEX('|', ScenarioName) > 0
         OR CHARINDEX('|', PlanVersion) > 0
         OR CHARINDEX('|', ProductKey) > 0
         OR NULLIF(LTRIM(RTRIM(PeriodKey)), '') IS NULL
         OR PeriodKey NOT LIKE '[12][0-9][0-9][0-9]-[01][0-9]'
         OR RIGHT(PeriodKey, 2) NOT BETWEEN '01' AND '12'
         OR PeriodStart IS NULL
         OR PeriodKey <> CONVERT(char(7), PeriodStart, 126)
         OR DAY(PeriodStart) <> 1
         OR PlanPeriodStatus IS NULL
         OR PlanPeriodStatus NOT IN ('ClosedLinkedActual', 'OpenSampleReference')
         OR CurrencyCode IS NULL
         OR CurrencyCode <> 'USD'
         OR ModelMeasureName IS NULL
         OR ModelMeasureName <> 'Gross Revenue'
         OR PlanMeasureName IS NULL
         OR PlanMeasureName <> 'Forecast'
         OR ModelGrossRevenue IS NULL
         OR PlanForecast IS NULL
     );

   SELECT ProductKey, COUNT_BIG(*) AS ConflictingProductRows
   FROM (
       SELECT DISTINCT ProductKey, Category, SubCategory
       FROM dbo.Lab09Stage
       WHERE SnapshotId = '<snapshot-id>'
         AND ScenarioName = '<scenario-name>'
         AND PlanVersion = '<plan-version>'
   ) AS ProductRows
   GROUP BY ProductKey
   HAVING COUNT_BIG(*) <> 1;

   SELECT PeriodKey, COUNT_BIG(*) AS ConflictingPeriodRows
   FROM (
       SELECT DISTINCT PeriodKey, PeriodStart, PlanPeriodStatus
       FROM dbo.Lab09Stage
       WHERE SnapshotId = '<snapshot-id>'
         AND ScenarioName = '<scenario-name>'
         AND PlanVersion = '<plan-version>'
   ) AS PeriodRows
   GROUP BY PeriodKey
   HAVING COUNT_BIG(*) <> 1;
   ```

   `InvalidExpectedRows = 0`であり, `AllStageRows`と`SelectedRows`がどちらも非公開検算記録の正の`ExpectedRows`と一致し, 残りの検査結果がすべて0行 / 0件の場合だけ続けます。ExpectedRowsが0 / 未記入, Stageが空 / ヘッダーのみ, またはSnapshotIdを間違えた場合は不合格です。CSVを作る前のFull Outer照合により, 両方の元エクスポートの全キーが一致していた記録も確認します。

8. 選択したSnapshotId / ScenarioName / PlanVersionに限定して, Warehouseで次の読み取り用テーブルを作ります。[`CREATE TABLE AS SELECT`（CTAS）](https://learn.microsoft.com/en-us/fabric/data-warehouse/create-table)が対象Warehouseで利用可能であることを現行資料で確認します。テーブルが既にある場合は同じ名前へ上書きせず, 別の識別名にするか中断します。

   ```sql
   CREATE TABLE dbo.Lab09Product AS
   SELECT DISTINCT ProductKey, Category, SubCategory
   FROM dbo.Lab09Stage
   WHERE SnapshotId = '<snapshot-id>'
     AND ScenarioName = '<scenario-name>'
     AND PlanVersion = '<plan-version>';

   CREATE TABLE dbo.Lab09Period AS
   SELECT DISTINCT PeriodKey, PeriodStart, PlanPeriodStatus
   FROM dbo.Lab09Stage
   WHERE SnapshotId = '<snapshot-id>'
     AND ScenarioName = '<scenario-name>'
     AND PlanVersion = '<plan-version>';

   CREATE TABLE dbo.Lab09RevenueObservation AS
   SELECT
       CONCAT(SnapshotId, '|', ScenarioName, '|', PlanVersion, '|',
              ProductKey, '|', PeriodKey) AS ObservationKey,
       SnapshotId, ScenarioName, PlanVersion, SourceWritebackRunIds,
       ProductKey, PeriodKey, PlanPeriodStatus, CurrencyCode,
       ModelMeasureName, ModelGrossRevenue, PlanMeasureName, PlanForecast,
       CAST(
           CAST(PlanForecast AS decimal(28, 10))
           - CAST(ModelGrossRevenue AS decimal(28, 10))
           AS decimal(29, 10)
       ) AS VarianceAmount,
       CAST(
           CASE WHEN ModelGrossRevenue = 0 THEN NULL
                ELSE (
                    CAST(PlanForecast AS decimal(28, 10))
                    - CAST(ModelGrossRevenue AS decimal(28, 10))
                ) / NULLIF(CAST(ModelGrossRevenue AS decimal(28, 10)), 0)
           END AS decimal(38, 9)
       ) AS VarianceRate
   FROM dbo.Lab09Stage
   WHERE SnapshotId = '<snapshot-id>'
     AND ScenarioName = '<scenario-name>'
     AND PlanVersion = '<plan-version>';
   ```

   `<...>`はCSVに記録した識別値へ置き換えます。入力値のシングルクォートはSQL文字列内で二重化し, 可能ならパラメーターを使います。ここでは金額を`decimal(28,10)`で保持します。Warehouseの型 / 精度と原値を確認し, 10桁を超える小数精度や型範囲を超える値がある場合は, 精度を失わない適切な型へ調整するまで停止します。`VarianceRate`はWarehouseの10進除算結果を`decimal(38,9)`で保存します。金額の元精度は10桁で保ち, 比率を表示するときは保存した9桁の値を使います。クエリ実行は読み取り / 作成の影響と課金を伴うため承認後に限ります。

9. Warehouseで次の検査を行います。`StageRows`と`ObservationRows`が同じ正の件数で, 不一致 / 重複 / 孤立キーが0件でなければOntologyへ進みません。

   ```sql
   SELECT ObservationKey, COUNT(*) AS RowCount
   FROM dbo.Lab09RevenueObservation
   GROUP BY ObservationKey
   HAVING COUNT(*) <> 1;

   SELECT COUNT_BIG(*) AS InvalidVarianceRows
   FROM dbo.Lab09RevenueObservation
   WHERE VarianceAmount IS NULL
      OR VarianceAmount <> CAST(
             CAST(PlanForecast AS decimal(28, 10))
             - CAST(ModelGrossRevenue AS decimal(28, 10))
             AS decimal(29, 10)
         )
      OR (ModelGrossRevenue = 0 AND VarianceRate IS NOT NULL)
      OR (ModelGrossRevenue <> 0
          AND (VarianceRate IS NULL OR VarianceRate <> CAST(
                  (
                      CAST(PlanForecast AS decimal(28, 10))
                      - CAST(ModelGrossRevenue AS decimal(28, 10))
                  ) / NULLIF(CAST(ModelGrossRevenue AS decimal(28, 10)), 0)
                  AS decimal(38, 9)
              )));

   SELECT
       (SELECT COUNT_BIG(*) FROM dbo.Lab09Stage
        WHERE SnapshotId = '<snapshot-id>'
          AND ScenarioName = '<scenario-name>'
          AND PlanVersion = '<plan-version>') AS StageRows,
       (SELECT COUNT_BIG(*) FROM dbo.Lab09RevenueObservation) AS ObservationRows;

   SELECT COUNT_BIG(*) AS MissingObservations
   FROM dbo.Lab09Stage AS s
   WHERE s.SnapshotId = '<snapshot-id>'
     AND s.ScenarioName = '<scenario-name>'
     AND s.PlanVersion = '<plan-version>'
     AND NOT EXISTS (
         SELECT 1 FROM dbo.Lab09RevenueObservation AS o
         WHERE o.SnapshotId = s.SnapshotId
           AND o.ScenarioName = s.ScenarioName
           AND o.PlanVersion = s.PlanVersion
           AND o.ProductKey = s.ProductKey
           AND o.PeriodKey = s.PeriodKey
     );

   SELECT COUNT_BIG(*) AS ExtraObservations
   FROM dbo.Lab09RevenueObservation AS o
   WHERE NOT EXISTS (
       SELECT 1 FROM dbo.Lab09Stage AS s
       WHERE s.SnapshotId = o.SnapshotId
         AND s.ScenarioName = o.ScenarioName
         AND s.PlanVersion = o.PlanVersion
         AND s.ProductKey = o.ProductKey
         AND s.PeriodKey = o.PeriodKey
   );

   SELECT COUNT_BIG(*) AS OrphanProductKeys
   FROM dbo.Lab09RevenueObservation AS o
   WHERE NOT EXISTS (
       SELECT 1 FROM dbo.Lab09Product AS p WHERE p.ProductKey = o.ProductKey
   );

   SELECT COUNT_BIG(*) AS OrphanPeriodKeys
   FROM dbo.Lab09RevenueObservation AS o
   WHERE NOT EXISTS (
       SELECT 1 FROM dbo.Lab09Period AS p WHERE p.PeriodKey = o.PeriodKey
   );
   ```

   `InvalidVarianceRows`, `MissingObservations`, `ExtraObservations`, `OrphanProductKeys`, `OrphanPeriodKeys`が0であることを確認します。さらにSnapshot全件について両エクスポートの元件数 / 一意キー件数 / Full Outer欠損0件というローカル照合記録を確認します。Data Agentに質問する1行を独立したWarehouse SELECTと電卓で検算し, 差異率がNULLになる0分母も含めて確認します。式を同じSQLで再計算するだけを正確性の根拠にせず, 元出力値 / 行範囲 / 数値を独立に照合します。為替換算,年計 / 月次の混在,履歴行の合算は行いません。

## パート4：Ontologyで製品 / 期間 / 差異の意味を定義する

Ontologyは定義とデータバインディングを持つ意味付けレイヤーであり, 全データを複製するデータベースや一般的なクエリエンジンではありません。ここでは比較用Warehouseの3テーブルをバインドします。セマンティックモデルを自動で更新したり, Planへ自動接続したりはしません。

1. Fabric Workspaceで **+ New item → Ontology (Preview)** を選び, 例として`HPC_Lab09_VarianceOntology`を作ります。Ontology / Fabric item作成のテナント設定, Preview対象,権限を確認します。旧Ontologyの画面と新しいPreviewエクスペリエンスを混在させず, 画面の現在の案内に従います。
2. Home configuration canvasで **Add entity type** を使い, 次の3種類を作ります。

   | Entity type | Key | Properties / 意味 |
   |---|---|---|
   | `Product` | `ProductKey` | `Category`, `SubCategory`。Lab04のモデルに存在する階層 |
   | `Period` | `PeriodKey` | `PeriodStart`, `PlanPeriodStatus`。例は月単位で, Year / Monthを一意に識別 |
   | `Revenue Observation` | `ObservationKey` | `ProductKey`, `PeriodKey`（Relationship用外部キー）, `SnapshotId`, `ScenarioName`, `PlanVersion`, `SourceWritebackRunIds`, `CurrencyCode`, `ModelGrossRevenue`, `PlanForecast`, `VarianceAmount`, `VarianceRate` |

3. 各Entity Typeを **View Entity Type details → Configure → Manage property bindings → Add binding and properties** から設定します。OneLake catalogで専用Warehouseの `Lab09Product`, `Lab09Period`, `Lab09RevenueObservation` をそれぞれ選び, Propertyを同名列へバインドします。`ProductKey`, `PeriodKey`, `ObservationKey`をEntity type keyとして指定できる型であることを確認します。`Revenue Observation`には両方のForeign Key Property（`ProductKey`, `PeriodKey`）も同名列へバインドします。キーが重複 / NULLなら先にWarehouseを修正します。
4. Home configuration canvasの **Add relationship** で関係を作ります。

   | Relationship | Origin → Target | 対応列 |
   |---|---|---|
   | `Product has Revenue Observations` | `Product` → `Revenue Observation` | `ProductKey` → `ProductKey` |
   | `Period contains Revenue Observations` | `Period` → `Revenue Observation` | `PeriodKey` → `PeriodKey` |

   公式手順のRelationship detailsで **Use mapping table? = Off** を選びます。`Product`をOriginにした関係ではOrigin property `ProductKey`からTarget entity `Revenue Observation` property `ProductKey`へ, `Period`をOriginにした関係ではOrigin `PeriodKey`からTarget `Revenue Observation` `PeriodKey`へ直接結び付けます。ObservationのEntity keyは`ObservationKey`のままです。両Entityのsource bindingと値の型が一致することを確認して保存し, 実データで全Observationが各Product / Periodへ結び付くことを検証します。操作は[公式Relationship type手順](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-create-relationship-types)の4〜8に従います。

5. Ontologyの **Overview → Rules** で, Product / Period / Revenue Observationへ関連付けた`Revenue variance interpretation`ルールを作成します。Rule definitionには次を明記します。

   > VarianceAmount is PlanForecast minus ModelGrossRevenue in USD at one ProductKey and one PeriodKey for the specified SnapshotId, ScenarioName, and PlanVersion. VarianceRate is not defined when ModelGrossRevenue is zero. OpenSampleReference periods compare a plan forecast with the Northwind sample-model value and must not be described as closed actual results. Never add multiple writeback history rows or multiple snapshots together.

   これは意味を伝えるルールで, 計算処理ではありません。数値はWarehouseの照合済み列を参照します。Ontologyのルールだけを根拠に計算が実行されたとは扱いません。
6. Ontologyを保存し, `Configure`画面で全Propertyのsource bindingとEntity key / Relationshipの対応を確認します。CSVロード後の更新があれば, 現行のOntology UIで明示的にRefreshし, Previewに表示される対象データの版を確認します。バインドを設定しただけで最新データへ自動更新されたとはみなしません。
7. この単純な集計演習では **Manage graph / Materialize** を使いません。Ontologyとその関係定義だけで目的を満たします。グラフのマテリアライズはこの分析に不要な別機能 / 実行コストです。

## パート5：Ontologyを使う読み取り専用Data Agentを作成する

1. Workspaceから **+ New item → Fabric data agent** を選び, `HPC_Lab09_Plan_Variance_Analyst`を作成します。OneLake catalogで**作成したOntologyだけ**をデータソースとして追加します。元セマンティックモデルや書き戻しSQLをAgentへ別ソースとして追加し, Ontologyを迂回させないでください。
2. Explorerで必要なEntity / Propertiesを選びます。`Product`, `Period`, `Revenue Observation`と比較の各数値, Scenario, PlanVersion, SnapshotId,期間状態だけを有効にし, 関係ない列は外します。Ontologyをデータソースとして加えるには, 当該ユーザーにOntologyへのReadと必要なBuild権限を確認します。セマンティックモデル直接クエリのRead要件を, OntologyバインドのRead + Build要件に取り違えません。
3. **Instructions**へ次の範囲を設定します。

   ```text
   このAgentはHPC_Lab09_VarianceOntologyだけを使う読み取り専用の分析Agentです。
   通常はSnapshotId, ScenarioName, PlanVersion, 一つのPeriodKey, CurrencyCodeを
   特定して回答してください。複数月を明示して尋ねられた場合だけ、
   指定されたPeriodKeyのリストを漏れなく確認し、PeriodKeyとPlanPeriodStatusごとに
   行数と金額合計を分けて示してください。未知の期間、指定外の期間、別Snapshot /
   Scenario / PlanVersionを混ぜず、範囲が曖昧なら回答前に質問してください。
   VarianceAmountはPlanForecast - ModelGrossRevenueです。
   複数行のVarianceRateを合算または単純平均しないでください。
   複数行の合計比率を求められた場合は
   (SUM(PlanForecast) - SUM(ModelGrossRevenue)) / NULLIF(SUM(ModelGrossRevenue), 0)
   とし、Warehouseの同じキー範囲のSQL結果と照合してください。
   ModelGrossRevenueが0の場合はVarianceRateを算出しないでください。
   OpenSampleReferenceはNorthwindサンプル上の比較値で, 確定実績とは呼びません。
   Closed period, Open periodを明示し, 結果に使ったSnapshotIdと条件を記します。
   データ不足,重複,複数の候補,未バインドの関係がある場合は推測せず回答を保留します。
   原因分析,将来予測,勧告やPlan変更を行ったとは主張しません。
   ```

4. Agent builderの **Test** でまずSnapshotId, Scenario, PlanVersionを明記した具体的な月次質問を行い, 日本語の質問でも同じ数値 / 条件が返るか検証します。Fabric Data Agentの非英語での挙動を事前に保証せず, 日本語での回答品質が不十分なら本番利用可能と判定しません。成功後に必要があればPublish / Shareします。公開範囲は最小限にし, 対象利用者本人のWarehouse / Ontologyアクセスで確認します。ワークスペース管理者での表示だけで本人別認可を実証したとはしません。
5. Agentが生成したQuery / stepsが参照するのはOntology内のRevenue Observationであることを確認します。別ソースを選ぶ, 関係のない期間を含める, 条件を落とす, Open periodを実績と言い換える,複数Versionを加算する場合はPublishせず, Entity / keys / rule / Instructionsを見直します。

## 問いかけ例と数値検算

`<snapshot-id>`, `<scenario>`, `<plan-version>`, `<period-key>`は自分の記録値に置き換えます。

1. **範囲を限定した合計**
   > Snapshot `<snapshot-id>`, Scenario `<scenario>`, Plan version `<plan-version>`, Period `<period-key>`について, USDのModelGrossRevenue合計, PlanForecast合計, VarianceAmount合計を比較してください。PeriodStatusと, この値が実績かサンプルモデル参照かも示してください。
2. **差異上位の製品**
   > 同じ条件の中で, VarianceAmountの絶対値が大きいSub Categoryを最大5件, Categoryと金額を付けて並べてください。欠損値は除外数を明記してください。
3. **1行の算術照合**
   > Product `<product-key>`について同じSnapshot / Scenario / Plan version / PeriodのModelGrossRevenue, PlanForecast, VarianceAmount, VarianceRateを示し, `PlanForecast - ModelGrossRevenue`を検算してください。
4. **Closed / Openの差**
   > 選択SnapshotのPeriodKey `<period-key-1>`, `<period-key-2>`, `<period-key-3>`だけを比較してください。各PeriodKeyとClosedLinkedActual / OpenSampleReferenceごとに行数, ModelGrossRevenue合計, PlanForecast合計, VarianceAmount合計を分けて示し, 全指定期間の合計比率はForecast合計とGross Revenue合計から計算してください。VarianceRate行を単純平均 / 合算せず, OpenSampleReferenceを実績と呼ばないでください。
5. **日本語での検証**
   > Snapshot `<snapshot-id>`, Scenario `<scenario>`, Plan version `<plan-version>`, Period `<period-key>`を指定し, `Product <product-key>` のGross Revenue, Forecast, 差異を全精度で示してください。Open期間なら確定実績と呼ばないでください。

**Agent回答の数値照合:** 同じフィルターを付けた読み取り専用Warehouse queryを実行し, 行数,一意キー,各値,合計を確認します。Agentがレポートした数値がUIの丸め値と違う場合は, Warehouseの全精度を基準にし, 丸め方法を報告します。Expected resultはこのSQL結果と一致することであり, 数値を教材に固定しません。

## 失敗時の切り分けと安全な終了

| 症状 | 対応 |
|---|---|
| CSVがLakehouse Filesにない / COPYに失敗 | 作成Workspace / Lakehouse ID / Filesパス, UTF-8 / ヘッダー / CSV引用符, Workspace Identityの承認済みソースアクセス, Stageの型とCOPY結果を確認。件数一致までOntologyへ進まず, 既存データの削除でやり直さない |
| Stageが空 / 件数が期待と違う | 正の`ExpectedRows`,アップロードしたファイルの内容 / Snapshot ID, COPYの実行結果と`COUNT_BIG(*)`を照合。想定外の行があるStageを再利用しない |
| Data Agent作成項目がない / Testが使えない | 有料F2 / P1, capacity-level Copilot, Tenant settings,クロスジオ条件,Preview提供地域,設定反映時間を管理者と確認。Planningの試用容量だけで動くと仮定しない |
| Ontologyが作成できない / Sourceが選べない | Preview設定,Create Fabric items設定,利用者権限,Warehouse sourceの一覧を確認。REST API / JSONで補わない |
| Semantic model exportとForecastでキーが合わない | 元のDate / Product field, ForecastのScenario / Measure, period statusを確認。文字列表示だけを結合キーにせず, 欠損を0で埋めない |
| SQLに複数履歴行 / IsLatest列がない | 最新行を時刻や`TOP 1`で選ばない。Lab04のログ / 公式の履歴意味を確認し, 完全なPlan現在状態の承認済みスナップショットが用意できなければ停止 |
| Ontologyの値が古い / 関係が不完全 | WarehouseのSnapshotIdとロード行数, OntologyのBindingとPreview / Refresh状態を確認。成功と推測しない |
| Agent回答が違う / 根拠を示さない | Publishせず, AgentのSteps / Query, 選択したEntity / property,条件とWarehouse結果を比較。原因分析や一般化した助言を事実として採用しない |
| 日本語の質問で意図しない列 / 条件が使われる | 英語の正式プロパティ名をUIで確認し, 同一Snapshot / Scenario / Period条件で再テストする。日本語で正しい数値が得られない場合は制約を明記し, 利用可能と見なさない |

終了時に, 利用者が作成したLab09用CSV, Lakehouse Filesのステージファイル, Lakehouse, Warehouse Stage / 比較テーブル, Ontology, Data Agentの名前とOwner, Snapshot / Scenario / Plan version,検査結果,未確認事項を承認済みのプライベート運用記録に残します。公開リポジトリにはテナントID,実行ID,資格情報,データ行を追加しません。ステージCSVの削除やLakehouse / Warehouse等のアイテム削除が必要な場合は, この演習で新規作成した個別対象だけを特定し, Owner / 利用者 / retention / billingへの影響を確認して明示承認を得てから行います。Workspace Identityや権限の解除も管理者の別途承認が必要です。Capacity停止やWorkspace全削除を自動cleanupに使いません。

## 公式資料

- [Fabric Data Agentの概要 / 前提条件 / 読み取り専用動作](https://learn.microsoft.com/en-us/fabric/data-science/concept-data-agent)
- [Fabric Data Agentの作成,Source選択,テストと共有](https://learn.microsoft.com/en-us/fabric/data-science/how-to-create-data-agent)
- [Data AgentのTenant settings](https://learn.microsoft.com/en-us/fabric/data-science/data-agent-tenant-settings)
- [Ontology Previewの概要](https://learn.microsoft.com/en-us/fabric/iq/ontology/overview)
- [Ontology Entity Typeの作成](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-create-entity-types)
- [Ontologyへのデータバインディング](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-bind-data)
- [Ontology Relationshipの作成](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-create-relationship-types)
- [Ontology Business Ruleの作成](https://learn.microsoft.com/en-us/fabric/iq/ontology/how-to-use-rules)
- [Fabric Warehouseを作成](https://learn.microsoft.com/en-us/fabric/data-warehouse/create-warehouse)
- [ローカルCSVをLakehouse Filesへアップロード](https://learn.microsoft.com/en-us/fabric/data-engineering/get-started-csv-upload)
- [WarehouseでOneLake / Azure Storageからデータを取込む（COPY INTO）](https://learn.microsoft.com/en-us/fabric/data-warehouse/ingest-data)
- [Warehouseでサポートされる保存データ型](https://learn.microsoft.com/en-us/fabric/data-warehouse/data-types)
- [Warehouseでデータを取込む](https://learn.microsoft.com/en-us/fabric/data-warehouse/tutorial-ingest-data)
- [Warehouse SQL Query Editor](https://learn.microsoft.com/en-us/fabric/data-warehouse/sql-query-editor)
- [Warehouseで使えるT-SQL構文](https://learn.microsoft.com/en-us/fabric/data-warehouse/tsql-surface-area)
- [Power BI visualからのExport](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-export-data)

---

**← 前へ：** [モジュール08：容量とガバナンス](08-sizing-and-governance.md) · [README](../README.md)
