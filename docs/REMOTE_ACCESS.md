# Доступ из облачной среды к GPU-серверу

2026-10-09: в текущей исследовательской сессии HTTPS работает,
`vpn_configured=false`, TCP grants пусты, CONNECT listener `proxy:8088`
недоступен. Пользователь уже настроил и опубликовал Tailscale в редакторе
среды, но текущая задача сохраняет прежнюю конфигурацию. Нужно проверить
новую задачу из опубликованной среды. Это не проверка пароля сервера.

Обновление: пользователь уже проверил новую опубликованную среду. Там
`vpn_configured=true`, но TCP grants всё ещё пусты, а подключение к
`proxy:8088` возвращает Connection refused. CONNECT и SSH authentication
не выполнялись. Доступный пользователю редактор TCP-разрешений не найден;
следующий шаг — уточнить поддержку TCP CONNECT у платформы. Текст запроса:
`docs/TCP_SUPPORT_REQUEST.md`. Повторное создание задачи как решение
того же результата не предлагать.

Официальная настройка: Settings → Codex Cloud → Environments → Edit →
Advanced → VPN → Add → Tailscale. Источник:
https://learn.chatgpt.com/docs/environments/cloud-environments#private-networking-vpn

В Tailscale создать учётную запись / сеть. Ключ для **облачной среды**:
Reusable и Ephemeral включены. Вводить его в VPN settings, не в Git или чат.
Узел GPU-сервера либо финской VM подключить к той же сети через обычный
browser login; не делать постоянный сервер ephemeral.

## Прямое подключение сервера

Если есть sudo и разрешение администратора на установку VPN, выполнить
на GPU-сервере команды официального Linux installer:

```sh
curl -fsSL https://tailscale.com/install.sh -o /tmp/install-tailscale.sh
sh /tmp/install-tailscale.sh
sudo tailscale up --accept-dns=false --accept-routes=false
tailscale ip -4
```

Installer может запросить sudo. Открыть ссылку, выданную `tailscale up`,
и войти в тот же Tailscale account. Сохранить адрес вида 100.x.y.z.
Использовать существующий OpenSSH на порту 22; Tailscale SSH включать не требуется.
Источник: https://tailscale.com/docs/install/linux

## Финская VM как промежуточный сервер

Это выбранная пользователем схема. VM успешно подключена к Tailscale,
ОС Ubuntu 24.04.4 LTS. Агент остаётся в облаке, sudo на GPU-сервере нет.
Пользователь подтвердил работу постоянного relay: получен SSH banner
`SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.19`. SSH authentication ещё не проверена.
VPN опубликован в настройках Codex; текущая задача остаётся без VPN/TCP grants.

Если GPU-сервер общий и устанавливать пакеты нельзя, установить Tailscale
по тем же командам на собственную финскую VM. AmneziaWG не является VPN
provider для Codex; менять её конфигурацию для этой схемы не требуется.
Сначала проверить, что сама VM может подключиться к GPU-серверу по обычному SSH.

На Debian/Ubuntu VM установить `socat`. Для временной проверки, подставив
адреса вместо CAPITALIZED placeholders:

```sh
sudo apt-get update
sudo apt-get install -y socat
socat TCP4-LISTEN:2222,bind=VM_TAILSCALE_IP,reuseaddr,fork TCP4:GPU_PUBLIC_IP:22
```

Пересылка слушает только Tailscale IP, не публичный интерфейс. Оставить команду
работающей на время проверки; для постоянной работы затем оформить systemd
service с тем же ExecStart и непривилегированным пользователем. Никакие
SSH credentials relay не нужны: authentication остаётся на GPU-сервере.
Codex подключается к VM_TAILSCALE_IP:2222, а SSH проверяет host key GPU-сервера.
Это relay одного сервиса, не перенаправление всего интернет-трафика.

Для постоянной пересылки подготовлен standalone helper
`scripts/setup_ssh_relay.py` (Python stdlib, Ubuntu/Debian). Он сначала
проверяет, что local Tailscale IP соответствует `--listen-ip`, и только потом
устанавливает socat и собственную systemd-службу. Запускать **на relay VM**:

```sh
python3 scripts/setup_ssh_relay.py --listen-ip VM_TAILSCALE_IP --target-ip GPU_PUBLIC_IP --print-unit
sudo python3 scripts/setup_ssh_relay.py --listen-ip VM_TAILSCALE_IP --target-ip GPU_PUBLIC_IP
```

Служба `lora-dora-ssh-relay.service` работает от nobody, слушает только заданный
Tailscale IPv4 на порту 2222, автоматически запускается после перезагрузки.
SSH credentials ей не нужны. Helper отказывается перезаписывать чужую службу
с тем же именем. Баннер SSH в результате доказывает работу VM-local TCP relay,
но не доступ из Codex или успешную SSH-аутентификацию. Если баннер не получен,
посмотреть собственный журнал службы и доступ VM к TCP/22 GPU-сервера:

```sh
sudo systemctl status lora-dora-ssh-relay.service --no-pager
sudo journalctl -u lora-dora-ssh-relay.service -n 20 --no-pager
```

Остановка и отключение именно этой службы:

```sh
sudo systemctl disable --now lora-dora-ssh-relay.service
```

## Облачная среда и разрешения

В VPN settings ввести auth key из той же Tailscale сети. Это уже выполнено:
пользователь прислал скриншот опубликованной среды с Tailscale «Настроено».
Показанный интерфейс не содержит отдельной настройки raw TCP/IP/CIDR;
документированный пользовательский способ добавить TCP grant не установлен.
Ранее агент ошибочно предположил, что такое поле может быть доступно.
Не просить пользователя искать не подтверждённый переключатель.

Для supported CONNECT на `proxy:8088` runtime-инструкция требует VPN и TCP
grant к точному IP/CIDR или hostname. HTTP allowlist сам по себе TCP не разрешает.
Tailscale access rules должны разрешать облачному узлу соответствующий порт:
22 либо 2222. Сначала проверить **новую задачу** из опубликованной среды:
startup policy, статус VPN, grants и доступность CONNECT listener. Не заключать,
что TCP недоступен во всех новых задачах, по состоянию старого executor.
Если новая конфигурация не даёт grant, понадобится поддерживаемое изменение
политики через оператора/настройку платформы. Редактирование локального JSON,
смена порта relay или установка VPN внутри контейнера grant не добавляют.

Save / Republish, затем использовать обновлённую среду. Изменение TCP grants
требует replacement environment. Согласно официальной документации existing
tasks сохраняют своё состояние; новая задача начинает работу из опубликованной среды.
Перед заменой сохранить работу в Git. Новая среда должна checkout ветку
`research/prepare-checkpoint-study` этого репозитория.

Агенту передать только Tailscale IPv4, выбранный порт и подтверждение
перезапуска среды. Далее агент проверит policy/CONNECT, настроит SSH
через разрешённый `proxy:8088`, с проверкой host key, и продолжит пилот.
Не устанавливать VPN внутри контейнера Codex и не обходить policy через
HTTP proxy. Сам агент остаётся в облаке.

Если пункта Advanced → VPN нет, сначала выяснить доступные настройки;
одна установка Tailscale на сервер этого ограничения не снимает.
