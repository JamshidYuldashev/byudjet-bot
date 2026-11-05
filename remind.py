#!/usr/bin/env python3
"""Byudjet rejasi bo'yicha Telegram eslatmalari (faqat Python stdlib).

Muhit o'zgaruvchilari: BOT_TOKEN, CHAT_ID, WEBAPP_URL, PLAN_JSON (reja — GitHub Secret).
Kompyuterda: PLAN_FILE=plan.local.json (git'ga kirmaydi). Reja kodda saqlanmaydi — repo ochiq.
TODAY=YYYY-MM-DD bilan sanani almashtirish mumkin (sinov uchun).
Bot faqat ish bo'lganda yozadi: to'lovsiz kunlarda xabar yo'q.
--slot morning  — 08:00: bugungi to'lovlar, oyning 1-sanasida oy rejasi.
--slot evening  — 20:00: ertangi to'lovlar, yakshanba — keyingi hafta va qoida.
--slot plan     — rejani trekerga joylash uchun botga matn qilib yuboradi.
--dry-run xabarlarni yubormasdan chop etadi (GitHub Actions'da matn chiqarilmaydi — loglar ochiq).

Reja bandi bor xabarlarda har band uchun «To'ladim» tugmasi bo'ladi: u trekerni
WEBAPP_URL?plan=YYYY-MM-DD:id bilan ochadi va shu to'lov tayyor holda chiqadi.
Trekerni ochish tugmasi chatda doim turadi (menyu tugmasi).
"""
import argparse
import html
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import quote
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone

TZ = timezone(timedelta(hours=5))  # Asia/Tashkent


@dataclass(frozen=True)
class Event:
    id: str
    kind: str  # "in" | "out" | "lock"
    amount: int
    title: str


# Moliyaviy reja PLAN_JSON dan yuklanadi (format index.html dagi `cleanPlan` bilan bir xil — CLAUDE.md).
PLAN: dict = {}
EVENT_ID = re.compile(r"^[a-z]{2,12}$")  # trekerdagi ?plan=ISO:id kaliti bilan bir xil


def _int(v, what: str, lo: int = 0) -> int:
    if not isinstance(v, int) or isinstance(v, bool) or v < lo or v > 999_999_999:
        raise ValueError(f"{what}: butun son kerak")
    return v


def _event(o: dict, where: str) -> Event:
    if not isinstance(o, dict):
        raise ValueError(f"{where}: band obyekt emas")
    eid, kind, title = o.get("id"), o.get("kind"), o.get("title")
    if not isinstance(eid, str) or not EVENT_ID.match(eid) or eid == "yol":
        raise ValueError(f"{where}: id 2–12 ta kichik lotin harfi bo'lishi kerak")
    if kind not in ("in", "out", "lock"):
        raise ValueError(f"{where}: kind in/out/lock bo'lishi kerak")
    if not isinstance(title, str) or not title.strip() or len(title) > 40:
        raise ValueError(f"{where}: title kerak (40 belgigacha)")
    return Event(eid, kind, _int(o.get("amount"), f"{where}: amount", 1), title.strip())


def parse_plan(raw: str) -> dict:
    """PLAN_JSON → ichki reja. Xatoda ValueError (matnda summalar chiqmaydi)."""
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON xato ({e.lineno}-qator)") from None
    if not isinstance(data, dict):
        raise ValueError("obyekt kutilgan")
    try:
        start, end = date.fromisoformat(data["start"]), date.fromisoformat(data["end"])
    except (KeyError, TypeError, ValueError):
        raise ValueError("start/end YYYY-MM-DD bo'lishi kerak") from None
    if start > end or (end - start).days > 731:
        raise ValueError("davr noto'g'ri (ko'pi bilan 2 yil)")
    monthly = {}
    for k, items in (data.get("monthly") or {}).items():
        if not str(k).isdigit() or not 1 <= int(k) <= 31 or not isinstance(items, list):
            raise ValueError(f"monthly[{k}] noto'g'ri")
        monthly[int(k)] = [_event(o, f"monthly[{k}]") for o in items]
    once = {}
    for k, items in (data.get("once") or {}).items():
        try:
            d = date.fromisoformat(k)
        except ValueError:
            raise ValueError(f"once[{k}]: sana noto'g'ri") from None
        if not isinstance(items, list):
            raise ValueError(f"once[{k}] noto'g'ri")
        once[d] = [_event(o, f"once[{k}]") for o in items]
    holidays = {}
    for k, name in (data.get("holidays") or {}).items():
        try:
            holidays[date.fromisoformat(k)] = str(name)[:40]
        except ValueError:
            raise ValueError(f"holidays[{k}]: sana noto'g'ri") from None
    transport = data.get("transport") or {}
    return {
        "start": start,
        "end": end,
        "start_balance": _int(data.get("startBalance", 0), "startBalance", -999_999_999),
        "transport": _int(transport.get("amount", 0), "transport.amount"),
        "monthly": monthly,
        "once": once,
        "holidays": holidays,
        "raw": json.dumps(data, ensure_ascii=False, separators=(",", ":")),
    }


def set_plan(plan: dict) -> None:
    PLAN.clear()
    PLAN.update(plan)


@dataclass
class Message:
    text: str
    plan: list[tuple[date, Event]] = field(default_factory=list)  # «To'ladim» tugmalari
    html: bool = True
    button: str = ""  # reja bandi yo'q xabardagi tugma


SIGNS = {"in": "+", "out": "−", "lock": ""}
ACTIONS = {"in": "Tushdi", "out": "To'ladim", "lock": "O'tkazdim"}
# Telegram tugma rangi (Bot API 9.4); eski ilovada oddiy ko'rinadi
STYLES = {"in": "success", "out": "success", "lock": "primary"}
WD_SHORT = ["Du", "Se", "Ch", "Pa", "Ju", "Sh", "Ya"]
MONTHS = ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust",
          "Sentabr", "Oktabr", "Noyabr", "Dekabr"]
BUTTON_TEXT = "Trekerni ochish"
MENU_TEXT = "Treker"
API_URL = "https://api.telegram.org/bot{token}/sendMessage"
MENU_URL = "https://api.telegram.org/bot{token}/setChatMenuButton"


def fmt(n: int) -> str:
    """1234567 -> '1 234 567'."""
    return f"{n:,}".replace(",", " ")


def in_period(d: date) -> bool:
    return PLAN["start"] <= d <= PLAN["end"]


def events_on(d: date) -> list[Event]:
    """Kunning rejalashtirilgan hodisalari (yo'lkirasiz)."""
    if not in_period(d):
        return []
    return PLAN["monthly"].get(d.day, []) + PLAN["once"].get(d, [])


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def amount(e: Event) -> str:
    return f"<b>{SIGNS[e.kind]}{fmt(e.amount)}</b>"


def event_line(e: Event) -> str:
    return f"{amount(e)} {esc(e.title)}"


def day_message(word: str, d: date, events: list[Event]) -> Message:
    """Bitta band: sarlavhada nomi. Bir nechta: sarlavhada soni, pastda ro'yxat."""
    if len(events) == 1:
        e = events[0]
        text = f"<b>{word}: {esc(e.title)}</b>\n{amount(e)} so'm"
    else:
        text = "\n".join([f"<b>{word}: {len(events)} ta band</b>"] + [event_line(e) for e in events])
    return Message(text, [(d, e) for e in events])


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


def month_summary(year: int, month: int) -> Message:
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
    return Message("\n".join([
        f"<b>{MONTHS[month - 1]} rejasi</b>",
        f"<b>+{fmt(ins)}</b> Kirim",
        f"<b>−{fmt(outs)}</b> To'lovlar",
        f"<b>−{fmt(work * PLAN['transport'])}</b> Yo'lkira, {work} kun",
        f"<b>{fmt(locks)}</b> Omonatga",
        "",
        f"Oy oxirida rejada: <b>{fmt(plan_balance(days[-1]))}</b> so'm",
    ]), button="Oyni ochish")


def week_digest(sunday: date) -> Message | None:
    days = [sunday + timedelta(days=i) for i in range(1, 8)]
    days = [d for d in days if in_period(d)]
    if not days:
        return None
    a, b = days[0], days[-1]
    span = f"{a.day}–{b.day}-{MONTHS[b.month - 1].lower()}" if a.month == b.month else f"{a.day}-{MONTHS[a.month - 1].lower()} – {b.day}-{MONTHS[b.month - 1].lower()}"
    lines = [f"<b>Keyingi hafta: {span}</b>"]
    items = [(d, e) for d in days for e in events_on(d)]
    lines += [f"{WD_SHORT[d.weekday()]} {d.day}  {amount(e)}  {esc(e.title)}" for d, e in items]
    if not items:
        lines.append("Rejali to'lov yo'q.")
    work = sum(is_workday(d) for d in days)
    lines += ["", f"Yo'lkira: {work} kun, {fmt(work * PLAN['transport'])} so'm.", "Qoida: ko'chada ovqat, kofe, taksi — 0 so'm."]
    return Message("\n".join(lines), button="Haftani ochish")


def build_morning(today: date) -> list[Message]:
    """08:00: faqat bugungi to'lovlar; oyning 1-sanasida oy rejasi. To'lov yo'q kuni — xabar yo'q."""
    if not in_period(today):
        return []
    messages: list[Message] = []
    events = events_on(today)
    if events:
        messages.append(day_message("Bugun", today, events))
    if today.day == 1:
        messages.append(month_summary(today.year, today.month))
    return messages


def build_messages(today: date) -> list[Message]:
    """20:00: ertangi to'lovlar; yakshanba — keyingi hafta."""
    messages: list[Message] = []
    tomorrow = today + timedelta(days=1)
    events = events_on(tomorrow)
    if events:
        messages.append(day_message("Ertaga", tomorrow, events))
    if today.weekday() == 6:
        digest = week_digest(today)
        if digest:
            messages.append(digest)
    return messages


def build_plan_message() -> Message:
    """Rejani trekerga joylash uchun: matnni bosib nusxalab, trekerda «Buferdan joylash»."""
    return Message(
        "<b>Reja</b>, trekerga joylash uchun.\n"
        "Pastdagi matnni bosing (nusxalanadi), keyin trekerni oching va «Buferdan joylash» → «Saqlash».\n\n"
        f"<code>{html.escape(PLAN['raw'])}</code>",
        html=True,
    )


def plan_url(webapp_url: str, d: date, e: Event) -> str:
    """Trekerni shu reja bandi bilan ochadigan manzil (kalit index.html dagi bilan bir xil: ISO:id)."""
    sep = "&" if "?" in webapp_url else "?"
    return f"{webapp_url}{sep}plan={quote(f'{d.isoformat()}:{e.id}', safe='')}"


def button_text(e: Event, many: bool) -> str:
    if not many:
        return ACTIONS[e.kind]
    if e.kind == "lock":
        return "Omonatga o'tkazdim"
    return f"{e.title} tushdi" if e.kind == "in" else f"{e.title} to'landi"


def keyboard(msg: Message, webapp_url: str) -> dict:
    many = len(msg.plan) > 1
    rows = [[{"text": button_text(e, many), "web_app": {"url": plan_url(webapp_url, d, e)}, "style": STYLES[e.kind]}] for d, e in msg.plan]
    if not rows:
        rows = [[{"text": msg.button or BUTTON_TEXT, "web_app": {"url": webapp_url}, "style": "primary"}]]
    return {"inline_keyboard": rows}


def get_today() -> date:
    raw = os.environ.get("TODAY", "").strip()
    if not raw:
        return datetime.now(TZ).date()
    try:
        return date.fromisoformat(raw)
    except ValueError:
        raise SystemExit(f"Xato: TODAY noto'g'ri formatda: {raw!r} (kerak: YYYY-MM-DD)")


def load_plan() -> str | None:
    """Rejani PLAN_JSON (yoki PLAN_FILE) dan yuklaydi; xato bo'lsa — matnini qaytaradi."""
    raw = os.environ.get("PLAN_JSON", "").strip()
    if not raw and os.environ.get("PLAN_FILE"):
        try:
            raw = Path(os.environ["PLAN_FILE"]).read_text(encoding="utf-8")
        except OSError:
            return "PLAN_FILE o'qilmadi"
    if not raw:
        return "PLAN_JSON topilmadi (GitHub Secret yoki PLAN_FILE=plan.local.json)"
    try:
        set_plan(parse_plan(raw))
    except ValueError as e:
        return f"reja noto'g'ri: {e}"
    return None


def send(token: str, chat_id: str, msg: Message, webapp_url: str) -> None:
    payload = {"chat_id": chat_id, "text": msg.text, "reply_markup": keyboard(msg, webapp_url)}
    if msg.html:
        payload["parse_mode"] = "HTML"
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


def set_menu(token: str, chat_id: str, webapp_url: str) -> None:
    """Trekerni ochish tugmasi chatda doim tursin. Bu ixtiyoriy: xato xabar yuborishga xalaqit bermaydi."""
    payload = {"chat_id": chat_id, "menu_button": {"type": "web_app", "text": MENU_TEXT, "web_app": {"url": webapp_url}}}
    req = urllib.request.Request(
        MENU_URL.format(token=token),
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=30):
            pass
    except (urllib.error.URLError, OSError):
        pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Byudjet eslatmalari")
    parser.add_argument("--dry-run", action="store_true", help="yubormasdan chop etish")
    parser.add_argument("--slot", choices=["evening", "morning", "plan"], default="evening",
                        help="morning — 08:00, evening — 20:00, plan — rejani botga yuborish")
    args = parser.parse_args(argv)
    # Windows konsolida emoji va belgilar chop etilishi uchun.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    err = load_plan()
    if err:
        print(f"Xato: {err}", file=sys.stderr)
        return 2
    today = get_today()
    if args.slot == "plan":
        messages = [build_plan_message()]
    else:
        messages = build_morning(today) if args.slot == "morning" else build_messages(today)

    if args.dry_run:
        url = os.environ.get("WEBAPP_URL") or "<WEBAPP_URL>"
        print(f"[dry-run] Bugun: {today:%d.%m.%Y}, {args.slot}, xabarlar: {len(messages)}")
        # Ochiq repoda Actions loglari hammaga ko'rinadi — u yerda summalar chop etilmaydi.
        if os.environ.get("GITHUB_ACTIONS") == "true":
            print("Matnlar ko'rsatilmaydi: GitHub Actions logi ochiq.")
            return 0
        for msg in messages:
            print("-" * 40)
            print(msg.text)
            for row in keyboard(msg, url)["inline_keyboard"]:
                print(f"[{row[0]['text']}] -> {row[0]['web_app']['url']}")
        return 0

    env = {k: os.environ.get(k, "").strip() for k in ("BOT_TOKEN", "CHAT_ID", "WEBAPP_URL")}
    missing = [k for k, v in env.items() if not v]
    if missing:
        print(f"Xato: muhit o'zgaruvchisi topilmadi: {', '.join(missing)}", file=sys.stderr)
        return 2

    if not messages:
        print(f"{today:%d.%m.%Y}: bugun eslatma yo'q.")
        return 0

    set_menu(env["BOT_TOKEN"], env["CHAT_ID"], env["WEBAPP_URL"])
    for msg in messages:
        try:
            send(env["BOT_TOKEN"], env["CHAT_ID"], msg, env["WEBAPP_URL"])
        except RuntimeError as e:
            print(f"Xato: {e}", file=sys.stderr)
            return 1
    print(f"{today:%d.%m.%Y}: {len(messages)} ta xabar yuborildi.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
