# Тестовий кейс #129

```
iOS app MVP · специфікація фінальна · вересень 2026

Микола і я провели 3 сесії по специфікації. Ось що будуємо для першого релізу.

MVP scope (October release):
✓ Перегляд тайлів (read-only + basic edit)
✓ Створення нового тайлу
✓ Quick Capture (global shortcut через widget)
✓ Пошук по тайлах
✓ Sync з web (real-time)
✓ Dark mode

NOT in MVP:
✗ AI Suggestions (Q1 2027)
✗ Collaboration (Q1 2027)  
✗ Offline mode (Q2 2027)
✗ Widgets крім Quick Capture

Ключові технічні рішення:
→ SwiftUI (не UIKit) — майбутнє, Микола впевнений
→ Local-first sync з CloudKit — offline буде легше додати потім
→ Push notifications: базові (тільки @ mentions)

App Store submission: 15 жовтня 2026.
Beta (TestFlight): 1 жовтня для 100 юзерів.
```
