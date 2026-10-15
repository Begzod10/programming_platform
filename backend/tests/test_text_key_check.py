from app.services.exercise_service import check_text_answer_by_key as chk


def test_braces():
    e = "Figurali qavslar {} yordamida"
    assert chk(e, "{}")
    assert chk(e, "Figurali qavs {}")
    assert not chk(e, "()")
    assert not chk(e, "${}")
    assert not chk(e, "[]")


def test_this_keyword():
    e = "this kalit so'zidan"
    assert chk(e, "this")
    assert chk(e, "This kalit so'zi")
    assert not chk(e, "Nomi (kalit) bo'yicha: obj.ism")
    assert not chk(e, "thistle")


def test_no_tokens():
    assert not chk("Metod (Method)", "metod")
    assert not chk(None, "x")
