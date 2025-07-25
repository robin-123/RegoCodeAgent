import os
from flask import Flask, render_template, request
from groq import Groq
import pandas as pd
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Get the API key from the environment
#api_key = os.environ.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY environment variable not set. Please create a .env file and add your key.")

client = Groq(
    api_key=api_key,
)

def generate_rego_with_groq(question, columns):
    prompt = f"""
    You are an expert Rego code generator. Your task is to convert a natural language query into a valid Rego policy.

    The data you are working with has the following columns: {columns}

    The user's query is: "{question}"

    Based on the query and the columns, generate a single Rego rule.

    - The rule should be named 'allow' for permissive queries (e.g., "allow", "permit") and 'deny' for restrictive queries (e.g., "deny", "block", "reject").
    - Use the columns provided to construct the rule.
    - Ensure the value in the rule is properly quoted (e.g., "USA").
    - If the query involves numbers, do not quote the number.

    Example 1:
    Query: "Allow access if the country is USA"
    Rego Code:
    allow = true {{
        input.country == "USA"
    }}

    Example 2:
    Query: "Deny if the age is less than 18"
    Rego Code:
    deny = true {{
        input.age < 18
    }}

    Now, generate the Rego code for the user's query.
    Rego Code:
    """

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama3-8b-8192",
        )
        rego_code = chat_completion.choices[0].message.content
        return rego_code
    except Exception as e:
        return f"# Error generating Rego code: {e}"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_rego():
    if 'csv_file' not in request.files: # Corrected from 'file' to 'csv_file'
        return "No file part"
    file = request.files['csv_file'] # Corrected from 'file' to 'csv_file'
    if file.filename == '':
        return "No selected file"
    if file:
        try:
            df = pd.read_csv(file)
            columns = df.columns.tolist()
        except Exception as e:
            return f"Error reading CSV file: {e}"

        question = request.form['question']
        rego_code = generate_rego_with_groq(question, columns)

        return render_template('index.html', rego_code=rego_code)

if __name__ == '__main__':
    app.run(debug=True)
