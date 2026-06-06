"""Test: run train_phase with just 2 rounds to debug"""
import json, urllib.request, re, time, os, sys
from copy import deepcopy
import random

sys.stdout.reconfigure(line_buffering=True)

DS_KEY, API2D_KEY = "", ""
with open(r"C:\Users\Administrator\Desktop\ai-agent-playground\.env") as f:
    for line in f:
        if m := re.match(r'DEEPSEEK_API_KEY=(.+)', line):
            DS_KEY = m.group(1).strip().strip('"').strip("'")
        if m := re.match(r'API2D_KEY=(.+)', line):
            API2D_KEY = m.group(1).strip().strip('"').strip("'")

def ds(sp, up, temp=0.7, mt=400, retry=3):
    for attempt in range(retry):
        try:
            b = json.dumps({"model":"deepseek-chat","messages":[{"role":"system","content":sp or " "},{"role":"user","content":up or " "}],"max_tokens":mt,"temperature":temp}).encode()
            r = urllib.request.Request("https://api.deepseek.com/chat/completions", data=b, method="POST")
            r.add_header("Content-Type","application/json")
            r.add_header("Authorization", f"Bearer {DS_KEY}")
            resp = urllib.request.urlopen(r, timeout=30)
            return json.loads(resp.read().decode())["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"  [DS attempt {attempt+1} failed: {e}]", flush=True)
            if attempt == retry-1: raise
            time.sleep(2**attempt)

def gpt4o_eval(task, ans_a, ans_b, strat_a, retry=3):
    for attempt in range(retry):
        try:
            up = f"""Evaluate objectively. Task: {task}
A ({strat_a}): {ans_a[:300]}
B (step_by_step): {ans_b[:300]}
Which is better? Output only A or B."""
            b = json.dumps({"model":"gpt-4o","messages":[{"role":"user","content":up}],"max_tokens":5,"temperature":0}).encode()
            r = urllib.request.Request("https://oa.api2d.net/v1/chat/completions", data=b, method="POST")
            r.add_header("Content-Type","application/json")
            r.add_header("Authorization", f"Bearer {API2D_KEY}")
            resp = urllib.request.urlopen(r, timeout=35)
            txt = json.loads(resp.read().decode())["choices"][0]["message"]["content"].strip().upper()
            return "A" if "A" in txt else ("B" if "B" in txt else ("A" if txt.startswith("A") else "B"))
        except Exception as e:
            print(f"  [GPT4o attempt {attempt+1} failed: {e}]", flush=True)
            if attempt == retry-1: raise
            time.sleep(2**attempt)

STRATEGIES = {
    "step_by_step":"逐步推理",
    "critical_check":"先答再审",
    "first_principles":"基本原理",
}

TEXT_TASKS = [
    {"mod":"text","q":"1+2*3=?","a":"7"},
    {"mod":"text","q":"5//2=?","a":"2"},
]

def train_phase(name, task_list, initial_weights, rounds, eval_fn):
    w = deepcopy(initial_weights)
    history = []
    
    for i in range(rounds):
        tk = task_list[i % len(task_list)]
        rv = random.random() * sum(w.values())
        cu = 0.0; st = "step_by_step"
        for k, v in w.items():
            cu += v
            if rv <= cu: st = k; break
        
        print(f"  Round {i+1}: strategy={st}, task={tk['q'][:30]}", flush=True)
        
        try:
            print(f"    Calling DS (strategy agent)...", flush=True)
            o = ds(f"你是专家AI。策略：{STRATEGIES[st]}", tk["q"])
            print(f"    DS response: {o[:50]}...", flush=True)
            
            print(f"    Calling DS (baseline)...", flush=True)
            c = ds("你是专家AI。策略：逐步推理。", tk["q"])
            print(f"    DS baseline: {c[:50]}...", flush=True)
            
            print(f"    Calling GPT-4o eval...", flush=True)
            wn = eval_fn(tk["q"], o, c, st)
            print(f"    GPT-4o result: {wn}", flush=True)
            
            upd = 0.08 if wn == "A" else -0.04
            w[st] += upd
            tot = max(0.01, sum(w.values()))
            w = {k: max(0.01, v/tot) for k, v in w.items()}
            tot = sum(w.values())
            w = {k: v/tot for k, v in w.items()}
            
            print(f"    Weights: {w}", flush=True)
            
        except Exception as e:
            print(f"    ERROR: {e}", flush=True)
            history.append({"round": i+1, "error": str(e)[:80]})
            continue
    
    return w, history

print("Starting 2-round test...", flush=True)
init = {k: 1/len(STRATEGIES) for k in STRATEGIES}
print(f"Initial weights: {init}", flush=True)
w, h = train_phase("test", TEXT_TASKS, init, 2, gpt4o_eval)
print(f"\nFinal weights: {w}", flush=True)
print("Done!", flush=True)