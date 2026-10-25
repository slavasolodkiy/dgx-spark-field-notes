# One Spark. Two software stacks. Real local AI outputs.


## The product question

One Spark, two software stacks, one owner — and the AI assistant that owner already uses. Beyond model execution, this case compares the practical route from first boot to remote work, and the identity/permissions architecture around personal and shared access.

Read [Product field notes](PRODUCT_FIELD_NOTES.md) for the two experience layers and the connection to my earlier reflections after hearing Jensen in London. The [technical evidence](EVIDENCE.md) remains separate: observed outcomes, documented capabilities and my product conclusions have different roles.

**Slava Solodkiy · field evidence, 22–25 October 2026**

A NVIDIA DGX Spark supplied by NVIDIA as a prize/gift, as reported by its owner: first exercised with its factory DGX OS, then clean-installed with the Spark-specific OlaresOS ARM64 image. This is an independently written field case, not a NVIDIA/Olares endorsement, production certification, or controlled OS performance ranking.

The practical question: **Can it run AI — and can the AI assistant its owner already uses help operate it?** An AI-assisted operator ran commands and inspected outputs. The owner handled cabling, UEFI, LarePass, approvals and independent visual checks. This was not an unattended installation and does not demonstrate an entirely offline agent workflow.

## Start here

- [Evidence index and claim boundaries](EVIDENCE.md)
- [Final Olares AI acceptance: original 64-file package](evidence/olares-acceptance/README.md)
- [NVIDIA driver / Secure Boot failure](reports/installation/spark-olares-install-failure.md)
- [Driver recovery](reports/installation/spark-olares-gpu-recovery.md)
- [DGX OS warm LLM series](reports/dgxos/sprint1-report.md)
- Companion static page: `site/dgx-spark.html` in the publication ZIP. It is a prepared file, not a claim of deployment.

## Two environments, not an A/B ranking

| | DGX OS phase | OlaresOS phase |
|---|---|---|
| Hardware | Same physical GB10 Spark; 128 GB advertised unified memory; 4 TB SSD | Same machine after clean installation |
| OS / kernel, recorded | Ubuntu 24.04.5; 7.0.0-1019-nvidia | Ubuntu 24.04.3; 6.14.0-1015-nvidia |
| NVIDIA driver | 580.178.04 | 595.84 open ARM64 |
| LLM serving | Native Ollama 0.40.8 | Market `ollamallmbasev3`, chart 1.3.18, Ollama 0.40.2, application-owned Kubernetes workload |
| Demonstrated LLM | gpt-oss:120b MXFP4 | Qwen2.5 0.5B Q4_K_M |
| Image workflow | Z-Image-Turbo BF16, 1024×1024, 8 steps | SD 1.5 FP16, 512×512, 20 steps |
| Operator access | SSH, NVIDIA Sync / Dashboard; Tailscale checked before OS replacement | Olares Web Desktop / Control Hub; Windows ARM64 VM, Chrome Remote Desktop |

The model, runtime, kernel, driver, memory quotas and image workflows differ. **Do not divide their speeds to claim that either OS is faster.** The previously configured DGX OS Tailscale identity is not presumed to survive replacement. CPU/GPU share memory; HAMi quotas are not additional physical VRAM.

## Results

### DGX OS — earlier reports recovered, raw benchmark bundles not included

- **120B local LLM:** three identical warmed requests averaged **43.565 generated tokens/s**, **7.912 s** end-to-end, 341 output tokens per request; temperature 0, seed 42, think=low, context 4096. Prompt caching is possible. [Sprint 1](reports/dgxos/sprint1-report.md)
- **Long context:** **64,688 input tokens** processed; output capped at 192 tokens. The 64K-window run included context/model reinitialization. This did not validate retrieval quality across the context. [Sprint 2](reports/dgxos/sprint2-report.md)
- **Concurrency:** four configured slots and four clients reached **63.62 aggregate tokens/s**; 42 measured requests across settings, no observed API/OOM failure. Tiny p95 samples were effectively maxima. [Sprint 3A](reports/dgxos/sprint3a-report.md)
- **Image generation:** Z-Image-Turbo 1024×1024, 8 steps, **14.064 s**, repeated in **17.582 s**. Sampling re-executed and outputs matched; the first run was not a pristine cold benchmark. Extra mug and unwanted lettering violated the prompt. [Sprint 3E](reports/dgxos/sprint3e-report.md)
- **Audio and vision:** CUDA Whisper on one 7.849 s synthetic English clip took **1.437 / 0.716 / 0.729 s**, WER 0% on those 24 words. Gemma 3 4B GPU vision worked, but still confused a colour and a remaining-item count. [Sprint 3F](reports/dgxos/sprint3f-report.md)
- **Two-node path:** a client on the separate Minisforum OlaresOS host called the Spark's DGX OS Ollama over a temporary SSH forward. The estimated additional client/network/SSH component was about 1 ms, not an exact isolated network measurement or a distributed model. [Sprint 4A](reports/dgxos/sprint4a-report.md)

### OlaresOS — raw responses, selected runtime metadata and output included

- **Ollama PASS:** Qwen2.5 0.5B, **25/25 layers offloaded**, 100% GPU reported; warm 42-token generation **117.47 tokens/s**, **0.410618 s** client wall. The OpenAI-compatible application endpoint also returned an answer. The source facts were retained, but a request for three bullets produced five. [Measured acceptance](evidence/olares-acceptance/sprint7b-report.md)
- **ComfyUI core PASS; optional plugins PARTIAL:** one uncached SD 1.5 workflow, **512×512**, 20 Euler steps, seed 42; **9.41 s** by the application log, **10.132 s** client polling wall. Output exists and opens. The prompt asked for a white pot/wooden table; the result had a brown pot/bluish surface. Twelve optional node packages failed imports; the tested core graph did not need them. [Raw history](evidence/olares-acceptance/evidence/comfy/history.json)
- **Specific FreeToken package BLOCKED:** `freetokenqwen3635ba3bnvfp4` 1.0.4 and its inspected container were amd64-only. This is not a claim that every FreeToken implementation cannot support ARM64. [Manifest](evidence/olares-acceptance/evidence/freetoken-manifest.yaml)
- **No observed new Xid/OOM in checked windows; VM remained up.** These snapshots are not a long-term reliability result.

## What broke, and what the evidence supports

1. **DGX OS GSP timeout:** Xid 119/154 occurred. A single normal reboot eventually restored access and subsequent GPU checks. The original cause remains unknown; the initial ten-minute observation window did not establish a failed boot. [Recovery observation](reports/dgxos/sprint3c-report.md), [later successful GPU workloads](reports/dgxos/sprint3f-report.md)
2. **Olares ISO driver stage:** Secure Boot rejected the unsigned NVIDIA module (`Key was rejected by service`). The aborted installation also left NVML missing. Olares waited at `InstallPlugin → CheckGPUState`, with no device-plugin Pod selected. This was not demonstrated driver/GB10 incompatibility. [Failure report](reports/installation/spark-olares-install-failure.md), [diagnostic excerpt](reports/installation/spark-olares-install-failure-evidence.txt)
3. **Targeted repair:** the owner disabled Secure Boot in UEFI; the operator completed the matching 595.84 open-module/userspace installation and ran the supported GPU enable command. CUDA/NVML initialized, HAMi became ready. Disabling Secure Boot alone would not restore absent libraries. This lab change is not a blanket production-security recommendation. [Recovery](reports/installation/spark-olares-gpu-recovery.md)
4. **Partial installation reset:** after code review, the owner used LarePass's install-phase uninstall/install to recreate the incomplete cluster without reinstalling the base OS. This is a recorded action, not a universally safe recovery recipe for existing installations with data.
5. **Activation TLS:** an initial handshake failure was followed by successful activation without a demonstrated TLS configuration repair. Provisioning delay was suspected, not proven. Do not rewrite this as a diagnosed network root cause.
6. **Application ownership:** a standalone CUDA Pod was rejected before execution (`pod has no owner application`). It was not bypassed. A normal Market-owned application subsequently ran inference. [Sprint 7A](reports/installation/sprint7a-report.md), [actual assigned Pod](evidence/olares-acceptance/evidence/ollama-pod-selected.json)
7. **Windows ARM64:** the earlier diagnosis found an installed x86 Chrome Remote Desktop Host running through Windows compatibility; MSI success was not the same as completed host registration. A signed ARM64 VirtIO display driver was already in DriverStore; the virtual device change was authorized. The owner later confirmed remote connection and a larger resolution after Windows Update. Exact final resolution and a complete post-change driver dump are not included. No NVIDIA GPU passthrough claim is made. [Historical diagnostics](reports/windows/sprint7b-report.md)

## Product feedback derived from this run

These are recommendations, not claims about an unpublished vendor roadmap:

- Check driver signing and Secure Boot **before** allowing an AI-platform installation to spend minutes waiting for an impossible GPU readiness state.
- Show the failing dependency, not only a percentage or generic `system-error`; make retry scope explicit.
- Distinguish desktop management, terminal access and a streamed physical/guest GUI in onboarding.
- Treat ARM64 app variants and optional plugin dependencies as separately testable compatibility contracts.
- Make an operator handoff small and machine-readable: actual state, last successful step, logs, safe next action and actions needing a person.

## Reproducing what is reproducible

Olares request/workflow clients and their inputs are included under [evidence/olares-acceptance](evidence/olares-acceptance). They expect an already installed, authorized application endpoint; they do not install models or replace cluster policy. Review them before executing. Reuse the specified model digest and workflow to repeat the acceptance scenario, rather than interpreting these short runs as a performance ranking.

Earlier DGX OS reports reference raw JSON/logs/scripts that are not included here. Their tables are retained at **report-level evidence**, not represented as independently re-run results. The original Z-Image output PNG is included in `outputs/`.

## Integrity and scope

The supplied Olares archive contained 64 files: **63/63 listed files matched its SHA-256 manifest** (the manifest does not hash itself). Those files are preserved unchanged in the acceptance subdirectory. Earlier report copies have host identifiers redacted; numbers are unchanged. Root `SHA256SUMS.txt` covers this assembled repository.

No new tests were run to create this publication package. No account credentials, private console URLs, cloud billing screenshots, personal inbox messages, model weights, ISO files or VM disks are included. See [NOTICE.md](NOTICE.md) for source/excerpt handling.


## Author’s public context

Related essays, original social notes, and cross-posts (not independent benchmark evidence) are catalogued in [PUBLIC_WRITING.md](PUBLIC_WRITING.md). The contest video link was intentionally omitted at the author’s request.
