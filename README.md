<div align="center">

<img src="assets/brand/fabric_48_color.svg" width="80" height="80" alt="Microsoft Fabric 公式製品アイコン">

# Microsoft Fabric Plan Workshop

**分散したExcelの予算から, 実績とつながる計画へ。**

配賦 / 見通し / 書き戻しを体験し, 自社で試すテーマを見つける。

**日本語** &nbsp; | &nbsp; **10 labs** &nbsp; | &nbsp; **集合開催180分** &nbsp; | &nbsp; **MIT**

[**HTML操作ガイド →**](docs/workshop-presentation.html) &nbsp; | &nbsp; [Markdownのラボ](labs/00-prerequisites.md) &nbsp; | &nbsp; [講師向けガイド](docs/FACILITATOR-GUIDE.md) &nbsp; | &nbsp; [原典 / English](https://github.com/Diaz506/fabric-planning-lab)

</div>

> [!NOTE]
> 本教材はDiego Diaz氏の **[Fabric Planning Lab: Harborlight Provisions Co.](https://github.com/Diaz506/fabric-planning-lab)** のLab00〜08を基にした日本語版です。原典のMITライセンスと著作権表示を保持し, 日本語訳, 手順の画像, 数値の確認方法, 集合開催の進行案に加えて,日本語版独自の発展編Lab09を追加しています。[変更点](LOCALIZATION.md) / [翻訳基準コミット](https://github.com/Diaz506/fabric-planning-lab/commit/486be63004b30554ab44a0e3ae654e3e762188ad)
>
> 独立した非公式のコミュニティ教材であり, Microsoftによる承認, 提携, 公式認定を示すものではありません。

## インタラクティブなHTML操作ガイド

**配布用は[参加者用HTML](docs/workshop-presentation.html)です。** READMEの概要とLab00〜09の操作 / 確認問題 / 安全上の注意を収録し, 解答と講師の進行資料を含みません。[講師用HTML](docs/workshop-instructor.html)は演習の解答と準備 / 180分の進行 / 復帰 / 費用確認も収録し, 講師だけが使用します。両版とも日本語 / Englishの全文切り替え, Yu Gothic UIによる可変文字サイズ, 明 / 暗とスマートフォン表示に対応し, 作者 **[Jiayi Yang, Swarm Data SE](https://www.linkedin.com/in/yangjiayi/)** を記載しています。

GitHub上ではHTMLが実行されないため, **`docs/workshop-presentation.html`をダウンロードしてEdge / Chromeで開く**と使えます。操作画像を含む単一のHTMLファイルで, `assets`フォルダーのコピーは不要です。CDNや外部フォントは使わず, 教材の表示はオフラインで動作します。Fabric操作, 外部資料, 公式サンプルの取得には通信が必要です。[使い方 / Markdownとの同期方法](docs/PRESENTATION-GUIDE-JA.md)

## このワークショップで学べること

Excel中心の予算管理を見直したいFP&A / 財務 / 経営企画の担当者と, Power BI / Fabricの導入担当者に向けたハンズオンです。**日本のお客様10〜20名**での集合開催を想定しています。

<table>
<tr>
<td width="50%">
<img src="assets/brand/planning_48_item.svg" width="32" height="32" alt="Fabric Plan アイテムの公式アイコン">
<h3>01 / 計画を組み立てる</h3>
<p>全社目標を配賦し, 現場の入力, ロック, コメント, 承認をつなぎます。</p>
</td>
<td width="50%">
<img src="assets/brand/planning_48_item.svg" width="32" height="32" alt="Fabric Plan の公式アイコン">
<h3>02 / 前提を比較する</h3>
<p>Optimizer, 統計予測, シナリオを使い, 目標を満たす数字と業務上の妥当性を分けて考えます。</p>
</td>
</tr>
<tr>
<td>
<img src="assets/brand/sql_database_48_item.svg" width="32" height="32" alt="Fabric SQL データベースの公式アイコン">
<h3>03 / 保存結果を確かめる</h3>
<p>Fabric SQLへの書き戻しを学び, 成功ログだけでなく保存された値も照合します。</p>
</td>
<td>
<img src="assets/brand/semantic_model_48_item.svg" width="32" height="32" alt="Fabric セマンティックモデルの公式アイコン">
<h3>04 / 導入条件を整理する</h3>
<p>実績と計画の見せ方, 権限, 容量, 課金を確認し, 自社のPoCで測る成功条件を決めます。</p>
</td>
</tr>
</table>

**読み進める:** [目的](#workshopの目的) / [アーキテクチャ](#アーキテクチャ) / [はじめ方](#はじめ方) / [ラボ一覧](#ラボ一覧) / [配備とAIプロンプト](#配備とaiエージェント向けプロンプト) / [注意点](#開催と利用上の注意) / [原典とライセンス](#原典とライセンス) / [English summary](#english-summary)

## Workshopの目的

架空のHarborlight Provisions Co.を題材に, Excelに分散した年間計画をFabric Planningで組み立て, 前提と結果を参加者が説明できるようになることが目的です。日本のお客様10〜20名向けの導入検討ワークショップとして, 製品デモだけでなく, 自社で試す業務 / データ / 関係者 / PoCの成功条件を整理します。

受講後は, 1) 全社目標を配賦し入力 / レビュー / 承認をつなぐ, 2) 実績 / 計画 / 見通しの違いと更新経路を説明する, 3) SQL書き戻しをログと実データで照合する, 4) 費用 / 容量 / 権限を確認し自社の検証範囲を決めることを目指します。サンプルの操作だけで, 性能, 費用削減, 会計上の正しさ, 本番適合を実証したことにはなりません。

## アーキテクチャ

<table>
<tbody>
<tr>
<td>
<img src="assets/brand/report_48_item.svg" width="36" height="36" alt="Power BI レポートの公式アイコン"><br>
<strong>1 / ソースのインポート</strong><br>
<code>Northwind_FMCG.pbix</code>をインポートすると, 既存レポートとセマンティックモデルの両方が作成されます。レポートは既存業績の確認用, 計画アイテムはセマンティックモデルへ接続します。
</td>
<td>
<img src="assets/brand/semantic_model_48_item.svg" width="36" height="36" alt="Fabric セマンティックモデルの公式アイコン"><br>
<strong>2 / 必須の計画ルート</strong><br>
<img src="assets/brand/planning_48_item.svg" width="30" height="30" alt="Fabric Plan アイテムの公式アイコン"> 主Planは1つのセマンティックモデルに接続し, Lab01〜06のシート / IntelligenceとLab08の容量・ガバナンス検討を進めます。接続先は後から付け替えず, モデル名も変更しません。
</td>
</tr>
<tr>
<td>
<img src="assets/brand/sql_database_48_item.svg" width="36" height="36" alt="Fabric SQL データベースの公式アイコン"><br>
<strong>3 / 書き戻しと後続分析</strong><br>
Lab04は見通しを別のFabric SQLテーブルへ書き戻します。標準のSQL書き戻しで, 元のセマンティックモデルやレポートが自動更新されるわけではありません。後続モデルで使う場合は, 公式手順に沿ったテーブル追加 / 接続 / 更新を明示的に構成します。
</td>
<td>
<img src="assets/brand/planning_48_item.svg" width="30" height="30" alt="任意演習で使用する別のFabric Plan アイテムの公式アイコン">
<img src="assets/brand/sql_database_48_item.svg" width="30" height="30" alt="PowerTable演習用Fabric SQLデータベースの公式アイコン"><br>
<strong>4 / 任意のLab07</strong><br>
PowerTableは主Plan内のシートではなく, 専用の別PlanとSQLデータベースを使います。Microsoft公式の資産台帳XLSXを参照データに使う独立演習です。
</td>
</tr>
</tbody>
</table>

<img src="assets/brand/semantic_model_48_item.svg" width="26" height="26" alt="Gross Revenue の出所となるFabric セマンティックモデル"> <img src="assets/brand/planning_48_item.svg" width="26" height="26" alt="Forecast の出所となるFabric Plan"> <img src="assets/brand/data_warehouse_48_item.svg" width="26" height="26" alt="比較Snapshotを保管するFabric Warehouse"> <img src="assets/brand/data_agent_48_item.svg" width="26" height="26" alt="Ontologyを使って読み取り専用で回答するFabric Data Agent">
**5 / 日本語版独自の発展編Lab09:** Lab04のGross Revenue / Forecastを同じProduct × 月の粒度で照合し, 一時Lakehouse FilesからWarehouseへCOPYして数値を検算します。Ontology / GraphにはWarehouseではなくLakehouseの管理Deltaテーブルをバインドし, Fabric Data AgentがOntologyを通じて読み取り専用で回答します。Plan / 元モデルへの自動書き戻しではありません。[Lab09](labs/09-variance-analyst.md) / [合成サンプルCSV](data/lab09-variance-snapshot-sample.csv) / [構成図](assets/diagrams/lab09-variance-analyst.md)

> **検証状況:** Part 3〜5は同梱の合成CSVを使ってFabricで操作し, Warehouse検算, Lakehouse Delta, Ontology / Graph, Data Agentの一部の質問を確認しました。Q4 / Q4aは`SQLCandidatesFailedFilterError`となりました。実機での確認範囲は[Lab09](labs/09-variance-analyst.md)を参照してください。

<!-- presentation-exclude-start: README-LAB09-END-TO-END -->
> Part 1〜2の実Plan / writebackからの抽出を含むEnd-to-End確認ではありません。
<!-- presentation-exclude-end: README-LAB09-END-TO-END -->

<!-- presentation-exclude-start: README-LAB09-ERROR-CAUSE -->
> Q4 / Q4aの`SQLCandidatesFailedFilterError`は原因未特定です。
<!-- presentation-exclude-end: README-LAB09-ERROR-CAUSE -->

**参照とコピーは異なります。** From Sheetsで参照した計画系列は参照元の変更を受け取ります。一方, Lab03の編集可能なコピーは元シートと自動同期しません。Intelligence上でも, From Sheetsの入力値とセマンティックモデル由来の実績を区別して設定します。[既存の構成図](assets/diagrams/lab-flow.md) / [データ構成ガイド](data/README.md)

```mermaid
flowchart LR
    PBIX["Northwind_FMCG.pbix"] -->|インポート| REPORT["既存レポート"]
    PBIX -->|インポート| MODEL["セマンティックモデル"]
    MODEL -->|接続| PLAN["主Plan<br/>Lab01–06 / 08"]
    PLAN --> SHEETS["計画シート / Intelligence"]
    PLAN -.->|書き戻し| SQL["Fabric SQL"]
    SQL -.->|利用には明示的な接続が必要| DOWNSTREAM["後続分析"]
    MODEL -->|元のGross Revenueを同粒度で抽出| SNAP["Lab09 比較Snapshot"]
    SQL -->|履歴 / Scenario / versionを照合| SNAP
    SNAP -->|UTF-8 CSVをアップロード| STAGING["一時Lakehouse Files"]
    STAGING -->|OneLake COPY INTO| WAREHOUSE["専用Warehouse<br/>Decimal検算"]
    STAGING -->|Spark SQLでDelta作成| DELTA["Lakehouse managed Delta<br/>Product / Period / Observation"]
    DELTA -->|バインド / Graph投影| ONTOLOGY["Ontology Preview"]
    ONTOLOGY -->|読み取り専用| AGENT["Fabric Data Agent"]
    WAREHOUSE -->|SQLで数値を検算| CHECK["回答と元値を独立照合"]
    AGENT -.-> CHECK
    XLSX["任意の資産台帳XLSX"] -.-> POWER_TABLE["別Plan / PowerTable"]
    POWER_TABLE -.-> SEPARATE_DB["専用Fabric SQL DB"]
```

**破線はSQL書き戻し / 明示的に構成する後続分析 / 独立検算 / 任意のPowerTable経路を示します。** Warehouseは正確なDecimal値を照合するSQL層で, Ontology / Graphのバインディング先はLakehouseの管理Deltaテーブルです。PlanningのSQL書き戻しから既存レポート / セマンティックモデルへの自動接続はありません。PowerTableは別Planと別DBに分かれています。

## はじめ方

1. **環境と費用を確認する。** [Lab00](labs/00-prerequisites.md)で容量, テナント設定, 操作別の権限, セッション課金を確認します。講師 / 管理者が開催前に準備してください。
2. **公式サンプルを用意する。** [データガイド](data/README.md)からMicrosoft公式の `Northwind_FMCG.pbix` を取得します。顧客データやAPIキーは使いません。
3. **Lab00から進める。** 集合開催は[180分の講師向けガイド](docs/FACILITATOR-GUIDE.md)に沿って進行します。自習では[ラボ一覧](#ラボ一覧)から順番に取り組めます。

ブラウザー上の教材だけで読み進められます。ローカルで読む場合は次のコマンドで取得してください。

```bash
git clone https://github.com/yang-jiayi/FabricPlanWorkshop.git
cd FabricPlanWorkshop
```

### 必要なもの

| 項目 | 準備すること |
|---|---|
| 容量 | Microsoft Fabric F2以上またはFabric試用容量。これは製品上の前提であり, 10〜20名の推奨容量ではありません |
| アカウントと権限 | 作成 / 接続設定の担当者はMember / Adminを基本に準備。Contributorで可能な操作やモデルのRead / Buildは[Lab00](labs/00-prerequisites.md)で確認。入力 / 閲覧だけの参加者に一律の管理権限を付与しません |
| ブラウザー | Microsoft EdgeまたはGoogle Chrome |
| 基礎知識 | Excelのピボットテーブル, 損益計算書, Power BIセマンティックモデルの基本 |
| 任意のツール | サンプルモデルを事前に確認する場合のみPower BI Desktop |
| Lab09発展編 | Data Agentは有料F2以上またはFabric有効化済みP1以上が必要。OntologyはPreviewで, Tenant AI / クロスジオ設定, 地域提供状況, 読取権限, 事前検証済みSnapshot, 専用Warehouse, Lakehouse Filesとmanaged Delta tablesを確認 |

Lab00〜08の基本ルートにSparkやPythonは必要ありません。任意発展編Lab09ではLakehouseのSpark SQLを使います。Pythonとデータパイプライン作成は演習に含みません。

> [!IMPORTANT]
> **操作の前に課金を確認してください。** Planningは操作に応じたユーザー単位のセッションが基本で, 途中終了できません。教材で参照する公式例ではPlannerの1セッションは **847 CU時間**です。Fabric SQLなどの消費は別途考慮します。試用容量や短時間の演習を理由に費用確認を省略せず, [Lab00](labs/00-prerequisites.md)と[公式課金資料](https://learn.microsoft.com/en-us/fabric/iq/plan/resources/billing-fabric-plan)を確認してください。

## ラボ一覧

**基本ルートはLab00〜06と08で165分。** 任意のPowerTableを加えると195分です。Lab09は追加の発展編（45〜60分 / データ準備時間を除く）で, 基本ルートと集合開催180分には含みません。Lab07とLab09の両方を追加する場合は240〜255分が目安です。各ラボの目安の合計であり, 環境準備や待ち時間を含む完走保証ではありません。集合開催の180分案はLab05の詳細とLab07 / Lab09を発展回へ分け, 講師デモと参加者の入力を組み合わせます。

```mermaid
flowchart TD
    subgraph A["準備 / 計画"]
        direction LR
        L00["00 / 準備"] --> L01["01 / シート"] --> L02["02 / 配賦"]
    end
    subgraph B["予測 / シナリオ"]
        direction LR
        L03["03 / 最適化"] --> L04["04 / 見通しと保存"] --> L05["05 / 損益"]
    end
    subgraph C["分析 / 導入判断"]
        direction LR
        L06["06 / 分析"] --> L08["08 / ガバナンス"] --> L09["09 / Variance Analyst<br/>発展編"]
        L06 -. 任意 .-> L07["07 / PowerTable"] --> L08
    end
    A --> B --> C
```

| Lab | 学ぶこと / 確かめる結果 | 目安 |
|---|---|---:|
| [**00 / 事前準備**](labs/00-prerequisites.md) | 容量, テナント設定, 権限, 操作前の課金確認 | 15分 |
| [**01 / 最初のシート**](labs/01-environment-and-first-sheet.md) | Plan作成, モデル接続, 計画シートの表示 | 20分 |
| [**02 / 配賦と共同作業**](labs/02-allocation-and-collaboration.md) | 全社目標と地域入力, ロック, コメント, 承認 | 25分 |
| [**03 / Optimizer**](labs/03-optimizer.md) | 売上総利益の目標からドライバーを逆算 | 15分 |
| [**04 / 見通しと書き戻し**](labs/04-forecast-and-writeback.md) | 統計予測, 期間の締め, SQLの保存値 | 25分 |
| [**05 / 損益とシナリオ**](labs/05-pl-models-and-scenarios.md) | メジャー / 行モデル, 集計粒度, シナリオ比較 | 25分 |
| [**06 / Intelligence**](labs/06-intelligence-canvas.md) | 差異分析, KPI, 入力とキャンバスの連動 | 25分 |
| [**07 / PowerTable**](labs/07-powertable.md) | 任意。参照データ, フォーム, 承認, アクセス制御 | 30分 |
| [**08 / 容量とガバナンス**](labs/08-sizing-and-governance.md) | 課金ロール, 容量試算, RLS, 機能の制約 | 15分 |
| [**09 / Plan Variance Analyst**](labs/09-variance-analyst.md) | 発展編。Product × 月の差異, Ontology Preview, 読み取り専用Data Agent | 45〜60分 |

[構成とデータの流れ](assets/diagrams/lab-flow.md) / [Lab09の構成図](assets/diagrams/lab09-variance-analyst.md)も参照できます。

## 配備とAIエージェント向けプロンプト

このリポジトリは**手順 / 画像 / サンプルデータへのリンクを含む教材**です。Fabric Gitと同期するPlan定義, PBIX本体, データベース定義, 一括デプロイ用テンプレートは格納していません。`git clone`やGit統合だけでラボ全体がFabricに作成されるわけではありません。

配備作業をAIツールに補助させる場合は, GitHub Copilot / OpenAI Codex / Claude Codeのリポジトリ作業セッションへ, 下のプロンプトを貼り付けてください。最初の実行は**変更を適用しない事前調査とdry-run**に限定し, テナント / ワークスペース / 容量 / 課金 / 権限を承認してから, 人が許可した範囲だけを進めます。[配備ガイドとLab00〜08, 任意のLab09の完了条件](docs/DEPLOYMENT-GUIDE-JA.md)

```text
あなたはMicrosoft Fabricワークショップの配備を補助するAIです。下の入力欄を利用者が埋めたうえで、最初にこのリポジトリのREADME.md、docs/DEPLOYMENT-GUIDE-JA.md、assets/diagrams/lab-flow.md、data/README.mdと各Labを読み、リポジトリに存在する定義と存在しない定義を区別してください。この教材リポジトリ自体をFabric Gitに接続すればLabが自動作成されると仮定してはいけません。

入力:
- 対象Tenant ID: <tenant-id>
- 対象Workspace ID: <workspace-id。初回構築では空であること>
- 実行区分: <初回 / 中断した前回実行の明示的な再開>
- 再開時の非公開運用記録: <組織承認済みの保管先。初回は「なし」>
- Capacity ID / SKU / Region: <capacity-id / sku / region>
- 実行モード: <full-workshop-demo または learner-start>
- Lab07 PowerTable: <trueが全Labの既定 / false>
- Lab09 Plan Variance Analyst: <falseが既定 / trueは発展編。Data Agent用の有料容量 / Tenant AI設定 / 検証済みSnapshot / Decimal検算用Warehouse / 一時Lakehouse Files / managed Delta tables / Ontology Previewが必要>
- 課金範囲の承認者と上限: <役割 / 明示した上限>
- 実行する本人の認証済みIDと方式: <本人委任 / サービスプリンシパル名。秘密情報は記載しない>
- ソースWorkspaceまたは承認済みFabric定義の所在: <あれば指定 / なければなし>

必ず次の順で進める:
1. 最初は読み取り専用で、現在のサインイン主体、テナント、対象Workspace、容量、全ページを取得したWorkspaceアイテム一覧を突き合わせる。**初回構築は空のターゲットWorkspaceが必須**で、アイテムがあれば停止する。既存Workspaceを自動的に再開扱いにしない。再開は利用者が明示した場合だけ、組織承認済みの非公開な前回実行記録で同じテナント / Workspace / 容量 / 所有者と作成済みitem IDを照合し、全ページのアイテムが記録上の想定ID / 種別 / バインディングと一致し、無関係なアイテムや差分がないことを確認する。記録がない / 信頼できない、ID不一致、想定外のアイテム / 差分、ページ取得未完了、必要権限不明の場合は停止する。既存アイテムを削除して空にしない。
2. 次に、空Workspaceからの初回構築か、検証済みソースWorkspaceからのCI/CD昇格かを判定する。前者にはMicrosoft公式 Northwind_FMCG.pbix / 必要なLab07用XLSXと、Planを構成する本人操作が必要。後者にもソースWorkspace / 公式にサポートされたPlan定義 / 依存するモデルとSQLが必要。どちらも無い場合は「自動配備可能」と言わず、不足と手作業箇所を示す。
3. API、依存関係、アイテム単位の必要権限、認証対象、料金、期待する作成物、既存アイテムとの競合、手作業が必要な箇所、Lab00〜08と、利用者が有効化した場合のみLab09の受入条件を記したdry-run案を提示する。Planのシート / 数式 / シナリオ / PowerTable / Ontology設定に未文書化のAPIやJSONを作って使わない。
4. dry-runの後は停止する。Workspace権限の変更、ロール / 承認者割り当て、容量消費が発生する操作、請求開始につながる操作、データ変更、上書き / 削除、外部送信は、対象と結果を示して利用者の具体的な承認を得るまで実行しない。ユーザー名義でのロール付与や承認の代行をしない。
5. 承認後だけ、公式に文書化されたAPIまたは管理画面を使う。明示的な再開では、検証済みの記録にある作成済みIDを再利用し、完了済みのPBIXインポートや作成を繰り返さない。Pipelineの更新 / 再配備も、レビュー済みのsource-target対応と所有対象だけに限定して承認後に行う。無関係な項目を上書き / 削除しない。202 Acceptedは完了ではない。APIが返すLocation / Retry-Afterと操作状態を使い、有限回で確認する。失敗時にWorkspaceを削除してやり直さない。
6. 各Labのオブジェクトと実際の挙動を受入表で確認する。Lab09が有効な場合は, Data Agentの容量 / Tenant AI設定 / Ontology Previewの利用可否と, Snapshotのキー / 粒度 / 履歴 / 数値照合を事前確認する。専用Lakehouseへの承認済みCSVアップロード, Warehouseの型指定COPY / 件数検査, Spark SQLでのmanaged Delta作成, Lakehouse binding / Graph materializationも受入項目に含める。AgentはOntologyだけをデータソースとして読み取り専用で使い, Plan変更や承認を行わない。**確認済みなのは合成CSVによるPart 3〜5で, 実Plan / writebackからの抽出を含むEnd-to-End確認ではありません。** 手順だけを根拠にライブ検証を報告せず, 実機の成功 / 失敗と未確認項目を分けます。認可テストは許可された別ユーザーごとに実行し、管理者アカウントの表示だけで本人別検証済みとしない。期待する初期値を上書きせず、承認・書き戻し・削除の演習を勝手に実行しない。未確認項目は手動対応として残す。
7. 非同期操作IDは組織が承認したプライベートな運用記録に保存し、公開内容には値を記載しない。最後に実際の結果、未完了 / 手動対応、証拠の保存先を報告する。トークン、パスワード、テナント固有情報、参加者データをGit、公開チャット、公開ログ、スクリーンショットへ保存しない。認証やMFAは公式の本人向けフローを使い、回避しない。Fabricに接続できていない場合は、配備成功と主張しない。
```

### 実行順序と方式

1. 利用者または管理者が, 対象テナントで演習専用の空Workspaceと容量を準備します。上記のプレースホルダーを実値でAIセッションに渡す場合も, credentials / tokensは貼り付けません。
2. AIにはまずリポジトリを調べさせ, Workspace全アイテムをページングして読み取り, 依存関係とdry-run計画を出させます。初回構築は空のWorkspaceが必須です。中断した実行の再開は明示的に指定し, 非公開の前回実行記録で同一テナント / Workspace / 容量 / 所有者とitem IDを照合し, 種別 / バインディングを含む全ページの状態が一致し, 無関係なアイテムや差分がない場合だけ行います。記録の欠落 / 不一致や想定外の状態では停止し, 既存アイテムを消して空にしません。
3. **空Workspaceからの初回構築:** `Northwind_FMCG.pbix`をMicrosoft公式ソースから取得してインポートし, 作成されたレポートとモデルを確認します。初回Importでは`nameConflict=Abort`を使います。明示的な再開時は記録で検証した完了済みImportのIDを再利用し, 再Importしません。Plan固有のシート, 数式, シナリオ, PowerTableは, 現行のサポートが確認できた管理画面 / 定義インポートを人が承認して構成します。存在しない自動化テンプレートを補ってはいけません。
4. **再現可能な環境昇格:** 検証済みで機密情報を除いたソースWorkspaceまたは公式サポートされたFabric定義を用意します。Pipelineの更新 / 再配備はレビュー済みのsource-target対応と所有対象に絞り, 承認後に実行します。依存するモデル / SQLを先にまたは一緒に展開し, 環境固有のVariable Library参照を適用した後にPlanを展開します。詳細は[配備ガイド](docs/DEPLOYMENT-GUIDE-JA.md)を参照します。
5. どちらの方式でもLab00〜08の受入表を完了するまで, 「基本Workshop配備済み」と扱いません。Lab09は別途指定された場合だけ追加する発展編です。Data Agentが使える有料F2以上 / P1以上, Tenant AI設定, Ontology Preview, 完全性確認済みSnapshot, 専用Warehouse, 一時Lakehouse Filesとmanaged Delta tablesの経路がそろわない場合は未実施として記録し, 「全Workshop配備済み」と表現しません。初回構築でLab09を追加する場合は新規の比較用成果物として明示し, 既存データや初期値を変更しません。費用 / 権限 / データ保存先 / 認可テストを別々に確認します。

> [!WARNING]
> Fabric Planningの操作は課金セッションを開始する場合があります。アイテム作成, 書き戻し, ロール付与, 承認割り当ては, 対象と費用範囲を明示し, 事前承認を得てから行ってください。失敗時に無関係なアイテムやWorkspaceを自動削除しないでください。

## シナリオ

架空の消費財企業 **Harborlight Provisions Co. / HPC** は, 北米, 欧州, アジア太平洋で事業を展開しています。FY25売上高は約**2,590万米ドル**。計画は40枚のExcelシートに分散し, 前回の見通しは取締役会に届くまでに11日かかりました。

あなたはFP&Aシステム担当責任者です。既存のセマンティックモデルを使い, FY26の **売上高3,000万米ドル / 売上総利益1,250万米ドル** に向けた計画を組み立てます。目標の達成だけでなく, 入力の前提と保存結果を説明することがゴールです。

会社名, 年度, 金額は演習の設定です。自社の効果測定や費用削減の実績を示すものではありません。

### サンプルデータ

| Microsoft公式サンプル | 用途 |
|---|---|
| [`Northwind_FMCG.pbix`](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/iq/plan/Northwind_FMCG.pbix) | 地域 / 製品別の実績, 損益ドライバー, 損益科目 |
| [`Northwind-FMCG-assets-powertable-tutorial.xlsx`](https://github.com/microsoft/fabric-samples/blob/main/docs-samples/iq/plan/Northwind-FMCG-assets-powertable-tutorial.xlsx) | 任意のPowerTable演習に使うIT資産台帳 |

取得方法とフィールドの注意点は[データガイド](data/README.md)にまとめています。表示名 **Northwind FMCG** はそのまま使い, シナリオ上はHarborlightのモデルと読み替えます。金額は原典との比較のため米ドルを保持します。

## 開催と利用上の注意

<!-- presentation-instructor-start -->
**講師が設計 / 設定し, 参加者が入力 / レビュー / 承認を体験する形式**を基本にします。[講師向けガイド](docs/FACILITATOR-GUIDE.md)には事前準備, 180分の時間割, ペアの役割, つまずいた場合の復帰方法, PoCの検討シートを収録しています。
<!-- presentation-instructor-end -->

<details>
<summary><strong>製品の提供状況と画面が教材と違う場合</strong></summary>

手順と画像は作成者のFabric環境で2026年10〜11月に確認した内容を含みます。FabricのUIと機能は変わります。**すべての個別機能, 地域, テナントが同じ提供状態とは断定しません。** 開催前に講師が実際のアカウントと環境でリハーサルし, [公式概要](https://learn.microsoft.com/en-us/fabric/iq/plan/overview), [前提条件](https://learn.microsoft.com/en-us/fabric/iq/plan/overview-prerequisites), [既知の制限](https://learn.microsoft.com/en-us/fabric/iq/plan/overview-limitations)を確認してください。

</details>

<details>
<summary><strong>容量と権限を人数に合わせて決めるには</strong></summary>

F2という最小容量から, 同時操作の性能や料金を推定しません。課金上のPlanner / Stakeholder / Viewerとワークスペースのロールは別です。容量と費用の責任者を決めてください。

<!-- presentation-instructor-start -->
[講師向けガイド](docs/FACILITATOR-GUIDE.md)の操作別試算を使います。
<!-- presentation-instructor-end -->

モデルRLS, 入力値, コメント, KPIの表示範囲は同一と決めつけず, [Lab08](labs/08-sizing-and-governance.md)の制約と確認手順を参照します。

</details>

<details>
<summary><strong>損益モデルを本番の判断に使えるか</strong></summary>

[Lab05](labs/05-pl-models-and-scenarios.md)では単純平均と数量加重単価, 年次と月次, メジャー / 行モデルを区別します。演習の簡略損益モデルを完全な会計モデルとして扱わず, 自社の定義, 集計粒度, 控除の符号, 費用範囲を別途確認してください。

</details>

## 日本語版で加えたもの

- **原典由来のLab00〜08を日本語化。** UIの英語識別子を保持し, 日本語の説明から画面の操作へ迷わず進める構成にしました。
- **手順を追うスクリーンショットと数値確認。** 原典の翻訳基準版には操作画像がありません。日本語版では操作の画像と, 計算 / 保存結果を確かめる方法を追加しました。
- **10〜20名向けの講師ガイド。** 180分の進行, 操作の役割分担, 費用確認, PoCにつなげる問いを追加しました。
- **仕様差とサンプルの補足。** Microsoft Learnとの照合に基づく接続 / 権限 / UIの注意点や, 所要時間の合計, 集計粒度の説明を改訂しました。
- **日本語版独自の発展編Lab09。** Lab04のGross Revenue / ForecastをProduct × 月で照合し, Ontology Previewと読み取り専用Fabric Data Agentを扱います。これは原典の翻訳内容ではありません。

原典の内容と日本語版の追加 / 訂正の詳細は[LOCALIZATION.md](LOCALIZATION.md)に記載しています。画面や手順の変更を見つけた場合は[CONTRIBUTING.md](CONTRIBUTING.md)に沿って共有してください。

## 原典とライセンス

**Original work:** [Fabric Planning Lab: Harborlight Provisions Co.](https://github.com/Diaz506/fabric-planning-lab) by **Diego Diaz**

**Translation base:** [`486be63004b30554ab44a0e3ae654e3e762188ad`](https://github.com/Diaz506/fabric-planning-lab/commit/486be63004b30554ab44a0e3ae654e3e762188ad) / 2026-09-21

教材のライセンスは[MIT](LICENSE)です。原典の **Copyright (c) 2026 Diego Diaz** とライセンス通知を保持しています。

Microsoft Fabricの製品ロゴとPlan / SQLデータベース / Warehouse / Data Agent / セマンティックモデル / レポートのアイコンは, Microsoft公式配布のファイルを無改変で使用しています。これらのブランド資産は教材のMITライセンスの対象ではなく, Microsoftの利用条件に従います。[出典 / 取得日 / 利用条件](assets/brand/README.md)

Microsoft Fabric and the Microsoft logo are trademarks of Microsoft Corporation. 本教材はMicrosoftと提携しておらず, Microsoftによる承認を受けた公式教材ではありません。

## English summary

A Japanese community adaptation of [Diego Diaz's Fabric Planning Lab](https://github.com/Diaz506/fabric-planning-lab), preserving the original MIT license. The original-derived Labs00–08 are translated and extended with the Japan-specific, optional Lab09 advanced module. The ten labs follow Harborlight Provisions Co. from planning and allocation to forecasting, SQL writeback, analysis, and governance.

This edition adds Japanese guidance, step-by-step screenshots, numerical checks, and a 180-minute facilitator-led format for 10–20 prospective customers. The self-study estimates 165 minutes for the core path, or 195 minutes with optional PowerTable. Lab09 adds 45–60 minutes plus data preparation and requires additional paid capacity, tenant AI settings, and preview features. Its Part 3–5 workflow was tested with a synthetic CSV; extraction from a real Plan/writeback flow was not end-to-end tested. Review permissions, billing, and current feature availability before running the labs. This is an independent, unofficial adaptation, not affiliated with or endorsed by Microsoft.
