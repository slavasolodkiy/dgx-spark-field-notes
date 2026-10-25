> ARCHIVED REPORT: host/account identifiers redacted for publication. Measurements are unchanged. This is a contemporaneous report, not a substitute for its referenced raw files.

# DGX Spark: локальный gpt-oss-120b — PASS

Дата: 22 октября 2026. Хост: [SPARK_HOST], [SPARK_LAN_IP]; SSH-профиль NVIDIA Sync `DGX-Spark`, пользователь `slava`.

## Проверка и установка

- Ollama изначально отсутствовал. Установлен Ollama 0.40.8 официальным установщиком, рекомендованным NVIDIA.
- Docker 29.6.2 и NVIDIA Container Toolkit 1.20.1-1 уже установлены. Docker доступен через sudo; пользователь slava не имеет прямого доступа к сокету. Контейнеры для этого теста не запускались, конфигурация Docker не изменялась; работа GPU внутри контейнера не тестировалась.
- Выбран нативный Ollama — минимальный путь из официального NVIDIA playbook. Работает одна systemd-служба `ollama`, включён автозапуск. API доступен только на `127.0.0.1:11434` самого Spark.
- Загружена только `gpt-oss:120b`: 116.8B, MXFP4, около 65.4 GB на диске. SHA-256 проверен Ollama. Идентификатор: `714d86958b6e870a9320e78126ac1ce3477727a1cd9bf7194b8ace0d84c62fd8`.
- DGX OS, драйвер 580.178.04 и сетевые настройки не менялись. Перезагрузок не было.

## Один тестовый запрос

Запрос: “Explain in about 150 words how unified memory helps a local AI workstation. Include two practical limitations.”
Настройки: think=low, temperature=0, num_ctx=4096, num_predict=512, keep_alive=10m. Получен завершённый текстовый ответ (`done_reason=stop`). Содержание ответа не использовалось как источник технических фактов.

| Метрика | Результат |
|---|---:|
| Полное время первого ответа, по клиенту | 55.05 с |
| Загрузка модели | 30.59 с |
| Обработка промпта | 87 токенов, 15.97 с |
| Генерация | 339 токенов, 8.46 с |
| Скорость генерации | **40.07 токена/с** |
| Память модели по Ollama size_vram | 64.33 GB / 59.91 GiB |
| Занято памяти до запроса, MemTotal−MemAvailable | 4.25 GiB |
| Пик занятой общей памяти | 67.43 GiB |
| Прирост к исходному состоянию | **63.18 GiB** |
| Доступно памяти после ответа | 54.31 GiB |
| Swap после теста | 40 KiB |

GPU подтверждён: NVIDIA GB10, CUDA backend; журнал `offloaded 37/37 layers to GPU`; `ollama ps` показывает `100% GPU`. Во время генерации отдельно наблюдалась загрузка GPU 95%.

Это один холодный запрос, не усреднённый benchmark. 40.07 токена/с рассчитано как eval_count / eval_duration; полная задержка включает загрузку и обработку промпта. На Spark память общая для CPU/GPU: показатель size_vram не следует складывать с системным использованием. Системная память измерялась примерно каждые 0.5 с; она включает остальные процессы. Отдельный показатель VRAM в nvidia-smi здесь не поддерживается.

## Использование

Из Windows: `ssh DGX-Spark`, затем `ollama run gpt-oss:120b`.
После 10 минут простоя модель выгрузится из памяти, но останется на диске; служба Ollama продолжит работать. Для следующего запроса она загрузится снова.

Исходные результаты: `dgx-spark-gpt-oss-benchmark.json`. Скрипт и журналы на Spark: `/home/[USER]/spark-gpt-oss-test/`.

Источники:
- NVIDIA playbook: https://build.nvidia.com/playbooks/vibe-coding/instructions
- Ollama Linux / ARM64: https://docs.ollama.com/linux
- Значения метрик API: https://docs.ollama.com/api/generate
