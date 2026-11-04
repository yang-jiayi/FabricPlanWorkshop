# モジュール 02：配賦と共同作業

**所要時間の目安：** 25分<br>
**このモジュールで作成するもの：** 前年の売上構成比で配賦した3,000万ドルのトップダウン目標、地域ごとの調整を反映したボトムアップの販売計画、申請状態と地域,本社の2つの承認段階を分けたワークフロー。

---

## このモジュールの位置づけ

経営陣が求めるFY26の売上目標は**3,000万ドル**です。HarborlightのFY25の売上実績は約**2,590万ドル**でした。差額の約400万ドルをどこで積み上げるのか。その答えを具体化するのが、今回の役割です。

ここでは、トップダウンの配賦で全体の枠組みを決めたうえで、地域の事情をよく知る責任者がボトムアップで調整します。その過程で、実務上とても重要な**ロック**機能も体験します。

目標は、あえて2段階で引き上げます。当初の経営目標は約10%増の2,850万ドルでしたが、その後、約16%増の3,000万ドルに変更されました。まず当初の目標を配賦し、すでに確定している四半期をロックします。そのうえで、追加分を調整の余地が残る期間だけに配賦します。

モジュール01で作成した `Plan Intro` シートを使います。

> [!IMPORTANT]
> **系列名と計画年度の日付キーは別です。** この演習の `2026 Target` と `2026 Sales Plan` は、FY25実績をコピーした系列の名前です。名前を付けるだけではDate階層の年月キーは2026年へ移りません。ここでは**2025年の時間軸を使い、目標の配賦や調整の操作を体験**します。FY26の実際の年月へ保存する計画や、年度をそろえた計画,実績比較では、日付キーと計画データの対象期間を別途設計します。

---

## パート1：トップダウンの目標を設定する

### 入力可能な列を作成する

1. **Planning** リボンの **Totals** を選択します。**Column Grand Total** のドロップダウンを開き、初期値の **Off** から **Left** に変更します。FY25の全期間の実績を合計した **Grand Total** 列が、期間別の列の左側に表示されます。

   ![TotalsメニューでColumn Grand TotalがOffになっている画面](../assets/screenshots/lab02/01-totals-menu.png)

   ![Column Grand Totalの選択肢からLeftを選ぶ画面](../assets/screenshots/lab02/02-grandtotal-left-option.png)

   ![Grand Total列が左側に追加され、All行で2025年列と同じ25.87Mが表示された画面](../assets/screenshots/lab02/03-grandtotal-enabled.png)

> [!TIP]
> **この後によく出てくる用語を確認します。** **総計列（grand total column）**は、この年間総計の列です。**総計セル（grand total cell）**は、その列と対象行が交差するセルを指します。*All* 行なら全社の年間合計、*Energy & Sports* 行ならそのサブカテゴリの年間合計です。ここに値を入力すると、配下の明細にも配賦されます。
>
> 総計列と *2025* 列には同じ数値が表示されます。*2025 Gross Revenue* は単年度のメジャーなので、全期間の合計がその年の合計と一致するためです。この違いは、次のセクションで四半期まで展開すると分かりやすくなります。

2. **Planning** リボンで **Number** → **Copy from another series** → **2025 Gross Revenue** を選択します。

   ![NumberからCopy from another seriesを開き、2025 Gross Revenueを選ぶ画面](../assets/screenshots/lab02/04-copy-series-menu.png)

3. **Data Input** ペインの **Title** 欄をクリックし、**Ctrl+A → Backspace** で既定の `Number` を消します。空欄になったことを確認してから、`2026 Target` と入力します。

   ![Data Inputの初期値。TitleはNumber、Visual Measure、Number、SumとSum、親から子への配賦がチェック済み](../assets/screenshots/lab02/05-data-input-defaults.png)

4. **Title** が `2026 Target` だけになっていることを確認します。**Insert as：Visual Measure**、**Input type：Number**、**Column aggregation type：Sum**、**Row aggregation type：Sum**、**Distribute parent value to children：チェックあり**のまま **Create** を選択します。

   ![Titleを2026 Targetに変更し、既定の入力,集計,配賦設定を維持した画面](../assets/screenshots/lab02/06-target-settings.png)

   ![Measure created successfullyと表示され、2026 Target列にFY25の基準値がコピーされた画面](../assets/screenshots/lab02/07-target-created.png)

> [!NOTE]
> **Title** の初期値が `Number` の場合があります。既存の文字列を残して入力すると、意図しない名前になります。作成前に、欄全体が `2026 Target` だけになっていることを確認してください。

新しい列には、**FY25の値があらかじめコピーされます**。合計は約2,590万ドルです。この値は計画の出発点であり、目標値ではありません。

<details>
<summary>その他の設定の意味と、この演習で既定値を使う理由</summary>

| 設定 | 既定値 | 設定の意味 |
|---|---|---|
| **Insert as** | Visual Measure | 列階層がある場合に、各カテゴリに列を挿入します。このシートでは Columns に Date 階層を使うため、各期間にメジャーを表示する Visual Measure が適しています。Visual Column では、階層に関係なく1列だけを挿入します |
| **Input type** | Number | 金額の入力に適した型です |
| **Column aggregation type** | Sum | 列階層の値をどのように集計するかを指定します |
| **Row aggregation type** | Sum | 行階層の値をどのように集計するかを指定します |
| **Distribute parent value to children** | オン | **このモジュールの前提となる設定です。** 親の値を、子のメンバーに構成比で自動配賦します。オフにすると、総計に2,850万ドルを入力しても地域やカテゴリには配賦されません |
| **Enable Multi-Dimension Allocation** | 内訳を追加しない | 今回の画面では、この見出しの下に **Add Breakdown** が表示されました。複数のディメンションをまたぐ配賦に使いますが、この演習では追加しません |
| **Minimum / Maximum Value** | なし | 最下位レベルの入力値に、必要に応じて下限,上限を設定できます |

**Create** を選択する前に、次の2点を確認してください。

- **列を作成した後は、Insert as と Input type を変更できません。** それ以外の設定は後から編集できます。
- **Distribute parent value to children** が使える集計方法は、Sum、Average (Leaf)、Minimum、Maximum、First、Last です。他の集計方法に変更すると、配賦機能は使えなくなります。

</details>

> [!NOTE]
> ネイティブ列は読み取り専用です。セマンティックモデルから取得したメジャーに、直接値を入力することはできません。コピーすることで編集可能な系列を作り、FY25実績を比較用の基準として残せます。この操作は、後のモジュールでも繰り返し使います。

### 目標を配賦する

1つのセルに数値を入力し、Planning で配下全体の計画を作成します。

**まず、入力するセルを確認してください。** 画面上の次の2つが交差するセルです。

- **All** 行：すべての地域とカテゴリを集計する最上位の行です。
- **2026 Target** の**総計列**：手順1で *Column Grand Total* を有効にして表示した年間総計列です。月別の列ではありません。

現在、このセルには全社のFY25売上実績、約 **25.9M** が表示されています。全体を代表する値です。

5. このセルをダブルクリックし、数式バーの元値を確認します。サンプルデータでは、表示の25.87Mに対し、元値は **`25866900.4`** です。この操作では新しい目標へ置き換えるため、`28.5m` を入力して **Enter** キーを押します。入力候補に28,500,000と表示されます。

   ![TargetのAll行の編集バーに、丸め前の25866900.4が表示された画面](../assets/screenshots/lab02/08-target-original-precision.png)

   ![28.5mを入力し、入力候補が28,500,000となった画面](../assets/screenshots/lab02/09-target-input-28-5m.png)

> [!NOTE]
> シングルクリックではセルが選択されるだけです。ダブルクリックすると編集できます。
>
> 接尾辞の `m` は million、つまり100万を意味します。このシートのように表示単位がすでに100万の場合は、`28.5` だけを入力しても同じ結果になります。それでも接尾辞を付けておくと、その時点の表示単位に左右されず、入力の意図を明確にできます。

約2,590万ドルの基準値を、約10%増となる当初の経営目標で置き換えました。Planning は、**FY25の売上構成比に応じて**、この値をすべての地域、カテゴリ、サブカテゴリに配賦します。

![Values savedが表示され、TargetがAll28.50M、Americas7.87M、Asia Pacific10.75M、Energy & Sports0.54Mとなった画面](../assets/screenshots/lab02/10-target-28-5m-result.png)

画面を広く使う場合は、**Fields** と **Data** の見出しにある折りたたみ用の矢印を選択します。上の入力後の画面では、両ペインを折りたたんでいます。

**サンプルデータの計算例：** 28,500,000 / 25,866,900.40 は約1.101794です。表示用の25.87Mは丸め値のため、配賦比率は元の値を使って計算します。

| 行 | FY25実績 | 2026 Target |
|---|---|---|
| All | 25.87 | **28.50** |
| Americas | 7.14 | **7.87** |
| Asia Pacific | 9.76 | **10.75** |
| Energy & Sports | 0.49 | **0.54** |

All行だけが変わるなど意図した結果にならない場合は、すぐに列を削除せず、コピー元が **2025 Gross Revenue** か、編集対象の系列,総計セルが正しいか、**Distribute parent value to children** が有効か、ロックやフィルターで対象が制限されていないかを確認します。設定と対象範囲を確認,修正してから、変更前後の値を照合してください。

1つの数値を入力するだけで、明細まで配賦された計画ができます。これがトップダウン計画の基本操作です。

### 上期をロックする

HarborlightではQ1とQ2の計画がすでに確定しています。販売促進施策も手配済みで、供給計画も変更できません。追加の成長分は、下期に配賦する必要があります。

6. **2025** の列見出しにポインターを合わせ、表示される **Expand/Collapse** 用の矢印を選択して四半期まで展開します。サンプルデータでのAll行のTargetはQ1〜Q4の順に **6.49 / 7.09 / 7.31 / 7.60M** です。

   ![28.5M配賦後に2025年を四半期へ展開し、TargetのQ1からQ4が6.49、7.09、7.31、7.60Mと表示された画面](../assets/screenshots/lab02/11-quarterly-28-5m.png)

7. **2026 Target** の **Q1** の合計セル（*All* 行とQ1が交差するセル）を選択します。セル右側の配賦アイコンのメニューを開き、**Lock all children** を選択します。**Lock this cell** は選ばないでください。**Q2** にも同じ操作を行い、両四半期のTarget配下が灰色になることを確認します。ネイティブ実績列の背景色と混同しないでください。

   ![All行のTargetのQ1を選択し、配賦メニューからLock all childrenを選ぶ画面](../assets/screenshots/lab02/12-lock-q1-menu.png)

   ![TargetのQ2でもLock all childrenを選ぶ画面](../assets/screenshots/lab02/13-lock-q2-menu.png)

   ![Q1とQ2のTarget配下が灰色になった状態](../assets/screenshots/lab02/14-q1-q2-locked.png)

8. 先ほど操作した **2026 Target** の年間総計セルをダブルクリックし、`30m` と入力します。入力候補が30,000,000であることを確認して **Enter** キーを押します。今回の画面では **Values saved** が表示され、年間総計が30.00Mになりました。

   ![ロック後の年間総計に30mを入力し、候補30,000,000を確認した画面](../assets/screenshots/lab02/15-target-input-30m.png)

   ![保存後、Targetが年間30.00M、Q1からQ4が6.49、7.09、8.05、8.37Mになった画面](../assets/screenshots/lab02/16-target-30m-locked-result.png)

経営目標が2,850万ドルから3,000万ドルに引き上げられ、**追加の150万ドルはQ3とQ4だけに配賦されます**。Q1とQ2の値は変わりません。

**結果を確認します。** *All* 行の四半期合計を、変更前後で比較してください。

| 四半期 | 2,850万ドルを配賦した後 | Q1,Q2をロックして3,000万ドルに変更した後 |
|---|---|---|
| Q1 | 6.49 | **6.49**（変更なし） |
| Q2 | 7.09 | **7.09**（変更なし） |
| Q3 | 7.31 | **8.05** |
| Q4 | 7.60 | **8.37** |

Q3への増分は約735,342.33、Q4は約764,657.67で、合計150万ドルです。百万単位,小数2桁で示すと、それぞれ約0.74と0.76になります。Q3とQ4の間の配賦比率は、それぞれの前年実績の構成比を維持します。

> [!NOTE]
> **表示値を合計するときの注意：** サンプルデータで元の精度から計算すると、28.5M配賦後のQ3は約7,311,492.347、百万単位,小数2桁では7.31です。四半期ごとの丸め表示を足すと28.49になる場合がありますが、年間総計の判定には丸め前の値を使います。

ロックしなかった場合は、4四半期すべてが30,000,000 / 25,866,900.40の比率で再計算されます。Q1は6,835,517.181…となり、百万単位,小数2桁では6.49から**6.84**へ変わります。原文の6.83は、元の精度での検算に基づき訂正しています。シート上部で目標を入力しただけで、すでに確定していた販売促進計画まで書き換わることになります。

このような変更から確定済みの計画を守るのが、ロックの役割です。ロックを使わずにトップダウンの修正を行うと、合意済みの計画が意図せず上書きされるおそれがあります。

9. **Q1** の合計セルを選択し、配賦メニューの **Unlock all children** を選択します。**Unlock this cell** とは別の操作です。**Q2** も同様に解除し、Target列の灰色表示が解消しても、年間総計30.00Mと四半期の値が変わらないことを確認します。

   ![TargetのQ1でUnlock all childrenを選ぶ画面](../assets/screenshots/lab02/17-unlock-q1-menu.png)

   ![TargetのQ2でもUnlock all childrenを選ぶ画面](../assets/screenshots/lab02/18-unlock-q2-menu.png)

   ![両四半期のロック解除後も、年間30.00Mと四半期6.49、7.09、8.05、8.37Mが変わっていない画面](../assets/screenshots/lab02/19-unlocked-target-result.png)

   値を細かく確認する場合は、各四半期をダブルクリックして編集バーを読み取り、値を変更せず **Escape** で閉じます。サンプルデータの編集値は小数第5位まで表示される例です。

   | 四半期 | 解除後の編集バーの表示 | 比較した期待値 |
   |---|---:|---|
   | Q1 | 6493741.32182 | 28.5M配賦時のQ1を小数第5位へ丸めた値 |
   | Q2 | 7091792.21025 | 28.5M配賦時のQ2を小数第5位へ丸めた値 |
   | Q3 | 8046834.67702 | Q1,Q2固定で30Mを配賦したQ3を小数第5位へ丸めた値 |
   | Q4 | 8367631.79091 | Q1,Q2固定で30Mを配賦したQ4を小数第5位へ丸めた値 |

<details>
<summary>四半期の編集バーに表示される値の例</summary>

![Q1の編集バーに6493741.32182が表示された画面](../assets/screenshots/lab02/20-q1-retained-precision.png)

![Q2の編集バーに7091792.21025が表示された画面](../assets/screenshots/lab02/21-q2-retained-precision.png)

![Q3の編集バーに8046834.67702が表示された画面](../assets/screenshots/lab02/22-q3-allocated-precision.png)

![Q4の編集バーに8367631.79091が表示された画面](../assets/screenshots/lab02/23-q4-allocated-precision.png)

</details>

**保存と再読み込みを行います。** 右上の **Save** を選択し、Saving表示が消えるまで待ってからブラウザーを再読み込みします。サンプルデータでは、再読み込み後に `Plan Intro`、Target系列、All30.00Mと四半期6.49 / 7.09 / 8.05 / 8.37Mが表示される例です。Readingモードでは右上から **Editing** に切り替えて続けます。

![保存と再読み込み後、ReadingモードでもTarget30.00Mと四半期の値,配置が保持された画面](../assets/screenshots/lab02/24-target-reloaded.png)

> [!TIP]
> 配賦が終わったらロックを解除してください。四半期をロックしたままにすると、次の変更時にもその期間が配賦対象から外れます。時間がたってから、意図しない結果につながりかねません。

---

## パート2：ボトムアップの計画を作成する

目標は全体の枠組みです。一方、計画は各地域が実行を約束する数値です。

1. **Planning** リボンで **Number** → **Copy from another series** → **2025 Gross Revenue** を選択します。コピー候補に **2026 Target** がある場合も、**そちらは選びません。** パート1と同様にTitle欄の既存文字列を全選択して消し、`2026 Sales Plan` だけを入力します。**Visual Measure / Number / Column aggregation type：Sum / Row aggregation type：Sum / Distribute parent value to children：チェックあり**を維持して **Create** を選択します。

   ![コピー元の候補に実績とTargetが並び、2025 Gross Revenueを選ぶ画面](../assets/screenshots/lab02/25-sales-copy-source.png)

   ![Titleを2026 Sales Planとし、入力,集計,配賦の既定設定を維持した画面](../assets/screenshots/lab02/26-sales-settings.png)

   作成したSales PlanはFY25実績のコピーです。サンプルデータでは、All行は実績と同じ **25.87M** となり、パート1のTarget **30.00M** とは異なります。

2. フッター右端の **Settings** アイコンを選択し、**Rows Per Page** のドロップダウンを開きます。今回の初期値は **Auto** でした。**All** を選択して、85行を同じページ内でスクロールできるようにします。設定後はページ表示が **1 of 1**、フッターは **Rows：85 / Columns：15** でした。85行すべてが同時に画面内へ収まるという意味ではありません。

   ![フッターのSettingsを開き、Rows Per PageがAutoになっている画面](../assets/screenshots/lab02/27-footer-settings.png)

   ![Rows Per Pageの選択肢All、Auto、10、15、25、50、75を表示した画面](../assets/screenshots/lab02/28-rows-per-page-options.png)

   ![Rows Per PageをAllにした画面。Sales Plan列、All25.87M、Target30.00Mを表示](../assets/screenshots/lab02/29-sales-created.png)

3. *Americas* の**行ラベルを右クリック**して、行コンテキストメニューを開きます。**Collapse** にポインターを合わせ、サブメニューの **Specific Level** ドロップダウンを開いて **Region** を選択します。今回の画面は、**Collapse** の直下で直接Regionを選ぶ形式ではありませんでした。

   ![Americas行のコンテキストメニューを開いた画面](../assets/screenshots/lab02/30-row-menu-inspection.png)

   ![CollapseのサブメニューにSpecific Levelが表示された画面](../assets/screenshots/lab02/31-collapse-region-menu.png)

   ![Specific Levelを開き、Region、Category、Sub CategoryからRegionを選ぶ画面](../assets/screenshots/lab02/32-collapse-specific-level.png)

   ![Regionへ折りたたみ、Allと4地域の5行になった画面](../assets/screenshots/lab02/33-region-collapsed.png)

   結果は **All、Americas、Asia Pacific、Europe、Middle East & Africa** の5行です。フッターは **Rows：5 / Columns：15** となり、All行のSales Plan **25.87M** とTarget **30.00M** は変わりませんでした。85行から5行への変化は、表示階層の折りたたみによるものです。行を削除する操作ではありません。

### サブカテゴリを調整する

Americasの営業責任者は、Energy & Sports飲料の成長を見込んでいます。

4. *Americas* 行の **＋** を選択し、続いて *Beverages* 行の **＋** を選択して、**Energy & Sports** 行を表示します。今回、変更する列は **2026 Sales Plan** の **Grand Total** です。隣にある **2026 Target** の値とは区別してください。

   ![AmericasとBeveragesを展開し、Energy & Sports行と3つの系列を表示した画面](../assets/screenshots/lab02/34-americas-beverages-expanded.png)
5. **Energy & Sports 行**にある **2026 Sales Plan** の総計セルをダブルクリックします。**数式バーまたは数値の編集欄にある既存の文字列を、その精度のまま残し**、末尾に `+8%` を追記して Enter キーを押します。画面上の `0.49` や式の `0.49+8%` は、百万単位で丸めた表示例です。**実際の編集値を0.49に打ち直さないでください。**

   サンプルデータの例では、編集欄に **`487740.11`** が表示されます。**End** キーで末尾へ移動し、消去せずに `+8%` を追加します。式は **`487740.11+8%`**、入力候補は **526,759.319** です。候補を確認して **Enter** キーで確定します。

   ![Energy & SportsのSales Plan年間値を開き、元の編集値487740.11を確認した画面](../assets/screenshots/lab02/35-energy-original-precision.png)

   ![元値を保持して487740.11+8%を入力し、候補526,759.319が表示された画面](../assets/screenshots/lab02/36-energy-append-8-percent.png)

> [!IMPORTANT]
> この操作は、**元の値への割合の追加**です。既存の数値が選択されたまま `+8%` を入力すると、元の文字列を置き換えてしまいます。編集欄または数式バーにフォーカスして、もう一度クリックするか **End** キーを押し、既存値の末尾へカーソルを移動してから追記してください。確定前に、**元の数値の全桁が残り、その後ろに `+8%` が付いていること**を確認します。
>
> [公式チュートリアル](https://learn.microsoft.com/fabric/iq/plan/planning-tutorial/planning/tutorial-1-allocation-collaboration)も、数式バーで「既存の値へ+8%を追加する」操作を案内しています。固定の丸め値を入力する操作ではありません。編集欄自体が丸めた値しか示さず元の精度を確認できない場合は、表示結果だけで精度を保持できたと判断せず、元値または既存値に対する割合変更の方法を確認してください。

**サンプルデータの計算例：** 487,740.11×1.08＝**526,759.3188**、増分は39,019.2088です。表示単位が百万の場合、Energy & Sportsは約**0.53M**、Beveragesは約**1.53M**、Americasは約**7.18M**、Allは約**25.91M**となります。

![8%加算後にValues savedが表示され、Energyと親階層のSales Planが更新された画面](../assets/screenshots/lab02/37-energy-increased-result.png)

入力候補は小数第3位、確定後の編集値は小数第2位で表示される例です。**同じ値を確認する目的で `+8%` を再度実行しないでください。**

| 確認箇所 | サンプルUIの表示例 | 計算例 |
|---|---:|---|
| 加算前のEnergy編集値 | 487740.11 | サンプルデータの例 |
| 入力中の候補 | 526,759.319 | 526759.3188を小数第3位へ丸めた値 |
| 確定後のEnergy編集値 | 526759.32 | 同じ値を小数第2位へ丸めた例 |
| 確定後のAll編集値 | 25905919.61 | サンプルデータの計算例 |

![確定後にEnergyの編集バーを開くと526759.32が表示された画面](../assets/screenshots/lab02/38-energy-increased-editor.png)

![AllのSales Plan編集バーに25905919.61が表示された画面](../assets/screenshots/lab02/39-all-sales-after-8-percent.png)

この値は表示桁に応じた丸め例です。TargetのAll **30.00M** とFY25実績 **25.87M** は、それぞれ別の系列として扱います。

![保存とブラウザー再起動後、Readingモードでも8%加算後の代表値,系列,行の展開が保持された画面](../assets/screenshots/lab02/40-sales-8-percent-reloaded.png)

> [!NOTE]
> **0.49Mに丸めてから入力し直すと、490,000×1.08＝529,200になります。** 元値487,740.11からの計算526,759.3188とは異なります。表示単位が百万で小数第2位までの場合、どちらも0.53に見えることがあるため、丸め値で元の値を置き換えないでください。

| 行 | 変更前 | 変更後 |
|---|---|---|
| Energy & Sports | 0.49 | **0.53** |
| Beverages | 1.49 | **1.53** |
| Americas | 7.14 | **7.18** |
| All | 25.87 | **25.91** |

Energy & Sportsが0.00になるなど元値を上書きしてしまった場合は、**Undo（Ctrl+Z）で直前の変更を戻し、元値487,740.11へ戻ったことを元の精度で確認**してから、追記をやり直してください。復旧のために `0.49` を打ち直すと、丸めによって元の値を変えてしまいます。Undoで戻せない場合も、丸めた表示値で復旧せず、コピー元の実績値と照合して元値を復元します。

増加分は、*Beverages*、*Americas* へと自動的に集計されます。

### 年間の配分に傾向を付ける

6. **Energy & Sports** 行の **2026 Sales Plan** の年間総計セルを選択し、配賦メニューを開きます。**Distribute to column with trend** にポインターを合わせ、サブメニューの **Input custom value** を選択します。**Apply Trend (%)** の入力欄に **4** を入力して **Apply** を選択します。スライダーを目測で合わせる代わりに、数値で設定できます。

   ![Energyの年間Sales Planの配賦メニューからDistribute to column with trendを選ぶ画面](../assets/screenshots/lab02/41-trend-distribution-menu.png)

   ![トレンドのスライダーとInput custom valueが表示された画面](../assets/screenshots/lab02/42-trend-controls.png)

   ![Apply Trend (%)の入力欄へ4を入力した画面](../assets/screenshots/lab02/43-trend-four-percent.png)

適用後、年間総計が変わっていないことと、期間別の値が変化したことを確認します。

![適用直後にSaving valuesが表示され、期間別の配分が変わった画面](../assets/screenshots/lab02/44-trend-applied-result.png)

Q4まで見えない場合は横方向にスクロールします。トレンド配賦では、設定に応じて期間別の値が変化します。

![横にスクロールしてQ1からQ4までのトレンド配賦後の列を表示した画面](../assets/screenshots/lab02/45-trend-q4-visible.png)

| 期間 | サンプルデータでの例 |
|---|---:|---|
| Q1 | 109,433.86 |
| Q2 | 123,098.21 |
| Q3 | 138,468.74 |
| Q4 | 155,758.51 |
| 4四半期の合計 | **526,759.32** |

<details>
<summary>トレンド配賦後の四半期別の値の例</summary>

![トレンド後Q1の編集バー109433.86012](../assets/screenshots/lab02/46-trend-q1-precision.png)

![トレンド後Q2の編集バー123098.20963](../assets/screenshots/lab02/47-trend-q2-precision.png)

![トレンド後Q3の編集バー138468.74447](../assets/screenshots/lab02/48-trend-q3-precision.png)

![トレンド後Q4の編集バー155758.50578](../assets/screenshots/lab02/49-trend-q4-precision.png)

</details>

年間総計は、Energyが約 **526,759.32**、全社のSales Planが約 **25,905,919.61** という例です。年間合計を維持したまま、期間別の配分を変更します。4%は年額に加算しません。

![トレンド適用後もEnergyの年間編集値526759.32が保たれた画面](../assets/screenshots/lab02/50-trend-energy-annual.png)

![全社Sales Planの年間編集値25905919.61も保たれた画面](../assets/screenshots/lab02/51-trend-all-annual.png)

> [!IMPORTANT]
> **4%を「四半期ごとに4%増」と読み替えないでください。** 列階層が **Year → Quarter → Month Short** の場合、トレンドは期間の配分に使います。表示された期間値は設定やデータによって異なります。適用前後で年間総計が保たれていることを確認します。

表示桁や配分結果はデータによって異なります。事業で使うトレンドを選ぶときは、列の期間階層と配分後の年間総計を確認してください。

### 複数地域を一括編集する

APACとEuropeでは、Q3の飲料とパーソナルケアの売上増加を見込んでいます。

7. **Planning** リボンで **Bulk Edit** を選択します。最初はMeasureや対象階層が未選択で、**Type** は **Set Value** です。

   ![Bulk Editを開いた初期画面。Measureと適用階層は未選択、TypeはSet Value](../assets/screenshots/lab02/52-bulk-edit-initial.png)

   **Measure：** `2026 Sales Plan` を選択します。

   **Select Filter：** **+ Add Filter** で、ディメンションごとに次の3つを追加します。演算子を **Is** にし、値の選択欄を開いて**対象メンバーのチェックボックス**を選択します。名前の表示だけをクリックして選択済みと思い込まず、チェックが付いたことを確認してください。複数選択できます。

   | ディメンション | 演算子 | 選択する値 |
   |---|---|---|
   | Region | Is | Asia Pacific, Europe |
   | Category | Is | Beverages, Personal Care |
   | Quarter | Is | Q3 |

   ![Regionの候補でAsia PacificとEuropeをチェックした画面](../assets/screenshots/lab02/53-bulk-region-selected.png)

   ![Categoryの候補でBeveragesとPersonal Careをチェックした画面](../assets/screenshots/lab02/54-bulk-category-selected.png)

   ![QuarterでQ3を選択した画面](../assets/screenshots/lab02/55-bulk-quarter-selected.png)

   選択欄が狭いと、先頭のメンバーしか見えないことがあります。値の選択欄を開き直して、2つの地域,2つのカテゴリそれぞれにチェックが付いていることを確認します。フィルターの欄内も必要に応じてスクロールし、3条件を確認してください。フィルター行のごみ箱アイコンは、その条件を削除する操作です。

   **Apply to Row Level：** `Sub Category`。**Apply to Column Level：** `Month Short`。これらの設定で、編集を適用する階層の深さを指定します。

   **Type：** **Set Value** から **Append By** に変更します。**Value：** `8%`。

   ![Typeの選択肢Set Value、Append By、Reset ValueからAppend Byへ変更する画面](../assets/screenshots/lab02/56-bulk-append-by-option.png)

   Value欄からフォーカスを移し、**Append By / 8%**、**Sub Category / Month Short** を確認します。今回、すべて設定すると **Apply** が有効になりました。

   ![Measureと適用階層、Append Byと8%を設定し、Applyが有効になった画面](../assets/screenshots/lab02/57-bulk-configured.png)

   ![フィルター欄の上部にRegionとCategoryの条件が表示された画面。Q3条件は下方](../assets/screenshots/lab02/58-bulk-filters-top.png)

   **Apply** を1回選択します。

> [!IMPORTANT]
> **Type の既定値は Set Value で、既存値を置き換える操作です。** 既存の対象値を8%増やすため、必ず **Append By** を選んでから **Apply** を実行します。確認のためにApplyを繰り返すと、増加を重ねて適用してしまいます。

両地域の両カテゴリについて、Q3の既存値に8%を追加します。調整する階層はサブカテゴリと月です。このデータでは対象範囲は2地域×6サブカテゴリ×3か月の36セルに相当します。

**サンプルデータでの結果例：** 適用後のAllは約 **26.10M** となり、対象のAsia PacificとEuropeが増加します。

![一括編集後のSales PlanはAll26.10M、Asia Pacific9.89M、Europe6.22Mとなった画面](../assets/screenshots/lab02/59-bulk-applied-result.png)

| 地域 | 変更前の表示（M） | 変更後の表示（M） | フィルター対象 |
|---|---:|---:|---|
| Americas | 7.18 | **7.18** | 対象外 |
| Asia Pacific | 9.76 | **9.89** | 対象 |
| Europe | 6.15 | **6.22** | 対象 |
| Middle East & Africa | 2.81 | **2.81** | 対象外 |
| **All** | 25.91 | **26.10** | |

以下はサンプルデータの年間総計の例です。対象地域では対象範囲が増加し、フィルター対象外の地域は変わりません。

| 行 | 一括編集後の年間総計例 |
|---|---:|
| All | **26095900.2404** |
| Americas | 7180538.91 |
| Asia Pacific | 9885587.2476 |
| Europe | 6217647.6128 |
| Middle East & Africa | 2812126.47 |

![一括編集後のAll編集バー26095900.2404](../assets/screenshots/lab02/60-bulk-all-precision.png)

<details>
<summary>4地域の年間編集値の例</summary>

![Americasの編集バー7180538.91](../assets/screenshots/lab02/61-bulk-americas-precision.png)

![Asia Pacificの編集バー9885587.2476](../assets/screenshots/lab02/62-bulk-apac-precision.png)

![Europeの編集バー6217647.6128](../assets/screenshots/lab02/63-bulk-europe-precision.png)

![Middle East & Africaの編集バー2812126.47](../assets/screenshots/lab02/64-bulk-mea-precision.png)

</details>

サンプルデータの計算例では、対象範囲の増分は **189,980.6304** です。直前の年額 **25,905,919.61＋189,980.6304＝26,095,900.2404** となります。

右上の **Save** を選び、Saving表示が消えるまで待ってからブラウザーを再読み込みします。All、対象地域の合計、系列や行の展開状態が保持されているか確認します。

![一括編集を保存して再読み込みしたReading画面。All26.10M、APAC9.89M、Europe6.22Mと系列,行展開が保持されている](../assets/screenshots/lab02/65-bulk-reloaded-reading.png)

続いて **Editing** に戻り、AllとAsia PacificのSales Plan年間総計をそれぞれダブルクリックします。編集バーを読み取ったら **Escape** で閉じ、値の変更は確定しません。今回、Allは **26095900.2404**、Asia Pacificは **9885587.2476** で、どちらも保存前に読み取った編集バーと一致しました。

![保存,再読み込み後のAll編集バー26095900.2404。保存前の表示と一致](../assets/screenshots/lab02/66-bulk-reloaded-all-precision.png)

![保存,再読み込み後のAsia Pacific編集バー9885587.2476。保存前の表示と一致](../assets/screenshots/lab02/67-bulk-reloaded-apac-precision.png)

意図しない地域が変わった場合は、**Undo** で戻してから、Measure、3つのフィルター、適用階層、Typeを確認してください。

---

## パート3：数値の前提を共有する

根拠の残っていない数値では、経営会議で十分な説明ができません。

1. *Americas* → *Beverages* 配下の **Energy & Sports** 行にある **2026 Sales Plan** の**年間総計セル（Grand Total）**を選択します。シングルクリックで構いません。編集ボックスは開かないでください。今回の表示は **0.53M** でした。
2. **画面右上**の **Comments** の右側にあるドロップダウンを開き、**Add Comment** を選択します。リボンのタブ名と同じ行に、Security、Comments、Editing、Save などが表示されます。原典の *Add new comment* とUIの項目名が異なる場合は、画面に表示された **Add Comment** を選択してください。

   ![Energy & SportsのSales Plan年間総計を選択し、右上CommentsからAdd Commentを開いた画面](../assets/screenshots/lab02/68-comment-menu.png)

3. コメント編集欄に、次の内容を入力します。

   > Americasの営業責任者と8%の売上増で合意済み。年間合計を、4%の成長トレンドに沿って各四半期に配賦しました。

   ![指定した日本語の前提コメントとSendアイコンが見える入力画面](../assets/screenshots/lab02/69-comment-text.png)

   **Send** アイコンを1回選択し、投稿された本文を確認します。

   ![Send後に表示された前提コメントの本文](../assets/screenshots/lab02/70-comment-posted-body.png)

> [!NOTE]
> コメントは、操作時に選択していた対象に紐づきます。セル、行、列のどれにコメントを付ける場合も、対象を確認してから投稿します。
>
> Planning リボンの **Notes** は固定の注記を残す機能です。スレッド形式のやり取りには **Comments** を使います。

コメントには投稿者名とタイムスタンプが記録されます。星を付けて重要なコメントとして扱うことも、**Assign to User** で担当者を割り当て、追跡可能なタスクにすることもできます。タスクは **Open** から始まり、対応後に **Resolved** に変更できます。

### コメント列を追加する

4. 画面右上の **Comments** のドロップダウンを開き、**Settings** を選択します。**Comment Settings** で **Enable Commenting** と **Comments Column** の状態を確認します。

   ![Comment Settingsの初期画面。Enable CommentingはOn、Comments ColumnはHide](../assets/screenshots/lab02/71-comment-settings-initial.png)

5. **Comments Column** のスイッチを **Hide → Show** に変更し、**Save** を選択します。期間列が多くてComments列が画面内に収まらない場合は、後述の手順7で列階層を折りたたみます。

   ![Comments ColumnをShowに変更し、Saveが有効になった画面](../assets/screenshots/lab02/72-comment-column-enabled.png)

   ![設定保存の成功メッセージと、Columns16への変化を確認した画面](../assets/screenshots/lab02/73-comment-column-result.png)

6. 新しい **Comments** 列の *Americas* 行をダブルクリックします。`販売計画のレビューが完了し、提出できる状態です` と入力し、必要に応じて `@` と相手の名前を入力します。候補から対象者を選択し、**Send** アイコンを選択します。Teams通知がオンの場合は、実際に相手へ通知が送信される可能性があります。

> [!TIP]
> コメントをタスクとして追加すると、Comments 列の隣に **Assignee** 列と **Status** 列が作成されます。Comments 列のヘッダーにある **>** アイコンで、これらの表示,非表示を切り替えられます。次に作成する入力用のStatus列とは別のものです。

### ステータス列を追加する

7. **2025** の列見出しの **Expand/Collapse** 用矢印を選択して、四半期から年間の表示へ折りたたみます。続いて **Planning** リボンで **List** → **Single Select** を選択します。

   ![2025を年間へ折りたたみ、右端にComments列が見える画面](../assets/screenshots/lab02/74-columns-collapsed-comments.png)

   ![PlanningのListメニューからSingle Selectを選ぶ画面](../assets/screenshots/lab02/75-list-menu.png)

8. **Data Input** ペインで **Presets** を開き、**Process Status** を選択します。次の5つの選択肢を確認して **Apply** を選びます。

   **Not Started / Started / In Progress / In Review / Completed**

   ![Presetsを開き、Process Statusを選ぶ画面。この段階の既定TitleはSingle Select](../assets/screenshots/lab02/76-status-presets.png)

   ![Process Statusの5つの選択肢を確認し、Applyが有効になった画面](../assets/screenshots/lab02/77-process-status-options.png)

   作成前に **Title** を **Ctrl+A → Backspace** で完全に消し、`Status` だけを入力します。既定の `Single Select` を残した連結名にしないでください。**Insert as：Visual Column**、**Input type：Single Select**、**Options Style：Chip**、**Default Value：None** を設定し、上の5つの選択肢とTitleを確認して **Create** を選択します。

   ![TitleをStatusにし、Visual Column、Single Select、5つの状態、Chip表示を確認した画面](../assets/screenshots/lab02/78-status-configured.png)

   ![Measure created successfullyとStatus列の追加を確認した画面](../assets/screenshots/lab02/79-status-created.png)

9. *Americas* 行の **Status** セルをダブルクリックし、**In Progress** を選択します。これは入力用リストの値であり、パート4の承認ステータスとは別です。

   ![Americas行のStatusセルを開き、選択肢からIn Progressを選ぶ画面](../assets/screenshots/lab02/80-status-options.png)

   ![Americasに黄色のIn Progressが表示された直後の画面。Saving valuesは保存途中の表示](../assets/screenshots/lab02/81-status-in-progress.png)

   右上の **Save** を選択し、保存が完了してからページを再読み込みします。Readingモードでコメント列,Status列と値が保持されていることを確認します。

   ![保存とブラウザー再起動後のReading画面。AmericasのIn Progress、Status列、Comments列とコメントのマーカーが保持されている](../assets/screenshots/lab02/82-comments-status-reloaded.png)


   ![ブラウザー再起動後に再表示した日本語の前提コメント。本文が同じ内容で保持されている](../assets/screenshots/lab02/83-comment-reloaded-body.png)

---

## パート4：承認を依頼する

このパートでは、**申請者が更新する全体の申請状態**と、**地域責任者,本社責任者による2つの承認段階**を分けます。以下は[承認ワークフロー設定手順](https://learn.microsoft.com/fabric/iq/plan/planning-how-to-configure-approval-workflows)に基づきます。設定画面の項目名、追加できる段階、状態の選択肢は、開催環境で確認してください。

> [!IMPORTANT]
> **最初のlevelは、全体の申請状態を管理します。** 公式の詳細設定記事では、最初のlevelにIn Progress,Submitted,Reopenedなどの申請状態を置き、後続のlevelに承認者を設定します。地域責任者と本社責任者の両方に承認を依頼する場合は、別々の承認levelを設定します。

この演習で目指す列と担当者は次のとおりです。パート3の進捗管理用 `Status` 列とは別に作成します。

| 列名 | 担当者 | 役割 |
|---|---|---|
| `Task Status` | 申請者 | 申請,再申請の状態を管理する |
| `Regional Manager` | 地域の承認者 | 1段階目の承認,却下を行う |
| `Finance Director` | 本社の承認者 | 2段階目の承認,却下を行う |

1. `Plan Intro` を開き、**Model** リボンで **Approval** を選択します。既存の設定がある場合は、列名,担当者,段階,通知設定を確認します。
2. 最初のlevelの状態選択肢を確認し、全体の申請状態を管理する列を `Task Status` とします。この列を更新する申請者を選択します。次の承認levelを `Regional Manager` とし、地域の承認者を選択します。画面に示された番号だけで、申請状態の列を承認段階として数えないでください。
3. `Finance Director` の承認levelを用意し、本社の承認者を選択します。段階が足りなければ、公式手順にある **Add** で承認levelを追加します。**申請状態1列と承認2列の計3列**、担当者、承認順序を確認して **Next** を選択します。ここでのAddやlevel名は、実際の画面で確認します。
4. **Reset on Rejection** をオンにします。公式では既定はオフで、最終承認者の却下時に、それまでの申請,承認状態をIn ProgressまたはReopenedへ戻すと説明されています。開催環境での状態名と適用先を確認してください。
5. **Teams Notifications** の設定を確認します。公式では、承認依頼時の承認者向け通知と、承認,却下時の申請者向け通知が既定でオンです。**オンのまま申請や承認,却下を行うと、設定した相手へ実際にTeams通知が送られ得ます。** 通知を送る場合は対象者へ事前に知らせます。通知を送らず状態遷移を試す場合は、両方をオフにし、既存のOn Change Formulaが通知を送るかも確認します。
6. **Submit** を選択して設定を作成します。`Task Status`、`Regional Manager`、`Finance Director` の3列、各列の状態選択肢と担当者を確認し、保存,再読み込み後の保持を照合します。ここでのSubmitはワークフローの設定作成で、個々の計画値を承認申請する操作は手順8です。

> [!NOTE]
> **申請者と1人の承認者**で1段階の引き渡しを行えます。**地域承認と本社承認を別の人が行う2段階のフロー**には、申請者と2人の承認者を用意します。同じ人を両承認段階に指定した場合は、職務分離の要件に照らして適切か確認してください。
>
> 承認者候補から、承認を担当する実在のユーザーを選択します。候補に出ない場合は、ユーザーの存在、Planとモデルのアクセス権、開催環境の構成を確認してください。Microsoft Entra B2Bゲストは一律に非対応とはせず、[モジュール00の前提条件](00-prerequisites.md)に従って事前確認します。参加者が実際に操作した際のセッション,課金ロールは、[モジュール08](08-sizing-and-governance.md)の確認事項です。

### 動作を確認する

7. 申請者のアカウントで *Asia Pacific → Beverages* を **Sub Category** まで,対象年の列を **Month** まで展開します。変更する **2026 Sales Plan** の範囲に含まれる全末端セルについて,年,月,地域,Category,Sub Category,シナリオ,変更前の値を記録します。地域計,All計も同じ範囲で記録してください。丸めた集計値だけでは復元できません。全末端値を記録できない場合は,講師が事前に用意した利用者別の正確なバックアップ / エクスポートを使います。復元元がない場合は値の変更と却下後の再申請演習を行わず,状態遷移の説明にとどめます。復元元を確保してから,同じ *Asia Pacific → Beverages* の総計セルへ戻り,既存の数値の末尾に `+10%` を一度だけ追記してEnterキーを押します。列名の2026から現在のセル値,日付キーを推測しないでください。
8. 同じ *Asia Pacific → Beverages* 行の **Task Status** 列で、**Submitted** を選択します。Task Status、Regional Manager、Finance Directorの状態と担当者を確認します。公式の詳細手順では、この申請によって最初の承認段階がPendingとなり、承認後に次の段階へ回付されます。Submittedは最終承認の完了ではありません。

### 提出後の引き渡し

- 地域の承認者本人で同じ対象行を開き、承認します。本社の承認者へ回付されることを、担当者,対象値,各列の状態で確認します。
- 本社の承認者本人で却下し、Task Statusと前段の承認状態がどう戻るかを確認します。**却下直後に再申請せず**、変更前に記録した値または演習前のバックアップから対象の月次 / Sub Category値を明示的に元へ戻します。年計を1.10で割るだけでは、元の明細配分まで復元できたとは判断しません。
- 計画を保存し、通常の再読み込み後に対象末端値,地域計,All計が変更前の記録と一致することを確認します。その後、復元した計画を再申請し、地域承認,本社承認の順に完了します。復元操作が新たな承認対象になる場合は、その状態も確認します。
- Teams通知は、設定と、宛先本人のTeamsでの受信を分けて確認します。送信表示だけで受信済みとは扱いません。
- **却下時のリセットは、入力値の自動復元を保証するものではありません。** 丸めた表示値で元の値を置き換えず、対象セル,集計値を保存後に照合します。

---

## ここまでの成果

このモジュールでは、前年の構成比を使うトップダウンの配賦、地域別に調整するボトムアップ計画、数値の前提共有、申請状態を分けた地域,本社の承認フローを扱います。サンプルシナリオでは、11日間の集約作業を単一のシートで進める設定です。

次のモジュールでは、売上高3,000万ドルと売上総利益1,250万ドルの目標を具体的な数値で検討します。

## 理解度チェック

1. *2025 Gross Revenue* の値を保持しながらメジャーをコピーして使う理由を説明してください。
2. Q1とQ2をロックして年間合計を引き上げた後、ロックを解除し忘れると、次回の修正で何が起こりますか。
3. **Distribute to column with trend** は、通常の配賦と何が違いますか。

<details>
<summary>解答</summary>

1. ネイティブ列およびセマンティックモデルのメジャーは読み取り専用です。コピーによって編集可能な系列を作り、実績は基準値として保持します。
2. 次回の変更でもQ1とQ2は配賦対象から外れ、変更分がロックされていない四半期にすべて配賦されます。期間別の構成がおかしいと気づくまで、見落とされることがあります。
3. 成長カーブに沿って各期間へ配賦し、年間合計を維持します。

</details>

---

**← 前へ：** [モジュール01](01-environment-and-first-sheet.md) · **次へ：** [モジュール03：Optimizer →](03-optimizer.md)

### 参考資料

- [Fabric計画チュートリアル パート1：配賦と共同作業](https://learn.microsoft.com/fabric/iq/plan/planning-tutorial/planning/tutorial-1-allocation-collaboration)
- [トップダウン計画](https://learn.microsoft.com/fabric/iq/plan/planning-concept-top-down-planning) · [ボトムアップ計画](https://learn.microsoft.com/fabric/iq/plan/planning-concept-bottom-up-planning)
- [承認ワークフロー](https://learn.microsoft.com/fabric/iq/plan/planning-concept-approval-workflow)
- [承認ワークフローの設定](https://learn.microsoft.com/fabric/iq/plan/planning-how-to-configure-approval-workflows)
