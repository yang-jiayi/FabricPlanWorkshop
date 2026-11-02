# Fabric Planning：調査メモ

> [!IMPORTANT]
> **この文書は原版に含まれる2026年9月16日付の調査メモを翻訳したものです。** 原版時点の記載を残しているため、現在の導入,設定,権限,課金に関する推奨事項ではありません。価格,ロール,制限値は、現在の仕様として引用せず、各モジュールに記載したMicrosoft Learnの資料を参照してください。

原版の作成日：2026年9月16日。記載されている調査元はMicrosoft Learn、`microsoft/fabric-samples`、fabricplanning.io、および`Diaz506/fabric-space-lab`（構成の参考のみ）です。

この文書は原版由来の参考資料です。内容の適用可否は、現在のMicrosoft Learn資料と開催環境で確認してください。

---

## 1. Fabric Planningとは

**Fabric IQ**の一部としてMicrosoft Fabricに組み込まれた、EPM/CPM（企業業績管理）のワークロードです。独立した計画ツールとスプレッドシートを組み合わせる従来の運用に代わり、分析で利用する、管理されたセマンティックモデル上で予算,見通し,シナリオを作成します。

基盤技術は**Lumel**（BPM Partnersの2025年「Best Overall EPM Vendor」に選出）が提供しています。製品としては、専任の開発チームを持つ、MicrosoftのファーストパーティFabricワークロードとして提供,訴求されています。

**原典時点の提供状況：** 全世界で一般提供（GA）。課金開始日は2026年8月1日と記載されています。

> [!NOTE]
> 提供状況,開始日は原典時点の記載です。現在の提供条件や契約上の扱いは、現行照合と公式資料を確認してください。

### 4つのコンポーネント

| コンポーネント | 用途 |
|---|---|
| **Planning sheets（計画シート）** | セマンティックモデルを基にした、Excelのようなグリッドで、予算,見通し,シナリオを作成します。 |
| **PowerTable** | 参照データやマスターデータを大規模に管理する、統制の取れたデータアプリです。フォーム、承認、自動化、ガントチャート、SCDに対応します。 |
| **Intelligence sheets（インテリジェンスシート）** | レポート作成用のキャンバスです。差異分析チャート、KPIカード、マトリックス、IBCS、改ページ対応レポートを扱います。 |
| **Infobridge** | データ連携と**計画の連動**に使用します。複数のシートを集約し、地域別の変更を本社の集計に自動反映します。 |

---

## 2. 前提条件：デモを進めるために必要な準備

> [!IMPORTANT]
> **この節は原典時点の記載です。** Contributor、共有クラウド接続、複合モデル、認証方法については、現行の公式資料と異なる記述があります。現行照合と、[更新済みのモジュール00](../labs/00-prerequisites.md)を参照してください。

**容量：** F2以上、またはFabric試用版。XMLAや埋め込みトークンを使うシナリオでは、Power BI ProとPPUは**非対応**です。Premium P1〜P5は利用できます。

**ワークスペースのロール：** MemberまたはAdmin。**Contributorでは不十分**です。クラウド接続の作成や埋め込みトークンの生成ができないためです。

**テナント設定**（管理ポータル）：

1. Integration → *Allow XMLA endpoints and Analyze in Excel with on-premises semantic models*
2. Developer → *Embed content in apps*
3. Developer → *Service principals can call Fabric public APIs*（サービスプリンシパル認証の場合のみ）

**容量の設定：** XMLA EndpointをRead OnlyまたはRead Writeに設定します。

**ブラウザー：** EdgeまたはChrome。Safariは非対応です。

**セマンティックモデル：** AdminまたはBuild権限が必要です。*My workspace*内のモデルや複合モデルは利用できません。Direct Lake / DirectQueryには、固定資格情報を使うゲートウェイが必要です（SSOはまだ非対応）。

---

## 3. 課金モデル：誤解しやすいポイント

> [!IMPORTANT]
> **この節の料金,ロール説明は原典時点の記録です。** 現行照合を参照してください。公式の課金資料にも「30日間（730時間）」という表記がありますが、暦上の30日間は720時間です。原典の数値は変更せずに残しています。実際のセッション期限や請求は管理画面,課金情報で確認してください。

ユーザー単位のライセンスではなく、セッション単位で課金されます。ユーザーがPlanアイテムを開く,作成する,編集するとセッションが始まり、**730時間（30日間）**継続します。**途中で終了することはできません。**

| ロール | 主な利用者 | 30日間の消費量 |
|---|---|---|
| **Planner** | FP&A担当者、モデル作成者、管理者 | 847 CU時間 |
| **Stakeholder** | 業務担当者、レビュー担当者、承認者 | 168 CU時間 |
| **Viewer** | 経営層、レポート閲覧者 | 37 CU時間 |

- セッションは**テナント＋ユーザー＋容量**の組み合わせごとに管理されます。容量が2つなら、セッションも2つです。
- 同じ容量に複数のワークスペースがある場合、**有効な最上位ロール**で課金されます。
- ロールが上がると、従来のセッションが日割り計算され、上位ロールのセッションが始まります。ロールの引き下げは、現在のセッションが終了してから適用されます。
- 自動化ジョブ（PowerTable）と計画連携のインスタンス（Infobridge）は、**成功したジョブ1件につき2 CU**です。失敗したジョブは課金されません。
- 関連するFabricワークロード（SQL、OneLake、XMLA）のために、**容量に約30%の余裕**を見込みます。
- セッションの途中で容量を一時停止,削除すると、残りのCU消費量がAzureの請求に加算されます。

**ロールは事前の割り当てではなく、操作に応じて決まります。** 原典ではfabricplanning.ioの説明を、2026年9月12日のLearn資料と照合したとしています。

- アイテムを開く,閲覧する → **Viewer**
- 計画値の入力,変更、承認、書き戻し、PowerTableまたはIntelligence sheetの作成,編集 → **Stakeholder**
- Planning sheetの作成、設計,ルール,書き戻し先の編集 → **Planner**。新しいPlanアイテムの作成者もPlannerになります。
- 2026年8月19日以降は、PowerTableやIntelligenceのレポートを作成しても、Plannerにはなりません。

容量見積もりツール：https://community.fabricplan.com/capacity-pricing/

---

## 4. 書き戻し

サポートされる書き戻し先は、**Fabric SQLデータベース**のみです。書き戻しは、接続先のセマンティックモデルを更新するものではありません。計画データを別途保存します。

4つの形式があります。

- **Long**：セルごとに1行を作成します。
- **Wide**：メジャーごとに1列を作成します。
- **Long with changes** / **Wide with changes**：変更履歴を保存し、変更されたセルだけを扱います。

自動書き戻し、コメントの保存、実行時のメジャー選択、実行時のフィルター、列の検証（空欄の禁止、`Value > 500M`などの数式ルール、検証失敗時の書き戻し停止）、シナリオごとの書き戻し対象の制御に対応します。

注意点として、計画シートの行を削除しても、SQLテーブルの該当行は**削除されません**。

Planアイテムを作成すると、ワークスペース内にFabric SQLデータベースが自動作成され、Planのメタデータが保存されます。これは、自分で設定する書き戻し先とは別のものです。

> [!NOTE]
> **この節も原典時点の説明です。** 特にメタデータのSQLデータベース自動作成については、現行FAQのOneLake保存の説明と差異があります。書き戻し先とアプリの保存先を混同せず、現行照合を参照してください。

---

## 5. 演習で説明しておきたい上限値

> [!IMPORTANT]
> **次の値とRLSの説明は原典時点の記載で、現在の仕様一覧ではありません。** Infobridgeや一括データ入力の上限、RLS/OLS、PowerTableのデータベースレベルRLSについて現行との差異があるため、導入判断には現行照合を使ってください。

| 制限項目 | 原典に記載された値 |
|---|---|
| Planアイテム当たりのシート数 | 25 |
| Planアイテム当たりのビジュアル数 | 50 |
| 書き戻し | 1操作当たり120万セル |
| Infobridgeクエリ | 120万セル（5シート全体で約500万セル） |
| 一括データ入力 | 100万行 |
| PowerTableの並べ替え / Group By / Insight / 検索と置換 / スクロールバー | 500万行 |
| PowerTableのGantt / Resourceレイアウト | 30,000行 |
| ExcelエクスポートのRaw / Labelモード | 2,000万セル / 500万セル |
| 自動化で連鎖するトリガーの深さ | 2階層 |
| 自動化のDBトリガーによる書き戻し | トリガーの種類ごとに10レコード |

ほかの注意点として、ワークスペースやセマンティックモデルの名前を変更すると、いずれもPlanアイテムが動作しなくなります。1つのPlanアイテムに接続できるセマンティックモデルは1つで、後から変更できません。別のソースで計画を作成するには、新しいPlanアイテムが必要です。RLSについては、ロールが割り当てられていないユーザーには、全ロールの**和集合**が表示されます。PowerTableでは接続IDでクエリを実行するため、データベースレベルのRLSは無視されます。

※最後のRLSに関する説明は原版時点の記載です。現在の動作として扱わず、公式資料と開催環境で確認してください。

---

## 6. 公式チュートリアル全12回：演習構成の土台

出典：`learn.microsoft.com/fabric/iq/plan/planning-tutorial/`

### Planning sheets（パート0〜6）

| # | タイトル | 内容 |
|---|---|---|
| 0 | 概要と環境の設定 | pbixのインポート、SQL DBの作成、Planアプリの作成、セマンティックモデルとDBへの接続、最初のシート、画面構成の確認 |
| 1 | 配賦と共同作業 | 前年度の構成比に基づく比例配賦で、トップダウン目標を2,850万米ドルから3,000万米ドルへ変更します。**四半期のロック**で増分をQ3/Q4だけに反映し、ボトムアップの売上計画、セグメントの8%上積み、共同作業用の列、承認フローを扱います。 |
| 2 | Optimizer | 目標の**売上総利益1,250万米ドル**に達するよう、編集可能な入力メジャー（売上成長率%、売上原価）を逆算します。ネイティブ,セマンティックモデルのメジャーは読み取り専用なので、編集可能なコピーが必要です。 |
| 3 | 見通しと書き戻し | 2026年のローリング予測、24か月の実績を基にした統計予測（Predict）、実績到着時の1月の確定、2027年1月までの期間延長、Fabric SQLへの確定値の書き戻しを行います。 |
| 4 | Measure model | セマンティックモデルのメジャーをP&Lの階層に整理します。Best-CaseとCost-Restructuringのシナリオを横に並べて比較します。 |
| 5 | Row model builder | Net Profit → Gross Profit → Net Revenue、COGS、OpExをノードとして接続し、P&Lを一から作成します。 |
| 6 | Cube | Regional Plan、Product Plan、Profitabilityの各シートを作成します。キューブのメジャーでディメンションをまたいで自動配賦し、3つのシートを同期します。 |

### PowerTable（パート7〜8）

| # | タイトル | 内容 |
|---|---|---|
| 7 | PowerTableを使い始める | IT資産データをスプレッドシートから管理されたデータアプリへ移します。DBを作成し、テーブルごとのシート、列の書式,接続、レコードの挿入,更新を設定します。 |
| 8 | 承認,アクセス制御,自動化 | 資産シートの承認フロー、アクセス制御、自動化ジョブを設定します。 |

### Intelligence sheets（パート9〜11）

| # | タイトル | 内容 |
|---|---|---|
| 9 | Intelligence sheetsの概要 | 差異分析チャート、グループ化した折れ線グラフ、KPIカード、マトリックス、日付フィルター、ダッシュボードのヘッダー、コメントを扱います。 |
| 10 | P&LのIntelligence sheet | 計算行と入力行、書式設定、カスタム列、レポートヘッダー、エクスポートを扱います。 |
| 11 | 計画シート,PowerTable,キャンバスの連携 | 計画のシミュレーション、Intelligence sheetへの計画シートの埋め込み、セマンティックモデルと計画を組み合わせたKPI、キャンバスへのPowerTableの埋め込みを扱います。 |

---

## 7. 利用できるサンプルデータ

`microsoft/fabric-samples` → `docs-samples/iq/plan/`から取得します。

| ファイル | サイズ | 用途 |
|---|---|---|
| `Northwind_FMCG.pbix` | 9.3 MB | メインのPlanningチュートリアル用モデルです。**Measures Table**、**Date**、**Fact Transactions**（地域,製品別の売上,原価実績。チュートリアル本文では「Sales Transactions」と呼ばれます）、**Geography**、**P&L Measures**（販売数量、平均販売価格、売上原価の内訳、営業費用などのドライバー）、**P&L Rows**（行として並ぶ損益計算書の項目）、**Product**の7テーブルを含みます。 |
| `planning-tutorial-dataset.pbix` | 9.3 MB | サイズが同じため、チュートリアル用の別名で提供された同じモデルと考えられます。 |
| `Northwind-FMCG-assets-powertable-tutorial.xlsx` | 36 KB | PowerTableの演習に使うIT資産データです。 |
| `region_dimension_pt.xlsx` | 6 KB | PowerTable用の地域ディメンションです。 |
| `gantt-data.csv` | 1 KB | Ganttレイアウトのサンプルです。 |
| `Enterprise Dataset.pbix` | 65 MB | 大規模なモデルです。 |
| `transaction-dataset.pbix` | 44 MB | 大規模なトランザクションモデルです。 |
| `semantic-modeling-sample.pbix` | 6 MB | セマンティックモデリングのサンプルです。 |

**演習設計への示唆：** NASA APIとPythonで合成データを生成するfabric-space-labとは異なり、Fabric PlanningにはMicrosoft提供のサンプルモデルがあります。この演習ではデータ生成の手順が不要で、所要時間を短くできる理由の1つになります。

※ファイルサイズや、同一モデルかどうかに関する推測は原典時点の記録です。ファイルサイズが同じことだけでは、ファイルの同一性を確認したことにはなりません。

---

## 8. fabric-space-labの構成から学べること

引き継ぐ点：

- 架空の会社と役割を設定します。たとえば「ZOSAのリードデータエンジニアとして採用された」という設定にし、モジュールごとにストーリーを進めます。
- 番号付きのモジュール一覧に、扱う内容と所要時間の目安を記載し、冒頭で全体の所要時間を示します。
- 機能の提供状況（GA / Preview）を表にまとめ、プレビュー機能に関する認識のずれを防ぎます。
- リポジトリを`README.md`、`labs/`、`data/`、`notebooks/`、`assets/diagrams/`、`assets/screenshots/`で構成します。
- 「APIキーがなくてもサンプルデータで実施可能」といった、始めやすい代替手段を用意します。
- 前提条件と対象者を明示します。

変更する点：

- 15モジュール,9.5時間ではなく、**6〜8モジュール,約2〜2.5時間**を目指します。
- Microsoft提供のpbixサンプルがあるため、Pythonによるデータ生成は行いません。
- 対象者をデータエンジニアから、**FP&A担当者と、財務部門を支援するデータ専門家**へ変更します。
- **コスト,容量見積もりのモジュール**を追加します。セッション課金は、このワークロードで最も誤解されやすい点なので、脚注ではなく演習の一部として扱います。

---

## 9. この演習で採用した設計

1. **シナリオ：** Northwind FMCGサンプルに架空のHarborlight Provisions Co.を重ね、モデル名やフィールド名を変更しなくても、ストーリーと数字が一致するようにしました。
2. **形式：** fabric-space-labの構成を参考に、番号付きモジュールを持つGitHubリポジトリにしました。
3. **対象範囲：** 計画シート、Optimizer、見通しと書き戻し、P&Lモデル、Intelligenceのキャンバスを基本ルートとします。PowerTableは任意、Infobridgeは作成演習ではなく説明にとどめます。
4. **コストの説明：** 特に誤解されやすいセッション課金を、モジュール00と08の主要テーマとして扱います。

---

## 10. 参考リンク

- 概要：https://learn.microsoft.com/fabric/iq/plan/overview
- 計画シート：https://learn.microsoft.com/fabric/iq/plan/planning-overview
- 前提条件：https://learn.microsoft.com/fabric/iq/plan/overview-prerequisites
- 制限事項：https://learn.microsoft.com/fabric/iq/plan/overview-limitations
- ロール：https://learn.microsoft.com/fabric/iq/plan/overview-roles
- 課金：https://learn.microsoft.com/fabric/iq/plan/resources/billing-fabric-plan
- 書き戻し：https://learn.microsoft.com/fabric/iq/plan/planning-concept-writeback
- 計画の連動：https://learn.microsoft.com/fabric/iq/plan/infobridge-concept-connected-planning
- チュートリアル パート0：https://learn.microsoft.com/fabric/iq/plan/planning-tutorial/planning/tutorial-0-introduction
- サンプル：https://github.com/microsoft/fabric-samples/tree/main/docs-samples/iq/plan
- コミュニティハブ：https://fabricplanning.io
- 容量見積もりツール：https://community.fabricplan.com/capacity-pricing/
- GAの発表：https://community.fabric.microsoft.com/t5/Fabric-Updates-Blog/Bring-Enterprise-planning-to-the-AI-Era-with-Planning-in/ba-p/5326315
