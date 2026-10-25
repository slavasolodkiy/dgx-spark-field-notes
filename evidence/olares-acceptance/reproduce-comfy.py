"""One execution against an already-running existing ComfyUI API proxy.
Usage: python3 reproduce-comfy.py http://<existing-comfyui-service>:8190 results-dir
Requires the already-downloaded checkpoint. Does not install, pull, or start services.
"""
import json
import pathlib
import sys
import time
import urllib.request

base, destination = sys.argv[1:3]
out = pathlib.Path(destination)
out.mkdir(parents=True, exist_ok=True)
workflow = json.loads((pathlib.Path(__file__).parent / 'comfy-workflow-api.json').read_text())

def call(path, data=None):
    req = urllib.request.Request(base.rstrip('/') + path,
        data=None if data is None else json.dumps(data).encode(),
        headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=30) as response:
        return json.load(response)

started = time.perf_counter()
submission = call('/prompt', {'prompt': workflow, 'client_id': 'sprint7b-acceptance'})
(out / 'submit.json').write_text(json.dumps(submission, indent=2))
prompt_id = submission['prompt_id']
for _ in range(600):
    history = call('/history/' + prompt_id)
    if prompt_id in history:
        (out / 'history.json').write_text(json.dumps(history, indent=2))
        (out / 'timing.json').write_text(json.dumps({
            'wall_seconds': time.perf_counter() - started,
            'poll_interval_seconds': 1, 'prompt_id': prompt_id}, indent=2))
        print(json.dumps(history[prompt_id]['status'], indent=2))
        if history[prompt_id]['status'].get('status_str') != 'success':
            raise SystemExit('Workflow failed; inspect history.json')
        break
    time.sleep(1)
else:
    raise SystemExit('Timed out waiting for history; inspect the existing server queue before retrying')
