from app.db import session


def test_create_database_initializes_tables(monkeypatch):
    calls = {}

    class DummyEngine:
        pass

    def fake_create_all(bind=None):
        calls["bind"] = bind

    monkeypatch.setattr(session, "engine", DummyEngine())
    monkeypatch.setattr(session.Base.metadata, "create_all", fake_create_all)

    session.create_database()

    assert calls["bind"] is session.engine
