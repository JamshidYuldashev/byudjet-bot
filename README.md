# byudjet-bot

Shaxsiy byudjet rejasi uchun **serversiz** Telegram Mini App
va eslatma bot. Hammasi bepul: sahifa GitHub Pages'da, eslatmalar GitHub Actions'da ishlaydi.

- **`index.html`** — Mini App (treker) quyidagilarni qiladi:
  - hisoblarni yuritadi: Karta, Naqd, Omonat;
  - har bir kirim va xarajatni kategoriya bilan yozadi;
  - reja kalendari, qarzlar va hisobotlarni ko'rsatadi;
  - HUMO xabarlaridan import qiladi.
- **`remind.py`** — har kuni 08:00 va 20:00 da (Toshkent) reja bo'yicha eslatma yuboradi: bugungi va ertangi
  to'lovlar, qulflash kuni — pul omonatga o'tkazildimi.
- **`.github/workflows/remind.yml`** — har kuni 15:00 UTC (20:00 Toshkent) da `remind.py` ni ishga tushiradi.
- **`.github/workflows/keepalive.yml`** — har oy workflowlarni qayta yoqadi, chunki GitHub
  60 kun faollik bo'lmasa cron'ni o'chirib qo'yadi.

**Shaxsiy ma'lumotlar kodda yo'q.** Repo ochiq, shuning uchun reja (summalar, sanalar, bayramlar, boshlang'ich
qarzlar) kodda saqlanmaydi: u faqat sizning Telegram bulutingizda (treker) va GitHub'ning yopiq `PLAN_JSON`
secret'ida (bot) turadi. Amallar, kartalar, qarzlar va boshqa barcha ma'lumot — faqat Telegram bulutida.

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

> Repo ochiq, lekin kodda shaxsiy ma'lumot yo'q: reja `PLAN_JSON` secret'ida va Telegram bulutida,
> token va chat_id — faqat Secrets'da. Ochiq repoda Actions loglari ham hammaga ko'rinadi, shuning uchun
> `remind.py` u yerda xabar matnlarini chop etmaydi.
> Treker faqat `CHAT_ID` ga teng Telegram akkauntida ochiladi (pastda «Faqat egasi» ga qarang).

### 4. Secrets qo'shish

Repo → **Settings → Secrets and variables → Actions → New repository secret**.
To'rtta secret qo'shing:

| Nomi | Qiymati |
|---|---|
| `BOT_TOKEN` | BotFather bergan token |
| `CHAT_ID` | 2-qadamda topilgan raqam |
| `WEBAPP_URL` | `https://<USERNAME>.github.io/byudjet-bot/` |
| `PLAN_JSON` | Reja (pastdagi format) — bir qatorga yozish shart emas |

#### Reja formati (`PLAN_JSON`)

Quyidagi misoldagi summalar to'qima — o'zingiznikini yozing. Kompyuterda shu matnni `plan.local.json` ga saqlab
qo'yish qulay (u `.gitignore` da — repoga tushmaydi).

```json
{
  "v": 1,
  "start": "2030-01-07",
  "end": "2030-04-30",
  "startBalance": 500000,
  "transport": { "amount": 8000, "title": "Yo'lkira" },
  "monthly": {
    "10": [
      { "id": "maosh", "kind": "in", "amount": 2000000, "title": "Maosh", "cat": "oylik" },
      { "id": "ijara", "kind": "out", "amount": 700000, "title": "Ijara", "cat": "uy" },
      { "id": "lock", "kind": "lock", "amount": 1000000, "title": "Jamg'armaga" }
    ]
  },
  "once": { "2030-01-20": [{ "id": "qarz", "kind": "in", "amount": 150000, "title": "Qarz qaytishi", "cat": "qarzq", "debt": "qarz" }] },
  "holidays": { "2030-03-08": "Bayram" },
  "debts": [{ "id": "qarz", "dir": "lent", "who": "Do'stim", "a": 150000, "due": "2030-01-20" }]
}
```

- `monthly` — har oyning shu kunidagi bandlar; `once` — faqat shu sanada; `kind`: `in` (kirim), `out` (chiqim),
  `lock` (omonatga qulflash — jami balans o'zgarmaydi).
- `id` — 2–12 ta kichik lotin harfi, hammasi har xil; `yol` band nomi band (yo'lkira uchun). Bot tugmalari va treker
  bandlarni shu `id` orqali taniydi, shuning uchun keyin o'zgartirmang.
- `cat` — trekerdagi kategoriya (`oylik`, `avans`, `kirim`, `qarzq`, `aloqa`, `talim`, `uy`, `boshqa` …).
- `transport.amount` — har ish kuni (Du–Ju, bayramlarsiz) yo'lkira; 0 bo'lsa yo'lkira yo'q.
- `debts` — boshlang'ich qarzlar (`owe` — men qarzdorman, `lent` — menga qarzdor).

### 5. Menu Button (bot ichida "Treker" tugmasi)

1. @BotFather → `/mybots` → botingizni tanlang.
2. **Bot Settings → Menu Button → Configure menu button**.
3. URL sifatida **WEBAPP_URL** ni yuboring, keyin tugma nomini yozing, masalan `Treker`.
4. Endi bot chatida, yozish maydonining chap tomonida "Treker" tugmasi paydo bo'ladi.

### 6. Qo'lda sinov

1. Repo → **Actions** bo'limi. Agar so'ralsa, workflowlarni yoqing (*I understand... enable*).
2. **remind** → **Run workflow**:
   - `slot`: `plan` → **Run workflow**. Botdan «📋 Reja» xabari keladi: matnni bosing (nusxalanadi), trekerni oching
     va «Rejani kiriting» ekranida **Buferdan joylash → Saqlash**. Reja shundan keyin Telegram bulutingizda turadi;
   - eslatmani sinash: `slot`: `evening`, `today` maydoniga reja to'lovidan bir kun oldingi sana (bo'sh — bugun).
3. Telegram'ga "Ertaga, …" xabari va "Trekerni ochish" tugmasi kelishi kerak.
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
| **Asosiy** | Jami balans, 7 kunlik chiziq va hisoblar (Karta, Naqd, Omonat). «Karta» bosilsa — har bank kartasining qoldig'i alohida; Naqd/Omonat bosilsa — qoldiqni tuzatish. Balans ostida ikki ko'rsatkich: **Erkin pul** — rejadagi barcha kelgusi to'lovlardan keyin karta va naqddan hozir sarflash mumkin bo'lgan summa (eng tig'iz kun bilan) va **Rejadan farq** (bosilsa, nimadan yig'ilgani). Tez amallar: Kirim, O'tkazma, HUMO, Yangi qarz. Keyin kartalar: **Yaqin to'lovlar** (o'tib ketgan belgilanmagan bandlar, eng yaqin to'lov kuni; asosiy kartada pul yetmasa — eng ko'p pul turgan karta yoki naqddan o'tkazish tugmasi), **Diqqat** (HUMO bilan farq, qarz muddati, limit, qoida buzilishi, xohishlar), Bugun / Seriya / Salomatlik plitkalari, Xohishlar, Yakuniy maqsad, Qarzlar, Oxirgi amallar. Ko'z tugmasi summalarni yashiradi. Yo'lkira bu yerda eslatilmaydi (pulsiz borilgan kunlar ham bo'ladi) |
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
- **Bot xabaridan bir bosishda** — eslatmada har to'lov uchun tugma bor: «✅ To'ladim: Internet»,
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
- **Rejadan farq** = jami balans − (boshlang'ich balans + bajarilgan reja bandlari).
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
- **O'z to'lovlaringiz**: Asosiy → «Yaqin to'lovlar» → «Qo'shish». Nima uchun, summa, sana (Ertaga / 1 haftadan keyin /
  Oy oxiri / istalgan kun), takrorlanishi (bir marta, har hafta, har oy, har yil) va qaysi karta yoki naqddan. «Pul kelishi
  kerak» — kutilayotgan kirim uchun (masalan, kimdir qarzni qaytaradi). To'lov sanasi yaqinlashganda (7 kun ichida)
  «Yaqin to'lovlar» da reja bandlari bilan birga turadi, Reja kalendarida binafsha nuqta bilan ko'rinadi, «Erkin pul» va
  prognoz uni hisobga oladi. «To'ladim» bosilsa amal tayyor ochiladi; saqlangach takrorlanadigan to'lov keyingi sanaga o'tadi,
  bir martaligi yopiladi. Takrorlanadiganini «Bu safar o'tkazib yuborish» mumkin. Bildirishnoma yuborilmaydi.
- **Bank kartalari**: Sozlamalar → Kartalar → «Karta qo'shish» (nomi, oxirgi 4 raqam, turi: HUMO / Uzcard / VISA /
  Mastercard, rangi). Avval oylik tushadigan **asosiy kartani** qo'shing — hozirgi karta puli va oldingi karta amallari
  shunga yoziladi. Keyingi kartalarni qo'shganda «Hozirgi qoldig'i» ni kiriting: shu summa asosiy kartadan yangi kartaga
  o'tkazma bo'lib yoziladi (jami balans o'zgarmaydi). So'ng:
  - «+» oynasida qaysi kartadan to'laganingizni tanlaysiz; o'tkazmada karta → karta ham mumkin;
  - reja bandi oxirgi marta qaysi kartadan to'langan bo'lsa, keyingi safar o'sha karta tanlanadi (masalan, obuna — VISA kartadan);
  - Asosiy ekranda «Karta» ni bossangiz — har karta qoldig'i; kartani bossangiz — qoldiqni tuzatish, tarixi, o'tkazma;
  - Tarix'da karta bo'yicha filtr, har qator ostida o'sha kartaning qoldig'i;
  - HUMO xabaridagi `*1234` kabi raqam bo'yicha amal to'g'ri kartaga yoziladi va solishtirish har karta bo'yicha qilinadi;
  - qoldig'i 0 bo'lgan kartani arxivlash mumkin (tarixi qoladi).
  Karta nomi va raqami kodda emas, faqat Telegram bulutingizda saqlanadi.
- **Balansni tuzatish**: Asosiy ekranda hisobni bosing va haqiqiy qoldiqni kiriting.
  Farq "Balans tuzatish" amali sifatida yoziladi.
- Oylik va avans Kartaga tushadi. Ularni uch xil yozish mumkin: Reja → «Tushdi», HUMO import yoki «+» → Kirim (qo'lda).
- Ishga bormagan kunni (masalan, Ramazon hayiti) Reja'da "Dam olish" ga o'tkazing.
  O'sha kunning yo'lkirasi rejadan olib tashlanadi.
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
   - naqd pul yechishni Karta → Naqd o'tkazmasi sifatida yozadi;
   - kartalar qo'shilgan bo'lsa, xabardagi karta raqami (`*1234`) bo'yicha amalni o'sha kartaga yozadi.
4. Oxirida trekerdagi karta qoldig'ini HUMO'dagi oxirgi qoldiq bilan solishtiradi.
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
| Har ish kuni, 08:00 | "Bugun ish kuni — faqat yo'lkira, tushlik uydan" |
| To'lov kuni, 08:00 | Bugungi reja: to'lovlar va kirimlar ro'yxati (dam olish kuni bo'lsa ham keladi) |
| Oyning 1-sanasi, 08:00 | Oy rejasi: kirim, majburiy to'lovlar, yo'lkira, omonat, oy oxiridagi reja balansi |
| To'lovdan bir kun oldin, 20:00 | Ertangi to'lov va kirimlar, har biri uchun «To'ladim» / «Tushdi» tugmasi |
| Qulflash kuni, 20:00 | Pul omonatga o'tkazildimi? |
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

# Git Bash / Linux / macOS — reja kompyuterdagi plan.local.json dan
PLAN_FILE=plan.local.json TODAY=2026-11-04 python remind.py --dry-run
PLAN_FILE=plan.local.json TODAY=2026-12-01 python remind.py --dry-run --slot morning   # ertalabki xabar + oy rejasi
```

PowerShell'da:

```powershell
$env:PLAN_FILE = "plan.local.json"; $env:TODAY = "2026-11-04"; python remind.py --dry-run
Remove-Item Env:TODAY
```

`--dry-run` xabarlarni yubormaydi, faqat ekranga chiqaradi va bot secretlarini talab qilmaydi (reja kerak).
GitHub Actions'da esa matnlar chop etilmaydi — ochiq repoda loglar hammaga ko'rinadi.
Testlar to'qima reja bilan ishlaydi (`tests/test_remind.py`).
Mini App'ni sinash uchun `index.html` ni brauzerda ochish kifoya (fayl va localhost'da egasi tekshirilmaydi).
Boshqa sanadagi holatni ko'rish uchun manzil oxiriga `?today=2026-11-13` qo'shing.

## Rejani o'zgartirish

Biror summa yoki sana o'zgarsa (masalan, oylik oshsa), reja matnini **ikki joyda** bir xil yangilang:

1. Trekerda: **Sozlamalar → Reja → Rejani yangilash** (matnni tahrirlab «Saqlash»; «Nusxalash» bilan olib qo'ying);
2. GitHub'da: **Settings → Secrets → `PLAN_JSON`** — o'sha matn (bot shu bo'yicha eslatadi).

Yakuniy reja balansi avtomatik qayta hisoblanadi. Kod o'zgarmaydi.
