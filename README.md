# Tower Defense Game

一個基於 Python 和 Pygame 開發的塔防遊戲。

## 遊戲特色

- 基於網格的塔防遊戲系統
- 可配置的遊戲參數（通過 config.json）
- 圖形化的遊戲界面
- 即時戰鬥系統

## 遊戲玩法

### 基本規則
- 敵人從右側生成，試圖向左移動
- 在網格上放置防禦塔來阻止敵人
- 如果敵人到達最左側，你會失去生命值
- 擊敗敵人可以獲得金錢和分數

### 遊戲操作
- 滑鼠左鍵：在網格上放置防禦塔（需要足夠金錢）
- 防禦塔會自動攻擊範圍內的敵人
- 敵人會攻擊路徑上的防禦塔

### 遊戲數值
- 初始金錢：100
- 初始生命值：10
- 防禦塔成本：50
- 擊敗敵人獎勵：10 金錢 + 1 分數

## 系統需求

- Python 3.x
- Pygame 2.5.2

## 安裝步驟

1. 克隆倉庫：
   ```bash
   git clone https://github.com/pkwbim/tower-defense.git
   cd tower-defense
   ```

2. 創建虛擬環境：
   ```bash
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
   ```bash
   pip install -r requirements.txt
   ```

## 運行遊戲

確保虛擬環境已激活，然後運行：
```bash
python main.py
```

## 配置說明

遊戲參數可以在 `config.json` 中調整，包括：

- 視窗設置（大小、標題）
- 網格配置（行數、列數、大小）
- 遊戲參數（初始金錢、生命值等）
- 防禦塔屬性（攻擊範圍、冷卻時間等）
- 敵人屬性（速度、生命值等）
- 子彈屬性（速度、傷害等）
- 顏色配置

## 開發者說明

### 代碼結構
- `main.py`: 主遊戲邏輯
- `config.json`: 遊戲配置文件
- `assets/`: 遊戲資源目錄

### 主要類別
- `GameState`: 管理遊戲狀態
- `GameRenderer`: 處理遊戲渲染
- `GameLogic`: 處理遊戲邏輯
- `EventHandler`: 處理用戶輸入
- `Tower`: 防禦塔類
- `Enemy`: 敵人類
- `Projectile`: 子彈類

## 版本歷史

### 最新版本
- 優化遊戲平衡性
- 修復多個敵人同時攻擊時的 bug
- 改進配置系統
- 添加防禦塔和敵人的血量顯示

## 授權協議

MIT License
