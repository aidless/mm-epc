import json,time,urllib.request,random,re,os

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

S={"step_by_step":"逐步推理","critical_check":"先答再审","first_principles":"基本原理","creative_leap":"创新方案","analogy_meta":"类比举例","evidence_cite":"引用依据","synthesis":"综合视角","counterfactual":"反例边界"}
T=[{"t":"verify","q":"1+2*3=?","a":"7"},{"t":"verify","q":"5//2=?","a":"2"},{"t":"verify","q":"git撤销commit?","a":"reset --soft"},{"t":"code","q":"写回文函数。"},{"t":"code","q":"写二分查找。"},{"t":"reasoning","q":"8硬币1假最少称?"},{"t":"design","q":"设计短链接。"},{"t":"explain","q":"B+树vs二叉?"},{"t":"explain","q":"HTTPS证书?"},{"t":"explain","q":"LoRA原理?"}]

w={k:1/8 for k in S};ok=0;t0=time.time()
print("Claude 3.5 Sonnet cross-model | 10 rounds")

for i in range(10):
    tk=T[i%10]
    rv=random.random()*sum(w.values());cu=0.0;st="step_by_step"
    for k,v in w.items():cu+=v
    if rv<=cu:st=k;break
    try:
        o=ds("专家。"+S[st],tk["q"]);c=ds("专家。逐步推理。",tk["q"])
        up="Task: "+tk["q"]+"\nA ("+st+"): "+o[:200]+"\nB (step): "+c[:200]+"\nOutput only A or B."
        bd=json.dumps({"model":"claude-3-5-sonnet","max_tokens":10,"temperature":0,"messages":[{"role":"user","content":up}]}).encode()
        rr=urllib.request.Request("https://oa.api2d.net/v1/messages",data=bd,method="POST")
        rr.add_header("Content-Type","application/json");rr.add_header("Authorization","Bearer "+K)
        resp=json.loads(urllib.request.urlopen(rr,timeout=25).read().decode())
        txt=resp["content"][0]["text"].strip().upper()
        hasA,hasB="A" in txt,"B" in txt
        wn="A" if(hasA and not hasB)else("B" if(hasB and not hasA)else("A" if txt.startswith("A")else"B"))
        ok+=1
        upd=0.08 if wn=="A" else -0.04
        w[st]+=upd;tot=max(0.01,sum(w.values()));w={k:max(0.01,v/tot) for k,v in w.items()}
        tot=sum(w.values());w={k:v/tot for k,v in w.items()}
        print("  [%2d] %-20s ->%s top=%s(%d%%) %ds"%(i+1,st,wn,max(w,key=w.get),int(w[max(w,key=w.get)]*100),int(time.time()-t0)))
        time.sleep(0.5)
    except Exception as e:print("  [%2d] ERR:%s"%(i+1,str(e)[:60]))

wv=list(w.values());mean_w=sum(wv)/len(wv);std_w=(sum((v-mean_w)**2 for v in wv)/len(wv))**0.5
pci=round(std_w/max(0.001,mean_w),4);top=max(w,key=w.get)
print("\nE_CLAUDE: %s(%.3f) PCI=%.4f"%(top,w[top],pci))
print("5组: counterfactual(.461) | synthesis(.451) | evidence_cite(.251) | creative_leap(.384) | %s(%.4f)"%(top,pci))
print("%s"%("ALL DIFFERENT!" if top not in ["counterfactual","synthesis","evidence_cite","creative_leap"] else "overlap"))

os.makedirs("experiments",exist_ok=True)
with open("experiments/epc_claude_final.json","w") as f:
    json.dump({"top":top,"pci":pci,"weights":{k:round(v,3) for k,v in w.items()}},f)
