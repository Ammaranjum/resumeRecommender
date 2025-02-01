

import groq
import pypdf
from flask import Flask, request, jsonify
from flask_cors import CORS
import json

# Create Flask app ONCE at the top
app = Flask(__name__)
CORS(app)  # Allow requests from frontend

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file using PyPDF."""
    reader = pypdf.PdfReader(pdf_file)
    text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    return text

def analyze_text_with_groq(text,requirments):
    """Send extracted text to Groq AI model and get structured JSON response."""
    client = groq.Client(api_key="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")
    response = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=[
    {
        "role": "system",
        "content": (
            "You are an ATS analyzer. Compare the resume against each job requirement. Return only a JSON object:"
            "{"
            "'experience': float,"
            "'skills': {"
            "    'matched': [], # Skills found in both resume and requirements"
            "    'missing': [], # Required skills not found in resume"
            "},"
            "'education': {'degree': str, 'cgpa': float},"
            "'requirements_match': {" 
            "    'met': [], # List of met requirements"
            "    'partially_met': [], # List of partially met requirements"
            "    'unmet': [] # List of unmet requirements"
            "},"
            "'score': int, # Overall match 0-100 based on requirements"
            "'feedback': str # Brief analysis focused on key requirements gaps"
            "}"
        )
    },
    {
        "role": "user",
        "content": f"Resume: {text}\n\nJob Requirements: {requirments}"
    }
]

    )
    return response.choices[0].message.content

@app.route("/extract-text", methods=["GET", "POST"])
def extract_from_pdf():
    print("reached the endpoint")
    if "pdf" not in request.files:
        return jsonify({"error": "No PDF file provided"}), 400
    pdf_file = request.files["pdf"]
    requirments = request.form.get("requirements")

    extracted_text = extract_text_from_pdf(pdf_file)
    structured_data = analyze_text_with_groq(extracted_text, requirments)
    print(structured_data)
    # output = jsonify({"data": structured_data})
    
    return structured_data




if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)