# Python-TencentAPI

騰訊雲帳單查詢工具，透過騰訊雲 Billing API 查詢指定月份的費用帳單，支援 L2（按產品匯總）及 L3（帳單明細）兩種層級，並支援多帳號批次查詢。

---

## 目錄

- [專案概覽](#專案概覽)
- [功能說明](#功能說明)
- [執行流程](#執行流程)
- [使用方法](#使用方法)
- [設定檔說明](#設定檔說明)
- [命令列參數說明](#命令列參數說明)
- [建議注意事項](#建議注意事項)

---

## 專案概覽

```
Python-TencentAPI/
├── main.py                     # 主程式，CLI 入口，支援參數化執行
├── src/
│   └── tencent.py              # TencentAPI 類別，封裝 Billing API 查詢
├── conf/
│   ├── config.ini              # 環境設定檔
│   └── tencent.json.default    # 帳號設定範本
└── logs/
    └── TencentAPIMain.log      # 預設 log 檔案位置（ERROR 等級以上）
```

---

## 功能說明

| 功能 | API 方法 | 說明 |
|---|---|---|
| L2 按產品匯總 | `DescribeBillSummaryByProduct` | 查詢指定月份各產品的費用加總 |
| L3 帳單明細 | `DescribeBillDetail` | 查詢指定月份每筆費用明細，每頁最多 100 筆 |

支援多帳號設定，`conf/tencent.json` 中可設定多組 `secret_id` / `secret_key`，程式會依序處理每個帳號。

---

## 執行流程

```
1. 安裝相依套件
   pip install -r requirements.txt

2. 複製設定檔範本並填入帳號資訊
   cp conf/tencent.json.default conf/tencent.json
   （填入 secret_id 與 secret_key）

3. 執行主程式（預設查詢上個月帳單）
   python main.py

4. 查詢指定月份
   python main.py --month 2025-09

執行流程示意：
   main.py
     └─ 解析 CLI 參數（--month, --info_path, --log_level 等）
          └─ 讀取 conf/tencent.json（支援多帳號陣列）
               └─ 遍歷每個帳號
                    └─ 初始化 TencentAPI(secret_id, secret_key)
                         ├─ get_l2_bill(month) → 輸出按產品匯總帳單
                         └─ get_l3_bill(month) → 輸出帳單明細
```

---

## 使用方法

### 安裝依賴

```bash
pip install -r requirements.txt
```

### 設定帳號

```bash
cp conf/tencent.json.default conf/tencent.json
# 編輯 conf/tencent.json，填入騰訊雲 SecretId 與 SecretKey
```

### 執行查詢

```bash
# 查詢上個月帳單（預設）
python main.py

# 查詢指定月份
python main.py --month 2025-09

# 指定設定檔路徑
python main.py --info_path conf/tencent.json --config_path conf/config.ini

# 不輸出至日誌檔案
python main.py --no_file

# 不輸出至控制台
python main.py --no_console

# 指定日誌等級
python main.py --log_level INFO
```

### 作為模組引用

```python
from src.tencent import TencentAPI

tencent = TencentAPI(
    secret_id='your_secret_id',
    secret_key='your_secret_key'
)

# 查詢 2025 年 9 月帳單
tencent.get_l2_bill(month='2025-09')
tencent.get_l3_bill(month='2025-09')
```

---

## 設定檔說明

### conf/tencent.json（從 tencent.json.default 複製）

支援多帳號設定，以陣列格式填入：

```json
[
  {
    "name": "tencent",
    "secret_id": "填入騰訊雲 SecretId",
    "secret_key": "填入騰訊雲 SecretKey"
  }
]
```

| 欄位 | 說明 |
|---|---|
| `name` | 帳號識別名稱，僅用於日誌識別 |
| `secret_id` | 騰訊雲 API 金鑰 SecretId |
| `secret_key` | 騰訊雲 API 金鑰 SecretKey |

SecretId 與 SecretKey 可至「騰訊雲控制台 > 訪問管理 > API 密鑰管理」取得。

可在陣列中新增多個物件，程式會依序查詢每個帳號的帳單資料。

---

## 命令列參數說明

```
usage: main.py [-h] [--month MONTH] [--config_path CONFIG_PATH]
               [--log_path LOG_PATH] [--log_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
               [--no_console] [--no_file]
               [--max_bytes MAX_BYTES] [--backup_count BACKUP_COUNT]
               [--info_path INFO_PATH]

params:
  --month MONTH               查詢月份，格式 YYYY-MM（預設：上個月）

config:
  --config_path CONFIG_PATH   設定檔路徑（預設：conf/config.ini）

log:
  --log_path LOG_PATH         日誌檔案路徑（預設：logs/TencentAPIMain.log）
  --log_level LEVEL           日誌等級，預設 DEBUG
  --no_console                不輸出日誌至控制台
  --no_file                   不輸出日誌至檔案
  --max_bytes MAX_BYTES       單一日誌檔最大位元組數（預設：10MB）
  --backup_count COUNT        保留的舊日誌檔案數量（預設：5）

json:
  --info_path INFO_PATH       tencent.json 路徑（預設：conf/tencent.json）
```

---

## 建議注意事項

- `conf/tencent.json` 含有騰訊雲 API 金鑰，屬敏感資訊，請勿提交至版本控制。
- 查詢月份格式必須為 `YYYY-MM`，例如 `2025-09`；格式錯誤會導致時間範圍計算失敗。
- L3 帳單明細每次最多返回 100 筆，資料量大時可能需要分頁處理（目前程式僅查詢第一頁，如需全量資料請手動調整 `Offset` 參數）。
- 日誌檔案僅記錄 ERROR 等級以上的訊息，控制台則依 `--log_level` 設定輸出。
- 若同時指定 `--no_file` 與 `--no_console`，所有日誌輸出將被完全停用，程式會發出警告提示。
- 騰訊雲 API 有呼叫頻率限制，請避免頻繁重複執行，以免觸發限流。
