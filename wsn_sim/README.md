# WSN 路由協議模擬

本專案模擬並比較三種無線感測網路路由協議：

- Direct Transmission
- LEACH
- PEGASIS

模擬會記錄 1%、20%、50%、100% 節點死亡時的輪數，並輸出比較長條圖 `comparison.png`。

## 安裝依賴

```bash
pip install -r requirements.txt
```

## 執行方式

```bash
python simulate.py
```

執行後會在終端機顯示節點死亡輪數對照表，並在同一個資料夾中產生 `comparison.png`。
# 研究流程的AI協作探索 - 專案檔案說明書

本專案為「書報討論」期中報告的實作成果，展示了如何利用 AI 工具（Codex、Zotero、Obsidian）完成從文獻探討、程式復現到論文撰寫的完整科研閉環。

## 📂 程式碼與實驗檔案
*   **`simulate.py`**：核心模擬程式。實作「一階無線電模型」，並模擬 Direct、LEACH、PEGASIS 三種路由協議的節點死亡輪數。
*   **`ablation.py`**：消融實驗程式。實作改良版的 PEGASIS（Proposed），使用「剩餘能量與距離加權」來選擇鏈頭，用以驗證改進機制的有效性。
*   **`requirements.txt`**：本專案所需的 Python 套件清單（包含 numpy, matplotlib 等）。

## 📊 實驗數據與圖表
*   **`comparison.png`**：Baseline 復現結果對比圖（Direct vs LEACH vs PEGASIS）。
*   **`ablation.png`**：消融實驗結果對比圖（LEACH vs PEGASIS vs Proposed）。
*   **`ablation_results.md`**：消融實驗的詳細數據與文字解析。
*   **`__pycache__`**：Python 執行時自動生成的快取資料夾（可忽略）。

## 📝 文獻與論文產出
*   **`paper_draft.md`**：透過 AI 整合 Obsidian 筆記與實驗數據，自動生成的論文初稿（包含 Abstract 到 Conclusion）。
*   **`PROJECT_GUIDE.md`**：由 Codex 自動盤點生成的專案導覽手冊。

## 🔗 外部工具捷徑與簡報
*   **`Obsidian.lnk`**：Obsidian 知識庫的快速捷徑（內含雙向連結卡片與知識圖譜）。
*   **`Zotero.lnk`**：Zotero 文獻庫的快速捷徑。
*   **`書報期中.pptx`**：期中報告的正式簡報檔。
*   **`蒸餾.md`**：知識蒸餾（Knowledge Distillation）概念驗證的相關筆記與程式碼紀錄。
*   **`..`**：返回上一層目錄。
