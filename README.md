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

3. Repo → **Settings → Pages** → *Build and deployment* → Source: **GitHub Actions**.
   Sahifani `pages` workflow'i chiqaradi. Unga `CHAT_ID` secret kerak, shuning uchun avval 4-qadamni bajaring,
   keyin **Actions → pages → Run workflow** ni bosing (keyingi har push'da o'zi ishlaydi).
4. 1–2 daqiqadan so'ng sahifa shu manzilda ochiladi:

   ```
   https://<USERNAME>.github.io/byudjet-bot/
   ```

   Bu — sizning **WEBAPP_URL**. Oddiy brauzerda u «Bu shaxsiy ilova» deb ko'rsatadi — bu to'g'ri.

> Diqqat: repo ochiq, shuning uchun koddagi reja summalari hammaga ko'rinadi.
> Token va chat_id esa faqat Secrets'da turadi va hech qayerda ko'rinmaydi.
> Treker faqat `CHAT_ID` ga teng Telegram akkauntida ochiladi (pastda «Faqat egasi» ga qarang).

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
   - `slot`: `evening` (20:00 xabari) yoki `morning` (08:00 xabari);
   - `today` maydoniga `2026-11-04` yozing (bo'sh qoldirilsa — bugungi sana olinadi);
   - `dry_run` belgilanmagan bo'lsin → **Run workflow**.
3. Telegram'ga "Ertaga, 05.11:" xabari va "Trekerni ochish" tugmasi kelishi kerak.
4. **keepalive** → **Run workflow** ni ham bir marta ishga tushirib, xatosiz o'tishini tekshiring.

Shundan so'ng eslatmalar har kuni avtomatik keladi. GitHub cron ba'zan 5–30 daqiqa
kechikishi mumkin — bu normal holat.

---

## Qanday ishlaydi

### Treker (Mini App)

Pastki menyu: **Asosiy · Tarix · «+» · Reja · Tahlil**. Sozlamalar Asosiy ekran tepasidagi ⚙ tugmasidan ochiladi.
Ustiga ochiladigan sahifalar (yangi amal, HUMO, sozlamalar, jurnal) Telegram «Orqaga» tugmasi bilan yopiladi.

| Bo'lim | Nima bor |
|---|---|
| **Asosiy** | Jami balans, 7 kunlik chiziq va hisoblar (Karta, Naqd, Omonat — bosilsa qoldiqni tuzatish). Balans ostida ikki ko'rsatkich: **Erkin pul** — rejadagi barcha kelgusi to'lovlardan keyin karta va naqddan hozir sarflash mumkin bo'lgan summa (eng tig'iz kun bilan) va **Rejadan farq** (bosilsa, nimadan yig'ilgani). Tez amallar: Kirim, O'tkazma, HUMO, Yangi qarz. Keyin kartalar: **Yaqin to'lovlar** (o'tib ketgan belgilanmagan bandlar, eng yaqin to'lov kuni; kartada pul yetmasa — «Naqddan o'tkazish» tugmasi), **Diqqat** (HUMO bilan farq, qarz muddati, limit, qoida buzilishi, xohishlar), Bugun / Seriya / Salomatlik plitkalari, Xohishlar, Yakuniy maqsad, Qarzlar, Oxirgi amallar. Ko'z tugmasi summalarni yashiradi. Yo'lkira bu yerda eslatilmaydi (pulsiz borilgan kunlar ham bo'ladi) |
| **Qo'shish (+)** | Tepada Chiqim / Kirim / O'tkazma. Raqamlar paneli, tez summalar, «Kecha» va **Saqlash doim pastda** — surmasdan, bosh barmoq bilan yetadi. Hisob (qoldig'i bilan) va sana, izoh, kategoriyalar. Izoh yozilsa kategoriya o'zi tanlanadi; summa hali kiritilmagan bo'lsa izohga `30k non karta` yozib Enter bosish kifoya. Taqiqlangan xarajatda ogohlantirish chiqadi, rejadan tashqari katta xaridda «⏳ 24 soat» tugmasi |
| **Tarix** | Barcha amallar kunlar bo'yicha; qidiruv va filtrlar tepada yopishib turadi. Har amal tagida shu amaldan keyingi hisob qoldig'i (HUMO 💰 bilan bir xil), har kun ostida kun oxiridagi qoldiq. Chapga surish — o'chirish, o'ngga — bugunga nusxalash, 5 soniya «Qaytarish». Tepadagi soat belgisi — **o'zgarishlar jurnali** |
| **Reja** | Uch bo'lim: **Kalendar** (kunlar xarajatga qarab bo'yalgan, kunni tanlab «To'lash» / «Tushdi» / «Qulflash», ish kuni ↔ dam olish), **Qarzlar** («Men qarzdorman» / «Menga qarzdor», bosilsa to'liq yoki qisman to'lash va tarix), **Xohishlar** (24 soat kutayotganlar, hal qilinganlar, tejalgan summa) |
| **Tahlil** | Oy bo'yicha kirim/chiqim, oy yakuni, **pul oqimi prognozi**, **HUMO bilan solishtirish**, moliyaviy salomatlik, **g'ayrioddiy xarajatlar**, **oy oxiri prognozi**, **reja va haqiqat jadvali**, «Agar…» va «Qachon olaman?», xulosalar, kategoriyalar, kundalik xarajat, limitlar, eng katta xarajatlar, intizom xaritasi |
| **Sozlamalar (⚙)** | Ko'rinish (mavzu, Asosiy ekran kartalari, summalarni yashirish), Xavfsizlik (PIN-kod, barmoq izi, hozir qulflash), Reja va hisoblar (boshlang'ich qoldiqlar, oylik limitlar, ish kunlari), Ma'lumotlar (HUMO import, o'zgarishlar jurnali, zaxira va eksport) |

Tahlil bo'limidagi professional ko'rsatkichlar:

- **Pul oqimi prognozi** — 145 kunlik grafik: reja (punktir), haqiqiy balans (chiziq) va bugundan keyingi prognoz
  (nuqtali). Grafikni bossangiz, o'sha kunning qiymatlari chiqadi. Ostida davr oxiri prognozi va **eng tig'iz kun** —
  karta va naqdda eng kam pul qoladigan kun.
- **HUMO bilan solishtirish** — har HUMO xabaridagi 💰 karta qoldig'i shu amal bilan birga saqlanadi va trekerdagi
  karta qoldig'i bilan solishtiriladi. Farq bo'lsa, Diqqat'da ogohlantirish chiqadi: farq qaysi ikki HUMO xabari
  oralig'ida paydo bo'lgani va o'sha oraliqda qo'lda yozilgan karta amallari ko'rsatiladi, «Farqni tuzatish» bir bosishda.
- **G'ayrioddiy xarajatlar** — odatdagi xariddan 3 barobar katta xarid, haftalik o'rtachadan 2 barobar ko'p kategoriya
  va kunlik o'rtachadan 3 barobar ko'p kun. Haftalik taqqoslash uchun kamida 4 hafta ma'lumot kerak.
- **Oy oxiri prognozi** — shu oydagi rejadan tashqari xarajat sur'ati bo'yicha har kategoriya oy oxirida qancha bo'lishi;
  limit bo'lsa — oshib ketadimi va «kuniga X dan oshmang».
- **Reja va haqiqat** — har oy uchun rejadagi va haqiqiy kirim/chiqim, farqi bilan (joriy oy — bugungacha).

Qo'shimcha imkoniyatlar:

- **Oy yakuni («Wrapped»)** — oy oxirgi kuni va keyingi oyning 1–5-sanalarida Asosiy ekranda 🎬 banner chiqadi
  (istalgan oyni Tahlil → «… yakunini ko'rish» dan ochish mumkin). Story kabi to'liq ekranli kartalar: pul oqimi,
  eng ko'p xarajat, eng katta xarajat, intizom xaritasi, jamg'arma, salomatlik bali. Oxirida konfetti va
  «Rasm sifatida saqlash» (1080×1350 PNG).
- **Moliyaviy salomatlik (0–100)** — intizom (40), rejaga muvofiqlik (30), reja bandlari (15), qarzlar (15).
  Tahlil'dagi kartani bossangiz — har qism alohida va 9 ta nishon («7 kun taqiqsiz», «Qarzsiz», «Reja ustasi» …).
  Yangi nishon olinganda tabrik va konfetti.
- **Xulosalar** (Tahlil) — o'tgan hafta bilan solishtirish, rejadan tashqari xarajatsiz kunlar, limit sur'ati,
  eng ko'p sarflanadigan hafta kuni va joy (HUMO bo'yicha).
- **«Agar…» simulyatori** — Tahlil'da: «har kuni +X sarflasam / har oylikdan +Y tejasam»
  slayderlari, mart oxiridagi balans darhol qayta hisoblanadi.
- **Intizom xaritasi** — Tahlil'da 145 kunlik kvadratchalar: yashil — qoida bajarilgan, qizil — buzilgan.
  Kvadratni bossangiz, o'sha kun Reja'da ochiladi.
- **Tez yozish** — «+» oynasida summa kiritmasdan izohga bir qatorda yozing: `30k non karta`, `kecha 12 000 taksi naqd`,
  `+3.3m oylik` va Enter. Summa, kategoriya, hisob va sana o'zi ajratiladi, keyin «Saqlash» ni bosasiz.
- **Bot xabaridan bir bosishda** — eslatmada har to'lov uchun tugma bor: «✅ To'ladim: Claude obunasi»,
  «💰 Tushdi: Asosiy oylik», «🔒 Qulfladim». Bosilsa, treker shu to'lov bilan tayyor ochiladi — faqat «Saqlash».
  Agar band allaqachon yozilgan bo'lsa, o'sha amal tahrirlash uchun ochiladi. PIN bo'lsa — avval PIN.
- **Kalkulyator** — klaviaturada «+ − × ÷»: `25 000 + 12 000`, `120 000 ÷ 3`. Natija darhol hisoblanadi
  (ko'paytirish va bo'lish avval), saqlanadigan summa — natija.
- **«24 soat qoidasi» — xohishlar ro'yxati** — taqiqlangan yoki 30 000+ rejadan tashqari xarid yozilayotganda
  «24 soat kutaman» tugmasi chiqadi. Xarid darrov yozilmaydi; 24 soatdan keyin Diqqat'da «hali ham kerakmi?» so'raladi:
  «Ha, sotib oldim» — amal yoziladi, «Kerak emas» — summa «Tejalgan» hisobiga qo'shiladi, «Yana 24 soat» — kechiktiriladi.
- **Qachon sotib ola olaman?** — narxni yozasiz (Tahlil, Reja → Xohishlar yoki «Erkin pul» oynasidan). Karta va naqd
  (omonatga tegmasdan) rejadagi barcha to'lovlar bilan kunma-kun hisoblanadi va xariddan keyin hech qaysi kunda
  pul yetmay qolmaydigan eng erta sana ko'rsatiladi. Xohishlar ro'yxatidagi har xarid yonida ham shu sana turadi.
- **Jonli animatsiyalar** — balans raqami sanab o'zgaradi, kartalar silliq paydo bo'ladi, oylik tushganda yoki
  qarz yopilganda konfetti. Telefonda «harakatni kamaytirish» yoqilgan bo'lsa — animatsiyasiz.

Hisob-kitob qoidalari:

- **Jami balans** = boshlang'ich qoldiqlar + barcha kirimlar − barcha chiqimlar.
  O'tkazma (masalan, Karta → Omonat) jami balansni o'zgartirmaydi, faqat pulni bir hisobdan boshqasiga ko'chiradi.
- **Rejadan farq** = jami balans − (1 000 000 + bajarilgan reja bandlari).
  Rejadan tashqari har bir xarajat farqni kamaytiradi. Hali belgilanmagan bandlar farqqa ta'sir qilmaydi.
- **Prognoz** = jami balans + hali bajarilmagan reja bandlari. O'tib ketgan, yozilmagan yo'lkira hisobga olinmaydi
  (pulsiz borilgan kunlar ham bo'ladi).
- **Erkin pul** = rejadagi barcha kelgusi to'lovlar, qulflash va yo'lkiradan keyin karta + naqdda eng kam qoladigan summa
  (omonat hisobga olinmaydi). Shuncha sarflasangiz ham hech qaysi kunda pul yetmay qolmaydi.
- **PIN-kod**: Sozlamalar → Xavfsizlik bo'limida o'rnatiladi. Shundan so'ng treker har ochilganda va 1 daqiqadan ko'p fonda turgandan keyin 4 xonali PIN so'raydi. 5 marta xato kiritilsa, 30 soniya kutiladi. PIN unutilsa, xavfsizlik uchun trekerdagi barcha ma'lumotlar o'chiriladi — shuning uchun JSON zaxira saqlab qo'ying.
- **Barmoq izi / yuzni tanish**: PIN o'rnatilgandan keyin Sozlamalar → Xavfsizlik'da «Barmoq izi bilan ochish» kaliti chiqadi
  (faqat telefonda biometrika bo'lsa, Telegram 7.2+). Yoqilsa, treker ochilganda barmoq izi avtomatik so'raladi.
  Bekor qilsangiz — PIN bilan ochasiz. Har qurilmada alohida yoqiladi. Telegram Desktop'da biometrika yo'q, u yerda PIN ishlaydi.
  PIN o'chirilsa, biometrik ochish ham o'chadi.
- **Balansni tuzatish**: Asosiy ekranda hisobni bosing va haqiqiy qoldiqni kiriting.
  Farq "Balans tuzatish" amali sifatida yoziladi.
- Oylik va avans Kartaga tushadi. Ularni uch xil yozish mumkin: Reja → «Tushdi», HUMO import yoki «+» → Kirim (qo'lda).
- Ishga bormagan kunni (masalan, Ramazon hayiti) Reja'da "Dam olish" ga o'tkazing.
  O'sha kunning 10 000 so'mlik yo'lkirasi rejadan olib tashlanadi.
- **Faqat egasi**: treker faqat Telegram ID si `CHAT_ID` ga teng akkauntda ochiladi. Boshqa odam botni topib
  «Treker» ni bossa yoki manzilni brauzerda ochsa, «Bu shaxsiy ilova» ekrani chiqadi. Hech narsa yuklanmaydi
  va yozilmaydi. ID kodda turmaydi: `pages` workflow'i sahifaga faqat uning SHA-256 hash'ini joylaydi.
  Sizning amallaringiz, qarzlaringiz va jurnalingiz baribir faqat sizning Telegram bulutingizda turadi —
  boshqa akkaunt ularni hech qachon ko'ra olmaydi.

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

Importdan keyin 5 soniya «Qaytarish» tugmasi turadi. Keyinroq ham HUMO oynasidagi «Oxirgi import → Bekor qilish»
bilan oxirgi importni to'liq qaytarish mumkin: qo'shilgan amallar, yangi qarzlar va balans tuzatishi o'chadi.

### Ma'lumotlar qayerda saqlanadi

- **Telegram ichida (versiya 6.9+)** — Telegram CloudStorage'da. Telefon va kompyuterdagi Telegram'da bir xil
  ma'lumot ko'rinadi.
  - Kalitlar: `meta` (sozlamalar), `debts` (qarzlar) va har oy uchun alohida `t_2026-11` (amallar).
  - Har bir hujjat 3 500 belgilik bo'laklarga bo'lib saqlanadi (`t_2026-11_0`, `t_2026-11_1`, …),
    chunki CloudStorage'da bitta qiymat 4 096 belgidan oshmasligi kerak.
- **Kompyuterda sinaganda** (fayl yoki localhost) — brauzerning `localStorage`'ida (`byudjet:` prefiksi bilan).
- Birinchi versiyada belgilangan to'lovlar (`m_2026-11`) birinchi ochilishda avtomatik ko'chiriladi.
- Telegram va brauzer ma'lumotlari bir-biridan alohida. Ko'chirish yoki zaxiralash uchun **Sozlamalar → Zaxira va eksport**
  bo'limidan foydalaning:
  - zaxiralash: *Eksport* → *Nusxalash* → xavfsiz joyga saqlang;
  - tiklash: JSON ni joylab, *Import qilish* ni bosing.
- Telegram mobil ilovasida «CSV» va «JSON zaxira» tugmalari ulashish oynasini ochadi; u bo'lmasa, matn buferga
  nusxalanadi. CSV'ni Excel yoki Google Sheets'ga joylasangiz, u ustunlarga bo'linadi.

### Eslatmalar

| Qachon | Xabar |
|---|---|
| Har ish kuni, 08:00 | "Bugun ish kuni — faqat 10 000 yo'lkira, tushlik uydan" |
| To'lov kuni, 08:00 | Bugungi reja: to'lovlar va kirimlar ro'yxati (dam olish kuni bo'lsa ham keladi) |
| Oyning 1-sanasi, 08:00 | Oy rejasi: kirim, majburiy to'lovlar, yo'lkira, omonat, oy oxiridagi reja balansi |
| 4-sana, 20:00 | Ertaga: avans, ingliz tili kursi (2026-11-04 da qarz qaytishi ham) |
| 13-sana, 20:00 | Ertaga: Claude obunasi (2026-11-13 da Uzum qarzi ham) |
| 19-sana, 20:00 | Ertaga: asosiy oylik, telefon, omonatga qulflash |
| 20-sana, 20:00 | 2 500 000 qulflandimi? |
| Yakshanba, 20:00 | Keyingi haftaning to'lovlari va yo'lkira summasi |

Dam olish va bayram kunlari to'lov bo'lmasa, ertalabki xabar kelmaydi.

Bot reja asosida ishlaydi. U trekerdagi ma'lumotlarni ko'rmaydi: haqiqiy xarajatlarni ham, qo'lda o'zgartirilgan
dam olish kunlarini ham. Shaxsiy ogohlantirishlar treker ichida chiqadi: Asosiy ekrandagi **Diqqat** blokida.
U yerda ko'rinadi:

- muddati 3 kun ichida bo'lgan yoki o'tib ketgan qarzlar;
- 80% ga yetgan yoki oshgan oylik limitlar;
- bugun qoida buzilgani;
- har 7 kunlik seriya.

---

## Kompyuterda sinash

Faqat Python 3 kerak, qo'shimcha kutubxona yo'q.

```sh
python -m unittest -v

# Git Bash / Linux / macOS
TODAY=2026-11-04 python remind.py --dry-run
TODAY=2026-11-13 python remind.py --dry-run
TODAY=2027-03-20 python remind.py --dry-run
TODAY=2026-12-01 python remind.py --dry-run --slot morning   # ertalabki xabar + oy rejasi
TODAY=2026-11-15 python remind.py --dry-run                  # yakshanba: keyingi hafta
```

PowerShell'da:

```powershell
$env:TODAY = "2026-11-04"; python remind.py --dry-run
Remove-Item Env:TODAY
```

`--dry-run` xabarlarni yubormaydi, faqat ekranga chiqaradi va secretlarni talab qilmaydi.
Mini App'ni sinash uchun `index.html` ni brauzerda ochish kifoya (fayl va localhost'da egasi tekshirilmaydi).
Boshqa sanadagi holatni ko'rish uchun manzil oxiriga `?today=2026-11-13` qo'shing.

## Rejani o'zgartirish

Biror summa yoki sana o'zgarsa (masalan, oylik oshsa), uni **ikki joyda** bir xil yangilang:

1. `index.html` → `PLAN` (va `LOCK`) obyekti;
2. `remind.py` → `PLAN` (va `LOCK`) obyekti;

so'ng `CLAUDE.md` dagi moliyaviy qoidalarni ham yangilab, `python -m unittest` ni ishga tushiring.
Yakuniy reja balansi avtomatik qayta hisoblanadi.
