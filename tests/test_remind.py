import io
import json
import os
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import date
from unittest import mock

import remind

ENV = {"BOT_TOKEN": "123:abc", "CHAT_ID": "42", "WEBAPP_URL": "https://example.github.io/byudjet-bot/"}


def messages(iso: str) -> list[str]:
    return remind.build_messages(date.fromisoformat(iso))


class BuildMessagesTest(unittest.TestCase):
    def test_nov_4_qarz_avans_ingliz(self) -> None:
        msgs = messages("2026-11-04")
        self.assertEqual(len(msgs), 1)
        text = msgs[0]
        self.assertTrue(text.startswith("⏰ Ertaga, 05.11:"))
        self.assertIn("+300 000 — Qarz qaytishi", text)
        self.assertIn("+523 691 — Oylik avans", text)
        self.assertIn("−600 000 — Ingliz tili kursi", text)

    def test_nov_13_claude_and_uzum(self) -> None:
        msgs = messages("2026-11-13")
        self.assertEqual(len(msgs), 1)
        self.assertIn("Ertaga, 14.11:", msgs[0])
        self.assertIn("−410 000 — Claude obunasi", msgs[0])
        self.assertIn("−430 000 — Uzum qarzini yopish", msgs[0])

    def test_dec_13_claude_only(self) -> None:
        msgs = messages("2026-12-13")  # yakshanba: ertangi to'lov + keyingi hafta
        self.assertEqual(len(msgs), 2)
        self.assertIn("Claude obunasi", msgs[0])
        self.assertNotIn("Uzum", msgs[0])
        self.assertTrue(msgs[1].startswith("🗓 Keyingi hafta, 14.12–20.12:"))

    def test_mar_20_lock_only(self) -> None:
        msgs = messages("2027-03-20")
        self.assertEqual(len(msgs), 1)
        self.assertNotIn("Ertaga", msgs[0])
        self.assertIn("2 500 000 so'm omonatga", msgs[0])

    def test_mar_21_nothing(self) -> None:
        self.assertEqual(messages("2027-03-21"), [])

    def test_ordinary_day_nothing(self) -> None:
        self.assertEqual(messages("2026-11-10"), [])

    def test_oct_20_before_period_no_lock(self) -> None:
        self.assertEqual(messages("2026-10-20"), [])

    def test_sunday_week_digest(self) -> None:
        msgs = messages("2026-11-15")
        self.assertEqual(len(msgs), 1)
        text = msgs[0]
        self.assertTrue(text.startswith("🗓 Keyingi hafta, 16.11–22.11:"))
        self.assertIn("• 20.11 (Ju): +3 325 200 — Asosiy oylik", text)
        self.assertIn("• 20.11 (Ju): → 2 500 000 — Omonatga qulflash", text)
        self.assertIn("Yo'lkira: 5 ish kuni × 10 000 = 50 000 so'm.", text)

    def test_sunday_after_period_no_digest(self) -> None:
        self.assertEqual(messages("2027-03-21"), [])


def morning(iso: str) -> list[str]:
    return remind.build_morning(date.fromisoformat(iso))


class MorningTest(unittest.TestCase):
    def test_workday_transport_only(self) -> None:
        msgs = morning("2026-11-13")
        self.assertEqual(len(msgs), 1)
        self.assertTrue(msgs[0].startswith("☀️ Bugun, 13.11 (Juma) — ish kuni."))
        self.assertIn("Faqat 10 000 so'm yo'lkira", msgs[0])
        self.assertNotIn("Bugungi reja", msgs[0])

    def test_weekend_with_payments(self) -> None:
        msgs = morning("2026-11-14")
        self.assertEqual(len(msgs), 1)
        self.assertIn("— dam olish kuni.", msgs[0])
        self.assertIn("−410 000 — Claude obunasi", msgs[0])
        self.assertIn("−430 000 — Uzum qarzini yopish", msgs[0])

    def test_plain_weekend_and_holiday_silent(self) -> None:
        self.assertEqual(morning("2026-11-15"), [])
        self.assertEqual(morning("2026-12-08"), [])

    def test_outside_period_silent(self) -> None:
        self.assertEqual(morning("2026-10-26"), [])
        self.assertEqual(morning("2027-03-22"), [])

    def test_month_start_summary(self) -> None:
        msgs = morning("2026-12-01")
        self.assertEqual(len(msgs), 2)
        text = msgs[1]
        self.assertTrue(text.startswith("📅 Dekabr rejasi:"))
        self.assertIn("• Kirim: +3 848 891", text)
        self.assertIn("• Majburiy to'lovlar: −1 062 000", text)
        self.assertIn("• Yo'lkira: 22 ish kuni — −220 000", text)
        self.assertIn("• Omonatga: → 2 500 000", text)

    def test_november_summary_matches_tracker(self) -> None:
        text = remind.month_summary(2026, 11)
        self.assertIn("• Kirim: +4 148 891", text)
        self.assertIn("• Majburiy to'lovlar: −1 492 000", text)
        self.assertIn("• Yo'lkira: 21 ish kuni — −210 000", text)

    def test_plan_final_balance(self) -> None:
        # CLAUDE.md dagi yakuniy reja balansi bilan bir xil bo'lishi kerak
        self.assertEqual(remind.plan_balance(date(2027, 3, 20)), 13_794_455)
        self.assertEqual(remind.plan_balance(date(2026, 10, 27)), 990_000)


class MainTest(unittest.TestCase):
    def run_main(self, env: dict[str, str], argv: list[str] | None = None) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), redirect_stdout(out), redirect_stderr(err):
            code = remind.main(argv or [])
        return code, out.getvalue(), err.getvalue()

    def test_missing_env_exits_nonzero(self) -> None:
        code, _, err = self.run_main({"TODAY": "2026-11-04", "BOT_TOKEN": "x"})
        self.assertNotEqual(code, 0)
        self.assertIn("CHAT_ID", err)
        self.assertIn("WEBAPP_URL", err)

    def test_sends_with_web_app_button(self) -> None:
        resp = mock.MagicMock()
        resp.__enter__.return_value = io.BytesIO(b'{"ok": true}')
        with mock.patch("urllib.request.urlopen", return_value=resp) as urlopen:
            code, _, _ = self.run_main({**ENV, "TODAY": "2026-11-13"})
        self.assertEqual(code, 0)
        payload = json.loads(urlopen.call_args.args[0].data)
        self.assertEqual(payload["chat_id"], "42")
        button = payload["reply_markup"]["inline_keyboard"][0][0]
        self.assertEqual(button, {"text": "Trekerni ochish", "web_app": {"url": ENV["WEBAPP_URL"]}})

    def test_api_error_exits_nonzero_without_leaking_token(self) -> None:
        resp = mock.MagicMock()
        resp.__enter__.return_value = io.BytesIO(b'{"ok": false, "description": "chat not found"}')
        with mock.patch("urllib.request.urlopen", return_value=resp):
            code, _, err = self.run_main({**ENV, "TODAY": "2026-11-13"})
        self.assertEqual(code, 1)
        self.assertIn("chat not found", err)
        self.assertNotIn(ENV["BOT_TOKEN"], err)

    def test_dry_run_needs_no_secrets(self) -> None:
        code, out, _ = self.run_main({"TODAY": "2026-11-04"}, ["--dry-run"])
        self.assertEqual(code, 0)
        self.assertIn("Qarz qaytishi", out)

    def test_morning_slot(self) -> None:
        code, out, _ = self.run_main({"TODAY": "2026-11-14"}, ["--dry-run", "--slot", "morning"])
        self.assertEqual(code, 0)
        self.assertIn("morning, xabarlar: 1", out)
        self.assertIn("Bugungi reja", out)


if __name__ == "__main__":
    unittest.main()
