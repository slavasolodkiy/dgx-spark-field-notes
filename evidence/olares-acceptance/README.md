# Sprint 7B acceptance

Read `sprint7b-report.md` for the Russian technical report and `evidence-index.md` for the evidence map.

- **Ollama PASS:** official Olares Market instance, Ollama 0.40.2, Qwen2.5 0.5B Q4_K_M, GB10 CUDA v13, 25/25 GPU layers. Warm generation 117.47 tok/s; 42 output tokens; 0.411 s client wall time. The full Olares OpenAI-compatible API also passed.
- **ComfyUI PASS for core text-to-image, PARTIAL for optional plugins:** download completed; on 2026-10-25 the official ARM64 application generated a real 512×512 SD 1.5 FP16 image on GB10 in 9.41 s. PyTorch 2.11.0+cu128, ComfyUI 0.42.1, 20 Euler steps, seed 42. Image and raw history are included. Twelve optional custom-node packages failed imports due to missing dependencies; no plugin repairs or extra scenarios were attempted. The engine was stopped through Launcher after the test; app and weights are retained.
- **FreeToken BLOCKED:** the inspected official Olares package and container are amd64-only. No ARM64 backend runtime was tested.

No gpt-oss:120b download. No defensible direct performance comparison with the user-reported DGX OS 120B baseline. No host reboot or driver, network, HAMi, or global Kubernetes changes.

`SHA256SUMS.txt` covers the distributed files after account/device-identifier redaction. Model weights, credentials and complete deployment dumps are not included.

## Handoff
All 64 files are packaged under public/. Start with sprint7b-report.md and evidence-index.md. The report separates user-reported DGX OS context from measured OlaresOS results, includes a chronological handoff and explicitly lists missing evidence. Do not describe the historical DGX OS number as a reproduced benchmark. No new tests were run for this packaging step.
