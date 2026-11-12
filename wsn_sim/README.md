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
