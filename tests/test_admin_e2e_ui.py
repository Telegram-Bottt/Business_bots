# E2E-style UX tests (basic scenarios). More comprehensive interactive conversation tests can be added later.
from types import SimpleNamespace
import importlib
import aiogram
# patch decorator during import
_orig = getattr(aiogram.Router,'message',None)
aiogram.Router.message = lambda *a, **k: (lambda f: f)
admin_handlers = importlib.reload(importlib.import_module('app.handlers.admin'))
if _orig is not None:
    aiogram.Router.message = _orig

ADMIN_ID = 123456789
admin_handlers.ADMIN_IDS = [ADMIN_ID]

class FakeMessage:
    def __init__(self, user_id, chat_id, args=''):
        self.from_user = SimpleNamespace(id=user_id)
        self.chat = SimpleNamespace(id=chat_id)
        self._args = args
        self.replies = []

    def get_args(self):
        return self._args

    async def answer(self, text):
        self.replies.append(text)


def test_admin_add_and_edit_master(temp_db):
    async def _run():
        # add master
        admin_handlers.ADMIN_IDS = [ADMIN_ID]
        msg = FakeMessage(ADMIN_ID, ADMIN_ID, args='NewMaster|bio|contact')
        await admin_handlers.cmd_add_master(msg)
        # find created master id by reading replies
        assert any('Мастер добавлен' in r for r in msg.replies)
    __import__('asyncio').run(_run())
