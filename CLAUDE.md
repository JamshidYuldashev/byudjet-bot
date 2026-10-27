# byudjet-bot

Serverless Telegram Mini App (`index.html`, GitHub Pages) + daily reminder bot
(`remind.py`, GitHub Actions cron) for a 5-month personal budget plan.

## Moliyaviy qoidalar (single source of truth)

Davr: **2026-10-27 — 2027-03-20** (ikkala sana ham kiradi).
Boshlang'ich balans 2026-10-27 holatiga: **1 000 000 so'm**.

### Kirimlar
- Har oyning 5-sanasi (Noyabr–Mart): +523 691 — oylik avans.
- Faqat 2026-11-05: +300 000 — qarz qaytishi.
- Har oyning 20-sanasi: +3 325 200 — asosiy oylik.

### Chiqimlar
- Har oyning 5-sanasi: −600 000 — ingliz tili kursi.
- Har oyning 14-sanasi: −410 000 — Claude obunasi.
- Faqat 2026-11-14: −430 000 — Uzum qarzini yopish.
- Har oyning 20-sanasi: −52 000 — telefon.
- Har ish kuni: −10 000 — yo'lkira (5k borish + 5k kelish).

### Qulflash
- Har oyning 20-sanasi: 2 500 000 omonatga/valyutaga o'tkaziladi.
  Naqddan qulflanganga ko'chadi, **jami balansni o'zgartirmaydi**.

### Ish kunlari
- Dushanba–Juma, quyidagi bayramlardan tashqari:
  2026-12-08 (Konstitutsiya kuni), 2027-01-01 (Yangi yil), 2027-03-08 (Xotin-qizlar kuni).
- Foydalanuvchi istalgan kunni "Ish kuni" / "Dam olish" ga almashtira oladi.

### Qat'iy qoidalar
- Ish kunlarida tushlik faqat uydan. Ko'chada ovqat, kofe, shirinlik, taksi — 0 so'm.
- Kunlik byudjet faqat 10 000 so'm yo'lkira.

### Yakuniy reja
Har doim qoidalardan hisoblanadi, hech qachon qattiq yozilmaydi.
Standart sozlamalarda: 101 ish kuni, yakuniy balans **13 794 455 so'm**
(master-promptdagi 13 754 455 oyiga 21 ish kuni deb taxmin qilingan).

## Loyiha qoidalari

- Moliyaviy ma'lumotlar `index.html` (`PLAN`) va `remind.py` (`PLAN`) da bir martadan
  config obyekt sifatida turadi. Biror summa o'zgarsa — **ikkalasini ham** va shu faylni yangilang.
- Foydalanuvchiga ko'rinadigan barcha matn (UI, bot xabarlari, README) — o'zbek tilida, lotin yozuvida.
- Secretlar (BOT_TOKEN, CHAT_ID, WEBAPP_URL) faqat GitHub Secrets / env orqali. Kodda hech qachon.
- `index.html`: vanilla HTML/CSS/JS, build yo'q. CDN: faqat telegram.org va jsdelivr (Tabler icons outline).
- `remind.py`: faqat Python 3 stdlib.
- Raqam formati: minglar bo'sh joy bilan (3 325 200), faqat butun sonlar.
- Reja sanalari UTC arifmetikasida; "bugun" — qurilmaning mahalliy sanasi.
- Ish beruvchi nomi kodda/README da ko'rsatilmaydi (repo ochiq).

## Tekshirish

```sh
python -m unittest
TODAY=2026-11-04 python remind.py --dry-run
```
