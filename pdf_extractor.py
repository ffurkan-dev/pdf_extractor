import os
import json
from typing import Dict, Any
import google.generativeai as genai
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Google Generative AI
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
if not GOOGLE_API_KEY:
    raise ValueError("Please set GOOGLE_API_KEY in your .env file")

genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-pro')

def load_schema():
    """Load the funding details schema from JSON file."""
    try:
        with open('funding_details.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        raise Exception(f"Error loading schema: {str(e)}")

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text content from a PDF file."""
    try:
        reader = PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise Exception(f"Error reading PDF file: {str(e)}")

def create_schema_prompt(schema) -> str:
    """Create a structured prompt based on the schema."""
    prompt_parts = ["Please extract the following information from the text and format it as JSON:"]
    
    for field in schema:
        if field.get("children"):
            if isinstance(field["children"], list):
                child_desc = []
                for child in field["children"]:
                    if isinstance(child, dict) and child.get("children"):
                        sub_children = [f"- {subchild['name']}: {subchild['description']}" 
                                      for subchild in child["children"]]
                        child_desc.extend(sub_children)
                    else:
                        child_desc.append(f"- {child['name']}: {child['description']}")
                prompt_parts.append(f"{field['name']} ({field['description']}):\n" + "\n".join(child_desc))
        else:
            prompt_parts.append(f"{field['name']}: {field['description']}")
    
    return "\n\n".join(prompt_parts)

def extract_json_from_response(text: str) -> Dict[str, Any]:
    """Extract JSON from the response text, handling various formats."""
    # Try to find JSON content between triple backticks
    try:
        if "```json" in text:
            start = text.find("```json") + 7
            end = text.find("```", start)
            json_str = text[start:end].strip()
        elif "```" in text:
            start = text.find("```") + 3
            end = text.find("```", start)
            json_str = text[start:end].strip()
        else:
            json_str = text.strip()
        
        return json.loads(json_str)
    except Exception as e:
        raise Exception(f"Failed to parse JSON from response: {str(e)}\nResponse text: {text}")

def process_pdf_with_gemini(pdf_path: str) -> Dict[str, Any]:
    """Process PDF content using Gemini and return structured JSON data."""
    # Load schema
    schema = load_schema()
    
    # Extract text from PDF
    pdf_text = extract_text_from_pdf(pdf_path)
    
    # Create structured prompt
    schema_prompt = create_schema_prompt(schema)
    
    # Full prompt for Gemini
    prompt = f"""
    {schema_prompt}

    Analyze the following text and extract the information according to the schema above.
    IMPORTANT: Your response MUST be valid JSON wrapped in triple backticks (```json).
    If certain information is not found in the text, use null or empty arrays as appropriate.

    Text to analyze:
    {pdf_text[:12000]}  # Limiting text length to avoid token limits
    """
    
    try:
        response = model.generate_content(prompt)
        if not response.text:
            raise Exception("Empty response from Gemini")
        
        # Extract and parse JSON from the response
        result = extract_json_from_response(response.text)
        return result
    except Exception as e:
        raise Exception(f"Error processing with Gemini: {str(e)}")

def print_extracted_data(data: Dict[str, Any], indent: int = 0):
    """Print the extracted data in a readable format."""
    for key, value in data.items():
        prefix = "  " * indent
        if isinstance(value, dict):
            print(f"{prefix}{key}:")
            print_extracted_data(value, indent + 1)
        elif isinstance(value, list):
            print(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    print_extracted_data(item, indent + 1)
                else:
                    print(f"{prefix}  - {item}")
        else:
            if value is None:
                value = "Not found"
            print(f"{prefix}{key}: {value}")

def main():
    # Get PDF file path from user
    pdf_path = input("Enter the path to the PDF file: ")
    
    if not os.path.exists(pdf_path):
        print(f"Error: File '{pdf_path}' not found.")
        return
    
    try:
        print(f"\nProcessing {pdf_path}...")
        result = process_pdf_with_gemini(pdf_path)
        
        print("\nExtracted Information:")
        print("=====================")
        print_extracted_data(result)
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 