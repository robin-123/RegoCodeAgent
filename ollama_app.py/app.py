from flask import Flask, render_template, request
import os
import pandas as pd
import chardet
import ollama

def create_app():
    app = Flask(__name__)
    app.config['UPLOAD_FOLDER'] = 'uploads'

    def generate_rego_with_ollama(question, columns):
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
            response = ollama.chat(model='llama3', messages=[
                {
                    'role': 'user',
                    'content': prompt,
                },
            ])
            rego_code = response['message']['content'].strip()
            return rego_code
        except Exception as e:
            return f"# Error generating Rego code: {e}"

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/generate', methods=['POST'])
    def generate():
        if 'csv_file' not in request.files:
            return 'No file part'
        file = request.files['csv_file']
        if file.filename == '':
            return 'No selected file'
        if file:
            filename = file.filename
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            with open(filepath, 'rb') as f:
                result = chardet.detect(f.read())
            
            df = pd.read_csv(filepath, encoding=result['encoding'])
            columns = [col.lower() for col in df.columns]

            question = request.form['question']
            rego_code = generate_rego_with_ollama(question, columns)

            return render_template('index.html', rego_code=rego_code)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
