"""Test API2D connectivity with recharged account."""
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


import urllib.request, json, time

API2D_KEY = _load_key("API2D_KEY")

models = [
    ("gpt-4o", "OpenAI GPT-4o (original evaluator)"),
    ("claude-fable-5", "Claude Fable 5 (new, user-recommended)"),
    ("gpt-4o-mini", "GPT-4o-mini (cheaper alternative)"),
]

for model_id, desc in models:
    try:
        t0 = time.time()
        body = json.dumps({
            "model": model_id,
            "messages": [{"role": "user", "content": "Say 'hello' in one word."}],
            "max_tokens": 10,
            "temperature": 0
        }).encode()
        req = urllib.request.Request(
            "https://oa.api2d.net/v1/chat/completions",
            data=body, method="POST"
        )
        req.add_header("Content-Type", "application/json")
        req.add_header("Authorization", f"Bearer {API2D_KEY}")
        resp = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
        content = resp["choices"][0]["message"]["content"]
        elapsed = time.time() - t0
        print(f"  {model_id} ({desc}): OK ({elapsed:.1f}s) -> '{content}'")
    except Exception as e:
        print(f"  {model_id} ({desc}): FAIL - {e}")

# Test eval-style prompt
print("\nEval-style test (claude-fable-5):")
try:
    t0 = time.time()
    body = json.dumps({
        "model": "claude-fable-5",
        "messages": [{"role": "user", "content": "Evaluate which response is better.\nTask: 1+1=?\nA (step_by_step): 1+1 equals 2.\nB (step_by_step): The answer is 2.\nBetter? Output only A or B."}],
        "max_tokens": 5,
        "temperature": 0
    }).encode()
    req = urllib.request.Request(
        "https://oa.api2d.net/v1/chat/completions",
        data=body, method="POST"
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", f"Bearer {API2D_KEY}")
    resp = json.loads(urllib.request.urlopen(req, timeout=20).read().decode())
    print(f"  Response ({time.time()-t0:.1f}s): '{resp['choices'][0]['message']['content']}'")
except Exception as e:
    print(f"  FAIL: {e}")
