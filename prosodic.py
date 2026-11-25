"""تحويل النص العربي المشكول إلى نمط ثنائي: 1 = متحرك، 0 = ساكن.

الإدخال يجب أن يكون مشكولًا. ويُستحسن كتابة همزة الوصل (ٱ) صراحةً حيث تُكتب ألفًا
(مثل: بِٱلْعَلْيَاءِ، فَٱصْبَحِينَا) لأن الألف وحدها قد تلتبس بألف المد.
"""
import re
from dataclasses import dataclass

FATHA, DAMMA, KASRA = "\u064E", "\u064F", "\u0650"
SHADDA, SUKUN, DAGGER, WASL = "\u0651", "\u0652", "\u0670", "\u0671"
TANWEEN = {"\u064B": FATHA, "\u064C": DAMMA, "\u064D": KASRA}
MADD = {"ا": FATHA, "ى": FATHA, "و": DAMMA, "ي": KASRA}
PROCLITICS = "وفبكل"
WORD_RE = re.compile(r"[\u0621-\u063A\u0641-\u065F\u0670\u0671]+")


@dataclass
class Unit:
    ch: str
    v: str = ""
    shadda: bool = False
    tan: str = ""
    tan_wasl: bool = False
    dagger: bool = False
    skip: bool = False


def _parse_word(word):
    units = []
    for c in word:
        if c == "آ":
            units += [Unit("أ", v=FATHA), Unit("ا")]
        elif c in (SHADDA, FATHA, DAMMA, KASRA, SUKUN, DAGGER) or c in TANWEEN:
            if not units:
                continue
            if c == SHADDA:
                units[-1].shadda = True
            elif c in (FATHA, DAMMA, KASRA):
                units[-1].v = c
            elif c in TANWEEN:
                units[-1].tan = TANWEEN[c]
            elif c == DAGGER:
                units[-1].dagger = True
        else:
            units.append(Unit(c))
    return units


def _fix_tanween_alif(w):
    """ألف تنوين الفتح لا تُنطق وصلًا: (وُقُوفًا) -> وُقُوفَنْ."""
    for j, u in enumerate(w):
        if u.ch in "اى" and u.tan == FATHA and j > 0 and not w[j - 1].v and not w[j - 1].tan:
            w[j - 1].tan = FATHA
            u.skip, u.tan = True, ""
        elif u.tan == FATHA and j == len(w) - 2 and w[j + 1].ch in "اى" \
                and not w[j + 1].v and not w[j + 1].tan:
            w[j + 1].skip = True


def _mark_wasl(words):
    """التقاط ألف الوصل غير المعلَّمة بـ (ٱ): ألف أول الكلمة، أو ألف (ال) بعد حرف جر/عطف."""
    for w in words:
        if w[0].ch == "ا" and not w[0].v and not w[0].tan:
            w[0].ch = WASL
        elif len(w) > 2 and w[0].ch in PROCLITICS and w[0].v \
                and w[1].ch == "ا" and not w[1].v and w[2].ch == "ل" and not w[2].v:
            w[1].ch = WASL


def _resolve_wasl(flat):
    for i, u in enumerate(flat):
        if u.ch != WASL:
            continue
        if i > 0:
            u.skip = True
            prev = flat[i - 1]
            if prev.tan:
                prev.tan_wasl = True
            elif not prev.v and not prev.shadda:
                if prev.ch in MADD and i >= 2 and flat[i - 2].v == MADD[prev.ch]:
                    prev.skip = True          # حذف حرف المد قبل همزة الوصل
                else:
                    prev.v = KASRA            # تحريك الساكن قبل همزة الوصل
        # لام شمسية: ٱلشُّ -> تُحذف اللام ويبقى الحرف المشدد
        if i + 2 < len(flat) and flat[i + 1].ch == "ل" and not flat[i + 1].v \
                and flat[i + 2].shadda:
            flat[i + 1].skip = True


def bits_for(text, lengthen_end=False):
    """يعيد سلسلة من 0/1. lengthen_end=True يُشبع حركة الحرف الأخير (ي/ا/و)."""
    words = [_parse_word(w) for w in WORD_RE.findall(text)]
    words = [w for w in words if w]
    for w in words:
        _fix_tanween_alif(w)
    _mark_wasl(words)
    flat = [u for w in words for u in w]
    _resolve_wasl(flat)

    bits = []
    for u in flat:
        if u.skip:
            continue
        if u.ch == WASL:          # همزة وصل في بداية النص تُنطق
            bits.append(1)
            continue
        if u.shadda:
            bits += [0, 1]
        elif u.tan:
            bits += [1, 1] if u.tan_wasl else [1, 0]
        elif u.v:
            bits.append(1)
        else:
            bits.append(0)
        if u.dagger:
            bits.append(0)
    if lengthen_end and bits and bits[-1] == 1:
        bits.append(0)
    return "".join(map(str, bits))
