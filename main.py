from Preprocess.data_preprocess import load_data
from Model.retrieval import RetrievalModel
import json
from tqdm import tqdm

async def main():
    with open('questions_preliminary.json', 'r', encoding='utf-8') as f:
        questions_data = json.load(f)

    questions = questions_data['questions']
    pages = await load_data() 
    retrieval_model = RetrievalModel(api_key="YOUR_API_KEY", pages=pages)
    preds = []

    # Iterate over each question and use the retrieval model to find the best match
    for row in tqdm(questions, total=len(questions), desc="Processing rows"):
        sources = row['source']
        category = row['category']
        best_match = retrieval_model.get_best_match(row['query'], sources, category)
        preds.append({"qid": row['qid'], "retrieve": best_match})

    # Save prediction results to a JSON file
    output_file_path = 'pred_retrieve.json'
    with open(output_file_path, 'w', encoding='utf-8') as f:
        json.dump({"answers": preds}, f, ensure_ascii=False, indent=4)

    print("Retrieval results saved to pred_retrieve.json")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
