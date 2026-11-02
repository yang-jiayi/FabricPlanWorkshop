# モジュール09：Plan Variance Analyst（計画差異アナリスト）

**所要時間の目安：** 45〜60分（Lab09用データの準備時間を除く）<br>
**このモジュールで作成するもの：** Lab04の売上実績 / 見通しを照合した比較スナップショット, Product / Period / Revenue Observationを結ぶOntology（Preview）, そのOntologyだけを参照する読み取り専用Fabric Data Agent。

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
- 比較用Warehouseは新しい演習アイテムとして作成します。Capacity / Warehouse / OneLake / Data Agentの消費やCSV保管場所を確認してから作成します。共有中のForecastや元モデルを置き換えません。
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
4. Excel等の承認済みローカルツールで2つの抽出を`ProductKey + PeriodKey`により突合し, [比較スナップショットの列テンプレート](../data/lab09-variance-snapshot-template.csv)の形へ整えます。マッチしないキー, 重複キー,片側だけの値,通貨違いがあれば修正可能な根拠が得られるまでロードを停止します。
5. 1行につき一つの`SnapshotId × ScenarioName × PlanVersion × ProductKey × PeriodKey`にします。`SourceWritebackRunIds`には現在値を構成する対象ログIDを識別できるよう記録します。全行で同一の単独Writeback IDが確認できないなら, その事実を隠さず複数IDまたは集約状態として残します。
6. Warehouseへロードする前に, CurrencyCodeが`USD`, Measure名が正確に`Gross Revenue` / `Forecast`,行の一意性,全精度の数値,対象期間状態を検査します。Open periodは`OpenSampleReference`とし, Closed periodは`ClosedLinkedActual`等の明示的ラベルを付けます。データのない値を0で埋めません。

> [!NOTE]
> 例としてLab04ではProductが21の末端Sub Categoryを持ちます。全てが選択月に存在する場合は1か月で21行が期待値です。実際の行数はサンプルの版 / フィルターにより確かめ, 21行に合わせるために欠損を補完しないでください。

## パート3：専用Warehouseに比較スナップショットを作る

1. 事前承認した演習Workspaceに, 専用のWarehouse（例：`HPC_Lab09_Analysis`）を作ります。Capacity / Warehouse / OneLakeの課金を確認し, 本番DBやLab04の書き戻し先を使いません。
2. CSVをFabric Warehouseに取り込み, `dbo.Lab09Stage`という新しいテーブル名を割り当てます。Fabricの **Copy job** または環境で承認済みのWarehouse取込手順を使い, フィールド名 / 型 / 文字コードをプレビューしてから確定します。入力元を選べない場合は管理者に確認し, 書き戻しSQLの認証情報をCSVや教材へ埋め込みません。
3. Stageの列を照合し, 読取クエリで対象SnapshotIdの件数,重複,欠損を検査します。次のSQLは**この新しい演習Warehouseだけ**で使い, 既存テーブルへ実行しません。先に同名の成果物がないことを確認し,既存データを消す`DROP`, `TRUNCATE`, `DELETE`で再実行を通しません。

   ```sql
   -- 新しいLab09専用Warehouseでのみ実行する。
   SELECT SnapshotId, ScenarioName, PlanVersion, ProductKey, PeriodKey, COUNT(*) AS RowCount
   FROM dbo.Lab09Stage
   GROUP BY SnapshotId, ScenarioName, PlanVersion, ProductKey, PeriodKey
   HAVING COUNT(*) <> 1;

   SELECT COUNT(*) AS MissingRequiredValues
   FROM dbo.Lab09Stage
   WHERE SnapshotId IS NULL
      OR ScenarioName IS NULL
      OR PlanVersion IS NULL
      OR ProductKey IS NULL
      OR PeriodKey IS NULL
      OR PeriodStart IS NULL
      OR PlanPeriodStatus IS NULL
      OR CurrencyCode IS NULL
      OR CurrencyCode <> 'USD'
      OR ModelMeasureName IS NULL
      OR PlanMeasureName IS NULL
      OR ModelGrossRevenue IS NULL
      OR PlanForecast IS NULL;

   SELECT ProductKey, COUNT(*) AS ConflictingProductRows
   FROM (
       SELECT DISTINCT ProductKey, Category, SubCategory
       FROM dbo.Lab09Stage
       WHERE SnapshotId = '<snapshot-id>'
         AND ScenarioName = '<scenario-name>'
         AND PlanVersion = '<plan-version>'
   ) AS ProductRows
   GROUP BY ProductKey
   HAVING COUNT(*) <> 1;

   SELECT PeriodKey, COUNT(*) AS ConflictingPeriodRows
   FROM (
       SELECT DISTINCT PeriodKey, PeriodStart, PlanPeriodStatus
       FROM dbo.Lab09Stage
       WHERE SnapshotId = '<snapshot-id>'
         AND ScenarioName = '<scenario-name>'
         AND PlanVersion = '<plan-version>'
   ) AS PeriodRows
   GROUP BY PeriodKey
   HAVING COUNT(*) <> 1;
   ```

4. 選択したSnapshotId / ScenarioName / PlanVersionに限定して, Warehouseで次の読み取り用テーブルを作ります。[`CREATE TABLE AS SELECT`（CTAS）](https://learn.microsoft.com/en-us/fabric/data-warehouse/create-table)が対象Warehouseで利用可能であることを現行資料で確認します。テーブルが既にある場合は同じ名前へ上書きせず, 別の識別名にするか中断します。

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
                    CAST(PlanForecast AS decimal(18, 10))
                    - CAST(ModelGrossRevenue AS decimal(18, 10))
                ) / NULLIF(CAST(ModelGrossRevenue AS decimal(18, 10)), 0)
           END AS decimal(38, 20)
       ) AS VarianceRate
   FROM dbo.Lab09Stage
   WHERE SnapshotId = '<snapshot-id>'
     AND ScenarioName = '<scenario-name>'
     AND PlanVersion = '<plan-version>';
   ```

   `<...>`はCSVに記録した識別値へ置き換えます。入力値のシングルクォートはSQL文字列内で二重化し, 可能ならパラメーターを使います。ここでは取込元の数値を小数点以下10桁まで保てることを前提に金額を`decimal(28,10)`へ変換します。比率計算は`decimal(18,10)`の範囲（絶対値が100,000,000未満）を前提にします。Warehouseの列型 / 精度と原値を確認し, 10桁を超える精度が必要, 取込で丸められた, または値の範囲が型に収まらない場合は, 型と式を精度を失わない形に調整するまで進みません。クエリ実行は読み取り / 作成の影響と課金を伴うため承認後に限ります。算術の照合は丸め前の値で行い, 表示時に限って小数桁を整えます。

5. Warehouseで次の検査を行います。すべて0件,一意キー件数一致,総数一致にならなければOntologyへ進みません。

   ```sql
   SELECT ObservationKey, COUNT(*) AS RowCount
   FROM dbo.Lab09RevenueObservation
   GROUP BY ObservationKey
   HAVING COUNT(*) <> 1;

   SELECT COUNT(*) AS InvalidVarianceRows
   FROM dbo.Lab09RevenueObservation
   WHERE VarianceAmount <> CAST(
             CAST(PlanForecast AS decimal(28, 10))
             - CAST(ModelGrossRevenue AS decimal(28, 10))
             AS decimal(29, 10)
         )
      OR (ModelGrossRevenue = 0 AND VarianceRate IS NOT NULL)
      OR (ModelGrossRevenue <> 0
          AND VarianceRate <> CAST(
                  (
                      CAST(PlanForecast AS decimal(18, 10))
                      - CAST(ModelGrossRevenue AS decimal(18, 10))
                  ) / NULLIF(CAST(ModelGrossRevenue AS decimal(18, 10)), 0)
                  AS decimal(38, 20)
              ));
   ```

   Data Agentに質問する値を1行選び, `ModelGrossRevenue`, `PlanForecast`, `VarianceAmount`, `VarianceRate`を手計算または同じWarehouseのSELECTで再確認します。為替換算,年計 / 月次の混在,履歴行の合算は行いません。

## パート4：Ontologyで製品 / 期間 / 差異の意味を定義する

Ontologyは定義とデータバインディングを持つ意味付けレイヤーであり, 全データを複製するデータベースや一般的なクエリエンジンではありません。ここでは比較用Warehouseの3テーブルをバインドします。セマンティックモデルを自動で更新したり, Planへ自動接続したりはしません。

1. Fabric Workspaceで **+ New item → Ontology (Preview)** を選び, 例として`HPC_Lab09_VarianceOntology`を作ります。Ontology / Fabric item作成のテナント設定, Preview対象,権限を確認します。旧Ontologyの画面と新しいPreviewエクスペリエンスを混在させず, 画面の現在の案内に従います。
2. Home configuration canvasで **Add entity type** を使い, 次の3種類を作ります。

   | Entity type | Key | Properties / 意味 |
   |---|---|---|
   | `Product` | `ProductKey` | `Category`, `SubCategory`。Lab04のモデルに存在する階層 |
   | `Period` | `PeriodKey` | `PeriodStart`, `PlanPeriodStatus`。例は月単位で, Year / Monthを一意に識別 |
   | `Revenue Observation` | `ObservationKey` | `SnapshotId`, `ScenarioName`, `PlanVersion`, `SourceWritebackRunIds`, `CurrencyCode`, `ModelGrossRevenue`, `PlanForecast`, `VarianceAmount`, `VarianceRate` |

3. 各Entity Typeを **View Entity Type details → Configure → Manage property bindings → Add binding and properties** から設定します。OneLake catalogで専用Warehouseの `Lab09Product`, `Lab09Period`, `Lab09RevenueObservation` をそれぞれ選び, Propertyを同名列へバインドします。`ProductKey`, `PeriodKey`, `ObservationKey`をEntity type keyとして指定できる型であることを確認します。キーが重複 / NULLなら先にWarehouseを修正します。
4. Home configuration canvasの **Add relationship** で関係を作ります。

   | Relationship | Origin → Target | 対応列 |
   |---|---|---|
   | `Product has Revenue Observations` | `Product` → `Revenue Observation` | `ProductKey` → `ProductKey` |
   | `Period contains Revenue Observations` | `Period` → `Revenue Observation` | `PeriodKey` → `PeriodKey` |

   Relationship detailsでWarehouseの同じキー列を対応付けて保存し, 実データ上で全観測が対応するProductとPeriodへ結び付くことを確認します。UIがソース間の関係を保存できない場合, バインディングを成功と記録せず, Warehouse側でサポートされる関係データに正規化してから再試行します。

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
   回答前にSnapshotId, ScenarioName, PlanVersion, PeriodKey, PlanPeriodStatus,
   CurrencyCodeを特定し, 質問に指定がない場合は不足情報を質問してください。
   一つのSnapshotId / Scenario / PlanVersion / Period / Product粒度に絞り,
   複数SnapshotやScenarioを合算しないでください。
   VarianceAmountはPlanForecast - ModelGrossRevenueです。
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
   > 選択SnapshotでClosedLinkedActualとOpenSampleReferenceを分け, 各区分の行数と合計を示してください。OpenSampleReferenceを実績と呼ばないでください。
5. **日本語での検証**
   > Snapshot `<snapshot-id>`, Scenario `<scenario>`, Plan version `<plan-version>`, Period `<period-key>`を指定し, `Product <product-key>` のGross Revenue, Forecast, 差異を全精度で示してください。Open期間なら確定実績と呼ばないでください。

**Agent回答の数値照合:** 同じフィルターを付けた読み取り専用Warehouse queryを実行し, 行数,一意キー,各値,合計を確認します。Agentがレポートした数値がUIの丸め値と違う場合は, Warehouseの全精度を基準にし, 丸め方法を報告します。Expected resultはこのSQL結果と一致することであり, 数値を教材に固定しません。

## 失敗時の切り分けと安全な終了

| 症状 | 対応 |
|---|---|
| Data Agent作成項目がない / Testが使えない | 有料F2 / P1, capacity-level Copilot, Tenant settings,クロスジオ条件,Preview提供地域,設定反映時間を管理者と確認。Planningの試用容量だけで動くと仮定しない |
| Ontologyが作成できない / Sourceが選べない | Preview設定,Create Fabric items設定,利用者権限,Warehouse sourceの一覧を確認。REST API / JSONで補わない |
| Semantic model exportとForecastでキーが合わない | 元のDate / Product field, ForecastのScenario / Measure, period statusを確認。文字列表示だけを結合キーにせず, 欠損を0で埋めない |
| SQLに複数履歴行 / IsLatest列がない | 最新行を時刻や`TOP 1`で選ばない。Lab04のログ / 公式の履歴意味を確認し, 完全なPlan現在状態の承認済みスナップショットが用意できなければ停止 |
| Ontologyの値が古い / 関係が不完全 | WarehouseのSnapshotIdとロード行数, OntologyのBindingとPreview / Refresh状態を確認。成功と推測しない |
| Agent回答が違う / 根拠を示さない | Publishせず, AgentのSteps / Query, 選択したEntity / property,条件とWarehouse結果を比較。原因分析や一般化した助言を事実として採用しない |
| 日本語の質問で意図しない列 / 条件が使われる | 英語の正式プロパティ名をUIで確認し, 同一Snapshot / Scenario / Period条件で再テストする。日本語で正しい数値が得られない場合は制約を明記し, 利用可能と見なさない |

終了時に, 利用者が作成したLab09用CSV, Copy job, Warehouse, Ontology, Data Agentの名前とOwner, Snapshot / Scenario / Plan version,検査結果,未確認事項を承認済みのプライベート運用記録に残します。公開リポジトリにはテナントID,実行ID,資格情報,データ行を追加しません。削除が必要な場合は, この演習で新規作成した個別アイテムだけを特定し, Owner / 利用者 / retention / billingへの影響を確認して明示承認を得てから行います。Capacity停止やWorkspace全削除を自動cleanupに使いません。

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
- [Warehouseでデータを取込む](https://learn.microsoft.com/en-us/fabric/data-warehouse/tutorial-ingest-data)
- [Warehouse SQL Query Editor](https://learn.microsoft.com/en-us/fabric/data-warehouse/sql-query-editor)
- [Warehouseで使えるT-SQL構文](https://learn.microsoft.com/en-us/fabric/data-warehouse/tsql-surface-area)
- [Power BI visualからのExport](https://learn.microsoft.com/en-us/power-bi/visuals/power-bi-visualization-export-data)

---

**← 前へ：** [モジュール08：容量とガバナンス](08-sizing-and-governance.md) · [README](../README.md)
