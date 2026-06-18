"""Quick API connectivity test for all providers."""
import urllib.request, json, re, os, sys

# Read DeepSeek key
DS_KEY = ""
for p in [
    os.path.expanduser("~/AppData/Local/hermes/.env"),
    os.path.expanduser("~/.hermes/.env"),
    os.path.expanduser("~/.ccx/.env"),
]:
    try:
        with open(p, encoding="utf-8") as f:
            for line in f:
                m = re.match(r'DEEPSEEK_API_KEY=(.+)', line)
                if m:
                    DS_KEY = m.group(1).strip().strip('"').strip("'")
                    break
        if DS_KEY:
            break
    except FileNotFoundError:
        continue

# Bailian key from user
BAILIAN_KEY = "sk-ab5c91f75f414e57ad5c04089a3ee0df"
API2D_KEY = "fk241999-dPFrOvXaTNUcFN3fFqBKL3bXgaJYlVc7"

results = {}

# Test 1: DeepSeek executor (generation)
if DS_KEY:
    try:
        body = json.dumps({
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content": "Say hello in one word."}],
            "max_tokens": 10, "temperature": 0
        }).encode()
        req = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {DS_KEY}")
        resp = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
        results["deepseek_gen"] = f"OK: {resp['choices'][0]['message']['content']}"
    except Exception as e:
        results["deepseek_gen"] = f"FAIL: {e}"

# Test 2: Bailian Qwen as evaluator
try:
    body = json.dumps({
        "model": "qwen-plus",
        "messages": [{
            "role": "user",
            "content": "Evaluate. Task: 1+1=?\nA (step_by_step): 1+1 = 2 (basic arithmetic)\nB (direct): 2\nBetter? Output only A or B."
        }],
        "max_tokens": 5,
        "temperature": 0
    }).encode()
    req = urllib.request.Request(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        data=body, method="POST"
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {BAILIAN_KEY}")
    resp = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
    results["bailian_qwen_plus"] = f"OK: '{resp['choices'][0]['message']['content']}'"
except Exception as e:
    results["bailian_qwen_plus"] = f"FAIL: {e}"

# Test 3: Bailian Qwen-turbo (cheaper alternative)
try:
    body = json.dumps({
        "model": "qwen-turbo",
        "messages": [{
            "role": "user",
            "content": "Evaluate. Task: 1+1=?\nA (step_by_step): 1+1 = 2\nB (direct): 2\nBetter? Output only A or B."
        }],
        "max_tokens": 5,
        "temperature": 0
    }).encode()
    req = urllib.request.Request(
        "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions",
        data=body, method="POST"
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {BAILIAN_KEY}")
    resp = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
    results["bailian_qwen_turbo"] = f"OK: '{resp['choices'][0]['message']['content']}'"
except Exception as e:
    results["bailian_qwen_turbo"] = f"FAIL: {e}"

# Test 4: API2D status
try:
    body = json.dumps({
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": "Say hi"}],
        "max_tokens": 5
    }).encode()
    req = urllib.request.Request("https://oa.api2d.net/v1/chat/completions", data=body, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {API2D_KEY}")
    resp = urllib.request.urlopen(req, timeout=10)
    results["api2d"] = f"OK: {json.loads(resp.read().decode())['choices'][0]['message']['content']}"
except urllib.error.HTTPError as e:
    results["api2d"] = f"HTTP {e.code}: {e.read().decode()[:200]}"
except Exception as e:
    results["api2d"] = f"FAIL: {e}"

# Test 5: DeepSeek as evaluator
if DS_KEY:
    try:
        body = json.dumps({
            "model": "deepseek-chat",
            "messages": [{
                "role": "user",
                "content": "Evaluate. Task: 1+1=?\nA (step_by_step): 1+1 = 2 (basic arithmetic)\nB (direct): 2\nBetter? Output only A or B."
            }],
            "max_tokens": 5,
            "temperature": 0
        }).encode()
        req = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body, method="POST")
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {DS_KEY}")
        resp = json.loads(urllib.request.urlopen(req, timeout=15).read().decode())
        results["deepseek_eval"] = f"OK: '{resp['choices'][0]['message']['content']}'"
    except Exception as e:
        results["deepseek_eval"] = f"FAIL: {e}"

# Print results
for k, v in results.items():
    print(f"  {k}: {v}")
