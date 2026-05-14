from src.integrations.fragment.session_storage import FragmentSession, SessionStorage


def test_save_cookies():
    storage = SessionStorage(session_key="any")
    storage.session = FragmentSession(
        hash="any",
        ton_proof_payload="any",
        cookies={"money": "power", "override": "me"},
    )

    assert storage.session.cookies == {"money": "power", "override": "me"}

    storage.save_cookies(cookies={"abc": "somevalue", "override": "diff"})

    assert storage.session.cookies == {
        "abc": "somevalue",
        "money": "power",
        "override": "diff",
    }


# TODO: tests for the saving


# def test_save_tokens():
#     pass
