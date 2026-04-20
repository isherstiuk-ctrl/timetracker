# Тестовий кейс #26

```
Нотатки після зустрічі по v3.0 bugs · понеділок 21 квітня

7 критичних багів. Висновок: 5 закриємо до 25-го, 2 — ні.

Баг 1 (AI вилітає при вставці > 5MB): race condition. До 23 квітня. ✓
Баг 2 (Sidebar не синхронізується): переписати WebSocket handler — 3-4 дні.
Рішення: включити з pop-up "real-time в beta".
Баг 3 (Dark mode не зберігається): простий фікс у localStorage. Олег сьогодні. ✓
Баг 4 (AI suggestions не відображаються на iOS 16): polyfill. 4-6 годин. До 22-го. ✓
Баг 5 (Search не знаходить тайли з emoji): Unicode normalization. 1 година. ✓
Баг 6 (Export в PDF обрізає > 3 сторінки): < 0.1% тайлів. "Known limitation".
Баг 7 (Notifications badge на Android): hotfix після релізу.

v3.0 виходить 29 квітня з двома "known limitations".
```
