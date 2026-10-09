# Запрос о TCP CONNECT в Codex Cloud

Статус на 2026-10-09: подготовлен для пользователя; агент его не отправлял.
Поддержка OpenAI: https://help.openai.com/ — кнопка чата внизу справа.
Официальная инструкция:
https://help.openai.com/en/articles/6614161-how-can-i-contact-support

## Текст запроса

В Codex Cloud настроен и опубликован Tailscale VPN. Проверка выполнена
в новой задаче из опубликованной среды, а не в прежнем executor.
В `/etc/codex/network-policy.json`:

```json
{
  "vpn_configured": true,
  "tcp_connect_proxy": "http://proxy:8088",
  "tcp_network_access": {
    "domains": [],
    "ip_ranges": []
  }
}
```

Имя `proxy` разрешается в IP, но TCP connection к `proxy:8088` завершается
`Connection refused`, поэтому CONNECT request не отправлялся. В редакторе
среды есть VPN/Tailscale и HTTP internet-access settings, но нет настройки
TCP destination grants (IP/CIDR/domains).

Нужен TCP-доступ к сервису в своей Tailscale-сети на `100.105.205.79:2222`;
запрашиваемый CIDR — `100.105.205.79/32`. Сам сервис на VM проверен локально:
получен SSH banner. Это подтверждение VM-local relay, не облачного доступа.

Доступен ли raw TCP через CONNECT proxy:8088 для моего плана и этой среды?
Если доступен, каким поддерживаемым способом добавить destination grant и
включить listener? Если нет, прошу подтвердить ограничение продукта.

## Дополнения при отправке

Указать свой план и ссылку/ID **новой задачи**, где vpn_configured=true,
добавить скриншот настроенного VPN и результат её сетевой диагностики.
Ключ Tailscale, SSH password и account tokens в обращение не включать.

## Что не установлено

- Фактическая готовность VPN не подтверждена одним флагом vpn_configured.
- Пустые grants и Connection refused не доказывают, что TCP отключён во всех
  планах или недоступен принципиально; оператор должен уточнить конфигурацию.
- В доступных публичных инструкциях не найден пользовательский редактор этих
  grants. Локальный network-policy.json — snapshot, его изменение не меняет
  sidecar enforcement. Tailscale ACL не включает listener облачного proxy.
- HTTP/HTTPS service access через VPN документирован отдельно; это не
  подтверждает разрешение непрозрачного SSH/TCP tunnel через HTTP proxy.
