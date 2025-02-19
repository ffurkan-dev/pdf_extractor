# PDF Data Extractor using Gemini

This tool extracts data from PDF files and converts it into structured JSON format using Google's Gemini AI model.

## Setup

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Get a Google API key:
   - Go to https://makersuite.google.com/app/apikey
   - Create a new API key
   - Copy the API key

3. Configure the API key:
   - Open the `.env` file
   - Replace `your_api_key_here` with your actual Google API key

## Usage

1. Place your PDF files in the same directory as the script
2. Run the script:
```bash
python pdf_extractor.py
```

The script will:
- Process all PDF files in the current directory
- Extract text content from each PDF
- Use Gemini to analyze the content and structure it
- Save the results in JSON files (one for each PDF) with the naming format: `{original_filename}_extracted.json`

## Output

The extracted data will be saved in JSON format with the following structure:
- Title (if found)
- Main topics or sections
- Key points or findings
- Dates, numbers, and significant data

Each PDF will generate its own JSON file with the extracted and structured data. 