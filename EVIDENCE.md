# Evidence index — assembled 25 October 2026

## Three evidence levels

**A — attached raw evidence.** Olares acceptance contains request/response JSON, counters, selected deployed Pod metadata, runtime logs, OCI metadata, the exact image workflow and output. Driver failure also has a diagnostic excerpt. These files can be inspected and cross-checked; collection itself was performed by the user's AI operator, not by the author of this assembled package.

**B — contemporaneous technical report.** Earlier DGX OS and installation reports were uploaded during the experiments and recovered from the conversation. They add exact conditions and results, but most referenced raw bundles are not available here. A report is not upgraded to raw evidence merely because it has been re-packaged.

**C — user-confirmed observation.** Physical/UEFI actions, successful LarePass activation, actual Web Desktop access, Windows guest GUI, larger display resolution and remote desktop sessions are confirmed in the recorded conversation/screenshots. Screenshots containing account information are not republished. Exact final display resolution is not asserted.

| Claim | Evidence | Level / boundary |
|---|---|---|
| 120B model on factory DGX OS; warm mean 43.565 tok/s | `reports/dgxos/sprint1-report.md`; `dgx-spark-gpt-oss-report.md` | B; three identical prompts, possible caching, raw timing JSON absent |
| 64,688 input tokens | `reports/dgxos/sprint2-report.md` | B; output truncated, no long-context quality evaluation |
| Parallel aggregate 63.62 tok/s | `reports/dgxos/sprint3a-report.md` | B; distinct configuration/aggregate metric; not single-user decode |
| Z-Image result | `reports/dgxos/sprint3e-report.md`, `outputs/dgxos-z-image-turbo-seed42.png` | B plus actual output; output alone does not prove timing |
| Vision/Whisper GPU tests | `reports/dgxos/sprint3f-report.md` | B; clean synthetic fixtures, small sample |
| Secure Boot/NVML causal chain | `reports/installation/spark-olares-install-failure.md` and `*-evidence.txt` | A/B; logs show signature rejection and missing library |
| Driver repair/HAMi readiness | `reports/installation/spark-olares-gpu-recovery.md` | B; successful initialization, not a stress test |
| Arbitrary Pod rejected | `reports/installation/sprint7a-report.md` | B; scheduler rejection, not failed CUDA execution |
| Qwen GPU inference | `evidence/olares-acceptance/evidence/response.json`, `metrics.json`, `ollama-gpu-log.txt`, `ollama-pod-selected.json` | A; one warmed acceptance response |
| ComfyUI success | `evidence/olares-acceptance/evidence/comfy/history.json`, `runtime-log.txt`, `timing.json`, PNG | A; one core graph, optional plugins not accepted |
| FreeToken backend amd64-only | `evidence/olares-acceptance/evidence/freetoken-manifest.yaml`, `freetoken-image.json` | A; only the inspected package/version, not a universal future claim |
| Windows/CRD/resolution | `reports/windows/sprint7b-report.md` plus user confirmations | B/C; report is historical and incomplete, final exact resolution missing |
| Browser agent controls remote GUI end-to-end | Not established by this package | Separate experiment; not promoted to a verified claim here |
| Olares faster/slower than DGX OS | Not established | Different models, versions, workflows and measurement conditions |

The original acceptance README says DGX OS evidence was absent **from its own package**. That statement remains true about that subdirectory. The assembled repository now adds earlier reports, not the missing raw bundles. Do not silently rewrite source reports to erase the distinction.

Private host/account identifiers were removed from earlier report copies. Original numeric metrics and model/container digests were preserved. The supplied acceptance subdirectory is byte-for-byte unchanged and keeps its own original hash manifest.
