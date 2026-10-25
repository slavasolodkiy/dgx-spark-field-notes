> ARCHIVED REPORT: host/account identifiers redacted for publication. Measurements are unchanged. This is a contemporaneous report, not a substitute for its referenced raw files.

# DGX Spark / OlaresOS 1.12.7 — GPU recovery

2026-10-23, SSH [USER]@[SPARK_LAN_IP]. Итог: GPU PASS; активация Olares PARTIAL, требуется повторная отправка параметров из LarePass.

## Выполнено

- Secure Boot: disabled (пользователь отключил до начала работ).
- Kernel 6.14.0-1015-nvidia; headers 6.14.0-1015.15, Makefile доступен.
- Сохранённый `/home/olares/.olares/pkg/components/cuda-driver-595.84.run` идентифицирован как NVIDIA Linux-aarch64 595.84.
- `--check`: checksums/MD5 OK. MD5 `845ef88dd1bafa9ccb283876648722d2` совпадает с ARM64-записью installation.manifest Olares.
- Полная установка: `sudo sh /home/olares/.olares/pkg/components/cuda-driver-595.84.run --kernel-module-type=open --silent`. Exit 0; `/var/log/nvidia-installer.log`: post-install sanity check passed, installation complete.
- `sudo olares-cli gpu enable`: exit 0; штатная команда назначила реальные GPU labels и перезапустила GPU/HAMi pods. Ручного изменения runtime или подделки GPU labels не было.

## Проверки

- `nvidia-smi`: NVIDIA GB10, driver 595.84, CUDA driver API capability 13.2, 39–40 °C; это не утверждение об установленном CUDA Toolkit.
- `/proc/driver/nvidia/version`: NVIDIA UNIX Open Kernel Module for aarch64 595.84.
- Через Python ctypes: `libcuda.so.1: cuInit(0)=0`; `libnvidia-ml.so.1: nvmlInit_v2()=0`, shutdown=0.
- `sudo nvidia-ctk cdi generate >/dev/null`: exit 0, спецификация CDI 0.7.0 с NVML и драйвером 595.84. Постоянный CDI-файл этой командой не записывался.
- hami-scheduler-7d47857bdf-vx9tn: 2/2 Running, 0 restarts.
- hami-device-plugin-4zn7q: 2/2 Running, 0 restarts; DaemonSet desired/current/ready 1/1/1.
- os-gpu/gpu-scheduler: 1/1 Running.
- Kubernetes allocatable nvidia.com/gpu=30 — виртуальные доли HAMi, не 30 физических GPU.
- По `sudo dmesg | grep -i Xid`: Xid текущей загрузки не обнаружены. CUDA kernel/inference stress test не проводился.
- Предупреждения установщика об X paths/Vulkan loader и необязательных CDI graphics/socket компонентах не блокировали CUDA/NVML/CDI. Проверка локального графического рабочего стола не выполнялась.

## Продолжение Olares

Прежний отказ CheckGPUState устранён по его критерию: локальный hami-device-plugin теперь Running. `kubectl get terminus` сообщает отсутствие типа ресурса; установленного экземпляра Olares пока нет. Исходники версии предусматривают повтор частичной установки, но не отдельную команду resume.

Прежние параметры аккаунта не удалось восстановить безопасно: user-env.yaml оказался схемой, account/values.yaml — исходными значениями шаблона; в журнале нет выполненных GetUserInfo/SetAccountValues. В журнале olaresd есть прежнее имя [OLARES_USER], но одного имени недостаточно для восстановления исходного запроса с доменом и password hash. Процесс прежней установки не работает, после пользовательской перезагрузки его environment утрачен. Новый пароль/аккаунт не генерировались.

Следующее действие пользователя: открыть в LarePass карточку Spark [SPARK_LAN_IP] и повторить Install now, если кнопка доступна; Uninstall не нажимать. Если интерфейс предлагает только Uninstall, нужен снимок карточки для выбора безопасного следующего шага. Затем можно наблюдать установку по SSH и довести её до Activate now/Web Desktop.

В рамках работы не было reboot, uninstall, удаления маркеров, переустановки ОС или повторного запуска Olares installer. Web Desktop ещё не получен.
