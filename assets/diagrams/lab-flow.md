# 演習全体の流れ

各要素のつながりと、モジュールごとに追加する内容を示します。

```mermaid
flowchart TB
    subgraph SRC["データソース"]
        PBIX["Northwind_FMCG.pbix<br/><i>Harborlightのモデル</i>"]
        XLSX["assets.xlsx<br/><i>任意</i>"]
    end

    subgraph ITEM["Plan アイテム：Harborlight_FY26_Plan"]
        direction TB
        PI["<b>Plan Intro</b><br/>M01：FY25実績<br/>M02：3,000万ドルの目標と販売計画"]
        GP["<b>Gross Profit</b><br/>M03：編集可能なコピーでOptimizerを検討"]
        FC["<b>Forecast</b><br/>M04：MSTLとローリング見通し"]
        PL["<b>P&amp;Lモデル</b><br/>M05：メジャーモデルと行モデル<br/>2つのシナリオ"]
        IS["<b>FY26 Plan Review</b><br/>M06：Lab02計画とモデル実績を可視化<br/>Lab04 Forecastは任意"]
    end

    subgraph PT["Plan アイテム：Asset Management（任意）"]
        PTS["<b>PowerTable</b><br/>M07：承認、アクセス制御、<br/>自動化"]
    end

    subgraph OUT["Fabric SQL"]
        SQL[("Forecast テーブル<br/><i>Long with Changes</i>")]
        ADB[("fabric_plan_training")]
    end

    subgraph ADV["モジュール09：発展編（別途準備）"]
        SNAP["Gross Revenue / Forecast<br/>Product × 月Snapshot"]
        STAGE["一時Lakehouse Files<br/>UTF-8 CSV"]
        WH[("専用Warehouse<br/>Decimal検算用")]
        DELTA["Lakehouse managed Delta<br/>Product / Period / Observation"]
        ONT["Ontology Preview"]
        AGENT["Fabric Data Agent<br/>Ontology経由 / 読み取り専用"]
        CHECK["回答とSQL値の<br/>独立照合"]
    end

    DS["後続分析<br/>接続を明示的に構成"]

    PBIX -->|セマンティックモデルへの接続| PI
    XLSX --> PTS

    PI -->|From Sheets| GP
    PI -->|From Sheets| IS
    FC -.->|任意：シートを埋め込みFrom Sheetsで参照| IS
    PBIX --> FC
    PBIX --> PL

    FC -->|書き戻し| SQL
    PTS --> ADB
    SQL --> DS
    PBIX -->|Gross Revenueを同じ粒度で抽出| SNAP
    SQL -->|履歴を検証 / 同一状態を照合| SNAP
    SNAP -->|承認済みCSVを手動Upload| STAGE
    STAGE -->|OneLake COPY INTO| WH
    STAGE -->|Spark SQLでDelta作成| DELTA
    DELTA -->|キー / 関係 / 意味をバインド| ONT
    ONT -->|読み取り専用の意味付け| AGENT
    WH --> CHECK
    AGENT -.-> CHECK

    classDef src fill:#e8f0fe,stroke:#4285f4,color:#111
    classDef sheet fill:#fff4e5,stroke:#f59e0b,color:#111
    classDef out fill:#e6f4ea,stroke:#34a853,color:#111
    classDef ds fill:#f3e8fd,stroke:#9334e6,color:#111
    class PBIX,XLSX src
    class PI,GP,FC,PL,IS,PTS sheet
    class SQL,ADB out
    class SNAP,WH,DELTA,ONT,AGENT,CHECK ds
```

## 図の読み方

**主要な演習は、1つのPlan アイテムにまとめます。** モジュール01〜06は、`Harborlight_FY26_Plan` の中で作成します。Plan アイテムは1つのセマンティックモデルに接続し、接続後に別のモデルへ変更できないためです。シート間は **From Sheets** で参照します。これは独立したコピーではありません。販売計画を編集すると、その系列を参照する売上総利益シートや、From Sheets で同じ計画系列を参照するキャンバス上のビジュアル,KPIに変更が反映されます。セマンティックモデルだけを参照するビジュアルまで、計画入力によって自動更新されるわけではありません。

**この演習では、書き戻しによって計画データを後続処理につなぎます。** モジュール04で、Plan アイテム内の見通しをFabric SQLのテーブルに書き戻します。Power BI、セマンティックモデル、データエージェントなどは、適切な接続を構成したうえで、そのテーブルを利用できます。本演習の標準SQL書き戻しだけでは、接続元のセマンティックモデルは変更しません。

> [!NOTE]
> 最新の公式資料では、SQLへの書き戻し後に **Add table to semantic model** を使って、書き戻したテーブルをセマンティックモデルに追加する手順も説明されています。これは本演習では実施しない追加操作です。使用する場合は、[公式手順](https://learn.microsoft.com/fabric/iq/plan/planning-writeback/planning-how-to-write-back-semantic-model)で対象モデル、リレーションシップ、権限、制約を確認してください。

**PowerTableは別のPlan アイテムに作成します。** モジュール07は、計画数値ではなく参照データの管理を扱います。そのため、専用のPlan アイテムとSQLデータベースを使う独立した演習としています。

## モジュール間の関係

```mermaid
flowchart LR
    M00["00<br/>事前準備"] --> M01["01<br/>環境構築"]
    M01 --> M02["02<br/>配賦"]
    M02 --> M03["03<br/>Optimizer"]
    M03 --> M04["04<br/>見通し"]
    M04 --> M05["05<br/>P&amp;L"]
    M05 --> M06["06<br/>キャンバス"]
    M06 --> M08["08<br/>サイジング"] --> M09["09<br/>Variance Analyst<br/><i>発展編</i>"]
    M01 -.-> M07["07<br/>PowerTable<br/><i>任意</i>"]
    M07 -.-> M08

    classDef core fill:#fff4e5,stroke:#f59e0b,color:#111
    classDef opt fill:#f1f3f4,stroke:#9aa0a6,color:#111,stroke-dasharray: 4 4
    class M00,M01,M02,M03,M04,M05,M06,M08 core
    class M07,M09 opt
```

モジュール02〜06は順番に進めます。モジュール03はモジュール02の値を編集可能なコピーへ取り込み、Optimizerの変更は元の販売計画を自動更新しません。モジュール06の基本ルートではモジュール02の販売計画とモデル実績を可視化します。モジュール04のForecastを比較する場合は、Forecastシートをキャンバスへ追加で埋め込み、From Sheetsの参照を設定します。モジュール07は独立しているため、環境構築が終われば任意のタイミングで実施でき、省略しても構いません。

**モジュール09はモジュール08の後に行う任意の発展編です。** UTF-8 CSVを一時Lakehouse Filesへ配置後, WarehouseへCOPYしてDecimal値を独立検算し, Spark SQLでLakehouse managed Delta tablesを作成します。Ontology / GraphはDelta tablesへバインドし, Data AgentはOntology経由の読み取り専用質問に限り, Forecastや元モデルを更新しません。実機確認は合成CSVのPart 3〜5のみで, 実Plan / writebackからの抽出を含むEnd-to-End確認ではありません。追加の容量 / Tenant AI設定 / Preview機能 / 認証 / データ準備が必要です。[詳細手順](../../labs/09-variance-analyst.md) / [構成図](lab09-variance-analyst.md)

### 参考資料

- [計画の既知の制限事項](https://learn.microsoft.com/fabric/iq/plan/overview-limitations)
- [計画データのセマンティックモデルへの書き戻し](https://learn.microsoft.com/fabric/iq/plan/planning-writeback/planning-how-to-write-back-semantic-model)
- [チュートリアル パート11：計画シート、PowerTable、キャンバスの連携](https://learn.microsoft.com/fabric/iq/plan/planning-tutorial/intelligence/tutorial-11-planning-sheet-powertable-canvas)
