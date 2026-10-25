> ARCHIVED REPORT: host/account identifiers redacted for publication. Measurements are unchanged. This is a contemporaneous report, not a substitute for its referenced raw files.

# Sprint 4A — Multi-node Integration: PARTIAL

23 октября 2026. **Основной путь OlaresOS host → Spark, вычисления и восстановление временного туннеля — PASS.** Необязательный контейнерный тест не выполнен; полностью автономное обнаружение/управление соединением не развёрнуто.

## Подтверждённый путь

Windows VM использовалась только как управляющий SSH-клиент. HTTP-клиент Python действительно выполнялся на физическом Minisforum: hostname `olares`, архитектура x86_64, пользователь olares, LAN `[MINISFORUM_LAN_IP]`. Spark: `[SPARK_HOST]`, aarch64, LAN `[SPARK_LAN_IP]`, SSH 22. Вложенное SSH-соединение **с OlaresOS** успешно вернуло hostname Spark. Ping с OlaresOS: 3/3, 0% потерь, среднее 0,863 ms.

На OlaresOS запущен временный OpenSSH local forward `127.0.0.1:21434 → Spark 127.0.0.1:11434`. Ollama не меняла адрес привязки. `/api/tags` обнаружил существующие gemma3:4b и gpt-oss:120b. Запросы к последней выполнены с OlaresOS через этот forward, без HTTP-проксирования через Windows.

## Измерения

Одинаковый prompt в сохранённом `sprint4a-probe.py`; temperature=0, seed=42, num_ctx=4096, num_predict=128, stream=true. По четыре запроса на каждом клиенте, первый исключён из тёплой статистики. Spark baseline первым загрузил модель: 13,844 s wall, 10,273 s load. Перед серией OlaresOS модель уже прогрета. `ollama ps`: gpt-oss:120b, 64 GB, **100% GPU**, context 4096.

| Среднее трёх тёплых запросов | Spark localhost | OlaresOS через SSH/LAN |
|---|---:|---:|
| End-to-end | 2,984 s | 2,927 s |
| TTFT, первый thinking/response token | 149,86 ms | 145,04 ms |
| Generation throughput | 44,09 tok/s | 44,91 tok/s |
| Wall − Ollama total_duration | 3,36 ms | 4,34 ms |
| Ошибки API/inference | 0/4 | 0/4 |

Среднее `/api/tags` после первого вызова: localhost 1,334 ms, OlaresOS 2,463 ms; разница **1,13 ms**. Добавка wall−server для inference **0,98 ms**, около 0,03% wall. Это оценка клиентского/SSH/сетевого пути, не чистая задержка провода. Замеры последовательные, n=3; небольшое преимущество OlaresOS по generation — вариация состояния GPU, не ускорение сетью. Prompt cache прогрет. Throughput включает thinking tokens; ответы ограничены 128 токенами и завершились `done_reason=length`, поэтому не являются завершёнными содержательными ответами. Это транспортный/вычислительный тест, не оценка качества.

## Отказ и восстановление — PASS

Завершена только принадлежащая тесту SSH-сессия с forward. Следующий HTTP-запрос на OlaresOS вернул структурированную `URLError: [Errno 111] Connection refused`. Локальный listener отсутствовал, Spark продолжал отвечать ping; ОС и сетевые службы не отключались. Повторное SSH-соединение и forward восстановили `/api/tags` (10/10 ответов). После восстановления повторный inference не запускался: восстановление проверено на API discovery endpoint.

Сырые результаты: `sprint4a-host/disconnected.json`, `restored.json`, `host-results.json`, `tags.json`; localhost baseline — `sprint4a-spark-baseline.json`. Probe сохраняет ошибку в JSON, но сам не возвращает ненулевой exit code: автоматический вызывающий код должен проверять поле `error`.

## Контейнер и Agent Readiness

- Контейнер — **BLOCKED в рамках обычного пользователя**: Docker/Podman/nerdctl не найдены; есть `/usr/bin/ctr` и `/run/containerd/containerd.sock`, но `ctr namespaces list` возвращает permission denied. Privileged-доступ к runtime OlaresOS/Kubernetes не использовался. Образы не скачивались, контейнеры не создавались.
- Обнаружение Spark — **PARTIAL**: использован известный LAN-адрес и существующий профиль DGX-Spark; hostname, SSH и список моделей подтверждены. Zero-config discovery не реализован.
- Вызов вычислений — **PASS**: агент выполнил запросы на OlaresOS через SSH, без ручного переключения пользователя между машинами.
- Диагностика недоступности — **PASS для смоделированного случая**: отказ локального туннеля отличён от недоступности Spark с помощью отсутствия listener, ping и успешного повторного SSH/API.
- Автономная эксплуатация — **PARTIAL**: сейчас оркестрация с Windows VM, интерактивные SSH credentials и временный tunnel; постоянного агента, secret-store, supervisor/retry policy на OlaresOS не установлено. Потеря питания, LAN и зависание API не моделировались.

## Состояние после теста

Новых Xid в текущем boot Spark не обнаружено при проверках до, между и после серий. nvidia-smi отвечает, последнее сохранённое состояние GB10 37°C. Проверки журналов были между сериями, не непрерывный watchdog. gpt-oss:120b выгружена после теста; временный туннель закрыт. ОС, драйверы, Kubernetes, сеть и постоянная Ollama не изменены; публичных listener нет, пакеты/модели/серверы не устанавливались. Временные скрипт/результаты остались в `/tmp/sprint4a` на OlaresOS; `/tmp/sprint4a-probe.py` на Spark. SSH host keys при первом соединении приняты по TOFU; отдельная внеполосная сверка fingerprint не выполнялась.
