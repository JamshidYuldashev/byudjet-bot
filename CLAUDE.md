# byudjet-bot

Serverless Telegram Mini App (`index.html`, GitHub Pages) + daily reminder bot
(`remind.py`, GitHub Actions cron) for a 5-month personal budget plan.

## Moliyaviy reja — kodda emas

Repo va GitHub Pages ochiq, shuning uchun reja (summalar, sanalar, bayramlar, boshlang'ich qarzlar) hech qachon kodga,
testga, README yoki shu faylga yozilmaydi. U uch joyda turadi:

- trekerda — foydalanuvchining Telegram bulutidagi `plan` hujjatida (`cleanPlan` → `setPlan`; yo'q bo'lsa
  «Rejani kiriting» ekrani, `load()` → `false`);
- botda — `PLAN_JSON` GitHub Secret'ida (`remind.parse_plan`);
- kompyuterda — `plan.local.json` (`.gitignore` da; `PLAN_FILE=plan.local.json` bilan dry-run va brauzer testlari).

Format ikkala tomonda bir xil (`cleanPlan` va `parse_plan` mos bo'lsin): `{ v, start, end, startBalance,
transport: { amount, title }, monthly: { "<kun>": [band] }, once: { "<ISO>": [band] }, holidays: { "<ISO>": nom },
debts: [{ id, dir, who, a, due }] }`, band — `{ id (2–12 kichik lotin harfi, hammasi har xil, «yol» emas),
kind: in|out|lock, amount, title, cat?, acc?, debt? }`. Misol (to'qima summalar) — README'da.

Qoidalar (summasiz): har ish kuni (Du–Ju, bayramlarsiz) yo'lkira; `lock` — omonatga o'tkazish, jami balansni
o'zgartirmaydi; foydalanuvchi istalgan kunni ish kuni / dam olishga almashtira oladi; taqiqlangan xarajatlar
(ko'cha ovqati, kofe, taksi) yozilgan kun — qoida buzilgan kun. Yakuniy reja har doim qoidalardan hisoblanadi.

## Loyiha qoidalari

- Reja kodda emas (yuqoriga qarang). Kodga, testlarga va hujjatlarga haqiqiy summa, karta raqami, ism yozilmaydi;
  testlar to'qima reja bilan ishlaydi. Actions loglari ochiq — `remind.py` CI'da xabar matnini chop etmaydi.
- `remind.py` slotlari: `--slot morning` (08:00 — bugungi to'lovlar, 1-sanada oy rejasi), `--slot evening` (20:00 — ertangi
  to'lovlar, yakshanba — keyingi hafta va qoida), `--slot plan` (reja matnini botga yuboradi — trekerga joylash uchun).
  To'lovsiz kunda xabar yo'q. Xabarlar HTML (`<b>` summa), tugma rangi `style` (Bot API 9.4), menyu tugmasi `setChatMenuButton`.
  Bot CloudStorage'ni o'qiy olmaydi, shuning uchun faqat reja asosida yozadi.
  Reja bandi bor xabarlarda har band uchun tugma: `WEBAPP_URL?plan=YYYY-MM-DD:id` — kalit index.html dagi
  `${iso}:${e.id}` bilan bir xil (Event id lari ikkala faylda bir xil bo'lishi shart). Treker shu bandni ochadi.
- Foydalanuvchiga ko'rinadigan barcha matn (UI, bot xabarlari, README) — o'zbek tilida, lotin yozuvida.
- Secretlar (BOT_TOKEN, CHAT_ID, WEBAPP_URL) faqat GitHub Secrets / env orqali. Kodda hech qachon.
- `index.html`: vanilla HTML/CSS/JS, build yo'q. CDN: faqat telegram.org va jsdelivr
  (`@fontsource-variable/manrope`, aniq versiya bilan). Ikonkalar — inline SVG (Tabler outline yo'llari).
- `remind.py`: faqat Python 3 stdlib.
- Raqam formati: minglar bo'sh joy bilan (1 234 567), faqat butun sonlar.
- Reja sanalari UTC arifmetikasida; "bugun" — qurilmaning mahalliy sanasi.
- Ish beruvchi nomi kodda/README da ko'rsatilmaydi (repo ochiq).

## Mini App ma'lumot modeli (v2)

- Hisoblar: `card` (Karta), `cash` (Naqd), `save` (Omonat — qulflangan). Boshlang'ich qoldiqlar `open` da
  (standart: Karta = rejadagi `startBalance`).
- Bank kartalari: `meta.cards = [{ id: k…, n, l4, ty: humo|uzcard|visa|mc, col, main, off }]` — «Karta» hisobi ichida.
  Nomi va raqami faqat bulutda (kodda emas). Bo'sh bo'lsa — bitta umumiy Karta. Boshlang'ich karta puli (`open.card`)
  birinchi kartada; keyingi karta qo'shilganda qoldig'i asosiy kartadan `tr` (karta → karta) bilan ajratiladi.
  Zaxira eksportiga kiradi.
- Amal: `{ id, d, tm, k: in|out|tr, a, acc, to, c, n, p, h, debt, b, cd, tc }`.
  - `p` — reja bandi kaliti (`2026-11-05:avans`): band bajarilgan deb hisoblanadi.
  - `h` — HUMO xabari izi (takror importdan himoya).
  - `debt` — qarz id si.
  - `cd` — karta (`acc === 'card'`), `tc` — qabul qiluvchi karta (`to === 'card'`). Yo'q yoki noma'lum bo'lsa — asosiy
    karta (`cardOf`). Karta → karta o'tkazmada `cd !== tc`. `addTx` → `fixCards` maydonlarni to'ldiradi.
  - `b` — HUMO xabaridagi 💰 karta qoldig'i (tiyin), shu amaldan keyin. «HUMO bilan solishtirish» (`reconcile`) shu bilan
    trekerdagi o'sha karta qoldig'ini tekshiradi; tuzatish farqli xabardan bir daqiqa oldinga yoziladi. Tiyin tashlanadi.
- Taqiqlangan kategoriyalar (`bad`): `kucha`, `kofe`, `taksi`. Ular yozilgan kun — "qoida buzilgan kun".
- Rejadan farq = jami balans − (startBalance + bajarilgan reja bandlari). Prognoz (`C.prog`) = yakuniy reja + farq +
  o'tib ketgan, yozilmagan yo'lkira (pulsiz borilgan kunlar) + o'zim qo'shgan to'lovlar. Foydalanuvchiga «Reja holati».
  «Sarflasa bo'ladi» (`freeMoney`) = `affordPath` minimumi (karta + naqd). Asosiy blokda: karta + naqd = ajratilgan + erkin.
- O'zim qo'shgan to'lovlar (`due` hujjati): `{ id: u…, n, a, k: out|in, d (keyingi sana), rp: ''|w|m|y, dd (oy kuni), acc, cd,
  st: ''|d, ld, la }`. `dueDates` — `d` dan davr oxirigacha takrorlar; `C.dueByIso` orqali `upcoming`, Reja taqvimi,
  `affordPath`, `forecast` va `C.prog` ga qo'shiladi. «To'ladim» → `openAdd({ due })` → saqlangach `advanceDue`.
  Bildirishnoma yo'q. Zaxira eksportiga kiradi.
- Xohishlar (`wish` hujjati): `{ id: w…, ts, a, c, n, acc, st: w|b|s, rd }` — «24 soat qoidasi». Zaxira eksportiga kiradi.
- Jurnal (`log`): `{ t, k: add|edit|del|debt|plan|set|import|wish, m, r }`, oxirgi 500 ta yozuv. Har bir o'zgarish
  `addTx` / `updateTx` / `removeTx` / `logEv` orqali yoziladi — ma'lumotni to'g'ridan-to'g'ri o'zgartirmang.
- PIN: `meta.pin = { s: salt, h: sha256(salt:pin) }` — ekran qulfi. Zaxira eksportiga kirmaydi.
- `meta.home = { order, off, v: 3 }` — Asosiy ekran bo'limlari tartibi/yashirilganlari (`HOME_CARDS` id lari).
  Boshqa `v` dagi eski tartib bir marta standartga qaytadi.
  `meta.imp = { t, tx, debts, h }` — oxirgi HUMO import, «Bekor qilish» uchun. Ikkalasi zaxira eksportiga kirmaydi.
- Faqat qurilmada (localStorage): mavzu `byudjet:ui:theme`, summalarni yashirish `byudjet:ui:hide`,
  tabriklangan nishonlar `byudjet:ui:badges`, ko'rilgan oy yakunlari `byudjet:ui:wrap`, birinchi ochilish `byudjet:ui:hello`.
- Animatsiyalar `prefers-reduced-motion` ga bo'ysunadi; rAF to'xtasa ham `setTimeout` yakuniy holatni ko'rsatadi.
- «Qoldiq tuzatildi» (`c: 'tuz'`) kirim/chiqim yig'indilariga kirmaydi (Tarix, Tahlil), lekin qoldiqqa kiradi.
- Biometrik ochish (BiometricManager, 7.2+): tasodifiy token qurilmaning xavfsiz xotirasida, bulutda faqat
  `meta.bio = { [deviceId]: sha256(token) }`. PIN bo'lmasa `bio` bo'sh. Zaxira eksportiga kirmaydi.
- Saqlash: hujjatlar `plan`, `meta`, `debts`, `log`, `wish`, `due`, `t_YYYY-MM`. PIN unutilsa — hammasi o'chadi, `plan` qoladi. Ular 3 500 belgilik bo'laklarga bo'linadi
  (`<doc>_<n>`, birinchi bo'lak `soni|` bilan boshlanadi). v1 shardlari (`m_YYYY-MM`) bir marta ko'chiriladi.
- Yozuv yo'qolmasligi: `flush` hujjatni avval navbatga (`pending`, `byudjet:queue` + DeviceStorage `byudjet_queue`, 9.0+), keyin bulutga
  yozadi (`sendPending`). Xato bo'lsa — `#netbar` banneri, 5/15/30/60 soniyada qayta urinish, `load` navbatdagini bulutdagidan yangi deb oladi.
  `saveUI.st`: `ok` | `offline` | `fail`.
- HUMO import faqat nusxalab joylangan matnni qurilmada tahlil qiladi — tarmoqqa hech narsa yuborilmaydi.
- Egasi tekshiruvi: `OWNER_HASH` = PBKDF2-SHA256(CHAT_ID, tuz `byudjet-bot`, 300 000 marta) — ID ni tanlab topish
  qimmat. Qurilmada tasdiqlangani `byudjet:ui:owner` da eslab qolinadi (id:hash). Uni `.github/workflows/pages.yml` deploy paytida
  `__OWNER_HASH__` o'rniga joylaydi (bu satr `index.html` da aynan bir marta bo'lishi shart). Pages manbasi — GitHub Actions.
  Begona akkaunt yoki Telegram'siz brauzerda `load()` chaqirilmaydi, faqat «Bu shaxsiy ilova» chiqadi.
  `file:` va localhost — tekshiruvsiz (testlar uchun).

## Tuzilma (UI)

- Suzuvchi menyu: `main` · `tarix` · `reja` · `tahlil` (`TABS`, `#nav`, skrollda kichrayadi). «+» — bo'lim emas, amal: alohida `#fab`, `add` oynasini ochadi.
  Boshqa sahifalar `push()` bilan ustiga ochiladi: `add`, `hisob`, `hello`, `humo`, `jurnal`, `sozlama`, `sz-plan`, `sz-home`, `sz-lim`, `sz-open`, `sz-backup` (`VIEWS`).
  Ichki sahifada menyu yo'q, kerak bo'lsa suzuvchi asboblar paneli `.tbar`. Telegram BackButton — `stack` bo'yicha.
- Asosiy: `heroHTML` («Sarflasa bo'ladi»), `.accs` → `hisob`, `bentoHTML` (Reja, Qarzlar), `HOME_CARDS` (wrap, notes, pay, today). Reja tugagach — `viewPlanDone`.
- `upcoming(C)` — reja bandlari, o'zim qo'shganlar va muddatli qarzlar bitta ro'yxatda. `payRow`: «To'ladim» faqat bugun, ertaga va kechikkanda.
- Reja: `reja.tab` `tolov` | `cal` | `qarz` | `wish`. Tahlil: `rep.tab` `xulosa` | `xarajat` | `prognoz`.
- «+» (`viewAdd`): `form.k` `out` | `in` | `tr` | `debt`. Hisob `pickHTML`, sana `dateHTML` oynasida. Raqamlar paneli `#f-pad` `position: fixed` — telefonda matn yozilayotganda (`body.typing`) yashiriladi.
  Telegram'da «Saqlash» — `WA.MainButton` (`syncMainButton`, faqat `#RRGGBB`), Telegram'dan tashqarida `#f-save`. `saveState(form)` ikkalasiga yozuv beradi.
- Oynalar: `openModal` (`.grab` + `.sheet-b`), fokus ichida aylanadi, pastga surib yopiladi. O'chirish: oqibatini ko'rsatadi, keyin 10 soniya «Qaytarish».

## Dizayn qoidalari

- WCAG 2.2 AA: matn 4,5:1, chegara va holat 3:1, nishon kamida 44 px (`.act`, `.chip` — 40 px + `::after`), shrift `rem`, ma'no faqat rangda emas (`.mk` belgilari shakl bilan).
- Rang: bitta asosiy `--accent`; `--amber` va `--coral` faqat muammoda. `.msg` foni aniq token (`--amber-t` …), shaffof qatlam emas.
- Telegram mavzusi: `applyTgColors` `themeParams` ni oladi, kontrasti 4,5:1 dan past bo'lsa o'z ranglarimiz qoladi.
- Shisha effekti faqat navigatsiyada (`#nav`, `.tbar`), summalarga tegmaydi; `prefers-reduced-transparency` va zaif Android (`.low-end`) da o'chadi. Harakat `prefers-reduced-motion` ga bo'ysunadi.
- Atamalar: «Sarflasa bo'ladi», «Reja holati», «To'ladim / Tushdi / O'tkazdim», «Intizom bahosi», «Qoldiq tuzatildi». Ilovada va botda bir xil.

## Tekshirish

```sh
python -m unittest
PLAN_FILE=plan.local.json TODAY=2026-11-04 python remind.py --dry-run
PLAN_FILE=plan.local.json TODAY=2026-12-01 python remind.py --dry-run --slot morning
```

Mini App'ni boshqa sana bilan ochish: `index.html?today=2026-11-13` (rejani `byudjet:plan_0` ga `1|<json>` qilib qo'ying).
Brauzer testlarida qiymatlarni o'qishdan oldin animatsiya tugashini kuting yoki Chrome'ni
`--force-prefers-reduced-motion` bilan ishga tushiring.
