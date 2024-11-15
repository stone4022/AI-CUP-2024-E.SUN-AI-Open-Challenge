# 檢索模型

`retrieval.py` 腳本包含 `RetrievalModel` 類，用於根據用戶提供的問題進行文件檢索。
使用 OpenAI API: gpt-4o 從一組預處理的文件中識別最相關的文件。

## 功能簡介

### 主要功能

- **初始化**：透過 OpenAI API 客戶端和預處理文件資料初始化檢索模型。
- **文件查找字典**：將所有文件的內容轉換為便於快速查找的字典格式。
- **提示生成**：根據用戶問題及文件的來源，動態生成提示。
- **檢索最佳匹配文件**：調用 OpenAI API，透過比對多個文件來返回最佳匹配的文件編號。

### 模型核心流程

1. **建立查找字典**：`load_json_dict()` 方法將文件清單轉換為字典，鍵為 `(source, category)`，值為文件內容，便於快速查找。
2. **生成提示**：`generate_prompt()` 方法根據問題和相關文件來源生成符合 OpenAI API 格式的提示。
3. **獲取最佳匹配**：`get_best_match()` 方法使用 OpenAI API 從多個候選文件中檢索最匹配的文件，若無法匹配則通過隨機選擇來源文件處理。
4. **錯誤處理**：針對 API 錯誤（如解析錯誤或速率限制），設置了重試機制。

### 特殊處理

此模型包含多重錯誤處理步驟，確保在遇到 API 或格式錯誤時進行適當處理。若多次重試後仍無法獲取有效結果，系統會隨機選擇一個文件以返回。
