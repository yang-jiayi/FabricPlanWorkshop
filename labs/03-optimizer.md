# モジュール 03：Optimizer

**所要時間の目安：** 15分<br>
**このモジュールで作成するもの：** 売上総利益シート。Fabricで、売上総利益1,250万ドルを達成する売上高と売上原価の組み合わせを逆算します。

---

## このモジュールの位置づけ

売上目標は3,000万ドルです。経営陣は同時に**売上総利益1,250万ドル**も求めていますが、この2つの目標が両立するかは、まだ分かりません。

> [!IMPORTANT]
> **この演習の目的は粗利目標の達成です。** 入力に使うのは、モジュール02のボトムアップの `2026 Sales Plan` であり、別列の3,000万ドルの `2026 Target` ではありません。粗利1,250万ドルを達成しても、売上3,000万ドルとの同時達成を意味しません。両方を目指す場合は、売上目標を制約に加えるなど、条件を設計します。

従来なら、売上を少し増やし、売上原価（COGS）を少し減らし、再計算する、といった試行錯誤を繰り返していたかもしれません。Optimizer は、その組み合わせの探索を支援します。

### Optimizer の仕組み

Optimizer は、**複数変数によるゴールシーク**です。数式を変形して一度で答えを出すのではなく、反復計算で解を探すソルバーです。1回の反復では、次の処理を行います。

1. 各入力値を仮に設定します。
2. 結果のメジャーを再計算します。
3. 結果を目標と比較します。
4. 入力値を調整し、同じ処理を繰り返します。

結果が目標の許容範囲に収まるか、反復回数の上限に達するまで、この処理を続けます。そのため、2つの入力の調整割合を事前に決めることはできません。また、同じ目標を達成する組み合わせが複数存在する場合もあります。

次の3つを用意する必要があります。

| 要素 | このモジュールで使うもの |
|---|---|
| **独立変数：** 変更を許可する入力 | 手順2で編集可能なコピーを作成する `Sales Plan` と `COGS` |
| **従属メジャー：** 解を求める対象の数式メジャー | 手順3で作成する `Gross Profit` |
| **目的：** 指定値の達成、最大化、または最小化 | 目標値 `12.5m` |

動作モードは2つあります。**Target-based** は指定した数値を達成する入力を探すモードで、この演習で使います。**Direction-based** は最大化,最小化を行うモードで、「この制約を守りながら、利益をどこまで高められるか」といった検討に使えます。

この例以外にも、売上目標に必要な販売数量と価格、予算に収めるための費目別の削減額、目標現金残高を確保するための回収,支払条件の調整などに応用できます。

---

## 手順1：売上総利益シートを作成する

1. **Home** リボンで **New Planning Sheet** を選択します。未保存の変更について **Confirm Action** が表示された場合は、**Save and Proceed** を選択し、保存が完了するまで待ちます。名前を `Gross Profit` にして **Create** を選択します。

   ![New Planning SheetのNameにGross Profitを入力した画面](../assets/screenshots/lab03/01-gross-profit-create.png)

   ![Explorerが2シートとなり、Gross Profitの空のRows,Columns,Valuesが表示された画面](../assets/screenshots/lab03/02-gross-profit-created.png)


2. 次のフィールドを割り当てます。**Values には、異なるソースから2つのメジャーを設定します。**

   | フィールド | 値 | ソース |
   |---|---|---|
   | **Rows** | *Region* → *Category* → *Sub Category* | *Geography*、続いて *Product* |
   | **Columns** | *Year* → *Quarter* → *Month Short* | *Date* |
   | **Values**（1つ目） | *2026 Sales Plan* | **From Sheets** → *Plan Intro* |
   | **Values**（2つ目） | *2025 COGS* | *Measures Table* |

   **Data** ペインから **Fields** の **Rows / Columns / Values** へ各フィールドを直接ドラッグします。**From Sheets** を展開し、その中の **Plan Intro** を開くと、モジュール02で作成した **2026 Target** と **2026 Sales Plan** が表示されます。ここでは **2026 Sales Plan** を選びます。続けて **Measures Table** を展開し、**2025 COGS** を **Values** へ追加します。

   ![From SheetsのPlan Introを展開し、2026 Targetと2026 Sales Planが並んだ画面](../assets/screenshots/lab03/09-from-sheets-options.png)

   ![2026 Sales Planの割り当て直後。ValuesのSum of 2026...と参照元のチェックを確認した画面](../assets/screenshots/lab03/10-sales-from-sheets.png)


   <details>
   <summary>行,列の各フィールドの割り当て画面</summary>

   ![GeographyのRegionをRowsへ割り当てた画面](../assets/screenshots/lab03/03-region-assigned.png)

   ![ProductのCategoryをRowsの2段目へ割り当てた画面](../assets/screenshots/lab03/04-category-assigned.png)

   ![RowsがRegion,Category,Sub Categoryの順になった画面](../assets/screenshots/lab03/05-rows-assigned.png)

   ![DateのYearをColumnsへ割り当てた画面](../assets/screenshots/lab03/06-year-assigned.png)

   ![DateのQuarterをColumnsの2段目へ割り当てた画面](../assets/screenshots/lab03/07-quarter-assigned.png)

   ![ColumnsがYear,Quarter,Month Shortの順になった画面](../assets/screenshots/lab03/08-columns-assigned.png)

   </details>

   > **Failed to refresh data after blend update** が表示された場合は、表示が戻るまで先へ進まず、参照元,フィールド配置,エラー内容を確認してください。

   ![2025 COGS追加直後、更新エラーとProcessing Dataが表示された途中の画面](../assets/screenshots/lab03/11-sales-and-cogs-assigned.png)

3. **Values** フィールド内の **Sum of 2026 Sales Plan** をダブルクリックします。インライン入力欄を `2026 Sales Plan` に置き換え、**Enter** キーで確定します。変更するのは、このシートでの参照メジャーの表示名です。

   ![Valuesのインライン入力欄で参照メジャー名を2026 Sales Planへ変更中の画面](../assets/screenshots/lab03/12-rename-source-measure.png)

   サンプルデータでは、**2025** のAll行に売上約 **26.10 in Millions**、原価約 **14,166.31 in Thousands** が表示されます。コピー列の **Sales Plan** は次の手順で作成します。

> [!TIP]
> **From Sheets** を使うと、同じ Plan アイテム内の計画シート同士をつなげられます。モジュール02で作成した販売計画を、このシートの入力として参照できます。元のシートを変更すると、こちらにも反映されるため、コピー＆ペーストや版の不一致を避けられます。

## 手順2：編集可能な入力列を作成する

Optimizer には、値の変更を許可する列が必要です。別のシートやセマンティックモデルから取得したメジャーは、読み取り専用です。

1. **Planning** リボンで **Number** → **Copy from another series** → **2026 Sales Plan** を選択します。

   ![NumberのCopy from another seriesに2026 Sales Planと2025 COGSが並び、グリッドにも両列の値が表示された画面](../assets/screenshots/lab03/13-copy-sales-menu.png)

   **Save changes to proceed** が表示された場合は、**Save and continue** を選択し、保存完了後にコピー設定が開くまで待ちます。シート切り替え時には **Save and Proceed** と表示されることがあります。

   ![コピー前にSave changes to proceedが表示され、Save and continueで保存を求められた画面](../assets/screenshots/lab03/14-save-before-copy.png)

   **Title の既存の文字列を全選択して削除**し、`Sales Plan` だけを入力します。**Visual Measure / Number / Column aggregation type：Sum / Row aggregation type：Sum / Distribute parent value to children：チェックあり**を確認して **Create** を選択します。

   ![Sales PlanのTitleとVisual Measure,Number,Sum/Sum,親値配賦を確認したコピー設定](../assets/screenshots/lab03/15-sales-copy-settings.png)

   ![参照元2列に加え、編集可能なSales Planが追加され、Allが26.10Mと表示された画面](../assets/screenshots/lab03/16-sales-copy-created.png)

2. **Number** → **Copy from another series** → **2025 COGS** を選択します。Title の既存の文字列を削除して `COGS` と入力し、同じ **Visual Measure / Number / Sum / Sum / 親値配賦あり**を確認して **Create** を選択します。

   ![COGSのコピー設定。Title COGSと集計,配賦設定を確認した画面](../assets/screenshots/lab03/17-cogs-copy-settings.png)

> [!NOTE]
> **Title** には自動生成された名前が入っています。入力前に削除してください。その他の設定は、[モジュール02](02-allocation-and-collaboration.md)で説明した既定値のままにします。

2つの調整対象について、編集可能なコピーができました。元のメジャーは、後で比較するための基準として残ります。この比較が、モジュールの最後に重要になります。

**次に進む前に確認します。** グリッドには、次の**4つ**のメジャー列があるはずです。

| 列 | 元データ | 編集可否 |
|---|---|---|
| 2026 Sales Plan | From Sheets、Plan Intro | 編集不可 |
| 2025 COGS | Measures Table | 編集不可 |
| **Sales Plan** | 自分で作成したコピー | **編集可能** |
| **COGS** | 自分で作成したコピー | **編集可能** |

![元の参照列と編集可能なコピーを合わせて4列となり、Allの売上26.10M,原価14,166.31Kがそれぞれ一致した画面](../assets/screenshots/lab03/18-four-series-stable.png)

サンプルデータでは、All行の元の **2026 Sales Plan** とコピーの **Sales Plan** はどちらも約 **26.10M**、元の **2025 COGS** とコピーの **COGS** はどちらも約 **14,166.31K** です。編集バーで細かい桁を確認する場合は、値を変更せず **Escape** で閉じます。

![Sales Planの年間総計を開き、編集バー26095900.2404を読み取った画面](../assets/screenshots/lab03/19-copy-sales-baseline-precision.png)

サンプルデータでは、COGSの年間総計は **14166310.36** です。値を変更せず **Escape** で閉じます。

![コピーCOGSの年間総計を開き、編集バー14166310.36を読み取った画面。後続で作成したGross Profit列も表示](../assets/screenshots/lab03/28-copy-cogs-baseline-precision.png)

2列しかない場合は、手順2の操作が反映されていません。このままでは、手順3の数式が必要な列を参照できません。

## 手順3：売上総利益を計算する

1. **Planning** リボンで **Formula** を選択します。**Formula Measure** ペインが開きます。今回の初期値は、Titleが **New Measure**、**Visual Measure / Number**、**Column aggregation type：Sum**、**Row aggregation type：Formula** でした。

   ![Formula Measureを開いた初期設定。列集計がSum、行集計がFormulaであることを確認](../assets/screenshots/lab03/20-formula-defaults.png)
2. 次のように設定します。

   | フィールド | 値 | 補足 |
   |---|---|---|
   | **Title** | `Gross Profit` | 既存の名前を削除してから入力します |
   | **Insert as** | Visual Measure | 既定値のままで、この演習に適しています |
   | **Data type** | Number | 既定値です |
   | **Formula** | `[Sales Plan] - [COGS]` | **References** から編集可能な **Sales Plan** と **COGS** を選び、半角の ` - ` でつなぎます |
   | **Column aggregation type** | **Formula** | **既定値は Sum です。必ず変更してください** |
   | **Row aggregation type** | Formula | 既定ですでにこの値になっています |

   **Column aggregation type** のドロップダウンを開き、**Sum** から **Formula** へ変更します。

   ![列集計のドロップダウンにFormulaがあり、初期選択はSumであることを確認した画面](../assets/screenshots/lab03/21-column-aggregation-options.png)


   ![Sの入力で開いたReferences候補に2026 Sales PlanとSales Planが並んだ画面](../assets/screenshots/lab03/23-formula-reference-candidates.png)

   ![減算演算子に続けてCを入力し、2025 COGSとCOGSの候補が表示された画面](../assets/screenshots/lab03/24-formula-cogs-reference.png)

   表示式が **`[Sales Plan] - [COGS]`**、列,行の集計がどちらも **Formula** であることを確認して **Create** を選択します。

   ![Referencesから選んだ表示式と、列,行ともFormulaになった最終設定](../assets/screenshots/lab03/25-formula-references-configured.png)

   作成後もペインが残り、ボタンが **Create** から **Update** に変わる場合があります。グリッドに新しい **Gross Profit** 列と計算結果が追加されたら、ペイン右上の **×** で閉じます。ペインが残っていることだけを理由に、Createを繰り返さないでください。

   ![Gross Profit列の作成後、ペインは編集状態のUpdateとなり、All11,929.59Kが表示された画面](../assets/screenshots/lab03/26-formula-created-update-pane.png)

   ![ペインを閉じ、元列2つ,入力コピー2つ,Gross Profitの5列を表示した画面](../assets/screenshots/lab03/27-gross-profit-result.png)

   > **Parse error** が表示された場合は、式欄を消して **References** から編集可能な2つの列を選び直します。見た目が同じ式でも、参照候補から選択して列が設定されたことを確認してください。

   ![Referencesから列を選択せず数式を入力したときに表示されるParse error](../assets/screenshots/lab03/22-formula-typed-syntax-error.png)

> [!TIP]
> **Formula** ボックスで入力を始めると、2つのタブを持つ候補一覧が表示されます。**References** には、このシートの *2026 Sales Plan* などの列に加え、*2025*、*GrandTotal*、*Category*、*Month Short*、*Quarter* などのディメンションメンバーが並びます。**Functions** には、組み込み関数が表示されます。
>
> **References** から実在する列を選択します。候補から選ぶことで、似た名前の元列とコピー列を区別できます。展開アイコンが表示される場合は、大きなエディターで式を編集できます。

> [!IMPORTANT]
> **Column aggregation の既定値は Sum です。Formula に変更してください。** Row aggregation は既定で Formula になっているため、特に列側の設定に注意します。
>
> Sum のままにすると、四半期や総計では各階層で `[Sales Plan] - [COGS]` を再計算せず、子の値を合計します。単純な引き算では合計が正しく見えることがあり、見落としやすい点です。同じ設定ミスを利益率や比率の行で起こすと、不適切な集計結果になります。

> [!IMPORTANT]
> **元のメジャーではなく、編集可能なコピーを参照してください。** 候補には両方が表示され、名前も似ています。
>
> | 選択するもの | 選択しないもの |
> |---|---|
> | `Sales Plan`：手順2で作成したコピー | `2026 Sales Plan`：読み取り専用の元データ |
> | `COGS`：手順2で作成したコピー | `2025 COGS`：セマンティックモデルのメジャー |
>
> Optimizer が調整できるのは、編集可能なデータ入力列だけです。数式が元のメジャーを参照していると、調整対象がなくなります。元の2列は、最後に比較するため、変更せずに保持する列です。

3. **Planning** リボンの **Totals** を開き、**Column Grand Total** のドロップダウンを **Off** から **Left** に変更します。

   ![TotalsのColumn Grand Totalが初期値Offになっている画面](../assets/screenshots/lab03/29-totals-off.png)

   ![Column Grand TotalのLeft,Right,OffからLeftを選ぶ画面](../assets/screenshots/lab03/30-grand-total-left-option.png)

   続いて、*Americas* の**行ラベルを右クリック**します。**Collapse** にポインターを合わせ、サブメニューの **Specific Level** ドロップダウンから **Category** を選択します。

   ![行メニューのCollapseからSpecific Levelを開き、Categoryを選ぶ画面](../assets/screenshots/lab03/31-category-level-options.png)

   ![Categoryを選択した後、各カテゴリ行が＋アイコン付きに折りたたまれた画面。コンテキストメニューは開いた状態](../assets/screenshots/lab03/32-category-collapsed-result.png)

   **Grand Total** と **2025** の2つのグループに、元列2つ,コピー2つ,粗利の5系列が表示されます。サンプルデータでのAll行の粗利は約 **11,929.59K** です。

> [!NOTE]
> Sales Plan が *in Millions*（100万単位）、COGS が *in Thousands*（1,000単位）など、列によって表示単位が異なる場合があります。これは表示形式の違いです。数式は元の値に対して計算されるため、表示値同士をそのまま減算せず、元の単位を考慮します。

次に進む前に、**All** 行のGross Profitを控えてください。サンプルデータの例では、売上 **26,095,900.2404** − COGS **14,166,310.36** ＝ Gross Profit **11,929,589.8804** です。千単位,小数第2位では **11,929.59K**、目標1,250万ドルとの差は **570,410.1196** です。

原典が紹介する **12,144.89 thousands**、目標との差約**35.5万ドル（$355K）**は、モジュール02で販売計画をさらに増やした場合の条件付き例です。現在の入力値と区別してください。

> [!TIP]
> **表示される数値は、入力計画によって異なります。** 以下はサンプルデータでの実行例です。Gross Profitが1,250万ドルの目標に近づくために、2つの入力値がどう変わるかを確認してください。

次の2点で、数式の設定が正しいことを確認します。

- シートのタイトルに *2026 Sales Plan, 2025 COGS, Sales Plan, COGS, Gross Profit* の5列が並んでいます。
- 各行の Gross Profit が、その行の Sales Plan から COGS を引いた値になっています。サンプルデータではAll行の粗利は **11,929,589.8804**、千単位,小数第2位では **11,929.59K** です。百万単位と千単位の表示値を、そのまま引かないでください。

## 手順4：Optimizer を実行する

Optimizer は、**Objective & Variables**、**Add Constraints**、**Output** の3段階のウィザードです。

1. **All** 行の **Grand Total** グループにある **Gross Profit** セルを選択し、**Planning** リボンで **Optimize** を選択します。有効な対象セルを選択するまでは、このコマンドは灰色で表示され、選択できません。

   ![OptimizerのObjectiveとTarget Valueの初期設定画面](../assets/screenshots/lab03/33-optimizer-objective-initial.png)
2. **Objective & Variables** で、**Objective** を `Target`、**Target Value** を `12.5m` に設定します。

   その下に、計算対象として **GrandTotal** と **Gross Profit** が表示されることを確認します。必要に応じて **Show Formula** を展開し、式を確認します。

3. **Variables to Update** の **Choose Series** ドロップダウンを開き、`Sales Plan` と `COGS` の両方を選択します。少なくとも1つの系列を選択するまでは、**Next** は有効になりません。

   ![実行時のTarget12.5mと、Choose SeriesにCOGS,Sales Planの候補が表示された画面](../assets/screenshots/lab03/34-optimizer-variable-options.png)

   ![COGSとSales Planの両方にチェックを付け、Nextが有効になった設定](../assets/screenshots/lab03/35-optimizer-configured.png)
4. **Next** を選択します。
5. **Add Constraints** で **No Constraints Added** を確認します。この基本演習では制約を追加せず、**Run** を1回選択します。

   ![Add ConstraintsのNo Constraints Addedを確認し、Runで実行する画面](../assets/screenshots/lab03/36-optimizer-no-constraints.png)
6. **Output** で、**Target Value** が12.50mであることと、実行の状態,**Achieved** の値を確認します。Toleranceが0.1%なら、目標に対する許容差は12,500ドルで、達成値の算術上の範囲は12,487,500〜12,512,500です。緑のチェックなどの状態表示に加え、実際の設定と元の精度の値で確認してください。表示が必ず12.50mに丸められるとは限りません。隣の **Variables** パネルには、ソルバーが求めた入力値が表示されます。
   ![OutputでTarget Value,Achievedとも12.50m、入力候補と既定パラメーターを確認した画面](../assets/screenshots/lab03/37-optimizer-output.png)

   サンプルデータでの実行例では、**Target Value：12.50m / Achieved：12.50m**、入力候補は **Sales Plan：約26.38m / COGS：約13.88m** です。表示値は百万単位,小数2桁の例です。許容差と実行状態も確認します。

7. 設定と結果を確認してから **Apply** を1回選択します。サンプルデータでの例では、**Sales Plan** は約 **26.38M**、**COGS** は約 **13,881.11K**、**Gross Profit** は約 **12,500.00K** です。

   ![Apply後のSales Plan編集バー26381105.29986と、変更されたコピー列,粗利。Saving valuesは途中表示](../assets/screenshots/lab03/38-optimized-sales-precision.png)

   ![Apply後のCOGS編集バー13881105.29986と、Allの粗利12,500.00Kを確認した画面](../assets/screenshots/lab03/39-optimized-cogs-precision.png)

   ![編集欄を閉じた適用後のシート。Grand Totalの粗利先頭は配賦メニューに隠れ、非編集バーはCOGS13881105.299862](../assets/screenshots/lab03/40-optimized-result.png)

   入力値を確認する場合は、コピー列の編集バーを読み取った後 **Escape** で閉じ、値を変更,再確定しないようにします。保存と再読み込みは別に行います。

右側の **Set Parameters** パネルには、調整用の3つの設定があります。既定値は **Strategy** が *Balanced*、**Tolerance** が *Standard (0.1%)*、**Iterations** が *Standard (200 tries)* です。その下に **Re-Run** ボタンがあります。目標に到達しない場合を除き、既定値のままで構いません。変更が必要な場合の考え方は、このモジュールの後半で説明します。

> [!NOTE]
> **Choose Series** に入力系列が表示されない場合は、手順2で編集可能なコピーを作成したか確認します。**Standard (200 tries)** は設定上の反復回数の上限であり、実際に200回反復することを意味しません。

## 手順5：何が変わったかを確認する

1. 元の **2026 Sales Plan** と **2025 COGS** が表示されていることを確認します。非表示の場合は、**Planning** リボンの **Show Columns** から表示します。

   元の総計セルをそれぞれ**シングルクリック**し、読み取り専用の数式バーで最適化前の値を確認します。サンプルデータでは売上 **26095900.2404**、COGS **14166310.36** です。

   ![最適化後も元の2026 Sales Planの年額26095900.2404が数式バーに表示された画面](../assets/screenshots/lab03/41-source-sales-retained-after-optimize.png)

   ![元の2025 COGSの年額14166310.36も保持され、コピー列と粗利だけ変わっている画面](../assets/screenshots/lab03/42-source-cogs-retained-after-optimize.png)

   ![Show Columnsで元の2026 Sales Planと2025 COGSがチェック済みであることを確認した画面](../assets/screenshots/lab03/45-show-columns-checked.png)

   コピー列では、セルを選択して編集後の売上 **26381105.299862**、原価 **13881105.299862** を確認できます。表示される桁数はUIによって異なります。

   ![Sales Planを選択し、非編集時の数式バーに26381105.299862が表示された画面](../assets/screenshots/lab03/43-optimized-sales-selected-full.png)

   ![COGSを選択し、非編集時の数式バーに13881105.299862が表示された画面](../assets/screenshots/lab03/44-optimized-cogs-selected-full-correct.png)

   次の表は、このサンプルデータにおける最適化前後の値の例です。

   | 対象 | 最適化前 | Apply後の例 | 変化量 |
   |---|---:|---:|---:|
   | Sales Plan | 26095900.2404 | 26381105.299862 | +285205.059462 |
   | COGS | 14166310.36 | 13881105.299862 | −285205.060138 |
   | 差から計算したGross Profit | 11929589.8804 | 12500000.000000 | +570410.119600 |

   サンプルデータのGross Profitは **12,500,000** です。目標12,500,000に対する0.1%の許容範囲 **12,487,500〜12,512,500** に入ります。

元の列と最適化後の列を横に並べて比較できます。

このサンプルデータの例では、売上を約28.5万ドル増やし、原価を約28.5万ドル減らす提案です。具体的な金額を使って、担当部門が実行できる条件かを検討します。

<details>
<summary>原典の条件付き算術例</summary>

次の表は**原典の条件付き算術例**です。売上総利益約1,214万ドルから約35.5万ドルの差額を埋める計算例であり、ソルバーが必ずこの値を返すわけではありません。

| 調整対象 | 変更前 | 変更後 | 変化量 |
|---|---|---|---|
| Sales Plan | $26,311.20K | **$26,488.75K** | 約+$177.55K |
| COGS | $14,166.31K | **$13,988.75K** | 約−$177.56K |
| **Gross Profit** | $12,144.89K | **$12,500.00K** | **約+$355.11K** |

> [!NOTE]
> **原典の「売上増+$179K」は他の数値と厳密には一致しません。** COGSを13,988.75K、粗利を12,500.00Kとする場合、売上は26,488.75Kです。上表は算術上の条件付き例で、Optimizerの出力を保証するものではありません。

この計算例では、Gross Profitは厳密に12,500.00Kになります。実際の実行結果は、設定した許容差の範囲で評価します。

この条件付きの計算例では、改善額が売上増と原価減におおむね半分ずつ分かれます。実際のソルバーが常に50対50に配分するというルールではありません。モジュール02の計画の結果によっても数値は変わります。ここでは、売上を少し増やし、原価を少し下げることで、売上総利益が目標に到達するという関係を確認してください。

このように具体化すると、経営陣との議論も変わります。「売上を5%伸ばす」という抽象的な依頼ではなく、この条件付きの計算例なら、**売上を約17.8万ドル増やし、原価を約17.8万ドル削減する**という、担当者を決めて検討できる数値になります。実行可能性は、業務の制約に照らして別途確認します。

> [!NOTE]
> 元の画面例ではSales Planが100万単位,小数点以下2桁で表示され、26.49は詳細な値を丸めたものでした。原典の条件付き計算例の表では比較しやすいよう千単位,小数点以下2桁にそろえています。表示値だけの引き算と、元の精度の数式結果には差が出ることがあります。百万単位,小数2桁なら表示丸めの半幅は5,000ドルなので、実際の照合では元の値を確認してください。

</details>

### 総計の調整が明細まで反映される

All 行だけでなく、地域,カテゴリ,サブカテゴリも確認します。**Apply後の同じシートに並ぶ元の2025 COGSとコピーCOGS**を選択し、値を比較します。次の値はサンプルデータでの例です。

| 行 | 元の2025 COGS | Apply後のコピーCOGS | 削減率の例 |
|---|---:|---:|---:|
| All | 14166310.36 | 13881105.299862 | 2.013263% |
| Americas | 3967101.81 | 3887233.624033 | 2.013263% |
| Americas → Beverages | 886785.31 | 868931.991017 | 2.013263% |
| Americas → Personal Care → Skin Care | 424906.5 | 416352.015395 | 2.013263% |

<details>
<summary>地域,カテゴリの元列とコピー列の比較例</summary>

![Americasの元2025 COGSは3967101.81](../assets/screenshots/lab03/46-americas-source-cogs.png)

![Americasの最適化後COGSは3887233.624033](../assets/screenshots/lab03/47-americas-optimized-cogs.png)

![AmericasのBeveragesの元2025 COGSは886785.31](../assets/screenshots/lab03/48-beverages-source-cogs.png)

![同じBeveragesの最適化後COGSは868931.991017](../assets/screenshots/lab03/49-beverages-optimized-cogs.png)

</details>

**Americas → Personal Care** の **＋** を選択し、**Skin Care** を表示します。元列とコピー列の同じ総計セルをそれぞれ選び、末端にも調整が反映されていることを確認します。

![Personal Careを展開し、Oral Care,Shampoo,Skin Careのサブカテゴリを表示した画面](../assets/screenshots/lab03/50-personal-care-expanded.png)

![Skin Careの元2025 COGSは424906.5](../assets/screenshots/lab03/51-skin-care-source-cogs.png)

![Skin Careの最適化後COGSは416352.015395](../assets/screenshots/lab03/52-skin-care-optimized-cogs.png)

サンプルデータの例では、各行のCOGSが同じ比率で変化します。実際の比率や値はデータとOptimizerの設定によって異なります。

総計だけでなく製品群ごとの負担を確認することで、カテゴリ責任者が実行できる調整かを検討できます。

元の2列を基準値として保持し、コピー列と比較します。

> [!NOTE]
制約を設けないと、Optimizerは両方の入力値を自由に変更できます。実務では、調達部門が合意した範囲を原価削減の上限にする、販売計画で裏付けられた売上を下限にするなど、必要な制約を加えます。

### 保存して読み込み直す

1. **Save** を選択し、Saving表示が消えて保存が完了するまで待ちます。ブラウザーを再読み込みし、実データが表示されるまで待ってから、**Reading** モードで結果を確認します。

   ![保存,再読み込み後のReadingモードで、5系列,All粗利12,500.00K,Grand Total/2025とSkin Careの展開が保持された画面](../assets/screenshots/lab03/53-optimizer-reloaded-reading.png)

   サンプルデータでは、All行に元売上 **26.10M**,元COGS **14,166.31K**、コピー売上 **26.38M**,コピーCOGS **13,881.11K**、粗利 **12,500.00K** という例が表示されます。

2. **Editing** に戻り、コピー列の年間総計をそれぞれダブルクリックします。編集バーの値を読み取ってから **Escape** で閉じ、変更を確定しません。

   ![再読み込み後のSales Plan編集バー26381105.29986が保存前の編集5桁値と一致した画面](../assets/screenshots/lab03/54-sales-reloaded-editor.png)

   ![再読み込み後のCOGS編集バー13881105.29986も保存前の編集5桁値と一致した画面](../assets/screenshots/lab03/55-cogs-reloaded-editor.png)

再読み込み後、代表値と編集値が保存前と同じであることを確認します。編集値の桁数はUIによって異なります。

### 制約を設定する場合

**Add Constraints** ページでは、2種類の制約を設定できます。

- **Range-based：** 入力値の下限と上限を指定し、その範囲内で解を求めます。たとえば、調達部門との合意に基づき、COGSの削減を2%以内に制限する場合に使います。
- **Fixed-value：** 特定の入力を固定し、他の入力で目標を達成します。たとえば、年間の価格が確定している場合は価格を固定し、販売数量で調整します。

Range-based制約を追加する場合は、**Add Constraints** で対象系列と **Set Type：Range** を選び、**Min / Max** を設定して、その制約カードの **Apply** を選択します。別の系列にも制約する場合は **+ Add** でカードを追加し、同じ手順で設定します。ここでの **Apply** は制約を確定する操作です。各カードに設定が反映されたことを確認してから **Run** または **Re-Run** を選びます。**Output** の **Apply** は別の操作で、確認した候補値を計画シートへ反映します。目標や制約の状態を確認する前にOutputのApplyを選ばないでください。

#### 任意演習：Range制約を2つ設定する

既存の最適化結果を保持した状態でOptimizerを開き、**Target Value** を `12.6m` にします。**Add Constraints** でCOGSの **Set Type：Range** を選び、**Min：13700000 / Max：13900000** を入力して、その制約カードの **Apply** を選びます。**+ Add** でSales Planの制約カードを追加し、**Range / Min：26000000 / Max：27000000** を設定してカードの **Apply** を選びます。2つの範囲が表示されていることを確認して **Run** を選び、Outputの達成値,実行状態,制約に合った候補値を読み取ります。

![COGSのRange制約カードにMin 13,700,000 / Max 13,900,000を設定した画面例](../assets/screenshots/lab03/optimizer-range-constraint-example.png)

カード内の **Apply** は制約を確定します。**Output** の **Apply** は候補値を計画へ反映する操作です。この任意演習ではOutputの **Apply** を選ばずに閉じ、既存の入力と粗利が変わっていないことを同じ精度で確認します。対象環境や初期値によって出力は異なるため、固定の達成値を合格条件にしません。

制約を設けなければ、計算上は正しくても、業務では実行できない提案になる可能性があります。20%の原価削減で目標に達しても、調達部門が実行できなければ計画としては使えません。

### 目標に到達しない場合

制約が厳しい場合などは、目標に到達しないことがあります。Output ページの **Set Parameters** で、次の3項目を調整してから **Re-Run** を選択できます。

| パラメーター | 既定値 | 調整する内容 |
|---|---|---|
| **Strategy** | Balanced | 1回あたりの調整幅です。小さい幅では収束が遅くなる一方、目標を飛び越えにくくなります。大きい幅では速く進みますが、解を飛び越える場合があります |
| **Tolerance** | Standard、0.1% | 目標にどの程度近づけば完了とするかを指定します。目標12.5mに対する0.1%の許容範囲は、12.4875m〜12.5125mです |
| **Iterations** | Standard、200 tries | 計算を終了するまでに繰り返せる回数です |

解が見つからない場合、まず疑うべきは、制約の下では目標そのものが達成できない可能性です。許容誤差を広げて結果を出そうとする前に、目標が実現可能かを確認してください。

---

## ここまでの成果

このモジュールでは、売上総利益1,250万ドルを目標として、売上と原価の調整をOptimizerで検討します。結果は入力値,制約,許容差に応じて変わり、売上目標3,000万ドルとの同時達成を意味するものではありません。

ただし、計画どおりに1年が進むとは限りません。モジュール04では、実績の変化を踏まえて更新していく見通しを作成します。

## 理解度チェック

1. 最適化の前に *2026 Sales Plan* と *2025 COGS* をコピーしたのはなぜですか。
2. 数式列で行,列の集計設定を確認せずに既定値のままにすると、どのような問題が起こり得ますか。
3. Optimizer がCOGSを20%削減する結果を出しましたが、調達部門から実行不可能だと言われました。事前に何を設定すべきでしたか。
4. 2人がこのモジュールを実行し、異なる Sales Plan と COGS の値で売上総利益1,250万ドルを達成しました。どちらかの操作が間違っているのでしょうか。

<details>
<summary>解答</summary>

1. Optimizer が調整できるのは、編集可能なデータ入力列だけだからです。別のシートやセマンティックモデルのメジャーは読み取り専用です。
2. Formula ではなく Sum になっている集計では、各階層で数式を再計算せず、子の値を合計します。利益率や比率などの小計,総計が不適切な値になるおそれがあります。なお、この演習では列側の既定値が Sum、行側は Formula です。
3. **Add Constraints** ページで、入力値が動ける範囲を指定するか、値を固定する制約を追加すべきでした。
4. いいえ。Optimizer は唯一の答えを返す数式ではなく、反復計算で解を探すソルバーです。同じ目標を達成する組み合わせは複数あり、開始時の値や調整幅によって、到達する組み合わせが変わります。

</details>

---

**← 前へ：** [モジュール02](02-allocation-and-collaboration.md) · **次へ：** [モジュール04：見通しと書き戻し →](04-forecast-and-writeback.md)

### 参考資料

- [Fabric計画チュートリアル パート2：データ入力メジャーの最適化](https://learn.microsoft.com/fabric/iq/plan/planning-tutorial/planning/tutorial-2-optimizer)
- [Optimizer の概要](https://learn.microsoft.com/fabric/iq/plan/planning-optimize/optimizer-overview)
