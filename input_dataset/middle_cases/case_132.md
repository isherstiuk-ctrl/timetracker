# Тестовий кейс #132

```
Incident review · third-party integration failure · 15 серпня

Наш Zapier integration ліг на 6 годин через зміни в Zapier API.
47 юзерів affected. Жодного enterprise клієнта — пощастило.

Timeline:
14:00: перша скарга в support
14:15: Влад повідомлений
15:30: root cause знайдено (deprecated endpoint)
16:00: fix deploy (1.5 години від виявлення)
20:00: всі affected юзери повідомлені (Олена + команда support)

Чому так довго (14:00 → 16:00):
→ Zapier не надіслали notice про deprecation (або ми пропустили)
→ Немає моніторингу на third-party integration health

Зміни після incident:
→ Zapier API changes: subscribe to their changelog
→ Synthetic monitoring: раз на 5 хвилин перевіряти ключові integrations
→ Runbook для Zapier incidents: написати до 25 серпня
```
