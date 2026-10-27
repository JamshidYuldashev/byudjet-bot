# byudjet-bot

5 oylik shaxsiy byudjet rejasi (2026-10-27 — 2027-03-20) uchun **serversiz** Telegram Mini App
va eslatma bot. Hammasi bepul: sahifa GitHub Pages'da, eslatmalar GitHub Actions'da ishlaydi.

- **`index.html`** — Mini App (treker): har kunlik to'lovlarni belgilash, rejadan tashqari
  xarajatni yozish, jami / naqd / qulflangan balans, maqsad sari progress.
- **`remind.py`** — har kuni soat 20:00 da (Toshkent) ertangi to'lovlar haqida xabar yuboradi,
  20-sanada esa 2 500 000 so'm qulflanganini so'raydi.
- **`.github/workflows/remind.yml`** — har kuni 15:00 UTC (20:00 Toshkent) da `remind.py` ni ishga tushiradi.
- **`.github/workflows/keepalive.yml`** — har oy workflowlarni qayta yoqadi, chunki GitHub
  60 kun faollik bo'lmasa cron'ni o'chirib qo'yadi.

Yakuniy reja balansi qoidalardan hisoblanadi: standart sozlamalarda 101 ish kuni,
**13 794 455 so'm**.

---

## Sozlash (bir martalik)

### 1. Bot yaratish (BotFather)

1. Telegram'da [@BotFather](https://t.me/BotFather) ni oching va `/newbot` yuboring.
2. Bot nomi va username'ini kiriting (username `bot` bilan tugashi kerak, masalan `mening_byudjet_bot`).
3. BotFather bergan **token**ni saqlab qo'ying (`123456789:AA...` ko'rinishida).
   Bu token — parol. Uni hech kimga bermang va kodga yozmang.

### 2. `chat_id` ni olish

1. O'zingizning yangi botingizni oching va unga `/start` yozing.
2. Brauzerda quyidagi manzilni oching (`<TOKEN>` o'rniga o'z tokeningizni qo'ying):

   ```
   https://api.telegram.org/bot<TOKEN>/getUpdates
   ```

3. Javobda `"chat":{"id":123456789, ...}` qismini toping. Shu raqam — sizning **CHAT_ID**.
   - Agar `"result":[]` bo'sh bo'lsa, botga yana bitta xabar yozib, sahifani yangilang.

> Eslatma: "Trekerni ochish" tugmasi (`web_app`) faqat bot bilan **shaxsiy chatda** ishlaydi.
> Shuning uchun CHAT_ID guruh emas, aynan sizning shaxsiy chatingiz bo'lishi kerak.

### 3. GitHub repo va Pages

1. GitHub'da **public** repo yarating: `byudjet-bot` (bepul Pages uchun repo ochiq bo'lishi kerak).
2. Kodni yuklang:

   ```sh
   git remote add origin https://github.com/<USERNAME>/byudjet-bot.git
   git push -u origin main
   ```

3. Repo → **Settings → Pages** → *Build and deployment*:
   - Source: **Deploy from a branch**
   - Branch: **main**, papka: **/ (root)** → **Save**.
4. 1–2 daqiqadan so'ng sahifa shu manzilda ochiladi:

   ```
   https://<USERNAME>.github.io/byudjet-bot/
   ```

   Bu — sizning **WEBAPP_URL**. Uni oddiy brauzerda ochib tekshirib ko'ring.

> Diqqat: repo ochiq, shuning uchun `index.html` dagi summalar hammaga ko'rinadi.
> Token va chat_id esa faqat Secrets'da turadi va hech qayerda ko'rinmaydi.

### 4. Secrets qo'shish

Repo → **Settings → Secrets and variables → Actions → New repository secret**.
Uchta secret qo'shing:

| Nomi | Qiymati |
|---|---|
| `BOT_TOKEN` | BotFather bergan token |
| `CHAT_ID` | 2-qadamda topilgan raqam |
| `WEBAPP_URL` | `https://<USERNAME>.github.io/byudjet-bot/` |

### 5. Menu Button (bot ichida "Treker" tugmasi)

1. @BotFather → `/mybots` → botingizni tanlang.
2. **Bot Settings → Menu Button → Configure menu button**.
3. URL sifatida **WEBAPP_URL** ni yuboring, keyin tugma nomini yozing, masalan `Treker`.
4. Endi bot chatida, yozish maydonining chap tomonida "Treker" tugmasi paydo bo'ladi.

### 6. Qo'lda sinov

1. Repo → **Actions** bo'limi. Agar so'ralsa, workflowlarni yoqing (*I understand... enable*).
2. **remind** → **Run workflow**:
   - `today` maydoniga `2026-11-04` yozing (bo'sh qoldirilsa — bugungi sana olinadi);
   - `dry_run` belgilanmagan bo'lsin → **Run workflow**.
3. Telegram'ga "Ertaga, 05.11:" xabari va "Trekerni ochish" tugmasi kelishi kerak.
4. **keepalive** → **Run workflow** ni ham bir marta ishga tushirib, xatosiz o'tishini tekshiring.

Shundan so'ng eslatmalar har kuni avtomatik keladi. GitHub cron ba'zan 5–30 daqiqa
kechikishi mumkin — bu normal holat.

---

## Qanday ishlaydi

### Treker (Mini App)

- **Jami balans** = boshlang'ich 1 000 000 + belgilangan kirimlar − belgilangan chiqimlar − barcha rejadan tashqari xarajatlar.
- **Qo'ldagi naqd** = jami − qulflangan. **Qulflangan** = belgilangan "Omonatga qulflash" (har 20-sana, 2 500 000).
  Qulflash jami balansni o'zgartirmaydi, faqat pulni naqddan omonatga ko'chiradi.
- **Bugun kechgacha reja** — reja bo'yicha bugun kechqurun bo'lishi kerak bo'lgan balans.
- **Qoida buzilgan kunlar** — rejadan tashqari xarajat yozilgan kunlar soni. Bunday kun qizil bo'ladi.
- Har bir kunda **"Ish kuni" / "Dam olish"** tugmasi bor: almashtirsangiz, o'sha kunning 10 000 so'mlik
  yo'lkirasi rejaga qo'shiladi yoki olib tashlanadi. Masalan, Ramazon hayiti sanasi e'lon qilinganda
  o'sha kunni "Dam olish" ga o'tkazing.

### Ma'lumotlar qayerda saqlanadi

- Telegram ichida (versiya 6.9+) — **Telegram CloudStorage**'da, har oy alohida kalitda (`m_2026-11` va h.k.).
  Telefon va kompyuterdagi Telegram'da bir xil ma'lumot ko'rinadi.
- Oddiy brauzerda — o'sha brauzerning `localStorage`'ida.
- Bu ikki joy bir-biridan alohida. Ma'lumotni ko'chirish yoki zaxiralash uchun sahifa pastidagi
  **Zaxira nusxa** bo'limidan foydalaning: *Eksport* → *Nusxalash* → xavfsiz joyga saqlang;
  tiklash uchun JSON ni joylab *Import qilish* ni bosing.

### Eslatmalar

| Qachon (20:00) | Xabar |
|---|---|
| 4-sana | Ertaga: avans, ingliz tili kursi (2026-11-04 da qarz qaytishi ham) |
| 13-sana | Ertaga: Claude obunasi (2026-11-13 da Uzum qarzi ham) |
| 19-sana | Ertaga: asosiy oylik, telefon, omonatga qulflash |
| 20-sana | 2 500 000 qulflandimi? |

Kundalik 10 000 so'mlik yo'lkira har kuni takrorlanmasligi uchun eslatmalarga kiritilmagan.

---

## Kompyuterda sinash

Faqat Python 3 kerak, qo'shimcha kutubxona yo'q.

```sh
python -m unittest -v

# Git Bash / Linux / macOS
TODAY=2026-11-04 python remind.py --dry-run
TODAY=2026-11-13 python remind.py --dry-run
TODAY=2027-03-20 python remind.py --dry-run
```

PowerShell'da:

```powershell
$env:TODAY = "2026-11-04"; python remind.py --dry-run
Remove-Item Env:TODAY
```

`--dry-run` xabarlarni yubormaydi, faqat ekranga chiqaradi va secretlarni talab qilmaydi.
Mini App'ni sinash uchun `index.html` ni brauzerda ochish kifoya.

## Rejani o'zgartirish

Biror summa yoki sana o'zgarsa (masalan, oylik oshsa), uni **ikki joyda** bir xil yangilang:

1. `index.html` → `PLAN` (va `LOCK`) obyekti;
2. `remind.py` → `PLAN` (va `LOCK`) obyekti;

so'ng `CLAUDE.md` dagi moliyaviy qoidalarni ham yangilab, `python -m unittest` ni ishga tushiring.
Yakuniy reja balansi avtomatik qayta hisoblanadi.
