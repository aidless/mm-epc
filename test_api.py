"""Quick API connectivity test for all providers."""
def _load_key(name: str) -> str:
    """读取敏感 key：环境变量优先 -> 同目录/.env 兜底 -> 缺失时报错。

    整改说明：原文件曾硬编码真实 key（已泄露并吊销，见 git 历史）。
    此后一律通过环境变量或 .env 提供，禁止写回代码。
    """
    import os
    v = os.environ.get(name, "").strip()
    if v:
        return v
    here = os.path.dirname(os.path.abspath(__file__))
    for d in (here, os.getcwd()):
        p = os.path.join(d, ".env")
        if os.path.isfile(p):
            with open(p, encoding="utf-8", errors="ignore") as fh:
                for line in fh:
                    line = line.strip()
                    if line.startswith(name + "="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
    raise SystemExit(
        f"[config] 缺少 {name}: 请 export {name}=... 或在脚本同目录 .env 写 {name}=... (不要写进代码)"
    )


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
BAILIAN_KEY = _load_key("BAILIAN_KEY")
API2D_KEY = _load_key("API2D_KEY")

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
