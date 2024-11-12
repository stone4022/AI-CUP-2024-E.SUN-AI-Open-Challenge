import json
import re
import random
import time
import openai

class RetrievalModel:
    """
    A model for retrieving the most relevant document based on a given question and a set of document sources.
    Uses the OpenAI API to determine the best match from a list of pre-processed documents.

    Attributes:
        client (openai.OpenAI): OpenAI client initialized with API key for model interactions.
        max_retries (int): Maximum number of retries for API requests in case of errors.
        SYSTEM_PROMPT (str): System prompt guiding the API on how to process questions and responses.
        json_dict (dict): Dictionary mapping (source, category) keys to document content for quick lookup.
    """

    def __init__(self, api_key, pages, max_retries=5):
        """
        Initializes the RetrievalModel with the OpenAI API client and converts page data into a lookup dictionary.

        Args:
            api_key (str): API key for OpenAI.
            pages (list): List of processed document dictionaries, each containing 'page_content' and 'metadata'.
            max_retries (int): Maximum retry attempts for API calls (default is 5).
        """
        self.client = openai.OpenAI(api_key=api_key)
        self.max_retries = max_retries
        self.SYSTEM_PROMPT = """
        From a list of articles, select the one that most closely matches the given question and return its document number in the following JSON format: {"文件編號": 123}

        # Steps

        1. **Analyze the Question**: Understand the key elements of the question to determine which article it pertains to.
        2. **Compare Articles**: Review each article in the list to identify the one that best matches the elements of the question.
        3. **Select Best Match**: Choose the article that aligns most closely with the question in terms of content and context.
        4. **Extract Document Number**: Note the document number of the selected article.

        # Output Format

        - The output should be a JSON object with the document number as an integer:
          - Example: `{"文件編號": 123}`

        # Notes

        - Consider articles' relevance and context when determining the best match.
        - Ensure that the output always follows the specified JSON format, even if the match is not perfect. If no match is possible, consider a default or null response strategy.
        """
        self.json_dict = self.load_json_dict(pages)

    def load_json_dict(self, pages):
        """
        Converts a list of page documents into a lookup dictionary.

        Args:
            pages (list): List of document dictionaries containing 'page_content' and 'metadata'.
        
        Returns:
            dict: A dictionary with keys as tuples of (source, category) and values as document contents.
        """
        return {(doc['metadata']['source'], doc['metadata']['category']): doc['page_content'] for doc in pages}

    def generate_prompt(self, question, sources, category, json_dict):
        """
        Generates a prompt for OpenAI API based on the question and the document sources provided.

        Args:
            question (str): The user's question.
            sources (list): List of document source IDs to consider.
            category (str): The category associated with the documents (e.g., 'insurance', 'finance').
            json_dict (dict): A lookup dictionary for retrieving document content by (source, category) keys.

        Returns:
            str: A formatted prompt that includes the question and the content of relevant documents.
        """
        prompt = f"問題: {question}\n請找出以下哪一個文件中包含有這個問題的答案或相關資訊，返回其文件編號。\n"

        for source_id in sources:
            key = (str(source_id), category)
            if key in json_dict:
                source_content = json_dict[key]
                prompt += f"文件編號 {source_id}:\n{source_content}\n"
            else:
                print(f"Key {key} not found in json_dict")

        prompt += "請回傳最能回答問題的文件編號, 並以下列json格式回傳: {\"文件編號\": 123}。"
        return prompt

    def get_best_match(self, question, sources, category):
        """
        Uses the OpenAI API to retrieve the most relevant document number for the given question.

        Args:
            question (str): The question or query provided by the user.
            sources (list): List of document source IDs to consider.
            category (str): The category of the documents to be checked against the question.

        Returns:
            int: The document number that best matches the given question.

        Raises:
            KeyError: If the '文件編號' key is missing in the API's JSON response.
            JSONDecodeError: If the API's response is not valid JSON.
        """
        prompt = self.generate_prompt(question, sources, category, self.json_dict)

        for attempt in range(self.max_retries):
            try:
                completion = self.client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": self.SYSTEM_PROMPT},
                        {"role": "user", "content": prompt}
                    ]
                )
                message_content = completion.choices[0].message.content
                print(f"API response for question '{question}': {message_content}")

                cleaned_message = re.sub(r'```json|```', '', message_content).strip()
                pred = json.loads(cleaned_message)
                retrieved_source = pred.get('文件編號')

                if retrieved_source is not None:
                    return int(retrieved_source)
                else:
                    raise KeyError("Missing '文件編號' in response JSON")

            except (json.JSONDecodeError, KeyError) as e:
                print(f"JSON parsing failed or missing key: {e}. Retry {attempt + 1}/{self.max_retries}")
                if attempt == self.max_retries - 1:
                    return random.choice(sources)

            except Exception as e:
                if "rate_limit_exceeded" in str(e):
                    print(f"Rate limit reached. Retrying after backoff...")
                    time.sleep(4 ** attempt)  
                    if attempt == self.max_retries - 1:
                        return random.choice(sources)
                else:
                    print(f"Unexpected error: {e}")
                    return random.choice(sources)

