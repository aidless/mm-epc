"""Minimal test: simulate one round of train_phase with debug"""
import json, urllib.request, re, time, os, sys

sys.stdout.reconfigure(line_buffering=True)

# API keys
DS_KEY, API2D_KEY = "", ""
with open(r"C:\Users\Administrator\Desktop\ai-agent-playground\.env") as f:
    for line in f:
        if m := re.match(r'DEEPSEEK_API_KEY=(.+)', line):
            DS_KEY = m.group(1).strip().strip('"').strip("'")
        if m := re.match(r'API2D_KEY=(.+)', line):
            API2D_KEY = m.group(1).strip().strip('"').strip("'")

print(f"DS_KEY: {DS_KEY[:15]}...", flush=True)
print(f"API2D_KEY: {API2D_KEY[:15]}...", flush=True)

# Test 1: DeepSeek call
print("\n[Test 1] DeepSeek call...", flush=True)
try:
    b = json.dumps({
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "你是专家AI。策略：逐步推理"},
            {"role": "user", "content": "1+2*3=?"}
        ],
        "max_tokens": 100,
        "temperature": 0.7
    }).encode()
    r = urllib.request.Request("https://api.deepseek.com/chat/completions", data=b, method="POST")
    r.add_header("Content-Type", "application/json")
    r.add_header("Authorization", f"Bearer {DS_KEY}")
    resp = urllib.request.urlopen(r, timeout=30)
    content = json.loads(resp.read().decode())["choices"][0]["message"]["content"]
    print(f"✅ DeepSeek: {content[:80]}", flush=True)
except Exception as e:
    print(f"❌ DeepSeek FAILED: {e}", flush=True)
    sys.exit(1)

# Test 2: GPT-4o evaluation
print("\n[Test 2] GPT-4o eval...", flush=True)
try:
    up = "Evaluate objectively. Task: 1+2*3=?\nA (step_by_step): 1+2*3=1+6=7\nB (step_by_step): 7\nWhich is better? Output only A or B."
    b = json.dumps({
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": up}],
        "max_tokens": 5,
        "temperature": 0
    }).encode()
    r = urllib.request.Request("https://oa.api2d.net/v1/chat/completions", data=b, method="POST")
    r.add_header("Content-Type", "application/json")
    r.add_header("Authorization", f"Bearer {API2D_KEY}")
    resp = urllib.request.urlopen(r, timeout=35)
    result = json.loads(resp.read().decode())
    print(f"✅ GPT-4o eval: {result['choices'][0]['message']['content'].strip()}", flush=True)
except Exception as e:
    print(f"❌ GPT-4o FAILED: {e}", flush=True)
    sys.exit(1)

print("\n✅ All tests passed!", flush=True)