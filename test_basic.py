from arudh import bits_for


def test_imru_alqais_sadr():
    # قِفَا نَبْ | كِ مِنْ ذِكْ رَى | حَبِيبِنْ | وَمَنْزِلِ  (النمط محسوب يدويًا)
    s = "قِفَا نَبْكِ مِنْ ذِكْرَى حَبِيبٍ وَمَنْزِلِ"
    expected = "11010" + "1101010" + "11010" + "11011"
    assert bits_for(s) == expected
    assert bits_for(s, lengthen_end=True) == expected + "0"


def test_antara_sadr():
    s = "هَلْ غَادَرَ ٱلشُّعَرَاءُ مِنْ مُتَرَدَّمِ"
    expected = "1010110" + "1110110" + "111011"
    assert bits_for(s) == expected
