# 日本語版の確認待ち項目

この一覧は日本語版の編集 / 検証用です。正本はREADME, 各Labと講師ガイドのMarkdownです。HTML操作ガイドでは, 独立した行の`<!-- presentation-exclude-start: STABLE-ID -->`と`<!-- presentation-exclude-end: STABLE-ID -->`で囲んだ範囲だけを表示対象から外します。IDは一意で, この文書の`### ID`と1対1に対応します。入れ子にはしません。この一覧自体をHTMLへ取り込んだり, HTMLからリンクしたりしません。

原文欄は編集前の文言をそのまま残します。表や段落に確認済みの観測が混在する場合は, 正本で原因 / 確認待ちの部分だけを独立させています。失敗の観測, 数値, 安全上の注意はHTMLにも残します。Part 1 / 2は手順全体が対象で, その範囲にスクリーンショット参照はありません。その他の除外範囲にも画像参照は含めず, 全578件のスクリーンショット参照と順序を維持します。

## 項目

### FACILITATOR-LAB09-EXTRACTION

- 出典: [講師ガイド / 発展編](FACILITATOR-GUIDE.md#発展編モジュール09追加4560分)
- 原文:

```text
モジュール04で使ったProduct × 月のGross RevenueとForecastを同一Scenario / Plan versionで照合し、UTF-8 CSVをLakehouse Filesへ一時配置します。実機で確認したのは合成CSVを使うPart 3〜5です。実Plan / writebackからの抽出を含むEnd-to-End確認ではありません。
```

- 検証作業: Lab09の実Plan / writeback抽出からPart 3〜5までを同一Snapshotで実行する。
- 受入条件: キー / Scenario / PlanVersion / 値の連続した対応と独立検算を記録すること。それまでは両HTMLとも合成CSVのPart 3〜5だけを実施範囲にする。

### FACILITATOR-LAB09-ERROR-CAUSE

- 出典: [講師ガイド / 発展編](FACILITATOR-GUIDE.md#発展編モジュール09追加4560分)
- 原文:

```text
AgentのQ4 / Q4aは`SQLCandidatesFailedFilterError`となり原因未特定です。
```

- 検証作業: Lab09と同じ合成CSVでエラーを再現し, 製品根拠と最小再現で原因を調査する。
- 受入条件: 原因を独立して説明できること。失敗した観測とQ4cの検算済み結果は両HTMLに維持する。

### README-LAB09-END-TO-END

- 出典: [README.md / アーキテクチャ](../README.md#アーキテクチャ)
- 原文（検証状況の段落内の該当文）:

```text
Part 1〜2の実Plan / writebackからの抽出を含むEnd-to-End確認ではありません。
```

- 検証作業: Lab09 Part 1 / 2で実PlanからSnapshotを抽出し, Part 3〜5まで連続実行する。
- 受入条件: 同一Snapshot / Scenario / PlanVersionの全件対応とWarehouse / Agentの数値一致を記録できること。HTMLには確認済みの合成CSVによるPart 3〜5の範囲を明記すること。

### README-LAB09-ERROR-CAUSE

- 出典: [README.md / アーキテクチャ](../README.md#アーキテクチャ)
- 原文（該当する段落全体）:

```markdown
> **検証状況:** Part 3〜5は同梱の合成CSVを使ってFabricで操作し, Warehouse検算, Lakehouse Delta, Ontology / Graph, Data Agentの一部の質問を確認しました。Part 1〜2の実Plan / writebackからの抽出を含むEnd-to-End確認ではありません。Q4 / Q4aは`SQLCandidatesFailedFilterError`となり, 原因未特定です。実機での確認範囲 / 未確認事項は[Lab09](labs/09-variance-analyst.md)を参照してください。
```

- 検証作業: Lab09のQ4 / Q4aを同じ合成CSVと条件で再現し, 実行内容 / Source / エラーを個人情報のない記録に残す。
- 受入条件: 原因を独立した最小再現と製品の根拠で説明できること。エラーの観測とQ4cの成功を消さず, 原因を推測で補わないこと。

### LAB00-MODEL-CONNECTION

- 出典: [labs/00-prerequisites.md / 事前に把握しておきたい制限](../labs/00-prerequisites.md#事前に把握しておきたい制限)
- 原文:

```markdown
| **Direct LakeおよびDirectQuery**モデル | 原文の固定資格情報,ゲートウェイ必須という説明は、現行の接続方法と照合が必要です。使用するモデルで事前検証してください |
```

- 検証作業: 現行の接続資料と, 演習で使うDirect Lake / DirectQueryモデルの認証 / ゲートウェイ要件をそれぞれ照合する。
- 受入条件: ストレージモード / 接続元 / 認証方法ごとに要件と接続成功を記録し, 原典との違いを明示できること。

### LAB00-TRIAL-DELETION

- 出典: [labs/00-prerequisites.md / 自動的に作成されるもの](../labs/00-prerequisites.md#自動的に作成されるもの)
- 原文:

```markdown
> 原文は、試用版でモジュール07を実施するためにモジュール01のPlanアイテムを削除する方法も挙げています。ただし、削除だけで関連データベースの枠が解放されることは確認できていません。
```

- 検証作業: 所有者の承認を得た破棄可能な環境でPlanの保存先と関連DBを特定し, 削除前後の枠を比較する。
- 受入条件: 対象構成と枠の変化を実測できること。既存の成果物を消す一般手順とせず, 別環境 / 有償容量の安全な選択肢を保持すること。

### LAB09-REAL-PLAN-ROUTE

- 出典: [labs/09-variance-analyst.md / 1. 目的と検証境界](../labs/09-variance-analyst.md#1-目的と検証境界)
- 原文:

```markdown
| **実Planルート** | Part 1〜2で自分のLab04データから完全な比較Snapshotを作り、Part 3以降へ渡す | 手順上の確認項目。Part 1〜2の実Plan / writeback抽出を含む実機End-to-End確認は未実施 |
```

- 検証作業: Part 1 / 2の受入条件を満たした実Plan由来のCSVをPart 3〜5へ渡す。
- 受入条件: 同一Snapshot / Scenario / PlanVersionの全件対応とWarehouse / Agentの数値一致を確認できること。合成CSVの証拠で代用しないこと。

### LAB09-VERIFICATION-BACKLOG

- 出典: [labs/09-variance-analyst.md / 確認済みの範囲](../labs/09-variance-analyst.md#確認済みの範囲)
- 原文（第1文は直前の箇条書きの末尾）:

```markdown
Edge traversalは未確認です。
- **未確認:** 実Plan / writebackからの抽出、Q2、Q5、合計比率だけを尋ねる質問、Q4cの生成SQL表示、`_LH2`のinstructionsがAgent再読込後にも残ること、edge traversal。日本語質問の全パターンや本番利用の適合性も保証しません。
```

- 検証作業: 実Plan抽出, Q2 / Q5, 合計比率の質問, Q4cのSQL, Instructionsの再読込, edge traversalを独立した試験項目として実行する。
- 受入条件: 各項目に入力条件 / 実行結果 / 独立した期待値を残し, 成功した範囲だけを個別に公開できること。日本語全般や本番適合性の包括的な保証に置き換えないこと。

### LAB09-ERROR-CAUSE-SUMMARY

- 出典: [labs/09-variance-analyst.md / 確認済みの範囲](../labs/09-variance-analyst.md#確認済みの範囲)
- 原文:

```markdown
- **失敗の記録:** Q4 / Q4aは`SQLCandidatesFailedFilterError`になりました。原因は特定されていません。複数月を指定する質問全般が失敗するとは結論付けず、同じ失敗を成功例として扱いません。
```

- 検証作業: Q4 / Q4aの失敗条件を最小化して原因候補を個別に比較する。
- 受入条件: 再現可能な根拠で原因を特定すること。HTMLには失敗観測と一般化しない注意を残すこと。

### LAB09-REAL-PLAN-PREPARATION

- 出典: [labs/09-variance-analyst.md / 2つのデータ経路](../labs/09-variance-analyst.md#2つのデータ経路)
- 原文:

```markdown
1. **実Planルート:** Part 1〜2でLab04の保存済みForecastとセマンティックモデルのGross Revenueを同一粒度で抽出し、全件一致を確認してからCSVを用意します。ここは実機でEnd-to-End確認していません。
```

- 検証作業: Lab04の保存状態と元モデルから同一Product / 月の全件を抽出する。
- 受入条件: Part 1 / 2と同じキー / 件数 / 金額の照合証拠がそろい, 抽出上限や欠損がないこと。

### LAB09-PART1-PROCEDURE

- 出典: [labs/09-variance-analyst.md / Part 1](../labs/09-variance-analyst.md#4-part-1実planから比較snapshotを準備する実機未検証)
- 原文（手順全体）:

```markdown
## 4. Part 1：実Planから比較Snapshotを準備する（実機未検証）

**合成サンプルルートではこのPartを飛ばし、Part 3へ進みます。** 以下は実Planを使う場合の安全な準備手順ですが、実Plan / writebackを使った一連の抽出は未検証です。画面や書き戻しスキーマが本書と異なる場合は推測せず停止してください。

1. Lab04のForecast sheetを開き、選択するScenario、期間、`Close Period till`、保存状態を人が決めます。`SnapshotId`と`PlanVersion`を一意に記録します。時間が最も新しいというだけで状態を選びません。
2. Writeback Logsで対象の成功した操作を確認し、`SourceWritebackRunIds`の出典を残します。対象Scenario / Measure / Product / Periodの全行がどの状態を構成するか明確でなければ停止します。
3. Lab04のSQL宛先の実スキーマを読み、Category / Sub Category / Year / Month / Scenario / Measure / Valueに対応する実在列を特定します。`IsLatest`、`PreviousValue`、実行IDなどは実在し、公式の意味と選択範囲での値を確認できた場合のみ使います。
4. 選択した全キーについて現在値が1行ずつ存在することを確認します。履歴行が差分なら履歴を合計して現在値を再構成しません。現在値の全件状態を証明できない場合、承認済みのサポートされた手順で完全なSnapshotを作れるまで停止します。
```

- 検証作業: 承認済みの専用環境で4手順を実施し, 実在列 / writeback履歴の意味 / Snapshotの現在値を確認する。
- 受入条件: 全対象キーに現在値が1行ずつ存在し, Scenario / Measure / Product / Periodと選択したwriteback実行の追跡ができること。既存値を書き換えず, 推測による履歴の再構成をしないこと。

### LAB09-PART2-PROCEDURE

- 出典: [labs/09-variance-analyst.md / Part 2](../labs/09-variance-analyst.md#5-part-2実績--forecastを同じ粒度で照合する実機未検証)
- 原文（手順全体）:

```markdown
## 5. Part 2：実績 / Forecastを同じ粒度で照合する（実機未検証）

1. 元レポートを変更せず、一時レポートまたは承認済みエクスポート経路を用意します。Dataペインで存在を確認した`Product[Category]`、`Product[Sub Category]`、`Date[Year]`と`Date[Month]`または`Date[Year Month]`、`Measures Table[Gross Revenue]`を使います。Month Shortだけでは期間キーにしません。
2. 選択した期間の全件をサマリー済みCSVへ出力します。列の欠落、エクスポート上限、異なる月 / 製品があれば停止し、基になる別メジャーを推測しません。
3. Forecast宛先から確認済みの列だけで同じScenario / Measure / Year / Month / Productの全行を抽出します。計画とモデルで製品キー / 月キーの対応を確定し、`ProductKey`と`PeriodKey`を文字列として作ります。
4. 両方の全件エクスポートで`ProductKey + PeriodKey`ごとに重複がないことを確認し、Full Outer結合でキー集合を比較します。片側だけのキーが1件でもある、行数が一致しない、通貨 / Measure / PeriodStatusが不明なら停止します。欠損行を補完したり0で埋めたりしません。
5. 合成サンプルルートではなく実Planルートを実施する場合、選択したSnapshot / Scenario / PlanVersionについて、各ソースの全行数と一意キー件数、結合後の正の期待件数を組織承認済みの非公開記録に残します。期待件数を0または未記入のままロードしません。
6. 列契約に合わせて15列のUTF-8 CSVを作り、独立して確認した正の`ExpectedRows`はCSVに追加せず非公開の検算記録へ保存します。金額の精度を保ち、PeriodStartがPeriodKeyの月初日であることを確認します。
```

- 検証作業: 全6手順を実Plan由来のデータで実行し, 両ソースの全件数 / 一意キー / 金額 / 期間状態を比較する。
- 受入条件: Full Outer結合の片側だけのキーが0件, 重複0件, 正のExpectedRowsが独立に確定すること。精度を保った15列CSVと非公開の検算記録を確認できること。

### LAB09-WAREHOUSE-CAUSE

- 出典: [labs/09-variance-analyst.md / 8. Part 4](../labs/09-variance-analyst.md#8-part-4ontologyを定義してgraphをmaterializeする)
- 原文:

```text
Warehouse / Lakehouseの変更を同時に行ったため、単独の根本原因は特定されていません。
```

- 検証作業: Warehouse / Lakehouseの変更要素を分離して同じOntology / Agent構成で比較する。
- 受入条件: `Unsupported Datasource`とAgentエラーの原因を独立に特定できること。観測した失敗とLakehouseの実証経路は保持すること。

### LAB09-EDGE-TRAVERSAL

- 出典: [labs/09-variance-analyst.md / 8.6 Graphへ投影する](../labs/09-variance-analyst.md#86-graphへ投影する)
- 原文:

```text
Edge traversalは未検証です。
```

- 検証作業: entity type数の表示とは別に, Product / PeriodからRevenue Observationへの関係を使うクエリを実行する。
- 受入条件: 期待するキー / 関係 / 件数が元Deltaテーブルと一致すること。`nodes 3 / edges 2`だけを証拠にしないこと。

### LAB09-INSTRUCTIONS-PERSISTENCE

- 出典: [labs/09-variance-analyst.md / 9.2 Instructionsを設定する](../labs/09-variance-analyst.md#92-instructionsを設定する)
- 原文:

```text
今回の`_LH2`では再読込後の永続確認は未実施です。
```

- 検証作業: `_LH2`の編集内容を確定後, Agentを閉じて再読込し, Instructionsを比較する。
- 受入条件: 17行 / 856文字の内容が再読込後も一致し, 対象Agentと確認時点を記録できること。

### LAB09-Q3-STANDALONE-PROMPT

- 出典: [labs/09-variance-analyst.md / 9.3 質問して結果を検算する](../labs/09-variance-analyst.md#93-質問して結果を検算する)
- 原文（説明の該当部分と質問文）:

````markdown
単独で再試行するときは下記のようにQ3にも条件をすべて明記してください。この完全なQ3文面自体は個別の新規実行で検証していません。

```text
Snapshot LAB09-SAMPLE-001, Scenario Base, PlanVersion FY26-Workshop-v1, PeriodKey 2026-03, Currency USDで、
Product SNK-NUTSのModelGrossRevenue, PlanForecast, VarianceAmount, VarianceRateを示し、
PlanForecast - ModelGrossRevenueを検算してください。
```
````

- 検証作業: 文脈のない新規チャットでこの文面をそのまま実行する。
- 受入条件: ModelGrossRevenue 0 / PlanForecast 12,500 / VarianceAmount 12,500 / VarianceRate NULLとなり, 同じキーのWarehouse値に一致すること。既存スレッドのQ3成功はHTMLに残すこと。

### LAB09-ERROR-CAUSE-QUESTIONS

- 出典: [labs/09-variance-analyst.md / 9.3 質問して結果を検算する](../labs/09-variance-analyst.md#93-質問して結果を検算する)
- 原文:

```text
原因は特定されていません。
```

- 検証作業: 直前に示すQ4 / Q4aの質問条件を再現し, 集計 / Status / 期間条件を個別に比較する。
- 受入条件: 原因を再現可能な証拠で説明すること。質問文と観測したエラーは原因と切り離して保持すること。

### LAB09-ERROR-CAUSE-RESULTS

- 出典: [labs/09-variance-analyst.md / 9.3 質問して結果を検算する](../labs/09-variance-analyst.md#93-質問して結果を検算する)
- 原文（結果表の2行）:

```markdown
| **Q4 / 複数月をStatus別に行数・合計・率まで質問** | `SQLCandidatesFailedFilterError` | 失敗。原因未特定 |
| **Q4a / 期間別・Status別の行数と合計を質問** | `SQLCandidatesFailedFilterError` | 失敗。原因未特定 |
```

- 検証作業: 結果表と同じ条件のQ4 / Q4aを再実行し, エラーと原因の証拠を別々に記録する。
- 受入条件: 原因を独立検証できること。表の失敗ステータスとエラー文字列はHTMLにも残すこと。

### LAB09-QUESTION-VARIATIONS

- 出典: [labs/09-variance-analyst.md / 9.3 質問して結果を検算する](../labs/09-variance-analyst.md#93-質問して結果を検算する)
- 原文（段落全体）:

```text
Q4 / Q4aの失敗を成功例として記載せず、複数条件を詰め込まずに1期間ずつの単純な合計へ分割する方法を推奨します。ただしその分割方法自体の全パターンは未確認です。3期間をまとめる場合、実証済みなのはPeriodKey別の3つの合計だけを尋ねるQ4cです。全期間の合計比率だけを問う質問や、Q4cの生成SQL表示は未実施です。
```

- 検証作業: 単月への分割, 合計比率だけの質問, Q4cの生成SQL表示を別々に試す。
- 受入条件: 個々の回答とSQLが同じ対象範囲のWarehouse検算に一致すること。実証済みのQ4cの期間別3合計はそのまま残すこと。

### LAB09-ERROR-CAUSE-TROUBLESHOOTING

- 出典: [labs/09-variance-analyst.md / 10. よくある問題と対応](../labs/09-variance-analyst.md#10-よくある問題と対応)
- 原文（該当する表の行）:

```markdown
| Warehouse-bound ontologyで`Unsupported Datasource` | WarehouseはSQL検算用に保ち、OntologyのGraph用sourceにはLakehouse管理Deltaテーブルを使います。単独原因は特定されていません |
| Instancesタブに`doesn't have a table named` | Spark側のdboテーブル存在とBindingを別々に確認し、しばらく待ってから再読込します。原因は未特定で、Instancesタブのエラーを成功 / 失敗の唯一の判定にしません |
| `SQLCandidatesFailedFilterError` | Q4 / Q4aで再現したが原因未特定です。Q4cのように期間ごとの合計だけに分けて試し、毎回Warehouseで検算します。成功を保証しません |
```

- 検証作業: 3種類のエラーを独立に再現し, ソース / binding / 対象テーブル / 質問条件の影響を個別に比較する。
- 受入条件: 各原因を製品資料または最小再現で確認できること。HTMLには観測したエラー, 実証した迂回経路, 検算と安全上の注意を保持すること。
