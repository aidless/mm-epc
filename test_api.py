import json, urllib.request, re, os, time

# Read API keys
with open(r"C:\Users\Administrator\Desktop\ai-agent-playground\.env") as f:
    for line in f:
        if m := re.match(r'API2D_KEY=(.+)', line):
            API2D_KEY = m.group(1).strip().strip('"').strip("'")
            break

print(f"API2D_KEY: {API2D_KEY[:10]}...")

# Test GPT-4o call
try:
    b = json.dumps({
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Say 'hello'"}],
        "max_tokens": 5,
        "temperature": 0
    }).encode()
    r = urllib.request.Request("https://oa.api2d.net/v1/chat/completions", data=b, method="POST")
    r.add_header("Content-Type", "application/json")
    r.add_header("Authorization", f"Bearer {API2D_KEY}")
    resp = urllib.request.urlopen(r, timeout=10)
    result = json.loads(resp.read().decode())
    print(f"✅ GPT-4o test success: {result['choices'][0]['message']['content']}")
except Exception as e:
    print(f"❌ GPT-4o test failed: {e}")