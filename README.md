# Tower Defense Game

一個基於 Python 和 Pygame 開發的塔防遊戲，靈感來自植物大戰殭屍。

## 遊戲特色

- 基於網格的塔防遊戲系統
- 多種防禦塔和敵人類型
- 可配置的遊戲參數（通過 config.json）
- 圖形化的遊戲界面
- 即時戰鬥系統
- 遊戲結束機制

## 遊戲玩法

### 基本規則
- 敵人從右側生成，試圖向左移動
- 在網格上放置防禦塔來阻止敵人
- 如果敵人到達最左側，你會失去生命值
- 當生命值降到 0 時遊戲結束
- 擊敗敵人可以獲得金錢和分數

### 遊戲操作
- 滑鼠左鍵：在網格上放置當前選擇的防禦塔（需要足夠金錢）
- 滑鼠右鍵：切換防禦塔類型（普通/強力）
- 防禦塔會自動攻擊同一行的敵人
- 敵人會攻擊路徑上的防禦塔

### 防禦塔類型
1. 普通植物
   - 成本：50 金幣
   - 攻擊力：15
   - 生命值：100
   - 攻擊冷卻：30 幀

2. 強力植物
   - 成本：100 金幣
   - 攻擊力：30
   - 生命值：150
   - 攻擊冷卻：20 幀（更快的攻擊速度）

### 敵人類型
1. 普通殭屍
   - 生命值：100
   - 攻擊力：10
   - 移動速度：1.0
   - 獎勵：25 金幣

2. 強力殭屍（分數達到 10 分後出現）
   - 生命值：200
   - 攻擊力：20
   - 移動速度：0.7（較慢）
   - 獎勵：50 金幣

### 遊戲數值
- 初始金錢：100
- 初始生命值：10
- 遊戲分數：擊敗每個敵人 +1 分

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
- 防禦塔屬性（類型、攻擊力、生命值等）
- 敵人屬性（類型、速度、生命值等）
- 子彈屬性（速度、大小等）
- 顏色配置

## 開發者說明

### 代碼結構
- `main.py`: 主遊戲邏輯
- `config.json`: 遊戲配置文件
- `assets/`: 遊戲資源目錄
  - `tower.png`: 普通植物圖片
  - `strong_tower.png`: 強力植物圖片
  - `zombie.png`: 普通殭屍圖片
  - `strong_zombie.png`: 強力殭屍圖片

### 主要類別
- `GameState`: 管理遊戲狀態（金錢、分數、生命值等）
- `GameRenderer`: 處理遊戲渲染（繪製遊戲元素和 UI）
- `GameLogic`: 處理遊戲邏輯（敵人生成、戰鬥等）
- `EventHandler`: 處理用戶輸入（滑鼠點擊等）
- `Tower`: 防禦塔類（普通和強力植物）
- `Enemy`: 敵人類（普通和強力殭屍）
- `Projectile`: 子彈類

## 版本歷史

### v1.1.0 (最新)
- 添加多種防禦塔類型（普通/強力）
- 添加多種敵人類型（普通/強力殭屍）
- 實現遊戲結束機制
- 優化子彈系統
- 添加植物類型切換功能
- 改進 UI 顯示

### v1.0.0
- 基礎遊戲系統實現
- 單一類型的防禦塔和敵人
- 基本的戰鬥機制
