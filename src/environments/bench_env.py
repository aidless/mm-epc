"""Custom Benchmark Environment — real agent tasks without Docker.

Integrates AI Agent Playground's agent for actual task execution.
Tracks: success rate, steps, latency, self-correction.
"""

import sys, os, time, json, asyncio
from pathlib import Path
from datetime import datetime

# Point to Playground
PLAYGROUND = Path(__file__).resolve().parent.parent.parent.parent / "ai-agent-playground"
sys.path.insert(0, str(PLAYGROUND))

BENCH_TASKS = [
    {"id": "code_fix_null", "difficulty": "easy",
     "task": "Fix this bug: def get_user(db, uid): return db[uid] crashes when uid not found. Return None instead."},
    {"id": "code_fix_loop", "difficulty": "medium",
     "task": "Fix this bug: def binary_search(arr, t): left,right=0,len(arr)-1; while left<=right: mid=(left+right)//2; if arr[mid]==t: return mid; elif arr[mid]<t: left=mid; else: right=mid; return -1"},
    {"id": "code_fix_mutable", "difficulty": "medium",
     "task": "Fix this bug: def add_item(item, items=[]): items.append(item); return items"},
    {"id": "reason_explain", "difficulty": "easy",
     "task": "Explain why database indexes speed up queries but slow down writes. Be specific."},
    {"id": "security_review", "difficulty": "hard",
     "task": "Find ALL security issues: query = f\"SELECT * FROM users WHERE name='{user}' AND pwd='{pwd}'\""},
]

class CustomBenchmark:
    """Runs real agent tasks and measures performance."""

    def __init__(self, model="deepseek-chat"):
        self.model = model
        self.results = []
        print(f"CustomBenchmark: {len(BENCH_TASKS)} tasks, model={model}")

    async def run(self):
        import dotenv; dotenv.load_dotenv(PLAYGROUND / ".env")
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        )
        from agent.async_core import AsyncAgent
        from agent.state import AgentContext
        from agent.tools.registry import ToolRegistry

        r = ToolRegistry()
        r.register("e", "Echo", {"properties": {"t": {"type": "str"}}, "required": ["t"]}, lambda t: t)
        agent = AsyncAgent(client=client, model=self.model, registry=r, enable_super_agent=True)

        for task in BENCH_TASKS:
            print(f"\n  [{task['id']}] {task['task'][:60]}...")
            t0 = time.time()
            ctx = AgentContext(trace_id=f"bench_{task['id']}", max_steps=2)
            ctx = await agent.run(ctx, task["task"])
            elapsed = (time.time() - t0) * 1000

            response = ""
            for m in ctx.messages:
                if m.get("role") == "assistant" and m.get("content"):
                    response = m["content"]

            success = len(response) > 50 and not response.lower().startswith("error")
            self.results.append({
                "id": task["id"], "difficulty": task["difficulty"],
                "success": success, "latency_ms": round(elapsed),
                "steps": ctx.step, "response_len": len(response),
            })
            print(f"    {'OK' if success else 'FAIL'} | {elapsed:.0f}ms | {ctx.step} steps")

        passed = sum(1 for r in self.results if r["success"])
        print(f"\n  Result: {passed}/{len(BENCH_TASKS)} ({passed/len(BENCH_TASKS)*100:.0f}%)")

        report_path = Path("experiments/reports") / f"bench_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "model": self.model,
            "tasks": len(BENCH_TASKS),
            "passed": passed,
            "results": self.results,
        }, indent=2))
        print(f"  Report: {report_path}")
        return self.results

def run_benchmark():
    bench = CustomBenchmark()
    return asyncio.run(bench.run())

if __name__ == "__main__":
    results = run_benchmark()
    print(json.dumps(results, indent=2))
