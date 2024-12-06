# 簡易版植物大戰殭屍

這是一個受到經典遊戲《植物大戰殭屍》啟發的簡化版塔防遊戲，使用 Python 和 Pygame 開發。

## 遊戲說明

在這個遊戲中，你需要防禦不斷來襲的敵人：

- 你扮演防守方，可以在格子上放置防禦塔（類似於植物大戰殭屍中的植物）
- 敵人會從右側出現，向左移動（類似於殭屍的進攻）
- 如果敵人到達最左側，你會失去生命值
- 擊敗敵人可以獲得金錢和分數

### 遊戲操作

- 滑鼠左鍵：在格子上放置防禦塔（需要足夠金錢）
- 防禦塔會自動攻擊範圍內的敵人
- 開始時有 100 金錢，每個防禦塔花費 50 金錢
- 擊敗敵人可獲得 25 金錢和 10 分數

## 環境設置

1. 確保你已經安裝了 Python 3.x
2. 創建虛擬環境（如果還沒有創建）：
   ```powershell
   python -m venv venv
   ```

3. 激活虛擬環境：
   - Windows PowerShell:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   - Windows CMD:
     ```cmd
     .\venv\Scripts\activate.bat
     ```

4. 安裝依賴：
   ```powershell
   python -m pip install -r requirements.txt
   ```

## 運行遊戲

1. 確保虛擬環境已激活（命令提示符前面應該有 `(venv)`）
2. 運行遊戲：
   ```powershell
   python main.py
   ```

## 遊戲目標

- 盡可能長時間防守，不讓敵人突破防線
- 合理運用金錢資源，策略性地放置防禦塔
- 獲得更高的分數
