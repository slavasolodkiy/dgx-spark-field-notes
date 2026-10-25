> ARCHIVED REPORT: host/account identifiers redacted for publication. Measurements are unchanged. This is a contemporaneous report, not a substitute for its referenced raw files.

> HISTORICAL WINDOWS DIAGNOSTICS — 23 October, before the user-confirmed final resolution/CRD result. NOT the final AI acceptance report; see evidence/olares-acceptance/sprint7b-report.md.

# Sprint 7B — Native OlaresOS AI inference

Дата: 23 октября 2026, Europe/London. Статус: INCOMPLETE — доступ к Olares восстановлен, CRD работает, согласована смена видеоустройства VM. См. последнее обновление ниже. Definition of Done НЕ достигнут: GPU inference не запускался.

## Выполненная диагностика Windows

- Windows 11 Pro 10.0.26200, ARM64; QEMU KVM Virtual Machine.
- RAM: 4 286 042 112 байт физической памяти, 4 185 588 КиБ видимо ОС. Свободно 418 484 КиБ в начале, 967 496 КиБ при последнем замере. Файл подкачки 3572 МиБ, использовано 946 МиБ, пик 1312 МиБ.
- LastBootUpTime: 2026-10-23 16:06:24 +01:00, не изменился в ходе диагностики. Команды выполнялись, сеть работала. Это подтверждает доступность в коротком окне наблюдения, но не стабильность под AI-нагрузкой.
- IP VM: [WINDOWS_VM_IP]. Хост [SPARK_LAN_IP] отвечает на ICMP, задержка <1 мс.
- Часовой пояс GMT Standard Time (London, сейчас UTC+1). w32tm: Leap Indicator 3, not synchronized; последняя успешная синхронизация 15:07:54. Прямые три NTP-замера time.windows.com: -1.59, -1.13, -3.65 мс. Значительной ошибки текущих часов нет; служба синхронизации требует отдельной проверки.
- В старых событиях есть время из будущего (до исправления часов); порядок по TimeCreated нельзя считать надёжным.
- Новых событий Resource-Exhaustion-Detector за проверенное часовое окно не найдено. Есть прежние ошибки Windows Update 0x8024200B и загрузки luafv; связь с CRD не установлена. Журналы Xid/OOM хоста недоступны.

## F. Chrome Remote Desktop

Статус: установлен, регистрация/реальное подключение НЕ завершены; несовместимость ARM64 НЕ доказана.

1. Подписанный Google LLC MSI в Downloads, 24 449 024 байта. Версия установленного Host 154.0.8037.40.
2. MsiInstaller 11707/1033 сообщает успешную первоначальную установку, код 0. Последняя повторная настройка 16:10:39: события 11728/1035, код 0. В прочитанных событиях нет MSI 1603/ошибки завершения.
3. Все 10 проверенных EXE Host имеют PE Machine 014C (x86), подписи Valid. Chrome — AA64 (нативный ARM64). Нельзя называть установленный Host нативным ARM64.
4. Реальный локальный запуск remoting_native_messaging_host.exe с документированным в исходниках протоколом дал:
   - helloResponse, version 154.0.8037.40, supportedFeatures pairingRegistry/oauthClient/getRefreshTokenFromAuthCode;
   - getDaemonStateResponse: STOPPED.
   Это подтверждает исполнение x86-компонента через совместимость Windows ARM64, но не захват экрана/удалённый сеанс.
5. Служба chromoting: Stopped, Manual, ExitCode 1077 (ещё не запускалась). Ожидаемый C:\ProgramData\Google\Chrome Remote Desktop\host.json отсутствует. NativeMessagingHosts зарегистрированы в WOW6432Node.
6. Причина наблюдаемой остановки мастера на 100% пока не установлена. Установка MSI успешна; дальнейшая регистрация хоста не завершена. Повторять установку вслепую оснований нет.
7. Инструмент браузера отказал в доступе к существующей вкладке CRD: другое расширение открыло UI, блокирующий автоматизацию. Пользователю предложено закрыть его. Google-регистрация/PIN/тест подключения с другого устройства остаются обязательными.
8. Простой резервный вариант — встроенный RDP Windows 11 Pro. Уже включён (fDenyTSConnections=0), TermService работает, TCP 3389 слушает IPv4/IPv6. Внешняя достижимость и вход не проверены, сеть/правила firewall не менялись. Адрес VM приватный; прямой доступ с другой машины не гарантирован. Не следует публиковать 3389 в Интернет.

Официальные источники:
- https://support.google.com/chrome/answer/1649523
- https://chromium.googlesource.com/chromium/src/+/HEAD/remoting/host/installer/win/BUILD.gn
- https://raw.githubusercontent.com/chromium/chromium/main/remoting/host/setup/me2me_native_messaging_host.cc

## G. Экран 800×600

Статус: ограничение подтверждено, исправление требует конфигурации хоста и проверки пакета драйвера.

- ROOT\BASICDISPLAY\0000, Microsoft Basic Display Driver, ARM64 basicdisplay.inf, версия 10.0.26100.4202, подписан, PnP status OK.
- Generic Non-PnP Monitor. Win32_VideoController не вернул адаптеров; BasicDisplay присутствует в классе System, а не Display.
- GraphicsDrivers/Configuration содержит PrimSurfSize 800×600 и ActiveSize 800×600. Перечень видеорежимов и изменение через Windows Settings пока не проверены.
- PCI-список не содержит VirtIO GPU; фактическая QEMU-командная строка не прочитана. ramfb известен из исходного контекста пользователя, а не подтверждён на хосте в этой сессии.
- Upstream virtio-win содержит Win11 ARM64 viogpudo в win11_arm64.ddf. Наличие сборочной цели не подтверждает доступность подходящего подписанного выпуска или его совместимость с конкретной VM. Случайные драйверы не устанавливались.
- Предлагаемое изменение после проверки: сохранить конфигурацию запуска/манифест VM и UEFI NVRAM, обеспечить независимую консоль/откат; проверить официальный подписанный ARM64 viogpudo (INF, CAT, аппаратные ID); добавить поддерживаемый QEMU virtio-gpu-pci с сохранением ramfb как аварийного пути, если конкретный менеджер и firmware это допускают. После согласования остановить только VM, изменить её штатную конфигурацию, установить подходящий драйвер и проверить 1920×1080 в Settings. Риск: чёрный экран/неудачная загрузка; откат — восстановление исходной конфигурации и NVRAM при выключенной VM. Точный diff пока невозможно подготовить без конфигурации хоста.
- Альтернатива для рабочего пространства 1920×1080 — RDP-сеанс с заданным размером; это не исправляет локальную ramfb-консоль. Реальный сеанс не проверен.

Источник: https://github.com/virtio-win/kvm-guest-drivers-windows/blob/master/win11_arm64.ddf

## OlaresOS / GB10 / Ollama

- Olares Desktop отвечает HTTP 303 на auth.[OLARES_USER].olares.com. Авторизованного административного доступа пока нет, SSH-пользователь/ключ не известны.
- OlaresOS 1.12.7, GB10, драйвер 595.84, CUDA/NVML PASS и HAMi PASS — предоставленные пользователем исходные данные, в этой сессии НЕ перепроверены.
- Доступная unified memory, текущие GPU процессы, Xid/OOM, состояние HAMi, фактический Market-каталог и установленная модель НЕ проверены.
- Ollama v3 НЕ установлена. Произвольные Kubernetes Pod не создавались, ownership не обходился.
- Официальная документация Olares описывает Engine Base и создание модельного инстанса через Market. v3 в OlaresManifest относится к формату приложения, а не автоматически к версии исполняемого Ollama. В установленном Market ещё нужно подтвердить точный app id, ARM64/GB10 accelerator, образ и версию runtime.
- Smoke test, GPU offload, tok/s и влияние на VM: NOT RUN, измерений нет.

Источники:
- https://www.olares.com/docs/manual/olares/market/market
- https://www.olares.com/docs/developer/develop/package/manifest

## План воспроизводимых измерений после снятия блокеров

1. Перед установкой: версия ОС/ядра/драйвера, nvidia-smi, /proc/meminfo, df, процессы GPU, текущие Xid/OOM и состояние HAMi. Сохранить baseline памяти и времени загрузки Windows.
2. Через Market выбрать штатный Ollama v3/Engine Base для ARM64+GB10. Проверить, что установка не запускает автоматическую загрузку крупной модели. Установить в штатном ownership.
3. Проверить app/workload/ownerReferences, GPU-ресурсы и аннотации HAMi, журналы выделения GPU, доступ к CUDA внутри приложения. Не менять конфигурацию кластера.
4. Сначала использовать существующую маленькую модель. Если отсутствует — выбрать совместимую субгигабайтную модель, подтвердив её фактический размер. Ограничить контекст (например, 2048), генерацию 128 токенами и одну одновременную задачу.
5. Сохранить модель/digest/квантизацию, параметры запроса, JSON ответа Ollama, ollama ps или /api/ps, журналы CUDA/offloaded layers. Провести cold run и три warm runs; generation tok/s = eval_count / (eval_duration / 1e9). Отдельно учитывать prompt processing и load_duration.
6. Во время теста наблюдать память хоста, GPU-процессы, Xid/OOM и доступность Windows. При новом Xid/OOM/нестабильности прекратить генерацию, выгрузить тестовую модель штатным способом и сохранить диагностику.

## Подготовка gpt-oss:120b / сравнение DGX OS

- Каталог Ollama указывает gpt-oss:120b MXFP4, 117B, digest-префикс 714d86958b6e, размер около 65 GB. Это размер загрузки, не полный рабочий набор RAM с KV/cache/runtime.
- Наличие локального кеша неизвестно. Большая модель НЕ скачивалась; требуется отдельное согласование загрузки, если её нет.
- Источник: https://ollama.com/library/gpt-oss:120b
- Baseline пользователя: DGX OS, Ollama 0.40.8, около 40–44 tok/s. В этой сессии он не перепроверен.
- Для сравнения нужны одинаковые digest модели, контекст, prompt, число выходных токенов, параметры reasoning/temperature/seed, concurrency и состояние warm cache. Без них сравнение будет ориентировочным. Новый runtime может отличаться от baseline; это нужно явно указать.

## Изменения и блокеры

Системное ПО/драйверы не переустанавливались. Хост и VM не перезагружались. NVIDIA, HAMi, Kubernetes, Secure Boot и сеть не менялись. Созданы локальная диагностика и этот отчёт; выполнен только краткий read-only запуск существующего CRD Native Messaging Host, затем процесс завершён.

Для продолжения: закрыть блокирующий UI расширения Chrome; предоставить авторизованный Olares Desktop и способ административного доступа к хосту без передачи паролей в чат. Отдельно потребуется реальный клиент для проверки CRD/RDP. Изменения QEMU будут согласованы после чтения конфигурации и подготовки отката.

## Обновление 23 октября, около 16:39 BST

- Веб-доступ восстановлен: авторизованные Desktop, Settings, Market и Control Hub. Linux-хост доступен через штатный терминал Control Hub.
- Host: kernel 6.14.0-1015-nvidia, aarch64; RAM 121 GiB, used 13 GiB, available 108 GiB; swap 1 GiB/0 used. NVIDIA GB10, driver 595.84, CUDA compatibility 13.2, 40 C, 5 W, 0% utilization, GPU processes отсутствуют. Поиск NVRM Xid / out of memory / oom-kill в текущем dmesg пуст.
- HAMi device plugin 2/2 Running, scheduler 2/2, exporter 1/1, webui 2/2, os-gpu scheduler 1/1; рестартов нет. Windows Pod windowsarm-667dcc657c-9vrrm: 3/3 Running, 0 restarts.
- Settings Accelerator показывает GB10 Shared RAM 96 Gi, No apps assigned. 96 Gi — пул в интерфейсе, а не свободная host memory.
- Market: официальный ollamallmbasev3 (Ollama Engine Base), chart 1.3.18, app 0.40.2, ARM64 и nvidia-gb10 явно поддержаны. Экземпляры не созданы. Малый кандидат smoke test: qwen2.5:0.5b Q4_K_M, 398 MB, https://ollama.com/library/qwen2.5:0.5b . Загрузки моделей пока не было.
- CRD: пользователь подтвердил, что теперь всё работает. Локально проверено: chromoting Running / Auto / ExitCode 0, host.json существует. Реальное удалённое подключение подтверждено пользователем, не отдельным клиентом агента. MSI переустанавливать не пришлось. Точная исходная причина остановки веб-мастера не доказана; прежние MSI попытки были успешны.
- QEMU фактически использует -device ramfb, 4 cores, -m 4G, accel=kvm, -rtc base=localtime. Образ beclab/dockurr-windows-arm:5.14. /run/display.sh поддерживает VGA, default ramfb; QEMU имеет virtio-gpu-pci.
- Ключевое уточнение: VirtIO GPU ARM64-драйвер УЖЕ в DriverStore: viogpudo.inf_arm64_3908a3ae1235a394, published oem7.inf, Red Hat 100.101.104.28500 (2025-07-09). INF рассчитан на NTARM64, PCI VEN_1AF4 DEV_1050. CAT/INF/SYS имеют Valid-подпись Microsoft Windows Hardware Compatibility Publisher; pnputil: Universal, Attested. Нужна смена устройства, а не скачивание драйвера.
- Пользователь явно согласовал VGA=virtio-gpu-pci и остановку/запуск только VM; подтвердил наличие доступа к Olares с другого устройства.
- Backup на Linux-хосте: /tmp/sprint7b-config.rz0HBv (0700), windowsarm-deployment.yaml (может содержать секреты, не публиковать) и qemu-command.txt. SHA256 deployment: 67b32de7a9678fc2531e7e199abb2d0c1e71be3c56c1806feb0ec14d60b2b931; qemu-command: 58f3c9f37a6c82b0152faba50df83b5373c05afa2c31cba308ade843c2b9c0d4. Это копия конфигурации, не дисковый snapshot. Перед reboot backup необходимо перенести из /tmp в постоянное хранилище при дальнейшей работе.
- Deployment уже использует Recreate, replicas=1, terminationGracePeriodSeconds=300; wrapper отправляет ACPI system_powerdown и ждёт завершения Windows. Поэтому изменение только env VGA штатно завершит старый Pod перед созданием нового, без двух VM на одном диске.
- Следующий согласованный шаг: установить env VGA=virtio-gpu-pci только в контейнере windows, дождаться перезапуска, проверить PnP/1920x1080/CRD и отсутствие новых Xid/OOM. Результат смены устройства пока НЕ подтверждён.
- Откат с другого устройства: Control Hub → Terminal → Olares; kubectl set env -n windowsarm-[OLARES_USER] deployment/windowsarm --containers=windows VGA- . Это вернёт default ramfb с новым штатным Recreate. Не применять backup YAML без проверки полей metadata/status.


Смена видеоустройства запущена через host nohup-скрипт /tmp/sprint7b-config.rz0HBv/switch-display.sh, PID 50382, с задержкой 30 секунд. Лог: switch-display.log. Автооткат VGA- только при неуспехе rollout за 8 минут. Успех загрузки/изображение ещё не проверены.
