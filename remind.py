#!/usr/bin/env python3
"""Byudjet rejasi bo'yicha Telegram eslatmalari (faqat Python stdlib).

Muhit o'zgaruvchilari: BOT_TOKEN, CHAT_ID, WEBAPP_URL.
TODAY=YYYY-MM-DD bilan sanani almashtirish mumkin (sinov uchun).
--slot morning  — 08:00: bugungi kun (ish kuni / to'lovlar), oyning 1-sanasida oy rejasi.
--slot evening  — 20:00: ertangi to'lovlar, 20-sanada qulflash, yakshanba — keyingi hafta.
--dry-run xabarlarni yubormasdan chop etadi.
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone

TZ = timezone(timedelta(hours=5))  # Asia/Tashkent


@dataclass(frozen=True)
class Event:
    id: str
    kind: str  # "in" | "out" | "lock"
    amount: int
    title: str


LOCK = 2_500_000  # har 20-sanada omonatga

# Moliyaviy reja — index.html dagi PLAN bilan bir xil bo'lishi shart (CLAUDE.md ga qarang).
PLAN = {
    "start": date(2026, 10, 27),
    "end": date(2027, 3, 20),
    "monthly": {
        5: [
            Event("avans", "in", 523_691, "Oylik avans"),
            Event("ingliz", "out", 600_000, "Ingliz tili kursi"),
        ],
        14: [
            Event("claude", "out", 410_000, "Claude obunasi"),
        ],
        20: [
            Event("oylik", "in", 3_325_200, "Asosiy oylik"),
            Event("telefon", "out", 52_000, "Telefon"),
            Event("lock", "lock", LOCK, "Omonatga qulflash"),
        ],
    },
    "once": {
        date(2026, 11, 5): [
            Event("qarz", "in", 300_000, "Qarz qaytishi"),
        ],
        date(2026, 11, 14): [
            Event("uzum", "out", 430_000, "Uzum qarzini yopish"),
        ],
    },
    "start_balance": 1_000_000,
    "transport": 10_000,  # har ish kuni: 5 000 borish + 5 000 kelish
    "holidays": {
        date(2026, 12, 8): "Konstitutsiya kuni",
        date(2027, 1, 1): "Yangi yil",
        date(2027, 3, 8): "Xotin-qizlar kuni",
    },
}

SIGNS = {"in": "+", "out": "−", "lock": "→ "}
WEEKDAYS = ["Dushanba", "Seshanba", "Chorshanba", "Payshanba", "Juma", "Shanba", "Yakshanba"]
WD_SHORT = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"]
MONTHS = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust",
          "Sentabr", "Oktabr", "Noyabr", "Dekabr"]
BUTTON_TEXT = "Trekerni ochish"
API_URL = "https://api.telegram.org/bot{token}/sendMessage"


def fmt(n: int) -> str:
    """3325200 -> '3 325 200'."""
    return f"{n:,}".replace(",", " ")


def in_period(d: date) -> bool:
    return PLAN["start"] <= d <= PLAN["end"]


def events_on(d: date) -> list[Event]:
    """Kunning rejalashtirilgan hodisalari (yo'lkirasiz)."""
    if not in_period(d):
        return []
    return PLAN["monthly"].get(d.day, []) + PLAN["once"].get(d, [])


def event_line(e: Event) -> str:
    return f"• {SIGNS[e.kind]}{fmt(e.amount)} — {e.title}"


def is_workday(d: date) -> bool:
    """Standart ish kuni (Du–Ju, bayramlarsiz). Trekerdagi qo'lda o'zgartirishlarni bot bilmaydi."""
    return d.weekday() < 5 and d not in PLAN["holidays"]


def delta(e: Event) -> int:
    return e.amount if e.kind == "in" else -e.amount if e.kind == "out" else 0


def plan_balance(d: date) -> int:
    """Reja bo'yicha d kuni oxiridagi jami balans (qulflash jami balansni o'zgartirmaydi)."""
    bal = PLAN["start_balance"]
    day = PLAN["start"]
    while day <= min(d, PLAN["end"]):
        bal += sum(delta(e) for e in events_on(day))
        if is_workday(day):
            bal -= PLAN["transport"]
        day += timedelta(days=1)
    return bal


def month_summary(year: int, month: int) -> str:
    day = date(year, month, 1)
    days = []
    while day.month == month:
        if in_period(day):
            days.append(day)
        day += timedelta(days=1)
    ins = outs = locks = 0
    for d in days:
        for e in events_on(d):
            if e.kind == "in":
                ins += e.amount
            elif e.kind == "out":
                outs += e.amount
            else:
                locks += e.amount
    work = sum(is_workday(d) for d in days)
    return "\n".join([
        f"📅 {MONTHS[month - 1]} rejasi:",
        f"• Kirim: +{fmt(ins)}",
        f"• Majburiy to'lovlar: −{fmt(outs)}",
        f"• Yo'lkira: {work} ish kuni — −{fmt(work * PLAN['transport'])}",
        f"• Omonatga: → {fmt(locks)}",
        "",
        f"{days[-1]:%d.%m} holatiga reja bo'yicha balans: {fmt(plan_balance(days[-1]))} so'm.",
    ])


def week_digest(sunday: date) -> str | None:
    days = [sunday + timedelta(days=i) for i in range(1, 8)]
    days = [d for d in days if in_period(d)]
    if not days:
        return None
    lines = [f"🗓 Keyingi hafta, {days[0]:%d.%m}–{days[-1]:%d.%m}:"]
    items = [(d, e) for d in days for e in events_on(d)]
    lines += [f"• {d:%d.%m} ({WD_SHORT[d.weekday()]}): {SIGNS[e.kind]}{fmt(e.amount)} — {e.title}" for d, e in items]
    if not items:
        lines.append("• Rejali to'lov yo'q")
    work = sum(is_workday(d) for d in days)
    lines += ["", f"Yo'lkira: {work} ish kuni × {fmt(PLAN['transport'])} = {fmt(work * PLAN['transport'])} so'm."]
    return "\n".join(lines)


def build_morning(today: date) -> list[str]:
    """08:00 xabarlari: ish kuni eslatmasi va bugungi reja; 1-sanada oy rejasi."""
    if not in_period(today):
        return []
    messages: list[str] = []
    events = events_on(today)
    work = is_workday(today)
    if work or events:
        head = f"☀️ Bugun, {today:%d.%m} ({WEEKDAYS[today.weekday()]})"
        if work:
            lines = [
                f"{head} — ish kuni.",
                f"Faqat {fmt(PLAN['transport'])} so'm yo'lkira (5 000 + 5 000), tushlik uydan. "
                "Ko'chada ovqat, kofe, shirinlik, taksi — 0 so'm.",
            ]
        else:
            holiday = PLAN["holidays"].get(today)
            lines = [f"{head} — dam olish kuni{f' ({holiday})' if holiday else ''}."]
        if events:
            lines += ["", "📌 Bugungi reja:"] + [event_line(e) for e in events]
            lines.append("Bajarilgach, trekerda belgilang: Reja → «To'lash» / «Tushdi» / «Qulflash».")
        messages.append("\n".join(lines))
    if today.day == 1:
        messages.append(month_summary(today.year, today.month))
    return messages


def build_messages(today: date) -> list[str]:
    messages: list[str] = []
    tomorrow = today + timedelta(days=1)
    events = events_on(tomorrow)
    if events:
        lines = [f"⏰ Ertaga, {tomorrow:%d.%m}:"]
        lines += [event_line(e) for e in events]
        lines += [
            "",
            "Bu pul ertangi reja uchun ajratilgan — unga tegmang. "
            "Ko'chada ovqat, kofe, shirinlik, taksi — 0 so'm.",
        ]
        messages.append("\n".join(lines))
    if today.day == 20 and in_period(today):
        messages.append(
            f"🔒 Bugun 20-sana. {fmt(LOCK)} so'm omonatga "
            "(yoki valyutaga) o'tkazildimi?\n\n"
            "Hali bo'lmasa — hoziroq o'tkazing va trekerda belgilang. "
            "Qulflangan pulga umuman tegilmaydi."
        )
    if today.weekday() == 6:
        digest = week_digest(today)
        if digest:
            messages.append(digest)
    return messages


def get_today() -> date:
    raw = os.environ.get("TODAY", "").strip()
    if not raw:
        return datetime.now(TZ).date()
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise SystemExit(f"Xato: TODAY noto'g'ri formatda: {raw!r} (kerak: YYYY-MM-DD)")


def send(token: str, chat_id: str, text: str, webapp_url: str) -> None:
    payload = {
        "chat_id": chat_id,
        "text": text,
        "reply_markup": {
            "inline_keyboard": [[{"text": BUTTON_TEXT, "web_app": {"url": webapp_url}}]]
        },
    }
    req = urllib.request.Request(
        API_URL.format(token=token),
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    # Xato matnlarida URL (token bilan) chiqmasligi uchun faqat kod/sabab ko'rsatiladi.
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.load(resp)
    except urllib.error.HTTPError as e:
        try:
            desc = json.load(e).get("description", "")
        except ValueError:
            desc = ""
        raise RuntimeError(f"Telegram API HTTP {e.code}: {desc or e.reason}") from None
    except urllib.error.URLError as e:
        raise RuntimeError(f"Telegram API ga ulanib bo'lmadi: {e.reason}") from None
    if not body.get("ok"):
        raise RuntimeError(f"Telegram API xatosi: {body.get('description', body)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Byudjet eslatmalari")
    parser.add_argument("--dry-run", action="store_true", help="yubormasdan chop etish")
    parser.add_argument("--slot", choices=["evening", "morning"], default="evening",
                        help="morning — 08:00 xabarlari, evening — 20:00 xabarlari")
    args = parser.parse_args(argv)
    # Windows konsolida emoji va belgilar chop etilishi uchun.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    today = get_today()
    messages = build_morning(today) if args.slot == "morning" else build_messages(today)

    if args.dry_run:
        url = os.environ.get("WEBAPP_URL") or "<WEBAPP_URL>"
        print(f"[dry-run] Bugun: {today:%d.%m.%Y}, {args.slot}, xabarlar: {len(messages)}")
        for text in messages:
            print("-" * 40)
            print(text)
            print(f"[{BUTTON_TEXT}] -> {url}")
        return 0

    env = {k: os.environ.get(k, "").strip() for k in ("BOT_TOKEN", "CHAT_ID", "WEBAPP_URL")}
    missing = [k for k, v in env.items() if not v]
    if missing:
        print(f"Xato: muhit o'zgaruvchisi topilmadi: {', '.join(missing)}", file=sys.stderr)
        return 2

    if not messages:
        print(f"{today:%d.%m.%Y}: bugun eslatma yo'q.")
        return 0

    for text in messages:
        try:
            send(env["BOT_TOKEN"], env["CHAT_ID"], text, env["WEBAPP_URL"])
        except RuntimeError as e:
            print(f"Xato: {e}", file=sys.stderr)
            return 1
    print(f"{today:%d.%m.%Y}: {len(messages)} ta xabar yuborildi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
