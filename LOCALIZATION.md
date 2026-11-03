# 翻訳と用語の方針

## 原版の出典

本ワークショップは、Diego Diaz による [fabric-planning-lab](https://github.com/Diaz506/fabric-planning-lab) を基にしています。原版は MIT License で公開されており、このリポジトリには原版の `LICENSE` を含めています。

翻訳の基準点は、2026年9月21日の [`486be63004b30554ab44a0e3ae654e3e762188ad`](https://github.com/Diaz506/fabric-planning-lab/commit/486be63004b30554ab44a0e3ae654e3e762188ad) です。原版の手順,シナリオ,数値,ライセンス上の表示と、日本語版で追加,改訂した説明を区別しています。

## 日本語版で改良・追加した点

- 原典由来のLab00〜08を日本語化し、日本語の説明と、画面で照合する英語のUI名,フィールド名を併記しました。
- 操作の流れに合わせたスクリーンショットと、手順,期待される結果を追加しました。
- 10〜20名の導入検討ワークショップ向けに、講師用の進行ガイドと運営上の提案を追加しました。
- READMEの概要とLab00〜09の正本Markdownから生成する[オフラインHTML操作ガイド](docs/workshop-presentation.html)を追加しました。手順ナビゲーション, 拡大できる操作画像, 明 / 暗の配色を備え, 生成物の同期をCIで確認します。作者Jiayi Yangによる日本語版の追加であり, Microsoftの公式教材ではありません。
- 製品用語を整理し、Plan アイテム,計画シート,予測,見通しなどを区別する用語方針を定めました。
- Microsoft Learn の説明と照合し、接続,権限,課金,書き戻し,サンプルデータに関する説明を補足,更新しました。テナントや提供地域,機能の状態によって異なる可能性がある項目は、環境ごとの確認事項として示しています。
- 原版の一部の例や説明を、サンプルデータと対応する値,手順に合わせて見直しました。各Labに示す期待値と注意事項は、対象の手順に沿って確認してください。
- 日本語版の発展編としてLab09「Plan Variance Analyst」を追加しました。Lab04のGross Revenue / ForecastをProduct × 月で照合し, WarehouseでのDecimal検算, Lakehouse Delta binding, Ontology Preview / Graph, 読み取り専用Fabric Data Agentを扱います。追加した画面手順の実機確認は合成CSVによるPart 3〜5に限られ, 実Plan / writebackからの抽出を含むEnd-to-End確認ではありません。これは原典の翻訳ではなく,日本語版で追加した内容です。

## 用語,表記

| 原語 | 日本語での扱い |
|---|---|
| Microsoft Fabric Planning / planning in Fabric | 製品,機能は Fabric Planning、アイテムの種類は Plan アイテム |
| Planning sheet | 計画シート。UIの **New Planning Sheet** は保持 |
| Plan / Budget / Forecast | 文脈に応じて計画 / 予算 / 見通し。フィールド名やメジャー名の `Forecast` は保持 |
| Predict / statistical forecasting | Predict / 統計予測。見通し全体の管理と、アルゴリズムによる予測を区別 |
| Allocation / writeback | 配賦 / 書き戻し |
| Gross profit / P&L | 売上総利益 / 損益計算書。モデル内の英語名は変更しない |
| Semantic model / measure | セマンティックモデル / メジャー |
| Planner / Stakeholder / Viewer | 操作に基づく課金,権限の名称として英語を保持。ワークスペースの役割とは区別 |
| Intelligence / PowerTable / Infobridge | 製品の識別に必要な名称を保持し、用途を日本語で説明 |

本文は自然で具体的な日本語を基本とし、区切りにはASCIIの `,` と ` / ` を使います。実際に画面で探すボタン,フィールド,モデル識別子,SQL,数式,URLは、照合しやすいよう原語を保持します。未確認の日本語UI名は作りません。USD / FYのサンプルは維持し、日本円や日本の会計年度へ機械的に置き換えません。
