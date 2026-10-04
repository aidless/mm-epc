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


import json,time,urllib.request,random,re,os,traceback

DS_KEY=''
with open('/mnt/c/Users/Administrator/Desktop/ai-agent-playground/.env') as f:
    for line in f:
        m=re.match(r'DEEPSEEK_API_KEY=(.+)',line)
        if m:DS_KEY=m.group(1).strip().strip('"').strip("'")
K = _load_key("API2D_KEY")

print(f"DS_KEY={DS_KEY[:12]}... K={K[:12]}...", flush=True)

def ds(sp,up,mt=350):
    b=json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":sp or " "},{"role":"user","content":up or " "}],"max_tokens":mt,"temperature":0.7}).encode()
    r=urllib.request.Request("https://api.deepseek.com/chat/completions",data=b,method="POST")
    r.add_header("Content-Type","application/json");r.add_header("Authorization",f"Bearer {DS_KEY}")
    return json.loads(urllib.request.urlopen(r,timeout=20).read().decode())["choices"][0]["message"]["content"]

# Quick test
try:
    t=ds("test","1+1=?",mt=20)
    print(f"DS test OK: {t.strip()}", flush=True)
except Exception as e:
    print(f"DS test FAIL: {e}", flush=True)
    traceback.print_exc()

# Claude test
try:
    up="Task: 1+1=?\nA: 2\nB: 3\nOutput only A or B."
    bd=json.dumps({"model":"claude-3-5-sonnet","max_tokens":10,"temperature":0,"messages":[{"role":"user","content":up}]}).encode()
    rr=urllib.request.Request("https://oa.api2d.net/v1/messages",data=bd,method="POST")
    rr.add_header("Content-Type","application/json");rr.add_header("Authorization",f"Bearer {K}")
    resp=json.loads(urllib.request.urlopen(rr,timeout=20).read().decode())
    txt=resp["content"][0]["text"].strip().upper()
    print(f"Claude test OK: '{txt}'", flush=True)
except Exception as e:
    print(f"Claude test FAIL: {e}", flush=True)
    traceback.print_exc()

# Run 1 full round with full debug
print("\n--- Full round test ---", flush=True)
try:
    o=ds("专家。逐步推理。","1+2*3=?",mt=100)
    print(f"DS1 OK: {o[:60]}", flush=True)
    c=ds("专家。逐步推理。","1+2*3=?",mt=100)
    print(f"DS2 OK: {c[:60]}", flush=True)
    
    up=f"Task: 1+2*3=?\nA (step): {o[:200]}\nB (step): {c[:200]}\nOutput only A or B."
    bd=json.dumps({"model":"claude-3-5-sonnet","max_tokens":10,"temperature":0,"messages":[{"role":"user","content":up}]}).encode()
    rr=urllib.request.Request("https://oa.api2d.net/v1/messages",data=bd,method="POST")
    rr.add_header("Content-Type","application/json");rr.add_header("Authorization",f"Bearer {K}")
    resp=json.loads(urllib.request.urlopen(rr,timeout=20).read().decode())
    txt=resp["content"][0]["text"].strip().upper()
    print(f"Claude: '{txt}'", flush=True)
    print("SUCCESS", flush=True)
except Exception as e:
    print(f"FAIL:", flush=True)
    traceback.print_exc()
