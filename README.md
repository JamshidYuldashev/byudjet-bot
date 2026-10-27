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

Pastki menyu: Asosiy · Tarix · **«+»** (o'rtada, yangi amal) · Qarzlar · Hisobot. Reja kalendari Asosiy ekrandagi
kalendar tugmasidan ochiladi (Telegram «Orqaga» tugmasi Asosiy'ga qaytaradi).

| Bo'lim | Nima bor |
|---|---|
| **Asosiy** | Jami balans, so'nggi 7 kunlik balans chizig'i va hisoblar (Karta, Naqd, Omonat), "Reja bo'yicha hozir" va rejadan farq — farqni bossangiz, u nimadan yig'ilgani chiqadi (rejadan tashqari xarajatlar kategoriyalar bilan, kirimlar, tuzatishlar). Ko'z tugmasi summalarni yashiradi, summani bosish yana ochadi. Qulf tugmasi trekerni darhol qulflaydi. "Bugungi xarajat" kartasi — bugun qancha sarflangani va rejadan tashqari qismi; bosilsa Tarix faqat bugungi amallar bilan ochiladi. Yo'lkira bu yerda eslatilmaydi (pulsiz borilgan kunlar ham bo'ladi): kerak bo'lsa «+» yoki Reja → «To'lash» orqali yoziladi. Keyingi to'lovlar (kartada pul yetadimi), belgilanmagan rejalar, maqsad va prognoz, qoidaga amal qilingan kunlar seriyasi, qarzlar, oxirgi amallar. Kartalarni Hisobot → Ko'rinish'da yashirish va tartiblash mumkin |
| **Qo'shish (+)** | Chiqim / Kirim / O'tkazma, raqamli klaviatura, tez summalar (5 000 … 100 000) va «Kecha» tugmasi, kategoriyalar, hisob, sana, izoh. Izoh yozilsa kategoriya o'zi tanlanadi (masalan, «sim karta» → Aloqa): tayyor kalit so'zlar va oldingi izohlaringizdan o'rganadi; qo'lda tanlangan kategoriya o'zgarmaydi. Ko'cha ovqati, kofe/shirinlik va taksi **taqiqlangan**: tanlansa ogohlantirish chiqadi, saqlansa kun "qoida buzilgan" bo'ladi |
| **Tarix** | **Amallar**: barcha amallar kunlar bo'yicha, qidiruv va filtrlar bilan. Har amal tagida shu amaldan keyingi hisob qoldig'i ko'rinadi, masalan «Karta: 939 040» — HUMO xabaridagi 💰 bilan bir xil (ko'z tugmasi yopiq bo'lsa — yashirin). Har kun ostida kun oxiridagi Karta/Naqd qoldig'i. «Balans tuzatish» qatorlari xira va kun/oy yig'indisiga kirmaydi. Qatorni **chapga surish — o'chirish**, **o'ngga — bugunga nusxalash**; amalni bosib tahrirlash, nusxalash yoki o'chirish ham mumkin. O'chirilgandan keyin 5 soniya «Qaytarish» tugmasi turadi. **Jurnal**: har bir o'zgarish vaqti bilan — amal qo'shildi, o'zgartirildi yoki o'chirildi; qarz ochildi, to'landi yoki yopildi; balans tuzatildi; ish kuni almashtirildi; sozlamalar o'zgardi; import qilindi |
| **Reja** | Oy kalendari, kunlar kundalik xarajatga qarab bo'yalgan (to'qroq — ko'proq sarflangan, qizil — qoida buzilgan). Kunni tanlab «To'lash» / «Tushdi» / «Qulflash» ni bosasiz. Kunni ish kuni yoki dam olish kuniga almashtirish mumkin |
| **Qarzlar** | Ikki ro'yxat: «Men qarzdorman» va «Menga qarzdor» (faollari tepada, yopilganlari pastda). Qarzni bossangiz oyna ochiladi: «To'liq to'landi / qaytdi» bir bosishda yoziladi, qisman summa ham kiritish mumkin, Karta yoki Naqd tanlanadi. Oynada qarzning to'liq tarixi ko'rinadi |
| **Hisobot** | Kategoriyalar diagrammasi, kunlik xarajat va limit, reja va haqiqiy balans grafigi, oylik kategoriya limitlari, eng katta xarajatlar. Shu yerda Ko'rinish (mavzu: Telegram / Yorug' / Qorong'i; Asosiy ekran kartalari), PIN-kod va barmoq izi (Xavfsizlik), CSV/JSON eksport, boshlang'ich qoldiqlar va zaxira ham bor. Balans tuzatishlar kirim/chiqim hisobiga kirmaydi |

Qo'shimcha imkoniyatlar:

- **Oy yakuni («Wrapped»)** — oy oxirgi kuni va keyingi oyning 1–5-sanalarida Asosiy ekranda 🎬 banner chiqadi
  (istalgan oyni Hisobot → «… yakunini ko'rish» dan ochish mumkin). Story kabi to'liq ekranli kartalar: pul oqimi,
  eng ko'p xarajat, eng katta xarajat, intizom xaritasi, jamg'arma, salomatlik bali. Oxirida konfetti va
  «Rasm sifatida saqlash» (1080×1350 PNG).
- **Moliyaviy salomatlik (0–100)** — intizom (40), rejaga muvofiqlik (30), reja bandlari (15), qarzlar (15).
  Kartani bossangiz — har qism alohida va 9 ta nishon («7 kun taqiqsiz», «Qarzsiz», «Reja ustasi» …).
  Yangi nishon olinganda tabrik va konfetti.
- **Xulosalar** — o'tgan hafta bilan solishtirish, rejadan tashqari xarajatsiz kunlar, limit sur'ati,
  eng ko'p sarflanadigan hafta kuni va joy (HUMO bo'yicha).
- **«Agar…» simulyatori** — Yakuniy maqsad kartasida: «har kuni +X sarflasam / har oylikdan +Y tejasam»
  slayderlari, mart oxiridagi balans darhol qayta hisoblanadi.
- **Intizom xaritasi** — Hisobot'da 145 kunlik kvadratchalar: yashil — qoida bajarilgan, qizil — buzilgan.
  Kvadratni bossangiz, o'sha kun Reja'da ochiladi.
- **Tez yozish** — «+» oynasining tepasida bir qatorda yozing: `30k non karta`, `kecha 12 000 taksi naqd`,
  `+3.3m oylik`. Summa, kategoriya, hisob va sana o'zi ajratiladi, keyin «Saqlash» ni bosasiz.
- **Jonli animatsiyalar** — balans raqami sanab o'zgaradi, kartalar silliq paydo bo'ladi, oylik tushganda yoki
  qarz yopilganda konfetti. Telefonda «harakatni kamaytirish» yoqilgan bo'lsa — animatsiyasiz.

Hisob-kitob qoidalari:

- **Jami balans** = boshlang'ich qoldiqlar + barcha kirimlar − barcha chiqimlar.
  O'tkazma (masalan, Karta → Omonat) jami balansni o'zgartirmaydi, faqat pulni bir hisobdan boshqasiga ko'chiradi.
- **Rejadan farq** = jami balans − (1 000 000 + bajarilgan reja bandlari).
  Rejadan tashqari har bir xarajat farqni kamaytiradi. Hali belgilanmagan bandlar farqqa ta'sir qilmaydi.
- **Prognoz** = yakuniy reja + rejadan farq.
- **PIN-kod**: Hisobot → Xavfsizlik bo'limida o'rnatiladi. Shundan so'ng treker har ochilganda va 1 daqiqadan ko'p fonda turgandan keyin 4 xonali PIN so'raydi. 5 marta xato kiritilsa, 30 soniya kutiladi. PIN unutilsa, xavfsizlik uchun trekerdagi barcha ma'lumotlar o'chiriladi — shuning uchun JSON zaxira saqlab qo'ying.
- **Barmoq izi / yuzni tanish**: PIN o'rnatilgandan keyin Xavfsizlik bo'limida «Barmoq izi bilan ochishni yoqish» chiqadi
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
- Telegram va brauzer ma'lumotlari bir-biridan alohida. Ko'chirish yoki zaxiralash uchun **Hisobot → Zaxira nusxa**
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
