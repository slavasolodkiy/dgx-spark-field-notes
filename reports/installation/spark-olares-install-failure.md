> ARCHIVED REPORT: host/account identifiers redacted for publication. Measurements are unchanged. This is a contemporaneous report, not a substitute for its referenced raw files.

# OlaresOS 1.12.7 — диагностика сбоя установки на DGX Spark

2026-10-23. SSH: `[USER]@[SPARK_LAN_IP]`. Только чтение; конфигурация и службы не изменялись, перезагрузок и повторных установок не было.

## Итог

**Диагностика PASS; установка BLOCKED (14%).** Точный failing step: модуль `InstallPlugin`, действие `CheckGPUState`. В 12:30:09.630 UTC оно завершилось после 8m18.091176512s ожидания GPU device plugin. Причина — незавершённая установка NVIDIA 595.84 после отказа ядра загрузить неподписанный модуль; отсутствует NVML. Это не подтверждение несовместимости версии 595.84 с GB10.

## Доказательства и причинная цепочка

1. `/var/log/nvidia-installer.log`, создан 23 октября 11:46:17 (часовой пояс в заголовке не указан), installer 595.84: сборка модуля завершилась; затем `Kernel module load error: Key was rejected by service`, сообщение ядра `Loading of unsigned module is rejected`, итог `Installation has failed`. Сейчас `mokutil --sb-state` показывает `SecureBoot enabled`. Отказ подписи подтверждён сохранённым журналом установки, а не новым событием текущей загрузки.
2. `ldconfig -p` не содержит `nvidia-ml`; поиск в `/usr/lib` и `/usr/local/lib` тоже не нашёл библиотеку. Следовательно, одного разрешения загрузки модуля недостаточно: нужно завершить установку согласованных библиотек драйвера.
3. `/home/olares/.olares/versions/v1.12.7/logs/install.log`: в 12:21:42.425 UTC — `NVIDIA driver is not installed`; затем `UpdateNodeGPUInfo success`. Узел не имеет `gpu.bytetrade.io/cuda-supported=true`. DaemonSet `hami-device-plugin` с этим node selector имеет **DESIRED/CURRENT/READY = 0/0/0**.
4. В 12:21:51.539 UTC Helm сообщает успешную установку chart hami, но `CheckGPUState` далее повторяет `GPU Container State is Pending`, завершаясь в 12:30:09.630 UTC. Это обобщённый текст проверки, а не свидетельство существующего Pod в фазе Pending: device-plugin Pod отсутствует.
5. Отдельно `hami-scheduler-564cc98697-2b5ck` имеет 1/2 Ready, CrashLoopBackOff. Контейнер `vgpu-scheduler-extender`, образ `beclab/hami:v2.6.28`: `StartError`, exit 128. OCI/CDI ошибка до запуска процесса: `failed to generate CDI spec for mode "auto"` → `failed to initialize NVML: ERROR_LIBRARY_NOT_FOUND`.
6. `/etc/containerd/conf.d/99-nvidia.toml` задаёт default runtime `nvidia` и `/usr/bin/nvidia-container-runtime`. NVIDIA Container Toolkit 1.19.1 установлен, но драйверная NVML отсутствует.

Исходник точно совпадает с установленным CLI commit `e4a353dfe737d1dd924b609b7576c047153a85b9`: [CheckGpuStatus](https://github.com/beclab/Olares/blob/e4a353dfe737d1dd924b609b7576c047153a85b9/cli/pkg/gpu/tasks.go) ждёт фазу Running у локального `hami-device-plugin`; [CudaInstalled](https://github.com/beclab/Olares/blob/e4a353dfe737d1dd924b609b7576c047153a85b9/cli/pkg/gpu/prepares.go) на GB10 возвращает true, предполагая готовую CUDA. Это объясняет, почему проверка GPU всё равно выполняется при фактически отсутствующем драйвере. [InstallPlugin](https://github.com/beclab/Olares/blob/e4a353dfe737d1dd924b609b7576c047153a85b9/cli/pkg/gpu/module.go) задаёт 50 попыток с задержкой 10 секунд.

## Что работает

- SSH доступен. Kernel `6.14.0-1015-nvidia`, ARM64, Ubuntu 24.04.
- `olaresd`, `containerd`, `k3s`: active; failed systemd units: 0.
- Kubernetes `v1.33.3+k3s1`, узел `olares`: Ready.
- Calico, CoreDNS, Multus, OpenEBS, KubeSphere apiserver и monitoring: Running/Ready.
- В журнале в 12:21:42.388 UTC: `k8s and kubesphere installation is complete`.
- Начальные ошибки Calico/service account не сохраняются у соответствующих pod. Сетевая ошибка или общий отказ Kubernetes не объясняют текущий failing step. Это не полная проверка всех внешних сетевых сервисов.

## Минимальное исправление — предложение, не выполнено

Восстановить **только NVIDIA driver stack**, сохранив существующие ОС и кластер: модуль под текущий kernel должен иметь доверенную подпись, а соответствующие ARM64 userspace библиотеки, включая NVML, должны быть полностью установлены. Предпочтителен путь с сохранением Secure Boot: подходящий подписанный пакет либо подписание модуля доверенным ключом. Конкретный пакет/ключ ещё не выбран; регистрация нового MOK может потребовать локального подтверждения и перезагрузки, поэтому это отдельная ремонтная операция.

[Официальная документация NVIDIA 595.84 ARM64](https://download.nvidia.com/XFree86/Linux-aarch64/595.84/README/installdriver.html#SigningTheNVIDIAModule) описывает подпись модуля и требование доверия к ключу. Простое отключение Secure Boot само по себе не завершит оборванную установку библиотек. Переключение runtime на runc также не создаст работающий GPU device plugin.

После ремонта нужны проверки `nvidia-smi`, NVML, готовности HAMi и корректной метки GPU, затем проверенный повтор установки поверх сохранённого состояния. Безопасный resume для именно этого частичного состояния ещё не подтверждён: не предлагаю вслепую запускать `install`, `uninstall` или вручную подделывать CUDA label. Признаков необходимости полной переустановки ОС не найдено.

[Официальная Spark ISO инструкция](https://www.olares.com/docs/manual/get-started/install-spark-iso) просмотрена; она не даёт адресного восстановления данного сбоя подписи/NVML. Указание на выключение/включение после ISO не заменяет выявленную причину; никакие power actions не выполнялись.

## Воспроизводимые read-only команды

```bash
olares-cli status
olares-cli version
systemctl is-active olaresd containerd k3s
systemctl --failed --no-pager
sudo kubectl get nodes
sudo kubectl get pods -A
sudo kubectl -n kube-system get ds -l app.kubernetes.io/component=hami-device-plugin -o wide
sudo kubectl get node olares -o jsonpath='{.metadata.labels}'
sudo kubectl -n kube-system describe pod hami-scheduler-564cc98697-2b5ck
tail -65 /home/olares/.olares/versions/v1.12.7/logs/install.log
sudo grep -E 'Kernel module load error|unsigned module|Installation has failed' /var/log/nvidia-installer.log
mokutil --sb-state
ldconfig -p | grep nvidia-ml
sudo cat /etc/containerd/conf.d/99-nvidia.toml
nvidia-ctk --version
```

Смежный файл `spark-olares-install-failure-evidence.txt` содержит вывод повторной проверки (с переносами интерактивного терминала). Пароли не сохранены.
