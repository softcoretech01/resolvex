import re
import subprocess
import os

with open('templates/Tickets.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Extract all content between <script> and </script>
script_match = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if script_match:
    js_code = script_match.group(1)
    temp_file = 'scratch/temp_script.js'
    os.makedirs('scratch', exist_ok=True)
    with open(temp_file, 'w', encoding='utf-8') as tf:
        tf.write(js_code)
    
    # Run node -c on the temp file
    result = subprocess.run(['node', '-c', temp_file], capture_output=True, text=True)
    if result.returncode == 0:
        print("SYNTAX OK")
    else:
        print("SYNTAX ERROR:")
        print(result.stderr)
else:
    print("No script tag found")
