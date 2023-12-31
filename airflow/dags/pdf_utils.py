from pypdf import PdfReader
import requests
from io import BytesIO
import re
import tiktoken
import pandas as pd
import openai
from urllib.parse import urlparse


def fetch_pdf_from_url(url):
    # Validate URL
    parsed_url = urlparse(url)
    if not all([parsed_url.scheme, parsed_url.netloc]):
        raise ValueError(f"Invalid URL: {url}")

    # Send an HTTP GET request to the provided URL.
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an error for failed requests
    except requests.RequestException as e:
        raise Exception(f"Failed to fetch the PDF from {url}. Error: {e}")

    # Check if the content is a valid PDF
    content = response.content
    if not content.startswith(b"%PDF"):
        raise ValueError(
            f"The content fetched from {url} does not appear to be a valid PDF."
        )

    # Return the content of the PDF as a BytesIO object.
    return BytesIO(content)


def parse_pdf_with_pypdf(pdf_data):
    """Parse the provided PDF data using pypdf and return the extracted text."""
    reader = PdfReader(pdf_data)
    text = "".join(page.extract_text() for page in reader.pages)
    return text

def parse_pdf_with_nougat(file_url, api_address):
    url = api_address + "/predict/"
    print(url)
    payload = {}
    pdf_response = requests.get(file_url)
    if pdf_response.status_code != 200:
            print(f"Failed to download PDF from {file_url}. Status code: {pdf_response.status_code}")
            return None
    
     # Extract the PDF content
    pdf_content = pdf_response.content

    files=[
    ('file',('filefromweb.pdf',pdf_content,'application/pdf'))
    ]
    
    headers = {}
    try:
        response = requests.request("POST", url, headers=headers, data=payload, files=files)

        response.raise_for_status()
        content = response.text
        return content
        
    except requests.exceptions.RequestException as e:
        print(f"Request Exception: {e}")
        return None

def get_form_number(context):
    # Define a regular expression pattern to find the form number
    form_pattern = r"FORM (\d+-[A-Z]+)"

    # Search for the pattern in the text
    match = re.search(form_pattern, context)

    if match:
        form_number = match.group(0)
        return form_number
    else:
        return None


GPT_MODEL = "gpt-3.5-turbo"  # to select which tokenizer to use


def count_tokens(text: str, model: str = GPT_MODEL) -> int:
    """Return the number of tokens in a string."""
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))


def split_context_to_rows(df, max_token):
    # Create a list of dictionaries to store the results
    result_data = []

    for index, row in df.iterrows():
        context = row["context"]
        token_count = count_tokens(context)

        # If the token count is less than or equal to max_token, add the row to the result list
        if token_count <= max_token:
            result_data.append(
                {
                    "context": context,
                    "token_count": token_count,
                    "form_url": row["form_url"],
                    "form_title": row["form_title"],
                }
            )
        else:
            # Split the context into multiple rows
            tokens = context.split()  # Split by whitespace for a rough estimation
            current_token_count = 0
            current_context = ""

            for token in tokens:
                current_token_count += count_tokens(token)  # Re-calculate token count
                current_context += token + " "

                if current_token_count >= max_token:
                    result_data.append(
                        {
                            "context": current_context,
                            "token_count": current_token_count,
                            "form_url": row["form_url"],
                            "form_title": row["form_title"],
                        }
                    )
                    current_context = ""
                    current_token_count = 0

            # If there are remaining tokens, add them to the result list
            if current_context:
                result_data.append(
                    {
                        "context": current_context,
                        "token_count": current_token_count,
                        "form_url": row["form_url"],
                        "form_title": row["form_title"],
                    }
                )

    # Create a new DataFrame from the result list
    result_df = pd.DataFrame(result_data)

    return result_df

# calculate embeddings
EMBEDDING_MODEL = "text-embedding-ada-002"  # OpenAI's best embeddings as of Apr 2023


# Define a function to generate embeddings for a single text
def generate_embeddings(text):
    # Create embeddings for the given 'text' using the specified EMBEDDING_MODEL
    response = openai.Embedding.create(model=EMBEDDING_MODEL, input=text)

    # Extract the embeddings from the API response and join them as a comma-separated string
    return response["data"][0]["embedding"]
