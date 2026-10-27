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
        msgs = messages("2026-12-13")
        self.assertEqual(len(msgs), 1)
        self.assertIn("Claude obunasi", msgs[0])
        self.assertNotIn("Uzum", msgs[0])

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


if __name__ == "__main__":
    unittest.main()
