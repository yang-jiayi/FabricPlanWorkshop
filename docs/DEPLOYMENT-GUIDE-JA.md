# Microsoft Fabric Plan Workshopの配備ガイド

このガイドはAIエージェントの**安全な事前調査と, 承認を得た後の配備支援**の手順です。Fabricへの接続やクラウド変更をこの文書だけで実行するものではありません。READMEにあるプロンプトをGitHub Copilot / OpenAI Codex / Claude Codeのリポジトリ作業セッションへ渡し, 最初は読み取り専用のdry-runから開始してください。

> [!IMPORTANT]
> このリポジトリにはLabのMarkdown / 画像, サンプルデータへの公式配布リンクがありますが, Plan定義, PBIX本体, SQLデータベース定義, 一括配備テンプレートはありません。このGitルートをFabric Gitに接続してもWorkshopは自動構成されません。空のWorkspaceからの初回作成にはFabric上での対話的なPlan作成と検証が必要です。

## 配備方式を選ぶ

| 方式 | 前提 / 自動化できる範囲 / 人が確認すること |
|---|---|
| **A / 空Workspaceから初回構築** | **前提:** 用意済みの空Workspace, 適切な容量 / 権限, Microsoft公式PBIX。Lab07を含む場合は公式XLSXも用意。**自動化:** 文書化されたAPIで対応する作成 / インポート, アイテム一覧, 非同期状態確認。**人が確認:** Planのシート / 数式 / シナリオ / PowerTable設定は, 現行API / 定義形式のサポートを確認できなければ管理画面で作成し, 実値を確認 |
| **B / 検証済みソース環境から昇格** | **前提:** 検証済みソースWorkspaceまたは公式サポート定義, 依存するモデル / SQL, Git統合 / Deployment Pipeline。**自動化:** サポート対象のPlanと依存アイテムを昇格し, Variable Libraryで環境参照を切り替える。**人が確認:** 権限 / 接続資格情報 / 環境変数 / 書き戻し先 / 本人別アクセス / 実データ / 受入条件 |

方式Bは空のターゲットWorkspaceだけでは実行できません。**方式Aで作った空のシェルを, 全Labが構成された成果物として数えないでください。** 自動化可否はアイテム単位に判定し, 未文書化のPlan API / JSON定義は作りません。

## 配備前に集める情報

公開READMEやプロンプトの本文に実際の識別子 / 内部情報を書かないでください。AIセッションに必要な値を渡す場合も, 資格情報やトークンは渡さず, サインインとMFAは本人が公式フローで行います。

| 入力 | 事前確認 |
|---|---|
| Tenant ID / Workspace ID / Capacity ID | 承認された演習テナントの値。WorkspaceのTenantと容量のSKU / Regionが想定通りであること |
| モード | `full-workshop-demo` または `learner-start`。Lab07は全ラボ構成の既定で含める |
| 実行主体 | 委任された本人または組織が承認したサービスプリンシパル。役割と対象スコープを確認し, secretsをソース / チャット / ログへ記録しない |
| 課金承認 | 課金セッションが始まる操作, Capacity / SQL / OneLakeの想定範囲, 承認者。数値の保証としてでなく上限と試算根拠を用意 |
| ソース資産 | 空Workspace方式なら公式PBIX / 任意のXLSX。昇格方式ならソースWorkspace / 定義 / 対応関係 / 依存項目の所有者 |
| 本人別テスト主体 | 閲覧 / 入力 / 承認 / RLSを許可範囲に応じて確認する別ユーザー。管理者での表示を本人別検証に流用しない |

**初回構築**では, 対象Workspaceの全アイテムを配備直前にページングして空であることを確認します。1つでも既存アイテムがある, 別テナント / ID / 容量が見える, または全ページを取得できない場合は停止し, 人に照合を依頼します。既存アイテムを削除して空にしてはいけません。

**中断した実行の再開**は利用者が明示した場合に限ります。組織承認済みの非公開な前回実行記録があり, 同じテナント / Workspace / 容量 / 所有者と作成済みitem IDを照合できること, Workspace全ページの状態が記録の想定ID / 種別 / バインディングと一致し, 無関係なアイテムや差分がないことを確認してください。記録がない / 信頼できない, ID不一致, 想定外のアイテム / 差分, またはページ取得未完了なら停止します。全件が一致する場合は記録上の作成済みIDを再利用し, 完了済みのインポート / 作成を繰り返しません。初回PBIX Importは`nameConflict=Abort`で衝突時に停止します。既存Workspaceを黙って再開扱いにしたり, 削除して空にしたりしません。

## A / 空Workspaceからの初回構築

1. **dry-run:** AIがリポジトリと全Labを読み, 作成予定アイテム, 依存順, 使うAPI / UI, 料金開始の可能性, 必要権限, 自動化できない手順, Lab別受入条件を整理します。この段階は読み取り専用です。
2. **ソース取得:** `Northwind_FMCG.pbix`と任意の`Northwind-FMCG-assets-powertable-tutorial.xlsx`は[Microsoft公式サンプル](../data/README.md)から取得します。顧客データを代わりに入れず, コピーライトと公式利用条件を確認します。
3. **PBIXをインポート:** Power BIの[Import API](https://learn.microsoft.com/en-us/rest/api/power-bi/imports/post-import-in-group)はmultipart/form-dataでPBIXをインポートできます。初回の衝突保護に`nameConflict=Abort`を使い, 対象のPBIX名を`datasetDisplayName`に渡します。元のレポートも演習で使うため`skipReport`を使いません。レスポンスが非同期の場合は完了状態を確認し, レポートとモデルの両方, 表示名, サンプルデータ / フィールドが期待通りに見えることを確認します。
4. **更新資格情報の問題を隠さない:** PBIXのImport後に`Refresh failed due to missing data source credentials`が表示された場合, 成功として握りつぶさず記録し, 更新履歴とモデル / レポートに必要なデータが実際にあるかを管理者が切り分けます。資格情報を推測しません。Power BI APIの認証対象はFabric REST APIと別なので, 資格情報やアクセストークンを表示 / ログ出力しません。
5. **依存アイテムを承認後に構成:** Lab01〜06 / 08のPlanは対応するセマンティックモデルへ接続します。モデルの名前 / Workspace名を変えません。SQL Database作成などは該当するMicrosoft公式手順と権限が確認できた範囲で実行し, 結果を再読み取りします。権限変更は対象と必要性を提示し, 利用者の明示承認がある場合だけ行います。
6. **Plan固有の構成を行う:** Microsoft RESTのCreate Itemの`ItemType`一覧にPlanがあることだけでは, Planning sheet / 数式 / シナリオ / PowerTableのAPIスキーマが文書化済みとはみなしません。現行の[Plan CI/CD手順](https://learn.microsoft.com/en-us/fabric/iq/plan/resources/cicd-planning)または製品UIに手順が存在し, 対象バージョン / アイテムでサポートされることを確認します。確認できない場合は作成者がUIで構成し, AIは手順と確認項目の案内に留まります。
7. **受入表を完了:** 下記のLab00〜08の条件を, 実際のWorkspace / モデル / データ / 権限で確認します。空のPlanや空シートを作っただけで「Workshopを配備」と報告しません。

### 初回構築でのモード

- **`full-workshop-demo` (既定):** 必須のLab00〜06 / 08に加えて, 別Planと別SQL Databaseを使う任意Lab07の構成も含めます。全Labの実体 / 接続 / 設定 / 必要なアクセス確認が完了するまで全体の完了を宣言しません。
- **`learner-start`:** 受講者がLab01から開始できる, Lab00の権限 / 容量確認と承認済みのサンプルPBIX / report / modelのみ準備する部分構成です。未作成のPlan / シート / SQL / PowerTableを明記し, 完全なWorkshop配備と表現しません。Lab07は指定がない限り含めません。

## B / 検証済みソース環境からの昇格

Planの[Git統合 / Deployment Pipeline](https://learn.microsoft.com/en-us/fabric/iq/plan/resources/cicd-planning)を使います。ソースWorkspace, 検証済みのサポート対象Plan定義, セマンティックモデル, Fabric SQLアプリケーションデータベースの依存関係が必要です。ターゲットWorkspaceが空でも, ソースの定義や依存項目の代わりにはなりません。

1. ターゲットとソースの全アイテムを列挙し, `sourceItemId`, アイテム種別, 依存先, 所有者, 環境別設定を対照します。更新 / 再配備ではレビュー済みのsource-target対応と所有対象だけを対象にし, 承認を得てから実行します。サポート対象外アイテム, 不明な差分, 環境違いの接続先があれば停止します。
2. 対象のセマンティックモデルとFabric SQLアプリケーションDBを, 先にまたはPlanと同じ昇格でターゲットに用意します。プライマリPlanの接続先モデルが移行先のIDに対応することを確認します。
3. Variable Libraryで, 移行先ごとの **semantic-model Item Reference** / **writeback Database / Connection Reference** を登録し, 適用するactive value setをPlanの配備より前に選びます。PlanがソースWorkspaceの接続や書き戻しDBを参照していないことを, ターゲット側で読み返して確認します。
4. `__fabric_plan_sys`はPlanで入力 / コメント / 書き戻し / アクセス等のメタデータに使うシステムリソースです。初回配備の際に一度デプロイし, 以後の更新ごとに繰り返しデプロイしません。
5. Deployment PipelineのDeploy Stage Contentは[REST API](https://learn.microsoft.com/en-us/rest/api/fabric/core/deployment-pipelines/deploy-stage-content)で実行できます。`Pipeline.Deploy`スコープ, Pipeline admin, 両WorkspaceのContributorなど, 実行する人 / identityに必要な権限とアイテム別サポートを事前確認します。サービスプリンシパルは対象の全アイテムがその認証方式をサポートする場合に限ります。

概念的なリクエスト形は次のとおりです。実際には組織の認証済みHTTPクライアントを使い, トークンをコマンド履歴 / 画面 / Gitへ出しません。`items`を省略するとPipelineで構成された範囲が対象になるため, 全アイテム対照なしに省略しません。

```http
POST https://api.fabric.microsoft.com/v1/deploymentPipelines/<pipelineId>/deploy
Content-Type: application/json

{
  "sourceStageId": "<sourceStageId>",
  "targetStageId": "<targetStageId>",
  "items": [
    { "sourceItemId": "<verified-source-item-id>", "itemType": "Plan" }
  ]
}
```

応答の`202 Accepted`は投入受付であってデプロイ成功ではありません。APIが返す`Location` / `Retry-After`を使って上限付きで状態をポーリングし, 非同期操作IDは組織が承認したプライベートな運用記録に保存します。最終状態, ターゲット側のアイテム, 接続先, 可視データを確認します。タイムアウト / 失敗時に同じリクエストを無制限に再送しません。

6. 移行後, ターゲットのモデルを更新 / 確認し, ターゲットPlanを開いてシート / 設定 / バインディングを検証します。書き戻し先テーブル名が初期に生成IDになる場合は, 公式手順に沿って期待する名前と宛先を確認 / 必要なら変更します。オート書き戻しを有効化する前に, 承認した対象へ手動書き戻しを1回行い保存の基準を確立します。
7. ソース側の書き戻し実行ログはターゲットへ移行しません。過去の承認や実行履歴が新環境に引き継がれたと主張せず, 必要な受入 / 運用記録を新規に作ります。運用中のPlan / セマンティックモデル / Workspaceを名前変更しないでください。

## Lab00〜08の受入表

この表は**受入条件の枠**です。配備の成功結果を前もって断定しません。実行者は各行の結果を承認済みのプライベート運用記録へ書き, 未確認 / 手動対応はそのまま残します。既定の期待値, 初期予算, 既存データ, 元レポートを変更しません。

| Lab | 必要な構成 / 確認内容 | 完了とみなす条件 |
|---|---|---|
| **00 / 事前準備** | 演習専用Workspace, 容量 / Region, Tenant settings, XMLA, 作成 / モデル接続担当の権限, 課金者 / 上限。Lab08で別ユーザーを使うなら事前に承認済みIDを用意 | 容量 / 設定が読み返され, 作成者と参加者の権限を区別。費用開始条件と未確認項目に責任者がいる。設定変更は実際に承認 / 適用された範囲だけ記録 |
| **01 / 環境と最初のシート** | Northwind PBIXの元reportとsemantic model, 主Plan, 接続先Item Reference, 初期Planning sheet | Import後にレポートとモデル両方が開く。主Planが期待するモデルに接続し, Lab01のシートに指定フィールド / 実績が現れる。名前変更なし |
| **02 / 配賦と共同作業** | 主Planの配賦シート, 計画系列, 必要なコメント / 承認列, 対象の編集 / レビューユーザー | 元の初期値を維持した状態で配賦 / 入力 / ロック / コメント / 承認経路をUIで確認。ユーザーごとの許可 / 拒否はそれぞれの実IDで確認し, 認証 / 通知まで確認した範囲を明記 |
| **03 / Optimizer** | 主PlanのGross Profit用シート, 元系列からのコピー / 編集系列, Optimizer入力 / 制約 / シナリオ | コピー値と元系列が別物であること, 変更対象が元シートへ同期されないことを確認。目標 / 制約 / 出力を記録し, 配備で既定の値を変更しない |
| **04 / Forecastと書き戻し** | 見通しシート, ローリング期間 / 予測設定, ターゲットFabric SQL DB / Connection Reference, 保存テーブル | 対象Plan / シナリオ / 実行のログとSQL側の表 / 代表値を照合。許可された手動書き戻しの基準を確立。**元のsemantic model / reportは書き戻しだけでは更新されない** |
| **05 / P&Lモデルとシナリオ** | 主Planのメジャー / 行モデル, 参照階層, シナリオ | 期待するテーブル / 階層 / 集計粒度と数値の定義を個別に確認。単純平均 / 数量加重や控除の符号など教材が注意する範囲を隠さず, 完全な会計モデルとして扱わない |
| **06 / Intelligence Canvas** | 主PlanのIntelligence sheet / canvas, モデル系列, From Sheets参照, 必要な埋め込みシート | 実績と入力値がどの系列から来るかを識別し, 許可された試験入力を戻しても元モデルの値と混同しない。参照 / コピーの設定を確認 |
| **07 / PowerTable (任意)** | 主Planとは別のPowerTable専用Plan, 専用SQL DB, 公式XLSX, Forms / approval / access controls / automations | XLSXの必要なテーブル, フォーム項目, 自動化の対象 / キー, ポリシーを確認。申請 / 承認 / RLSは各許可ユーザー本人で確認し, 初期データを保全 |
| **08 / SizingとGovernance** | 容量試算, 課金ロール, モデルRLS, Lab07を含むならData Input上限 / 役割設計 | 実機の容量 / 認可テストと想定を区別する。権限のないユーザーを推測で一般化しない。地域, テナント, UIごとの制限 / 未確認事項に担当者を割り当て |

## 制限と運用上の注意

- [Planning CI/CD](https://learn.microsoft.com/en-us/fabric/iq/plan/resources/cicd-planning)に記載された**現行のサポート対象**だけを使います。古いPlanning Plan参照は, 2026年8月以前のものを新しい運用に載せる前にGit上の正規化 / コミットが必要となる場合があります。
- Planningの上限としてPlan当たり最大25 sheets / 50 visualsが案内されています。[Data Inputが100件あるPlanのPipeline配備には失敗する既知の制限があります](https://learn.microsoft.com/en-us/fabric/iq/plan/overview-limitations)。実際の対象数と最新の既知の制限を確認します。WorkspaceレベルのPrivate Link非対応, 個別item / identity権限も別途確認します。
- 現行のPlanning CI/CDではサービスプリンシパルを使ったアプリケーションデータベースの作成もサポートされています。これを一般のREST Create Item操作へ拡張解釈せず, Pipeline / アイテム / identityごとの公式サポート範囲と必要権限を確認します。
- 既知の制約やAPIの対応範囲は変わります。Create ItemにPlanのItemTypeがあること, または他のFabricアイテム向けにdefinition APIがあることだけを根拠に, 未公開のPlan固有RESTエンドポイントやJSONを作りません。
- 別のモデル / writeback DBへのバインド, 権限 / 承認者の割当, Capacity / SQL / OneLakeの課金, import / deploymentのいずれも事前確認します。アイテムが作成されたことはアクセス制御の確認ではありません。
- 更新するたび, 全ページのアイテム差分と所有IDを照合します。既存アイテムに競合したら停止し, 上書き / 名前変更 / 削除で隠しません。失敗時は今回作成したIDだけを一覧化し, クリーンアップも個別に明示承認を得ます。Workspace全体を失敗時に削除しません。
- 配備ログ, 証拠画像, 共有画面からトークン / 資格情報 / Tenant URL / 顧客データを除き, publicリポジトリや公開プロンプトへ保存しません。Fabricが未接続なら成功を主張しません。
- 容量停止 / 一時停止, Plan / DB /アイテムの削除でセッション課金が消えると想定しません。計画 / SQL / OneLakeの費用を分け, 実テナントのBilling / Capacity Metricsと管理者の条件で確認します。

## 公式資料

- [Fabric PlanningのGit統合とCI/CD](https://learn.microsoft.com/en-us/fabric/iq/plan/resources/cicd-planning)
- [Planningの既知の制限](https://learn.microsoft.com/en-us/fabric/iq/plan/overview-limitations)
- [Fabric Create Item API](https://learn.microsoft.com/en-us/rest/api/fabric/core/items/create-item)
- [Fabric Item Management API対応範囲](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/item-management-overview)
- [Fabric item definition API対応範囲](https://learn.microsoft.com/en-us/rest/api/fabric/articles/item-management/definitions/item-definition-overview)
- [Deployment Pipelineのコンテンツ昇格API](https://learn.microsoft.com/en-us/rest/api/fabric/core/deployment-pipelines/deploy-stage-content)
- [Power BIグループへのPBIXインポートAPI](https://learn.microsoft.com/en-us/rest/api/power-bi/imports/post-import-in-group)
