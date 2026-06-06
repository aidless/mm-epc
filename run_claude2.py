import json,time,urllib.request,random,re,os,traceback,sys

DS_KEY=''
with open('/mnt/c/Users/Administrator/Desktop/ai-agent-playground/.env') as f:
    for line in f:
        m=re.match(r'DEEPSEEK_API_KEY=(.+)',line)
        if m:DS_KEY=m.group(1).strip().strip('"').strip("'")
K='fk241999-dPFrOvXaTNUcFN3fFqBKL3bXgaJYlVc7'

def ds(sp,up,mt=350):
    b=json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":sp or " "},{"role":"user","content":up or " "}],"max_tokens":mt,"temperature":0.7}).encode()
    r=urllib.request.Request("https://api.deepseek.com/chat/completions",data=b,method="POST")
    r.add_header("Content-Type","application/json");r.add_header("Authorization",f"Bearer {DS_KEY}")
    return json.loads(urllib.request.urlopen(r,timeout=20).read().decode())["choices"][0]["message"]["content"]

def claude_eval(task, ans_a, ans_b, strat_a):
    up = f"Task: {task}\nA ({strat_a}): {ans_a[:200]}\nB (step_by_step): {ans_b[:200]}\nOutput only A or B."
    bd = json.dumps({"model":"claude-3-5-sonnet","max_tokens":10,"temperature":0,"messages":[{"role":"user","content":up}]}).encode()
    rr = urllib.request.Request("https://oa.api2d.net/v1/messages",data=bd,method="POST")
    rr.add_header("Content-Type","application/json");rr.add_header("Authorization",f"Bearer {K}")
    resp = json.loads(urllib.request.urlopen(rr,timeout=25).read().decode())
    txt = resp["content"][0]["text"].strip().upper()
    hasA, hasB = "A" in txt, "B" in txt
    if hasA and not hasB: return "A"
    if hasB and not hasA: return "B"
    return "A" if txt.startswith("A") else "B"

S={"step_by_step":"逐步推理","critical_check":"先答再审","first_principles":"基本原理","creative_leap":"创新方案","analogy_meta":"类比举例","evidence_cite":"引用依据","synthesis":"综合视角","counterfactual":"反例边界"}
T=[{"t":"verify","q":"1+2*3=?","a":"7"},{"t":"verify","q":"5//2=?","a":"2"},{"t":"verify","q":"git撤销commit?","a":"reset --soft"},{"t":"code","q":"写回文判断函数。"},{"t":"code","q":"写二分查找。"},{"t":"reasoning","q":"8硬币1假币(轻)最少称几次?"},{"t":"design","q":"设计URL短链接系统核心组件。"},{"t":"explain","q":"数据库索引为何用B+树而非二叉搜索树?"},{"t":"explain","q":"HTTPS握手证书验证步骤?"},{"t":"explain","q":"LoRA高效微调核心原理?"}]

w={k:1/8 for k in S}; ok=0; t0=time.time()

print("="*50, flush=True)
print("Claude 3.5 Sonnet -> DeepSeek | 10 rounds", flush=True)
print("="*50, flush=True)

for i in range(10):
    tk = T[i%10]
    rv = random.random()*sum(w.values()); cu=0.0; st="step_by_step"
    for k,v in w.items(): cu+=v
    if rv<=cu: st=k; break
    
    try:
        o = ds(f"你是专家。策略：{S[st]}", tk["q"], mt=350)
        sys.stderr.write(f"  [{i+1}] DS1 OK\n")
        c = ds("你是专家。策略：逐步推理。", tk["q"], mt=350)
        sys.stderr.write(f"  [{i+1}] DS2 OK\n")
        
        wn = claude_eval(tk["q"], o, c, st)
        sys.stderr.write(f"  [{i+1}] Claude={wn}\n")
        
        ok += 1
        upd = 0.08 if wn=="A" else -0.04
        w[st] += upd
        tot = max(0.01, sum(w.values()))
        w = {k: max(0.01, v/tot) for k,v in w.items()}
        tot = sum(w.values())
        w = {k: v/tot for k,v in w.items()}
        
        print(f"  [{i+1:2d}] {st:20s} claude->{wn} top={max(w,key=w.get)}({w[max(w,key=w.get)]:.0%}) {int(time.time()-t0)}s", flush=True)
        time.sleep(0.5)
    except Exception as e:
        print(f"  [{i+1:2d}] FAIL: {e}", flush=True)
        traceback.print_exc()

wv=list(w.values()); mean_w=sum(wv)/len(wv)
std_w=(sum((v-mean_w)**2 for v in wv)/len(wv))**0.5
pci=round(std_w/max(0.001,mean_w),4); top=max(w,key=w.get)

print(f"\nE_CLAUDE: {ok} rounds | top={top}({round(w[top],3)}) | PCI={pci}", flush=True)
print("Weights:", {k:round(v,3) for k,v in sorted(w.items(),key=lambda x:-x[1])}, flush=True)
