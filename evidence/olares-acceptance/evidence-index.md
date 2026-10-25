# Evidence index

LLM measurements are from 2026-10-24; ComfyUI execution is from 2026-10-25. API timestamps use UTC.

| Files | What they establish |
|---|---|
| `evidence/request.json`, `response-first.json`, `metrics-first.json` | First actual Ollama request, including preload overlap |
| `evidence/response.json`, `metrics.json` | Same request after preload; primary warm measurement |
| `evidence/openai-request.json`, `openai-response.json`, `proxy-smoke.log`, `openai-models.json` | Full Olares llm-init OpenAI-compatible request path |
| `evidence/ollama-gpu-log.txt`, `ollama-ps.txt`, `ps-after.json` | CUDA v13, GB10, 25/25 layers, 100% GPU |
| `evidence/ollama-pod-selected.json` | Selected live Pod metadata: application ownership, HAMi assignment, image, resources, restarts |
| `evidence/tags.json` | Actual cached model digest, size, quantization |
| `evidence/baseline.txt`, `memory-*.txt`, `pods-*.txt`, `kernel-*.txt`, `gpu-final.txt` | Resource and limited stability snapshots. Empty kernel files mean zero matching Xid/OOM lines |
| `evidence/*manifest.yaml`, `*-server.yaml`, `apps-commit.txt` | Public official Olares app specifications; these are source templates, not deployed secrets |
| `evidence/*-image.json`, `comfy-oci-manifest.json` | Docker Hub architecture, digest and compressed layer sizes; not runtime proof |
| `evidence/checkpoint-source.json`, `image-model-size.json`, `checkpoint-sha256.txt` | Comfy-Org checkpoint metadata and verified downloaded SHA-256 |
| `evidence/download-progress.txt` | Historical incomplete-download snapshot from October 24; resolved on October 25 |
| `reproduce-ollama.py` | Reproduction request; does not download or install software |
| `comfy-workflow-api.json`, `reproduce-comfy.py` | The single SD 1.5 workflow executed successfully on October 25 and its reproduction client |
| `evidence/comfy/history.json`, `submit.json`, `timing.json` | Successful execution, no cached nodes, output filename, raw timing |
| `evidence/comfy/system-stats.json`, `runtime-log.txt`, `pod-selected.json` | Actual ComfyUI/PyTorch/CUDA versions, GB10, HAMi binding, GPU loading and optional-plugin failures |
| `evidence/comfy/sprint7b_sd15_seed42_00001_.png`, `image-sha256.txt` | Generated image, visually inspected; original PNG metadata preserved |
| `evidence/comfy/launcher-*.json`, `memory-*.txt`, `pods-after.txt`, `kernel-*.txt` | Launcher start/stop and limited stability evidence |

Personal account labels and device identifiers are redacted in distributed evidence. Numeric inference metrics and model/container digests are preserved. The archive does not include credentials, complete Kubernetes deployment dumps, model weights, container images, or the earlier Windows diagnostics.

The historical DGX OS result (40–44 tok/s for gpt-oss:120b) is user-supplied context; no raw DGX OS measurement is present in this archive.

## Handoff chronology
The report's final handoff section distinguishes direct measurements from user-confirmed history. No primary DGX OS benchmark or full early-install/Windows-repair logs are included. The chronological summary is a synthesis of existing evidence and conversation, not an additional experiment.
