# DGX Spark — Sprint 7B: AI software & models acceptance

Даты проверки: 24–25 октября 2026. Последнее обновление: 25 октября 2026. Измерения API и журналов — UTC. Это продолжение Sprint 7B; прежний отчёт от 23 октября сохранён отдельно и описывает состояние до этих тестов.

| Приложение | Итог | Практический результат |
|---|---|---|
| Ollama v3 / Qwen 0.5B | **PASS** | Реальный GB10 inference, 25/25 GPU layers, работающий OpenAI API; прогретый ответ 0.411 s |
| ComfyUI | **PASS для базового text-to-image; PARTIAL для дополнительных плагинов** | SD 1.5 FP16, 512×512, 20 steps: реальная генерация на GB10 за 9.41 s; изображение сохранено |
| FreeToken | **BLOCKED** | Штатный backend и образ amd64-only, GB10 исключён |

Definition of Done выполнен: подтверждены полноценный GPU LLM inference и практически полезный сценарий text-to-image на GB10 внутри штатных приложений. Матрица ограничена тремя приложениями и одним workflow ComfyUI.

## Подтверждённый LLM inference

**Ollama v3 — PASS для GPU inference и API.** Штатный экземпляр `Sprint 7B Qwen` создан через Olares Market из `ollamallmbasev3`, chart 1.3.18, Ollama 0.40.2. Модель `qwen2.5:0.5b`, 494.03M параметров, Q4_K_M, digest `a8b0c51577010a279d933d14c2a8ab4b268079d44c5c8830c0a93900f1827c67`. Веса около 398 MB. Контейнер ARM64 — около 2.81 GB сжатых слоёв.

Установлено штатным механизмом приложений: в Pod присутствуют application owner/name/raw-app-name labels, владелец ReplicaSet, `schedulerName=hami-scheduler`, `runtimeClassName=nvidia`, `hami.io/bind-phase=success`. Обход application ownership не применялся. Контейнер Ollama: request/limit памяти 4 GiB, GPU share 1, CPU limit 6.

Подтверждение offload: CUDA backend `/usr/lib/ollama/cuda_v13/libggml-cuda.so`, GB10 compute capability 12.1; журнал `offloaded 25/25 layers to GPU`; `ollama ps` показывает `100% GPU`; `/api/ps` — `size_vram=size=442803158` байт и контекст 2048. Показатель HAMi 4352 MiB — виртуальная квота, а не физическая ёмкость unified memory. CUDA v12 сначала отклонил GB10 по списку скомпилированных архитектур, после чего корректно выбран CUDA v13.

Параметры Market: `OLLAMA_KEEP_ALIVE=5m OLLAMA_CONTEXT_LENGTH=2048 OLLAMA_FLASH_ATTENTION=1 OLLAMA_KV_CACHE_TYPE=q8_0 OLLAMA_NUM_PARALLEL=1`; требуемая память `4Gi`, mode Chat, supports None. Штатный chart также задаёт `GGML_CUDA_DISABLE_GRAPHS=1`, однако runtime пишет `USE_GRAPHS=1` и `graphs reused`; фактическое отключение графов **не подтверждено**.

## Измерения

Один сценарий: кратко пересказать инструкцию резервного копирования с сохранением времени и количества копий. Temperature 0, seed 42, context 2048, максимум 160 выходных токенов. Один первый запрос, один повтор после завершения preload и одна проверка того же сценария через OpenAI-совместимый API приложения.

| Путь / состояние | Выходных токенов | Время генерации | Скорость генерации | Полное время клиента |
|---|---:|---:|---:|---:|
| Ollama `/api/chat`, первый запрос во время preload | 42 | 0.252416 s | 166.39 tok/s | 21.197924 s |
| Ollama `/api/chat`, прогретый повтор | 42 | 0.357545 s | 117.47 tok/s | 0.410618 s |
| llm-init `/v1/chat/completions` | 42 | API не сообщает | не рассчитывалась | 0.413673 s |

Формула: `eval_count / eval_duration × 1e9`, где duration в наносекундах. Это короткий acceptance smoke test, не статистический benchmark. Первый запрос перекрылся с preload (журнал сообщает 93 s preload), поэтому его полное время нельзя выдавать за нормальную задержку прогретой модели. Скорость зависит от фоновой нагрузки; в это время выполнялась загрузка ComfyUI. Prompt cache использовался; исходные счётчики сохранены в JSON. TTFT отдельно не измерялся, streaming выключен.

Практический результат: локальное резюмирование работает; все факты 02:00, 7 daily, 4 weekly, monthly restore test и alert сохранены. **Ограничение качества:** запрошено три пункта, получено пять. PASS относится к инфраструктуре inference, а не к строгому соблюдению формата. Исходный запрос и полный ответ находятся в `evidence/`.

## Крупная модель и DGX OS

До установки общий каталог Ollama занимал 4 KiB, model manifests отсутствовали. После установки доступен только Qwen 0.5B. Большая модель не запускалась; gpt-oss:120b не скачивалась. Указанный пользователем baseline DGX OS — Ollama 0.40.8, gpt-oss:120b, около 40–44 tok/s — остаётся историческим пользовательским измерением без исходного benchmark в этом пакете. Сравнивать его с Qwen 0.5B нельзя. Для честного сравнения требуются одинаковые веса, квантование, контекст, запрос, параметры и способ измерения. Размер gpt-oss:120b в Ollama — около 65 GB, отдельного разрешения на эту загрузку нет.

## FreeToken

**BLOCKED для штатного ARM64/GB10 deployment.** Проверен текущий пакет `freetokenqwen3635ba3bnvfp4`, chart 1.0.4. `supportArch` содержит только amd64; `nvidia-gb10` отсутствует, комментарий manifest прямо объясняет amd64-only образ. Docker Hub подтверждает единственный linux/amd64 вариант `beclab/leamon2code-freetoken:0.1.3-cu132`, digest `sha256:b3f8c48f4bcf14ff90ca122a38b3f2577e39180d14a0db4168d778b4ede2605e`.

Работающий ARM64 backend этим штатным пакетом не предоставляется. Контейнер и веса не скачивались, x86-эмуляция и сборка другого backend не предпринимались. GPU offload, latency и tok/s — N/A. Заявленная польза пакета — локальный MoE inference, изображения и tool calling; на проверенной ARM64 машине эта польза не подтверждена. Это вывод о текущем Olares-пакете и образе, не утверждение о невозможности будущей ARM64-поддержки FreeToken вообще.

## ComfyUI

**PASS для базового text-to-image; PARTIAL для набора дополнительных плагинов.** Загрузка, мешавшая проверке 24 октября, завершилась. Штатный application перешёл в Running 24 октября около 21:01 UTC; 25 октября Pod 3/3 Running, 0 рестартов. 25 октября движок запущен через штатный ComfyUI Launcher `/api/start`; затем выполнен ровно один подготовленный workflow через API proxy приложения, без обхода application ownership.

Chart 1.1.38, ComfyUI 0.42.1, Python 3.12.3, PyTorch **2.11.0+cu128**, launcher 0.2.54. Активный frontend по argv и журналу — 1.58.0; отдельный Python package `comfyui-frontend-package` в `/system_stats` имеет версию 1.55.18. Это разные способы поставки frontend, оба значения сохранены. ARM64-образ `beclab/comfyui_launcher-arm64:v0.42.1-fe1.58.0-launcher0.2.54-arm64`, фактический imageID совпадает с digest `sha256:0ad052806ba478d00cd3635b56009ecdbff8d14da7f0080feb9ae3da884c8be6`.

**GPU:** `/system_stats` сообщает `cuda:0 NVIDIA GB10 : native`, type cuda. Pod использует `hami-scheduler`, runtime `nvidia`, `hami.io/bind-phase=success`, GPU share 1; request памяти 22 GiB, limit 70 GiB. HAMi-квота 22528 MiB и показания 22 GiB VRAM в API не являются физическим объёмом памяти GB10. Журнал: CLIP и VAE load device cuda:0, CPU указан как offload device; полностью загружены компоненты 235.84 MB, 1639.41 MB и 159.56 MB. Штатные CPU-offload механизмы сохранены; не утверждается, что все компоненты постоянно находятся на GPU. Фактическая GPU-генерация успешно выполнена.

Пользователь согласовал до 12 GB суммарной загрузки. Основной контейнер: 9,639,977,041 байт сжатых слоёв; checkpoint Comfy-Org `v1-5-pruned-emaonly-fp16.safetensors`: 2,132,696,762 байта. Сумма основных артефактов 11,772,673,803 байта (~11.77 GB); это сумма размеров, не измеритель фактического сетевого трафика с повторами. Дополнительных моделей 25 октября не скачивали. SHA-256 checkpoint: `e9476a13728cd75d8279f6ec8bad753a66a1957ca375a1464dc63b37db6e3916`, проверен 24 октября. Общий путь `/olares/rootfs/Common/comfyui/model/checkpoints/`.

Сценарий: эскиз предметной фотографии растения для каталога — text-to-image SD 1.5 FP16, **512×512, batch 1, seed 42, Euler/normal, 20 steps, CFG 7**. Prompt и отрицательный prompt сохранены в workflow и PNG metadata. Узлы — штатные CheckpointLoaderSimple, CLIPTextEncode, EmptyLatentImage, KSampler, VAEDecode, SaveImage. History: `status_str=success`, `completed=true`, `execution_cached.nodes=[]` — готовое изображение не было взято из кеша.

| Измерение | Результат |
|---|---:|
| ComfyUI log `Prompt executed` | **9.41 s** |
| History execution_start → execution_success | 9.282 s |
| Время клиента submit → обнаружение завершения | 10.132 s, polling раз в 1 s |
| Sampling | 20/20 steps, около 3 s; итоговый tqdm 6.15 it/s |
| Изображение | `sprint7b_sd15_seed42_00001_.png`, 512×512 |

Это один первый workflow после запуска движка, включая загрузку checkpoint/компонентов, не прогретый benchmark. Различия таймеров обусловлены границами измерения и polling; нельзя трактовать client wall time как чистое время GPU.

**Визуальная проверка:** PNG открыт и просмотрен. Получено связное изображение зелёного суккулента в горшке с мягким оконным светом. Сценарий пригоден для локальных концептов/эскизов. Ограничение prompt adherence: запрашивались белый горшок и деревянный стол, а получились коричневый горшок и голубоватая поверхность. Это не точная товарная фотография и не тест качества современных diffusion-моделей.

**Ограничения установки:** 12 дополнительных custom-node пакетов не импортировались, включая Impact-Pack, controlnet_aux, segment_anything, Crystools, PuLID, Impact-Subpack, InstantID, layerdiffuse, FaceAnalysis, FizzNodes, Inspire-Pack и VideoHelperSuite. В журнале отсутствуют зависимости `cv2`, `numexpr`, `segment_anything`, `insightface`, `deepdiff`. Эти пакеты не нужны проверенному базовому workflow. Они не исправлялись и не тестировались, поэтому полного PASS для всех встроенных расширений нет. Префикс `[ComfyUI-Error]` также встречается у обычных INFO/progress строк, поскольку Launcher так помечает stderr; он сам по себе не означает ошибку генерации.

После workflow: ComfyUI и Windows VM 3/3 Running, 0 рестартов; новых Xid/OOM нет, swap used 0, host available memory 111,350,562,816 байт (~103.7 GiB). Это контрольный срез, не измерение пикового потребления. Движок после теста остановлен штатным Launcher `/api/stop`, приложение, веса и выходное изображение сохранены. Новых экспериментов с ОС, сетями или VM не проводилось.

Исторические `download-progress.txt` и `download-observations.txt` сохранены как доказательство задержки 24 октября; они больше не описывают текущее состояние установки.
## Среда и ограничения измерения

OlaresOS 1.12.7 (контекст предыдущего спринта), узел arm64, kubelet v1.33.3+k3s1, базовая ОС Ubuntu 24.04.3 LTS. NVIDIA GB10, driver 595.84, CUDA driver compatibility 13.2. В начале около 121 GiB общей памяти и 108 GiB available; swap 1 GiB, использовано 0. Встроенный `nvidia-smi` не сообщает обычный VRAM Memory-Usage для этой unified-memory платформы. Не следует трактовать это как отсутствие CUDA.

HAMi scheduler/device plugin работали без рестартов. До нагрузки совпадений Xid/OOM в проверенном текущем kernel ring buffer нет; пустые файлы журналов в evidence означают ноль совпадений, а не потерянный вывод. Это ограниченная проверка текущего журнала, не гарантия всей истории машины. Windows VM оставалась запущенной; её настройки в acceptance не менялись.

Контроль в 15:55 UTC: новых Xid/OOM нет, VM Pod 3/3 Running, restartCount 0; GB10 41°C, GPU utilization 0% после выгрузки LLM. Available memory 116,137,058,304 байт (~108.16 GiB), swap used 0. Работоспособность текущей сессии VM сохранялась; отдельный стресс-тест Windows или повторная проверка remote desktop не проводились по ограничению пользователя.

Никакие host reboot, изменения драйверов, Secure Boot, HAMi, глобальной Kubernetes-конфигурации или сети не выполнялись. После LLM-проверки модель выгружена командой `ollama stop`; установленные приложение и веса сохранены.

## Воспроизведение

1. Использовать установленный Market instance с перечисленными env и моделью, дождаться завершения preload.
2. Из авторизованного Control Hub terminal определить существующий Ollama Service в namespace экземпляра. Не создавать произвольный Pod.
3. Запустить `python3 reproduce-ollama.py http://<ollama-service>:11434 result-dir`. Скрипт не скачивает модели. Для повторного замера использовать другой каталог, чтобы сохранить исходные результаты.
4. Сохранить `ollama ps`, `/api/ps`, журналы CUDA/offload, доступную память и kernel Xid/OOM до и после. Для проверки входа приложения повторить `evidence/openai-request.json` на существующем llm-init Service `/v1/chat/completions`.
5. Не использовать эти короткие результаты для вывода о преимуществе OlaresOS над DGX OS.

## Источники

Официальные manifest/template и registry metadata сохранены в `evidence/`; snapshot beclab/apps: `94a3136dc337c09beb9cfbc085138c6fb5760695`.

- https://github.com/beclab/apps/tree/94a3136dc337c09beb9cfbc085138c6fb5760695/ollamallmbasev3
- https://github.com/beclab/apps/tree/94a3136dc337c09beb9cfbc085138c6fb5760695/comfyuisharev3
- https://github.com/beclab/apps/tree/94a3136dc337c09beb9cfbc085138c6fb5760695/freetokenqwen3635ba3bnvfp4
- https://ollama.com/library/qwen2.5:0.5b
- https://ollama.com/library/gpt-oss:120b
- https://huggingface.co/Comfy-Org/stable-diffusion-v1-5-archive

## Final handoff — среды и хронология

Материалы для передачи другому ChatGPT находятся в `public/`. Это локальная подготовка файлов; публикация и отправка третьим лицам не выполнялись. После закрытия спринта новых измерений не проводилось.

### DGX OS — исторический baseline, со слов пользователя

Ollama 0.40.8, gpt-oss:120b, около 40–44 tok/s. Исходные JSON/логи, точные параметры запроса, контекст, квантование, методика, дата и подробные версии среды в этом пакете отсутствуют. Эти цифры нельзя представлять как независимо проверенный benchmark или использовать для прямого сравнения с Qwen 0.5B.

### OlaresOS — измерено в Sprint 7B

Ollama v3 / Qwen 0.5B: PASS, 25/25 слоёв на GB10, прогретая генерация 117.47 tok/s, клиентское время 0.411 s. ComfyUI: PASS для одного базового SD 1.5 workflow, 512×512 за 9.41 s; дополнительные плагины PARTIAL. FreeToken: BLOCKED для штатного ARM64 deployment, подтверждён amd64-only образ. Источники каждого утверждения перечислены в `evidence-index.md`.

### Хронология установки, ошибок и восстановления

| Дата / время UTC, где известно | Событие и качество доказательства |
|---|---|
| До Sprint 7B | DGX OS baseline 40–44 tok/s — сообщение пользователя, сырых данных нет. |
| Предыдущий спринт | Произвольный CUDA Pod отклонён: `pod has no owner application`. Исторический контекст переписки; исходный admission-log не включён. |
| 23–24 октября | CRD и увеличенное разрешение Windows VM подтверждены пользователем; работа прерывалась Windows Update/reboot. Подробные журналы ремонта и конфигурации VM не входят в AI acceptance-пакет. |
| 24 октября, 15:43 UTC | Штатный экземпляр Ollama создан через Market. CUDA v12 пропустил GB10 из-за списка архитектур; автоматически выбран CUDA v13. Доказательства: `ollama-pod-selected.json`, `ollama-gpu-log.txt`. |
| 24 октября, 15:45–15:47 UTC | Реальные запросы Ollama и llm-init. Первый запрос пересёкся с preload, поэтому выделен отдельно; прогретый повтор и API проверены. Доказательства: JSON ответов, metrics, proxy log. |
| 24 октября, 15:53–15:55 UTC | ComfyUI оставался на загрузке контейнера; checkpoint уже получен и хеш проверен. Слой 4.47 GB рос медленно. Доказательства: download-progress/observations, OCI manifest, checkpoint SHA-256. |
| 24 октября, около 21:01 UTC | Установка ComfyUI завершилась. Время наблюдалось в статусе Application/Launcher; полный исходный install-log в пакет не включён. |
| 25 октября, 08:37 UTC | Выполнен один workflow ComfyUI: success, без cached nodes, PNG сохранён. Время по журналу 9.41 s. Доказательства: `evidence/comfy/history.json`, `runtime-log.txt`, PNG. |
| 25 октября, после теста | Ошибки импорта 12 дополнительных плагинов задокументированы, не исправлялись. Новых Xid/OOM и рестартов VM не было в контрольных срезах. Движок штатно остановлен. Доказательства: runtime-log, pods, kernel, launcher-stop. |

### Недостающие материалы и пределы публичных выводов

- Нет сырых DGX OS benchmark-данных и сопоставимого теста одной модели на обеих ОС.
- Нет OlaresOS-измерений gpt-oss:120b: весов не было, повторная загрузка не выполнялась.
- Нет полного сквозного журнала ранней установки OlaresOS, ремонта CRD/видеовывода и Windows Update; имеются только исторические сведения из переписки. Не выдавать их за первичные технические доказательства.
- Нет теста FreeToken на ARM64 и проверки работоспособности всех дополнительных ComfyUI-плагинов.
- Нет статистической серии, TTFT, пикового потребления памяти или длительного стресс-теста. Имеющиеся короткие acceptance-измерения не заменяют их.

Публичные материалы должны сохранять эти оговорки. Обнаруженные токен-подобные имена в официальных Helm templates (например, HF_TOKEN) — названия переменных и пустые шаблоны, а не учётные данные. Пользовательские имена и GPU UUID в evidence редактированы. PNG содержит только синтетический prompt/workflow; фото пользователя и личных данных нет.