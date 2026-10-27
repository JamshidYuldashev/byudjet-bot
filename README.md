# byudjet-bot

5 oylik shaxsiy byudjet rejasi (2026-10-27 — 2027-03-20) uchun **serversiz** Telegram Mini App
va eslatma bot. Hammasi bepul: sahifa GitHub Pages'da, eslatmalar GitHub Actions'da ishlaydi.

- **`index.html`** — Mini App (treker) quyidagilarni qiladi:
  - hisoblarni yuritadi: Karta, Naqd, Omonat;
  - har bir kirim va xarajatni kategoriya bilan yozadi;
  - reja kalendari, qarzlar va hisobotlarni ko'rsatadi;
  - HUMO xabarlaridan import qiladi.
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

Pastki menyuda 5 ta bo'lim bor. **«+»** tugmasi istalgan ekrandan yangi amal qo'shadi.

| Bo'lim | Nima bor |
|---|---|
| **Asosiy** | Jami balans va hisoblar (Karta, Naqd, Omonat), "Reja bo'yicha hozir" va rejadan farq. "Bugun sarflash mumkin" kartasi — yo'lkira bir bosishda yoziladi. Keyingi to'lovlar (kartada pul yetadimi), belgilanmagan rejalar, maqsad va prognoz, qoidaga amal qilingan kunlar seriyasi, qarzlar, oxirgi amallar |
| **Qo'shish (+)** | Chiqim / Kirim / O'tkazma, raqamli klaviatura, kategoriyalar, hisob, sana, izoh. Ko'cha ovqati, kofe/shirinlik va taksi **taqiqlangan**: tanlansa ogohlantirish chiqadi, saqlansa kun "qoida buzilgan" bo'ladi |
| **Tarix** | Barcha amallar kunlar bo'yicha, qidiruv va filtrlar bilan. Amalni bosib tahrirlash yoki o'chirish mumkin |
| **Reja** | Oy kalendari. Kunni tanlab «To'lash» / «Tushdi» / «Qulflash» ni bosasiz. Kunni ish kuni yoki dam olish kuniga almashtirish mumkin |
| **Qarzlar** | Men qarzdorman / menga qarzdor, muddat, qisman va to'liq to'lash, to'lovlar tarixi |
| **Hisobot** | Kategoriyalar diagrammasi, kunlik xarajat va limit, reja va haqiqiy balans grafigi, oylik kategoriya limitlari, eng katta xarajatlar. Shu yerda CSV/JSON eksport, boshlang'ich qoldiqlar va zaxira ham bor |

Hisob-kitob qoidalari:

- **Jami balans** = boshlang'ich qoldiqlar + barcha kirimlar − barcha chiqimlar.
  O'tkazma (masalan, Karta → Omonat) jami balansni o'zgartirmaydi, faqat pulni bir hisobdan boshqasiga ko'chiradi.
- **Rejadan farq** = jami balans − (1 000 000 + bajarilgan reja bandlari).
  Rejadan tashqari har bir xarajat farqni kamaytiradi. Hali belgilanmagan bandlar farqqa ta'sir qilmaydi.
- **Prognoz** = yakuniy reja + rejadan farq.
- **Balansni tuzatish**: Asosiy ekranda hisobni bosing va haqiqiy qoldiqni kiriting.
  Farq "Balans tuzatish" amali sifatida yoziladi.
- Oylik va avans Kartaga tushadi. Ularni uch xil yozish mumkin: Reja → «Tushdi», HUMO import yoki «+» → Kirim (qo'lda).
- Ishga bormagan kunni (masalan, Ramazon hayiti) Reja'da "Dam olish" ga o'tkazing.
  O'sha kunning 10 000 so'mlik yo'lkirasi rejadan olib tashlanadi.

### HUMO'dan import

Telegram botlarga boshqa bot bilan bo'lgan chatni o'qishga ruxsat bermaydi. Shuning uchun @HUMOcardbot
xabarlari nusxalab joylanadi:

1. @HUMOcardbot chatida xabarni bosib turing va kerakli xabarlarni belgilang, keyin **Nusxa olish** ni bosing.
2. Trekerda **HUMO import** → matnni joylang (yoki **Buferdan joylash** ni bosing).
3. Ilova har bir xabardan summa, joy, sana va qoldiqni ajratadi va quyidagilarni qiladi:
   - kategoriyani joy nomidan aniqlaydi (PAYNET → Aloqa, KORZINKA → Oziq-ovqat va h.k.);
   - reja bandiga mos kelsa (summa ±5%, sana ±3 kun), amalni o'sha bandga bog'laydi;
   - avval import qilingan xabarni qayta qo'shmaydi;
   - P2P o'tkazmada turini so'raydi: Omonatga, Qarz berdim yoki Xarajat;
   - naqd pul yechishni Karta → Naqd o'tkazmasi sifatida yozadi.
4. Oxirida trekerdagi Karta qoldig'ini HUMO'dagi oxirgi qoldiq bilan solishtiradi.
   Farq bo'lsa, uni "Balans tuzatish" sifatida yozishni taklif qiladi.

Matn faqat telefoningizda tahlil qilinadi va hech qayerga yuborilmaydi.

### Ma'lumotlar qayerda saqlanadi

- **Telegram ichida (versiya 6.9+)** — Telegram CloudStorage'da. Telefon va kompyuterdagi Telegram'da bir xil
  ma'lumot ko'rinadi.
  - Kalitlar: `meta` (sozlamalar), `debts` (qarzlar) va har oy uchun alohida `t_2026-11` (amallar).
  - Har bir hujjat 3 500 belgilik bo'laklarga bo'lib saqlanadi (`t_2026-11_0`, `t_2026-11_1`, …),
    chunki CloudStorage'da bitta qiymat 4 096 belgidan oshmasligi kerak.
- **Oddiy brauzerda** — shu brauzerning `localStorage`'ida (`byudjet:` prefiksi bilan).
- Birinchi versiyada belgilangan to'lovlar (`m_2026-11`) birinchi ochilishda avtomatik ko'chiriladi.
- Telegram va brauzer ma'lumotlari bir-biridan alohida. Ko'chirish yoki zaxiralash uchun **Hisobot → Zaxira nusxa**
  bo'limidan foydalaning:
  - zaxiralash: *Eksport* → *Nusxalash* → xavfsiz joyga saqlang;
  - tiklash: JSON ni joylab, *Import qilish* ni bosing.
- Telegram mobil ilovasida «CSV» va «JSON zaxira» tugmalari ulashish oynasini ochadi; u bo'lmasa, matn buferga
  nusxalanadi. CSV'ni Excel yoki Google Sheets'ga joylasangiz, u ustunlarga bo'linadi.

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
Mini App'ni sinash uchun `index.html` ni brauzerda ochish kifoya. Boshqa sanadagi holatni ko'rish uchun
manzil oxiriga `?today=2026-11-13` qo'shing.

## Rejani o'zgartirish

Biror summa yoki sana o'zgarsa (masalan, oylik oshsa), uni **ikki joyda** bir xil yangilang:

1. `index.html` → `PLAN` (va `LOCK`) obyekti;
2. `remind.py` → `PLAN` (va `LOCK`) obyekti;

so'ng `CLAUDE.md` dagi moliyaviy qoidalarni ham yangilab, `python -m unittest` ni ishga tushiring.
Yakuniy reja balansi avtomatik qayta hisoblanadi.
