# Доступ из облачной среды к GPU-серверу

2026-10-09: HTTPS работает, но VPN не настроен (`vpn_configured=false`),
TCP grants пусты, CONNECT listener `proxy:8088` недоступен. До изменения
настроек подключение по SSH невозможно; это не проверка пароля сервера.

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

## Облачная среда и разрешения

В VPN settings ввести auth key из той же Tailscale сети. Дополнительно
разрешить **raw TCP** к точному Tailscale IPv4 /32 (GPU либо relay VM).
Обычный HTTP allowlist сам по себе TCP не разрешает. Tailscale access rules
должны разрешать облачному узлу соответствующий порт: 22 либо 2222.
Если интерфейс не показывает отдельного TCP-разрешения, требуется настройка
через поддерживаемый flow облачной среды, а не редактирование контейнера.

Save / Republish, затем использовать обновлённую среду. Изменение TCP grants
требует replacement environment. Старый task может сохранить старые настройки.
Перед заменой сохранить работу в Git. Новая среда должна checkout ветку
`research/prepare-checkpoint-study` этого репозитория.

Агенту передать только Tailscale IPv4, выбранный порт и подтверждение
перезапуска среды. Далее агент проверит policy/CONNECT, настроит SSH
через разрешённый `proxy:8088`, с проверкой host key, и продолжит пилот.
Не устанавливать VPN внутри контейнера Codex и не обходить policy через
HTTP proxy. Сам агент остаётся в облаке.

Если пункта Advanced → VPN нет, сначала выяснить доступные настройки;
одна установка Tailscale на сервер этого ограничения не снимает.
