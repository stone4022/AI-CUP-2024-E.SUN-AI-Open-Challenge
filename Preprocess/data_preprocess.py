import os
import json
import csv
from opencc import OpenCC
from langchain_community.document_loaders import PyPDFLoader

# Initialize OpenCC converter (Simplified to Traditional Chinese)
cc = OpenCC('s2t')

# Define folder paths for datasets
folder_paths = ["./datasets/finance", "./datasets/insurance"]
json_file_path = "./datasets/faq/pid_map_content.json"

# Global variable `pages` to store processed documents
pages = []

async def load_pdf_content(file_path):
    """
    Load content from a PDF file and concatenate it into a single string.

    Args:
        file_path (str): Path to the PDF file.
    
    Returns:
        str: Concatenated content of all PDF pages.
    """
    loader = PyPDFLoader(file_path)
    all_page_content = []
    
    async for page in loader.alazy_load():
        all_page_content.append(page.page_content)
    return "\n".join(all_page_content)

async def process_files():
    """
    Main function to process PDF, txt, csv, and JSON files, storing results in the global `pages` list.

    - PDF files are loaded with `load_pdf_content` and concatenated.
    - TXT files are loaded and converted from Simplified to Traditional Chinese.
    - CSV files are loaded row by row, converted from Simplified to Traditional Chinese, and prefixed with a header.
    - JSON FAQ files containing Q&A pairs are processed and stored as concatenated entries.

    Returns:
        None
    """
    # Process PDF, txt, and csv files in each folder
    for folder_path in folder_paths:
        files = [f for f in os.listdir(folder_path) if f.endswith((".pdf", ".txt", ".csv"))]
        
        for file in files:
            file_path = os.path.join(folder_path, file)
            file_number = os.path.splitext(file)[0] 
            category = os.path.basename(os.path.normpath(folder_path))  

            if file.endswith(".pdf"):
                concatenated_content = await load_pdf_content(file_path)

            elif file.endswith(".txt"):
                with open(file_path, 'r', encoding='utf-8') as txt_file:
                    content = txt_file.read()
                    concatenated_content = cc.convert(content)

            elif file.endswith(".csv"):
                concatenated_content = ["這是一份csv格式的參考資料\n"]
                with open(file_path, 'r', encoding='utf-8-sig') as csv_file:
                    reader = csv.reader(csv_file)
                    for row in reader:
                        row_content = cc.convert(",".join(row))
                        concatenated_content.append(row_content)
                concatenated_content = "\n".join(concatenated_content)

            metadata = {"source": file_number, "category": category}
            pages.append({"page_content": concatenated_content, "metadata": metadata})

    # Process JSON FAQ files
    with open(json_file_path, 'r', encoding='utf-8') as file:
        faq_data = json.load(file)

    # Process each source in the JSON file
    for source, qa_list in faq_data.items():
        all_qa_content = []

        for qa in qa_list:
            question = qa["question"]
            answers = "\n".join(qa["answers"])
            qa_content = f"這是一個問答對參考資料\n問題: {question}\n答案: {answers}"
            all_qa_content.append(qa_content)

        concatenated_content = "\n\n".join(all_qa_content)
        metadata = {"source": source, "category": "faq"}
        pages.append({"page_content": concatenated_content, "metadata": metadata})

    print("All files processed successfully.")

async def load_data():
    """
    Load and process all data files, storing the results and returning the `pages` list.

    Returns:
        list: A list of dictionaries containing the content and metadata of all processed files.
    """
    await process_files()
    return pages  
