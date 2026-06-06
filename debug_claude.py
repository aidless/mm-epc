import json,time,urllib.request,random,re,os,traceback

DS_KEY=''
with open('/mnt/c/Users/Administrator/Desktop/ai-agent-playground/.env') as f:
    for line in f:
        m=re.match(r'DEEPSEEK_API_KEY=(.+)',line)
        if m:DS_KEY=m.group(1).strip().strip('"').strip("'")
K='fk241999-dPFrOvXaTNUcFN3fFqBKL3bXgaJYlVc7'

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
