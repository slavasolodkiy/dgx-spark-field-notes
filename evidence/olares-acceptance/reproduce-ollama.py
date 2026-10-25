"""Run against the existing Olares Ollama Service; never pulls a model.
Usage: python3 reproduce-ollama.py http://<existing-ollama-service>:11434 evidence-dir
Run from the host's authorized Control Hub terminal or an existing authorized client.
"""
import json
import pathlib
import sys
import time
import urllib.request

base, destination = sys.argv[1:3]
out = pathlib.Path(destination)
out.mkdir(parents=True, exist_ok=True)
request = {
    "model": "qwen2.5:0.5b",
    "messages": [{"role": "user", "content": "Summarize this maintenance note in three concise bullet points, preserving all numbers: The backup runs daily at 02:00. Keep 7 daily copies and 4 weekly copies. A restore test is required every month. Alert the operator if the backup fails."}],
    "stream": False,
    "keep_alive": "5m",
    "options": {"temperature": 0, "seed": 42, "num_ctx": 2048, "num_predict": 160},
}
(out / "request.json").write_text(json.dumps(request, indent=2))
started = time.perf_counter()
with urllib.request.urlopen(urllib.request.Request(
    base.rstrip('/') + '/api/chat', data=json.dumps(request).encode(),
    headers={'Content-Type': 'application/json'}), timeout=180) as response:
    result = json.load(response)
wall = time.perf_counter() - started
(out / "response.json").write_text(json.dumps(result, indent=2))
metrics = {"wall_seconds": wall,
           "eval_count": result.get("eval_count"),
           "eval_duration_ns": result.get("eval_duration"),
           "tokens_per_second": result.get("eval_count", 0) * 1e9 / max(result.get("eval_duration", 1), 1)}
(out / "metrics.json").write_text(json.dumps(metrics, indent=2))
print(json.dumps(metrics, indent=2))
print(result.get("message"))
