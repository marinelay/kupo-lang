# Custom Language IDE using Flask and Cloudflare (GitHub + Cloudflare Pages Auto Deployment)

from flask import Flask, render_template, request, jsonify
import subprocess
import os

app = Flask(__name__)

@app.route('/')
def index():
    return '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Custom Language IDE</title>
        <style>
            body { font-family: Arial, sans-serif; padding: 20px; }
            textarea { width: 100%; height: 300px; }
            button { padding: 10px 15px; margin-top: 10px; }
            pre { background-color: #f0f0f0; padding: 10px; }
        </style>
    </head>
    <body>
        <h1>Custom Language IDE</h1>
        <textarea id="code" placeholder="Write your code here..."></textarea><br>
        <button onclick="runCode()">Run</button>
        <h3>Output:</h3>
        <pre id="output"></pre>

        <script>
            async function runCode() {
                const code = document.getElementById("code").value;
                const response = await fetch("https://kuppo-lang.pages.dev", {
                    method: "POST",
                    headers: { "Content-Type": "application/x-www-form-urlencoded" },
                    body: new URLSearchParams({ code })
                });
                const result = await response.json();
                document.getElementById("output").innerText = result.stdout + "\n" + result.stderr;
            }
        </script>
    </body>
    </html>
    '''

@app.route('/run_code', methods=['POST'])
def run_code():
    print("OK")
    code = request.form.get('code')
    file_path = "temp.kupo"

    with open(file_path, "w") as file:
        file.write(code)

    try:
        result = subprocess.run(["python", "kuppolang.py", file_path], capture_output=True, text=True)
        return jsonify({"stdout": result.stdout, "stderr": result.stderr})
    except Exception as e:
        return jsonify({"stdout": "", "stderr": str(e)})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)