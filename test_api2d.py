"""Test API2D connectivity with recharged account."""
import urllib.request, json, time

API2D_KEY = "fk241999-dPFrOvXaTNUcFN3fFqBKL3bXgaJYlVc7"

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
