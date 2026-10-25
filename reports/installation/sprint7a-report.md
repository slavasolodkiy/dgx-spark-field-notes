> ARCHIVED REPORT: host/account identifiers redacted for publication. Measurements are unchanged. This is a contemporaneous report, not a substitute for its referenced raw files.

# Sprint 7A — OlaresOS GPU Acceptance

Дата: 2026-10-23. Узел: olares@[SPARK_LAN_IP], NVIDIA DGX Spark. Итог: **PARTIAL; Kubernetes CUDA compute — BLOCKED**. Установлен конкретный блокер планирования; GPU-ядро в Pod не выполнялось.

## Проверенные результаты

| Проверка | Результат и доказательство |
|---|---|
| Olares | PASS: 1.12.7, terminus-running, installation 100%, initialized; профиль [OLARES_ID]. Web Desktop подтверждён пользователем. |
| Kubernetes | PASS: узел olares Ready, v1.33.3+k3s1. |
| GPU host | PASS для обнаружения и инициализации: один NVIDIA GB10, драйвер 595.84, cuInit(0)=0, nvmlInit_v2()=0. Это не новый host compute benchmark. |
| HAMi | Scheduler и device plugin 2/2 Running; exporter, webui и os-gpu scheduler Running. Device split count=30, runtimeClass=nvidia. |
| GPU labels | gpu.bytetrade.io/cuda=13.2, cuda-supported=true, driver=595.84, nvidia-gb10=true. CUDA 13.2 здесь — заявленная совместимость драйвера, не версия установленного toolkit. |
| GPU allocation | nvidia.com/gpu=30 — виртуальные доли HAMi одного физического GB10, не 30 GPU и не доказательство MIG. |
| UMA/RAM | В конце: 121 GiB total, 13 GiB used, 108 GiB available; swap 1 GiB, used=0. Память CPU/GPU общая; нельзя складывать RAM и «VRAM» как независимые ёмкости. |
| Финальное здоровье | cuInit=0, NVML=0; GB10 40°C, 0% utilization, 4.99 W. Поиск NVRM Xid в текущем dmesg пуст; новых Xid во время проверки не наблюдалось. |

## Kubernetes smoke test — BLOCKED

Создан только временный Pod `default/sprint7a-cuda-smoke`: ARM64 selector, runtimeClass nvidia, один виртуальный GPU, 1 GiB memory limit, Python + CUDA Driver API/PTX (21+21, ожидается 42). Штатный admission назначил hami-scheduler. Scheduler отклонил Pod до запуска контейнера:

```text
FailedScheduling: 0/1 nodes are available: 1 pod has no owner application.
FilteringFailed: cannot schedule pod without applications.app.bytetrade.io/name label
```

Это блокер регистрации приложения Olares, не ошибка CUDA, драйвера или нехватки GPU. Образ не был запущен, результат 42 не получен. Скрипт остаётся неподтверждённым на данном runtime. Не использованы чужой application label, bypass scheduler или изменение глобальной политики. После фиксации событий удалён только созданный тестовый Pod; приложения не удалялись.

Минимальный следующий тест: оформить этот smoke test как собственное временное приложение по штатному механизму Olares, с корректной регистрацией владельца и GPU injection. Простое добавление случайного label не считается проверенным решением. Для GB10 следует следовать UMA-ветке официальных chart: память Pod, а не механически переносить дискретные VRAM quotas. В этой итерации после установления блокера дальнейшее развёртывание остановлено.

## Olares Market: проверка исходных manifests и образов

Проверен официальный [beclab/apps](https://github.com/beclab/apps/tree/47da3f2d4f926dff31d1608710ac4fabc0e6647f), commit `47da3f2d4f926dff31d1608710ac4fabc0e6647f`. Это проверка chart/source, **не runtime acceptance**; образы не скачивались, registry digests/содержимое CUDA libraries не проверены. Версия каталога, доступная установленному Market, может отличаться.

| Приложение | Подтверждённая декларация / ограничение |
|---|---|
| [Ollama v3](https://github.com/beclab/apps/tree/47da3f2d4f926dff31d1608710ac4fabc0e6647f/ollamallmbasev3) 1.3.18 | ARM64 и явная GB10/UMA ветка, Olares >=1.12.6. Образ ollama/ollama:0.40.2; GGML_CUDA_DISABLE_GRAPHS=1. RAM задаётся параметрами. Лучший кандидат для сопоставления с прежней Ollama, но GPU execution ещё не проверен. |
| [ComfyUI v3](https://github.com/beclab/apps/tree/47da3f2d4f926dff31d1608710ac4fabc0e6647f/comfyuisharev3) 1.1.38 | Явная GB10/ARM64 ветка: beclab/comfyui_launcher-arm64:v0.42.1-fe1.58.0-launcher0.2.54-arm64; GB10 RAM request 22 GiB, server limit 70 GiB (manifest aggregate limit 71 GiB), disk request 10 GiB / limit 40 GiB. |
| [vLLM v3](https://github.com/beclab/apps/tree/47da3f2d4f926dff31d1608710ac4fabc0e6647f/vllmllmbasev3) 1.2.31 | ARM64/GB10, >=1.12.6; helper выбирает vllm/vllm-openai:v0.31.0-aarch64, память GB10 через Pod quota/GPU injection. Не устанавливался. |
| [FreeToken Qwen NVFP4](https://github.com/beclab/apps/tree/47da3f2d4f926dff31d1608710ac4fabc0e6647f/freetokenqwen3635ba3bnvfp4) 1.0.4 | Только amd64; manifest прямо исключает GB10 из-за amd64-only образа 0.1.3-cu132. Этот backend для Spark не подходит. Название AI Engine само по себе не доказывает поддержку всех backend. |
| Legacy Ollama / Ollama v2 | Legacy ARM64 заявлен, но фиксированные небольшие quotas не подходят 120B. Ollama v2 требует Olares <1.12.6, поэтому не кандидат для 1.12.7. |
| Legacy ComfyUI / GPT-OSS120B llama.cpp v2 | amd64-only; GPT-OSS chart дополнительно требует Olares <1.12.6. Не выбирать для этого Spark. |

## Windows VM — только наблюдение

`windowsarm-[OLARES_USER]/windowsarm-667dcc657c-9vrrm`: 3/3 Running, 0 restarts. Образ `beclab/dockurr-windows-arm:5.14`; выбран ARM64 guest. Фактический процесс `qemu-system-aarch64`, `-cpu host`, `accel=kvm`, 4 vCPU, `-m 4G`. Pod requests 4 CPU/6 GiB, limits 12 CPU/24 GiB — это не размер памяти гостевой ОС. Диск настроен на 1000 GB growable raw; это логический размер, а не доказанные занятые 1000 GB.

Журнал показывает подготовку Windows 11 ARM64 и загрузку UEFI Windows Boot Manager с внутреннего GPT-диска. Сообщение wrapper «Windows started successfully» и Running Pod **не доказывают завершённую установку или открытие Windows Desktop**. Этот этап остаётся неподтверждённым. Конфигурация VM не менялась, ввод в гостевую ОС не выполнялся. QEMU использует ramfb; GPU passthrough не установлен и не предполагается. См. [NVIDIA: passthrough virtualization support](https://docs.nvidia.com/dgx/dgx-spark/support.html#passthrough-virtualization-support).

## Следующий измеримый inference-тест

После завершения установки VM и успешного CUDA Pod: один штатный Ollama v3 backend в режиме GB10; сначала проверить наличие прежних весов, затем отдельно согласовать необходимую загрузку gpt-oss:120b при их отсутствии. Сопоставить точный digest/quantization, prompt, num_ctx, seed, num_predict и один клиент с baseline DGX OS. Прогрев + три одинаковых тёплых запроса; streaming TTFT, end-to-end, prompt_eval_duration/count, eval_duration/count, tokens/s, RAM, температура/мощность и Xid. Подтвердить GPU offload. Не запускать одновременно ComfyUI/другие тяжёлые модели.

Baseline 40–44 tok/s получен на Ollama 0.40.8; chart использует 0.40.2 и отключает CUDA graphs, поэтому различия нельзя автоматически приписывать OlaresOS. Текущие 108 GiB available — снимок, не резерв под модель. В этом спринте AI-модели и серверы не устанавливались.

## Воспроизведение

Read-only команды: `olares-cli status`; `sudo kubectl get nodes`; `sudo kubectl get pods -A`; `sudo kubectl get node olares -o yaml`; `sudo kubectl get cm hami-scheduler-device -n kube-system -o yaml`; `nvidia-smi`; `free -h`; `sudo dmesg | grep -i 'NVRM: Xid'`.

Проверка инициализации: `python3 -c 'import ctypes; print(ctypes.CDLL("libcuda.so.1").cuInit(0)); print(ctypes.CDLL("libnvidia-ml.so.1").nvmlInit_v2())'`.

Сохранены `sprint7a-cuda-pod.json` и `sprint7a-cuda-smoke.py`. JSON воспроизводит отклонённый самостоятельный Pod, а не готовое Olares-приложение. События: `sudo kubectl get events -n default --field-selector involvedObject.name=sprint7a-cuda-smoke --sort-by=.lastTimestamp`. Очистка выполнена: `sudo kubectl delete pod sprint7a-cuda-smoke -n default --wait=false`.

Никаких reboot, изменений драйверов, VM, сетей, системной конфигурации или больших загрузок не выполнялось.
