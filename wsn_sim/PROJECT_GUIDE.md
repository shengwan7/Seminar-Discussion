# WSN 路由協議模擬專案說明書

## 1. 專案概述

本專案用 Python 模擬無線感測網路（Wireless Sensor Networks, WSN）中的節能路由協議，主要比較 Direct Transmission、LEACH、PEGASIS，以及一個改進版 PEGASIS 鏈頭選擇策略。專案核心目標是觀察不同資料收集機制對網路壽命的影響，並以節點死亡輪數作為主要評估指標。

本專案對應兩篇經典文獻：

| 文獻 | 年份 | 對應主題 |
|---|---:|---|
| Heinzelman et al., LEACH | 2000 | 分簇式 WSN 節能路由、簇頭輪換、資料融合 |
| Lindsey and Raghavendra, PEGASIS | 2002 | 鏈式 WSN 節能路由、鏈頭輪換、近鄰傳輸 |

主模擬 `simulate.py` 重現 Direct Transmission、LEACH、PEGASIS 三種協議的死亡輪數比較；消融實驗 `ablation.py` 則比較 Baseline PEGASIS、Proposed PEGASIS 與 LEACH。

## 2. 當前資料夾盤點

目前 `C:\Users\user\Desktop\wsn_sim` 實際包含下列檔案與資料夾。

| 名稱 | 類型 | 用途 | 備註 |
|---|---|---|---|
| `simulate.py` | 檔案 | 主模擬程式，模擬 Direct Transmission、LEACH、PEGASIS，輸出死亡輪數表格與 `comparison.png`。 | 核心程式 |
| `requirements.txt` | 檔案 | 列出執行所需套件：`numpy`、`matplotlib`。 | 依賴設定 |
| `README.md` | 檔案 | 簡短執行說明，包含安裝依賴與執行主模擬指令。 | 入門說明 |
| `comparison.png` | 檔案 | 主模擬結果圖，顯示三種協議在 1%、20%、50%、100% 節點死亡比例下的輪數比較。 | 由 `simulate.py` 產生 |
| `paper_draft.md` | 檔案 | 論文初稿，整合 LEACH、PEGASIS、WSN 研究脈絡與複現實驗結果。 | 研究寫作輸出 |
| `ablation.py` | 檔案 | 消融實驗腳本，比較 LEACH、Baseline PEGASIS、Proposed PEGASIS。 | 新增實驗程式 |
| `ablation.png` | 檔案 | 消融實驗長條圖，顯示三種協議在 1%、50%、100% 節點死亡比例下的輪數比較。 | 由 `ablation.py` 產生 |
| `ablation_results.md` | 檔案 | 消融實驗結果報告，包含結果矩陣與圖表引用。 | 由 `ablation.py` 產生 |
| `PROJECT_GUIDE.md` | 檔案 | 本專案說明書，整理檔案用途、執行方式、論文章節對應與下一步建議。 | 本次建立 |
| `Obsidian.lnk` | 檔案 | Windows 捷徑。 | 非核心研究檔案 |
| `Zotero.lnk` | 檔案 | Windows 捷徑。 | 非核心研究檔案 |
| `.packages/` | 資料夾 | 專案本地安裝的 Python 套件，包含 `numpy`、`matplotlib` 與其相依套件。 | 執行環境輔助資料夾 |
| `.mplconfig/` | 資料夾 | Matplotlib 字型與設定快取，協助圖表正常顯示中文。 | 執行時產生 |
| `__pycache__/` | 資料夾 | Python 匯入模組後產生的位元碼快取。 | 執行時產生 |
| `.pip-tmp/` | 資料夾 | pip 暫存資料夾，目前為空。 | 可視為暫存殘留 |
| `.venv/` | 資料夾 | 先前嘗試建立虛擬環境留下的骨架資料夾。 | 非必要執行條件 |

## 3. 檔案總覽

| 檔名 | 用途 | 對應論文章節 | 誰產生 |
|---|---|---|---|
| `simulate.py` | 實作能量模型、Direct Transmission、LEACH、PEGASIS，並產生主實驗結果。 | Methodology、Experiments | Codex 依使用者需求建立 |
| `requirements.txt` | 宣告 `numpy` 與 `matplotlib` 依賴。 | 執行環境，不直接對應論文章節 | Codex 依使用者需求建立 |
| `README.md` | 提供基本專案介紹與執行指令。 | 專案使用說明，不直接對應論文章節 | Codex 依使用者需求建立 |
| `comparison.png` | 主實驗比較圖。 | Experiments | `simulate.py` 產生 |
| `paper_draft.md` | 完整論文初稿，包含摘要、緒論、相關研究、方法、實驗、討論、結論與參考文獻。 | 全文章節 | Codex 整合 Obsidian 筆記建立 |
| `ablation.py` | 實作 PEGASIS 鏈頭選擇消融實驗。 | Methodology、Experiments、Discussion 可延伸內容 | Codex 依使用者需求建立 |
| `ablation.png` | 消融實驗比較圖。 | Experiments 或後續消融分析小節 | `ablation.py` 產生 |
| `ablation_results.md` | 消融實驗結果矩陣與圖表引用。 | Experiments、Discussion | `ablation.py` 產生 |
| `PROJECT_GUIDE.md` | 專案總覽、檔案盤點、執行方式、進度與下一步建議。 | 專案管理文件，不直接放入論文章節 | Codex 本次建立 |
| `Obsidian.lnk` | Obsidian 捷徑。 | 不對應 | 外部捷徑，非本專案程式產生 |
| `Zotero.lnk` | Zotero 捷徑。 | 不對應 | 外部捷徑，非本專案程式產生 |
| `.packages/` | 本地 Python 套件目錄。 | 執行環境，不對應 | pip 安裝依賴時產生 |
| `.mplconfig/` | Matplotlib 設定與字型快取。 | 執行環境，不對應 | Matplotlib 執行時產生 |
| `__pycache__/` | Python 位元碼快取。 | 執行環境，不對應 | Python 執行時產生 |
| `.pip-tmp/` | pip 暫存資料夾。 | 執行環境，不對應 | pip 安裝過程產生 |
| `.venv/` | 虛擬環境骨架資料夾。 | 執行環境，不對應 | venv 建立嘗試產生 |

## 4. 執行方式

### 4.1 安裝套件

一般 Python 環境可使用：

```powershell
cd "$env:USERPROFILE\Desktop\wsn_sim"
pip install -r requirements.txt
```

此指令會安裝：

| 套件 | 用途 |
|---|---|
| `numpy` | 節點座標、能量陣列、距離與統計計算 |
| `matplotlib` | 繪製 `comparison.png` 與 `ablation.png` |

### 4.2 執行主模擬

```powershell
cd "$env:USERPROFILE\Desktop\wsn_sim"
python simulate.py
```

主模擬會產生：

| 產出 | 說明 |
|---|---|
| 終端機死亡輪數表格 | Direct、LEACH、PEGASIS 在 1%、20%、50%、100% 節點死亡時的輪數 |
| `comparison.png` | 三種協議死亡輪數比較長條圖 |

### 4.3 執行消融實驗

目前 `ablation.py` 已存在，可使用：

```powershell
cd "$env:USERPROFILE\Desktop\wsn_sim"
python ablation.py
```

消融實驗會產生：

| 產出 | 說明 |
|---|---|
| 終端機消融實驗矩陣 | LEACH、PEGASIS、Proposed 在 1%、50%、100% 節點死亡時的輪數與能量標準差 |
| `ablation.png` | 三種協議在三個死亡比例下的比較長條圖 |
| `ablation_results.md` | 消融實驗 Markdown 結果報告 |

## 5. 產出檔案對照論文

| 論文章節 | 對應檔案 | 說明 |
|---|---|---|
| Abstract | `paper_draft.md` | 摘要整理研究目的、方法、主要結果與核心結論。 |
| Introduction | `paper_draft.md` | 說明 WSN 能量限制、研究問題與本文貢獻。 |
| Related Work | `paper_draft.md` | 整理 Direct Transmission、LEACH、PEGASIS 的演進。 |
| Methodology | `simulate.py`, `ablation.py`, `paper_draft.md` | 程式實作一階無線電模型與協議流程；論文草稿描述方法。 |
| Experiments | `simulate.py`, `comparison.png`, `ablation.py`, `ablation.png`, `ablation_results.md`, `paper_draft.md` | 主實驗與消融實驗的表格、圖表與結果說明。 |
| Discussion | `paper_draft.md`, `ablation_results.md` | 討論 LEACH 誤差、PEGASIS 優勢、Proposed 鏈頭選擇的初步效果。 |
| Conclusion | `paper_draft.md` | 總結複現成果與未來方向。 |
| References | `paper_draft.md` | 收錄 LEACH 2000 與 PEGASIS 2002。 |

## 6. 完整性檢查

| 檔案 | 狀態 |
|---|---|
| `simulate.py` | 已存在 |
| `requirements.txt` | 已存在 |
| `README.md` | 已存在 |
| `comparison.png` | 已存在 |
| `paper_draft.md` | 已存在 |
| `ablation.py` | 已存在 |
| `ablation.png` | 已存在 |
| `ablation_results.md` | 已存在 |

目前指定檢查清單中的檔案皆已建立。

## 7. 目前進度

### 已完成

| 階段 | 狀態 | 說明 |
|---|---|---|
| 專案骨架 | 已完成 | 已建立 `simulate.py`、`requirements.txt`、`README.md`。 |
| 主模擬 | 已完成 | 已模擬 Direct Transmission、LEACH、PEGASIS。 |
| 主圖表 | 已完成 | 已產生 `comparison.png`。 |
| 論文初稿 | 已完成 | 已建立並修訂 `paper_draft.md`。 |
| 消融實驗 | 已完成 | 已建立 `ablation.py`，並產生 `ablation.png`、`ablation_results.md`。 |
| 專案說明書 | 已完成 | 已建立本檔 `PROJECT_GUIDE.md`。 |

### 尚缺階段

| 階段 | 狀態 | 說明 |
|---|---|---|
| 多次隨機種子實驗 | 尚未建立 | 目前主要使用 `np.random.seed(42)`，尚未做多次重複實驗與平均值、標準差統計。 |
| 更完整 LEACH 細節 | 尚未建立 | 目前為簡化實作，尚未完整納入原論文中的 TDMA、CDMA 與完整簇建立開銷。 |
| 更多文獻擴充 | 尚未建立 | 目前論文初稿主要涵蓋 LEACH 2000 與 PEGASIS 2002。 |
| 自動化測試 | 尚未建立 | 尚未加入單元測試或固定輸出檢查腳本。 |
| 清理執行環境資料夾 | 尚未整理 | `.pip-tmp/`、`.venv/` 屬於執行過程殘留或環境資料夾，可視需求清理或加入忽略清單。 |

## 8. 下一步建議

1. 將 `paper_draft.md` 擴充消融實驗章節，納入 `ablation_results.md` 的結果與 `ablation.png`。
2. 加入多個隨機種子重複實驗，避免單一節點部署造成結論偏差。
3. 補強 LEACH 實作，逐步納入更完整的簇頭閾值公式、TDMA 排程與控制開銷。
4. 將 `simulate.py` 與 `ablation.py` 的共用邏輯抽成模組，降低重複程式碼。
5. 清理或管理執行環境資料夾，例如移除空的 `.pip-tmp/`，並決定 `.packages/`、`.venv/` 是否保留。
6. 擴充 References，加入更多 WSN 節能路由研究，建立更完整的文獻脈絡。
