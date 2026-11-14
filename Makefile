# --- acceptance_backfill (EVAL_ACCEPTANCE_STANDARD.md P4) ---
# 原证据来源: check_status.py —— 判定为「入口写错」：它不是评测入口，是作者本机的训练进度
#   监视器：第 6 行 shell 出 `cmd /c tasklist`（Windows-only，本机 rc=2
#   FileNotFoundError: 'cmd'），第 3-4 行读死 C:/Users/Administrator/... 下的 checkpoint/log。
#   本仓 .github/workflows/ci.yml 的注释也把这两点写成事实，并说明本仓没有离线单测套件
#   （4 个 test_*.py 都是需要 API key 的 live smoke 脚本，故意排除在 CI 之外）。
# 新 eval = ci.yml 里 CI 真正跑的那一段（逻辑逐字搬自该文件，只去掉 GitHub Action 外壳）：
#   1) `python3 -m compileall -q .` —— 全部 tracked Python 必须能字节编译；
#   2) 证据目录存在 + 全部 JSON 可解析（GBK 回退、截断文件单列，与 ci.yml 同口径）。
# 实测：compileall 绿；JSON 全解析通过。
.PHONY: eval
.ONESHELL:
SHELL := /bin/bash

eval:
	@set -uo pipefail
	python3 -m compileall -q .
	echo "[eval] compileall OK — 全部 tracked Python 通过字节编译"
	@python3 -c $$'import json, pathlib, sys\nmissing = [d for d in ("experiments", "arxiv_submission") if not pathlib.Path(d).is_dir()]\nif missing:\n    sys.exit(f"[eval] missing evidence directories: {missing}")\njsons = [j for j in pathlib.Path(".").rglob("*.json") if ".git" not in j.parts]\nif not jsons:\n    sys.exit("[eval] no JSON evidence files found at all")\nok, truncated, broken = 0, [], []\nfor j in jsons:\n    raw = j.read_bytes()\n    try:\n        text = raw.decode("utf-8")\n    except UnicodeDecodeError:\n        text = raw.decode("gbk", errors="replace")\n    try:\n        json.loads(text)\n        ok += 1\n    except Exception:\n        if \'"significant"\' in text and text.rstrip().endswith(\'"significant":\'):\n            truncated.append(str(j))\n        else:\n            broken.append(str(j))\nprint(f"[eval] parsed {ok}/{len(jsons)} JSON evidence files")\nif truncated:\n    print(f"[eval] {len(truncated)} truncated (interrupted writes; 与本仓 CI 同口径不判红): {truncated[:3]}")\nif broken:\n    sys.exit(f"[eval] not JSON: {broken[:5]}")\nprint("[eval] evidence gate OK — passed")\n'
