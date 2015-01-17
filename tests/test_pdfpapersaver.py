from pdfpapersaver.__main__ import main


def test_main():
    assert main([]) == 0
    raise Exception("jason bourne ...")