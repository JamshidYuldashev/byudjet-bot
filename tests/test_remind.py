import io
import json
import os
import unittest
import urllib.error
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from unittest import mock

import remind

# Testlar uchun to'qima reja — haqiqiy reja faqat PLAN_JSON secret va plan.local.json da (repoda emas).
TEST_PLAN = {
    "v": 1,
    "start": "2030-01-07",
    "end": "2030-04-30",
    "startBalance": 500000,
    "transport": {"amount": 8000, "title": "Yo'lkira"},
    "monthly": {
        "10": [
            {"id": "maosh", "kind": "in", "amount": 2000000, "title": "Maosh", "cat": "oylik"},
            {"id": "ijara", "kind": "out", "amount": 700000, "title": "Ijara", "cat": "uy"},
            {"id": "lock", "kind": "lock", "amount": 1000000, "title": "Jamg'armaga"},
        ],
        "15": [{"id": "internet", "kind": "out", "amount": 90000, "title": "Internet", "cat": "aloqa"}],
    },
    "once": {"2030-01-20": [{"id": "qarz", "kind": "in", "amount": 150000, "title": "Qarz qaytishi", "cat": "qarzq", "debt": "qarz"}]},
    "holidays": {"2030-03-08": "Bayram"},
    "debts": [{"id": "qarz", "dir": "lent", "who": "Do'stim", "a": 150000, "due": "2030-01-20"}],
}
PLAN_JSON = json.dumps(TEST_PLAN, ensure_ascii=False)
ENV = {"BOT_TOKEN": "123:abc", "CHAT_ID": "42", "WEBAPP_URL": "https://example.github.io/byudjet-bot/", "PLAN_JSON": PLAN_JSON}


def setUpModule() -> None:
    remind.set_plan(remind.parse_plan(PLAN_JSON))


def messages(iso: str) -> list[str]:
    return [m.text for m in remind.build_messages(date.fromisoformat(iso))]


def morning(iso: str) -> list[str]:
    return [m.text for m in remind.build_morning(date.fromisoformat(iso))]


def plan_keys(msg: remind.Message) -> list[str]:
    return [f"{d.isoformat()}:{e.id}" for d, e in msg.plan]


class ParsePlanTest(unittest.TestCase):
    def test_parsed(self) -> None:
        p = remind.parse_plan(PLAN_JSON)
        self.assertEqual((p["start"], p["end"], p["start_balance"], p["transport"]), (date(2030, 1, 7), date(2030, 4, 30), 500000, 8000))
        self.assertEqual([e.id for e in p["monthly"][10]], ["maosh", "ijara", "lock"])
        self.assertEqual(p["holidays"], {date(2030, 3, 8): "Bayram"})

    def test_invalid_plans_rejected_without_amounts(self) -> None:
        bad = [
            "{",
            json.dumps({**TEST_PLAN, "start": "2030-13-01"}),
            json.dumps({**TEST_PLAN, "end": "2029-01-01"}),
            json.dumps({**TEST_PLAN, "monthly": {"40": []}}),
            json.dumps({**TEST_PLAN, "monthly": {"10": [{"id": "Maosh1", "kind": "in", "amount": 1, "title": "x"}]}}),
            json.dumps({**TEST_PLAN, "monthly": {"10": [{"id": "yol", "kind": "out", "amount": 1, "title": "x"}]}}),
            json.dumps({**TEST_PLAN, "monthly": {"10": [{"id": "maosh", "kind": "in", "amount": 1.5, "title": "x"}]}}),
        ]
        for raw in bad:
            with self.subTest(raw=raw[:40]), self.assertRaises(ValueError) as ctx:
                remind.parse_plan(raw)
            self.assertNotIn("2000000", str(ctx.exception))


class BuildMessagesTest(unittest.TestCase):
    def test_payday_tomorrow(self) -> None:
        msgs = messages("2030-02-09")
        self.assertEqual(len(msgs), 1)
        text = msgs[0]
        self.assertTrue(text.startswith("<b>Ertaga: 3 ta band</b>"))
        self.assertIn("<b>+2 000 000</b> Maosh", text)
        self.assertIn("<b>−700 000</b> Ijara", text)
        self.assertIn("<b>1 000 000</b> Jamg'armaga", text)
        self.assertNotIn("0 so'm", text)  # qoida har kuni takrorlanmaydi

    def test_single_event_in_title(self) -> None:
        msgs = messages("2030-01-19")
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0], "<b>Ertaga: Qarz qaytishi</b>\n<b>+150 000</b> so'm")

    def test_lock_day_evening_has_no_nag(self) -> None:
        msgs = messages("2030-02-10")  # yakshanba: faqat keyingi hafta
        self.assertEqual(len(msgs), 1)
        self.assertTrue(msgs[0].startswith("<b>Keyingi hafta: 11–17-fevral</b>"))

    def test_sunday_week_digest(self) -> None:
        msgs = messages("2030-01-13")
        self.assertEqual(len(msgs), 1)
        text = msgs[0]
        self.assertTrue(text.startswith("<b>Keyingi hafta: 14–20-yanvar</b>"))
        self.assertIn("Se 15  <b>−90 000</b>  Internet", text)
        self.assertIn("Ya 20  <b>+150 000</b>  Qarz qaytishi", text)
        self.assertIn("Yo'lkira: 5 kun, 40 000 so'm.", text)
        self.assertIn("Qoida: ko'chada ovqat, kofe, taksi — 0 so'm.", text)

    def test_digest_across_months(self) -> None:
        self.assertTrue(messages("2030-01-27")[0].startswith("<b>Keyingi hafta: 28-yanvar – 3-fevral</b>"))

    def test_quiet_days(self) -> None:
        self.assertEqual(messages("2030-01-08"), [])
        self.assertEqual(messages("2030-01-05"), [])  # davrdan oldin
        self.assertEqual(messages("2030-05-01"), [])  # davrdan keyin

    def test_title_escaped(self) -> None:
        self.assertEqual(remind.event_line(remind.Event("ab", "out", 5, "A<b>&")), "<b>−5</b> A&lt;b&gt;&amp;")


class ButtonsTest(unittest.TestCase):
    def test_evening_buttons_for_tomorrow(self) -> None:
        msg = remind.build_messages(date(2030, 2, 9))[0]
        self.assertEqual(plan_keys(msg), ["2030-02-10:maosh", "2030-02-10:ijara", "2030-02-10:lock"])

    def test_digest_and_summary_open_button(self) -> None:
        digest = remind.build_messages(date(2030, 1, 13))[0]
        self.assertEqual(digest.plan, [])
        self.assertEqual(remind.keyboard(digest, "https://x/")["inline_keyboard"][0][0]["text"], "Haftani ochish")
        month = remind.build_morning(date(2030, 2, 1))[-1]
        self.assertEqual(remind.keyboard(month, "https://x/")["inline_keyboard"][0][0]["text"], "Oyni ochish")

    def test_keyboard_many(self) -> None:
        msg = remind.build_messages(date(2030, 2, 9))[0]
        rows = remind.keyboard(msg, "https://x.github.io/b/")["inline_keyboard"]
        self.assertEqual(len(rows), 3)  # band tugmalari bor xabarda «Trekerni ochish» takrorlanmaydi
        self.assertEqual(rows[0][0], {"text": "Maosh tushdi", "web_app": {"url": "https://x.github.io/b/?plan=2030-02-10%3Amaosh"}, "style": "success"})
        self.assertEqual(rows[1][0]["text"], "Ijara to'landi")
        self.assertEqual(rows[2][0]["text"], "Omonatga o'tkazdim")
        self.assertEqual(rows[2][0]["style"], "primary")

    def test_keyboard_single(self) -> None:
        msg = remind.build_messages(date(2030, 1, 19))[0]
        self.assertEqual(remind.keyboard(msg, "https://x/")["inline_keyboard"][0][0]["text"], "Tushdi")

    def test_plan_message_html_escaped(self) -> None:
        msg = remind.build_plan_message()
        self.assertTrue(msg.html)
        self.assertIn("<code>{&quot;v&quot;:1,", msg.text)
        self.assertIn("Jamg&#x27;armaga", msg.text)


class MorningTest(unittest.TestCase):
    def test_plain_workday_silent(self) -> None:
        self.assertEqual(morning("2030-01-08"), [])

    def test_payment_day(self) -> None:
        msgs = morning("2030-02-10")
        self.assertEqual(len(msgs), 1)
        self.assertTrue(msgs[0].startswith("<b>Bugun: 3 ta band</b>"))
        self.assertIn("<b>+2 000 000</b> Maosh", msgs[0])
        self.assertEqual(plan_keys(remind.build_morning(date(2030, 2, 10))[0]), ["2030-02-10:maosh", "2030-02-10:ijara", "2030-02-10:lock"])

    def test_plain_weekend_and_holiday_silent(self) -> None:
        self.assertEqual(morning("2030-01-12"), [])
        self.assertEqual(morning("2030-03-08"), [])

    def test_outside_period_silent(self) -> None:
        self.assertEqual(morning("2030-01-06"), [])
        self.assertEqual(morning("2030-05-01"), [])

    def test_month_start_summary(self) -> None:
        msgs = morning("2030-02-01")
        text = msgs[-1]
        self.assertTrue(text.startswith("<b>Fevral rejasi</b>"))
        self.assertIn("<b>+2 000 000</b> Kirim", text)
        self.assertIn("<b>−790 000</b> To'lovlar", text)
        self.assertIn("<b>−160 000</b> Yo'lkira, 20 kun", text)
        self.assertIn("<b>1 000 000</b> Omonatga", text)
        self.assertIn("Oy oxirida rejada:", text)

    def test_plan_final_balance(self) -> None:
        # 500 000 + 4 × (2 000 000 − 700 000 − 90 000) + 150 000 − 81 ish kuni × 8 000
        self.assertEqual(remind.plan_balance(date(2030, 4, 30)), 4_842_000)
        self.assertEqual(remind.plan_balance(date(2030, 1, 7)), 492_000)


class MainTest(unittest.TestCase):
    def run_main(self, env: dict[str, str], argv: list[str] | None = None) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), redirect_stdout(out), redirect_stderr(err):
            code = remind.main(argv or [])
        return code, out.getvalue(), err.getvalue()

    def tearDown(self) -> None:
        remind.set_plan(remind.parse_plan(PLAN_JSON))

    def test_missing_plan_exits_nonzero(self) -> None:
        code, _, err = self.run_main({"TODAY": "2030-02-09", "BOT_TOKEN": "x"}, ["--dry-run"])
        self.assertEqual(code, 2)
        self.assertIn("PLAN_JSON", err)

    def test_bad_plan_does_not_leak_amounts(self) -> None:
        raw = json.dumps({**TEST_PLAN, "end": "2029-01-01"})
        code, out, err = self.run_main({"TODAY": "2030-02-09", "PLAN_JSON": raw}, ["--dry-run"])
        self.assertEqual(code, 2)
        self.assertIn("reja noto'g'ri", err)
        self.assertNotIn("2000000", out + err)

    def test_missing_env_exits_nonzero(self) -> None:
        code, _, err = self.run_main({"TODAY": "2030-02-09", "BOT_TOKEN": "x", "PLAN_JSON": PLAN_JSON})
        self.assertNotEqual(code, 0)
        self.assertIn("CHAT_ID", err)
        self.assertIn("WEBAPP_URL", err)

    def test_sends_with_web_app_button(self) -> None:
        resp = mock.MagicMock()
        resp.__enter__.return_value = io.BytesIO(b'{"ok": true}')
        with mock.patch("urllib.request.urlopen", return_value=resp) as urlopen:
            code, _, _ = self.run_main({**ENV, "TODAY": "2030-02-09"})
        self.assertEqual(code, 0)
        payload = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(payload["chat_id"], "42")
        self.assertEqual(payload["parse_mode"], "HTML")
        rows = payload["reply_markup"]["inline_keyboard"]
        self.assertEqual(rows[0][0]["web_app"]["url"], ENV["WEBAPP_URL"] + "?plan=2030-02-10%3Amaosh")
        # Oldin menyu tugmasi o'rnatiladi, keyin xabar yuboriladi
        first = urlopen.call_args_list[0].args[0]
        self.assertTrue(first.full_url.endswith("/setChatMenuButton"))
        self.assertEqual(json.loads(first.data)["menu_button"]["web_app"]["url"], ENV["WEBAPP_URL"])

    def test_version_in_urls(self) -> None:
        resp = mock.MagicMock()
        resp.__enter__.return_value = io.BytesIO(b'{"ok": true}')
        with mock.patch("urllib.request.urlopen", return_value=resp) as urlopen:
            code, _, _ = self.run_main({**ENV, "TODAY": "2030-02-09", "GITHUB_SHA": "abc1234def"})
        self.assertEqual(code, 0)
        first = json.loads(urlopen.call_args_list[0].args[0].data)
        self.assertEqual(first["menu_button"]["web_app"]["url"], ENV["WEBAPP_URL"] + "?v=abc1234")
        rows = json.loads(urlopen.call_args.args[0].data)["reply_markup"]["inline_keyboard"]
        self.assertEqual(rows[0][0]["web_app"]["url"], ENV["WEBAPP_URL"] + "?v=abc1234&plan=2030-02-10%3Amaosh")

    def test_menu_error_does_not_stop_messages(self) -> None:
        resp = mock.MagicMock()
        resp.__enter__.return_value = io.BytesIO(b'{"ok": true}')
        calls = iter([urllib.error.URLError("x"), resp])
        def fake(*a, **k):
            r = next(calls)
            if isinstance(r, Exception):
                raise r
            return r
        with mock.patch("urllib.request.urlopen", side_effect=fake):
            code, _, _ = self.run_main({**ENV, "TODAY": "2030-02-09"})
        self.assertEqual(code, 0)

    def test_plan_slot_sends_html(self) -> None:
        resp = mock.MagicMock()
        resp.__enter__.return_value = io.BytesIO(b'{"ok": true}')
        with mock.patch("urllib.request.urlopen", return_value=resp) as urlopen:
            code, out, _ = self.run_main({**ENV, "TODAY": "2030-02-09"}, ["--slot", "plan"])
        self.assertEqual(code, 0)
        payload = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(payload["parse_mode"], "HTML")
        self.assertIn("<code>", payload["text"])
        self.assertNotIn("2000000", out)

    def test_api_error_exits_nonzero_without_leaking_token(self) -> None:
        resp = mock.MagicMock()
        resp.__enter__.return_value = io.BytesIO(b'{"ok": false, "description": "chat not found"}')
        with mock.patch("urllib.request.urlopen", return_value=resp):
            code, _, err = self.run_main({**ENV, "TODAY": "2030-02-09"})
        self.assertEqual(code, 1)
        self.assertIn("chat not found", err)
        self.assertNotIn(ENV["BOT_TOKEN"], err)

    def test_dry_run_needs_no_secrets(self) -> None:
        code, out, _ = self.run_main({"TODAY": "2030-01-19", "PLAN_JSON": PLAN_JSON}, ["--dry-run"])
        self.assertEqual(code, 0)
        self.assertIn("Qarz qaytishi", out)

    def test_dry_run_in_actions_hides_texts(self) -> None:
        code, out, _ = self.run_main({"TODAY": "2030-01-19", "PLAN_JSON": PLAN_JSON, "GITHUB_ACTIONS": "true"}, ["--dry-run"])
        self.assertEqual(code, 0)
        self.assertIn("xabarlar: 1", out)
        self.assertNotIn("150 000", out)

    def test_plan_file(self) -> None:
        path = os.path.join(os.path.dirname(__file__), "_plan_test.json")
        with open(path, "w", encoding="utf-8") as f:
            f.write(PLAN_JSON)
        try:
            code, out, _ = self.run_main({"TODAY": "2030-02-01", "PLAN_FILE": path}, ["--dry-run", "--slot", "morning"])
        finally:
            os.remove(path)
        self.assertEqual(code, 0)
        self.assertIn("morning, xabarlar: 1", out)
        self.assertIn("Fevral rejasi", out)


if __name__ == "__main__":
    unittest.main()
