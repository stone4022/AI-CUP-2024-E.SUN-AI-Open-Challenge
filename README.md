
# AI CUP 2024玉山人工智慧公開挑戰賽

此專案提供文件檢索系統用於參加AI CUP 2024玉山人工智慧公開挑戰賽初賽，透過 OpenAI API 從預處理過的資料集中，根據問題識別最相關的文件。系統會處理儲存在特定目錄中的文件，轉換成字典格式用於檢索，最終透過官方提供的問題集生成對應格式的JSON檔。

## 目錄

- [專案結構](#專案結構)
- [安裝與設定](#安裝與設定)
- [使用方式](#使用方式)
- [設定說明](#設定說明)
- [範例](#範例)
- [輸出格式](#輸出格式)

## 專案結構

```
.
├── Preprocess/
│   └── data_preprocess.py                # 加載和處理文件的腳本
│   └── exploratory_data_analysis.py      # 確認 PDF 文件內容性質(純文字、純圖片、混合)
├── Model/
│   └── retrieval.py                      # 使用 OpenAI API 的檢索模型
├── main.py                               # 執行檢索的主程式
├── questions_preliminary.json            # 包含使用者問題和相關元數據的 JSON 文件
└── requirements.txt                      # 依賴項列表
```

- **Preprocess**：包含 `data_preprocess.py` 腳本，用於加載和處理文件。
- **Model**：包含 `retrieval.py` 腳本，定義了用於查詢處理後文件的 `RetrievalModel` 類別。
- **main.py**：執行檢索系統的主程式。

## 安裝與設定

1. **複製專案**：
   ```bash
   git clone https://github.com/stone4022/AI-CUP-2024-E.SUN-AI-Open-Challenge.git
   cd AI-CUP-2024-E.SUN-AI-Open-Challenge
   ```

2. **下載處理後的資料集**：

   由於原始資料集中的部分 PDF 僅包含圖片，本專案已對其中內容進行手動文字提取，將其轉換成可檢索的 `txt` 和 `csv` 格式。請先從以下雲端連結下載處理後的資料集 `datasets.rar`，並將其解壓縮至專案的主目錄：
   
   [由 Google 雲端下載](https://drive.google.com/file/d/1YpfDvjFP1nTzJXdlUl8oA5AUrWw5VIla/view?usp=drive_link)

3. **安裝依賴項**：
   使用 `requirements.txt` 安裝所需套件：
   ```bash
   pip install -r requirements.txt
   ```

4. **設定 OpenAI API 金鑰**：
   將 `main.py` 中的 `YOUR_API_KEY` 替換為您的實際 OpenAI API 金鑰。
## 使用方式

執行檢索系統，使用以下指令：

```bash
python main.py
```

系統將執行以下操作：
- 從 `questions_preliminary.json` 加載問題。
- 使用 `data_preprocess.py` 處理並加載指定目錄中的文件。
- 使用 `RetrievalModel` 為每個問題找到最佳匹配的文件。
- 將檢索結果儲存至 JSON 文件 `pred_retrieve.json`。

## 設定說明

- **questions_preliminary.json**：此文件包含問題列表及其相關元數據，格式如下：
  ```json
  {
    "questions": [
      {
        "qid": 1,
        "source": [334, 523, 501, 369, 11, 498, 354, 388],
        "query": "這份保險契約的組成部分有哪些？",
        "category": "insurance"
      },
      ...
    ]
  }
  ```

- **文件目錄**：預設情況下，系統會在 `datasets/finance` 和 `datasets/insurance` 中尋找文件，並在 `datasets/faq` 中尋找 JSON 問答文件。如有需要，可以在 `data_preprocess.py` 中調整這些路徑。

## 範例

執行腳本的範例：

```bash
python main.py
```

預期輸出：
```
Processing rows: 100%|██████████████████████████| 100/100 [00:10<00:00, 10.00it/s]
檢索結果已保存到 pred_retrieve.json
```

## 輸出格式

- 結果會儲存在 `pred_retrieve.json` 中，格式如下：
  ```json
  {
    "answers": [
      {"qid": 1, "retrieve": 334},
      {"qid": 2, "retrieve": 523},
      ...
    ]
  }
  ```

每個條目包含問題 ID (`qid`) 和最佳匹配的文件 ID (`retrieve`)。

## 注意事項

- 確保 OpenAI API 金鑰有效，並且有足夠的配額來處理請求。
- 本專案採用非同步處理，以便在處理大型數據集時提高效率。
