from app.debugger.verifier import verify

def test_debugger():
    assert verify("x = 1")["verified"] is True
    assert verify("x =")["verified"] is False
