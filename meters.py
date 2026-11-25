"""جداول البحور وزحافاتها وعللها — مسودة أولية تحتاج مراجعة صاحب الاختصاص.

كل بحر = قائمة خانات (تفعيلات) للصدر وأخرى للعجز، وكل خانة قاموس {نمط ثنائي: اسم الصورة}.
عدّل الجداول بحرية؛ المحرك لا يحكم، بل يعرض المطابقات الممكنة فقط.
"""

def _u(*ds):
    out = {}
    for d in ds:
        out.update(d)
    return out

# ---- الطويل
_t1 = {"11010": "فعولن", "1101": "فعولُ"}
_t2 = {"1101010": "مفاعيلن", "110110": "مفاعلن", "110101": "مفاعيلُ"}
_t_arud = {"110110": "مفاعلن"}
_t_darb = {"110110": "مفاعلن", "1101010": "مفاعيلن", "11010": "فعولن"}
# ---- البسيط
_b1 = {"1010110": "مستفعلن", "110110": "متفعلن", "101110": "مستعلن"}
_b2 = {"10110": "فاعلن", "1110": "فعلن"}
_b_end = {"1110": "فعلن", "10110": "فاعلن", "1010": "فعْلن"}
# ---- الكامل
_k = {"1110110": "متفاعلن", "1010110": "مُتْفاعلن"}
_k_darb = _u(_k, {"111010": "متفاعلْ"})
# ---- الوافر
_w = {"1101110": "مفاعلتن", "1101010": "مفاعلْتن"}
_w_end = _u({"11010": "فعولن"}, _w)
# ---- الخفيف
_f1 = {"1011010": "فاعلاتن", "111010": "فعلاتن"}
_f2 = {"1010110": "مستفعلن", "110110": "متفعلن"}
_f_end = _u(_f1, {"10110": "فاعلن", "1110": "فعلن"})

METERS = {
    "الطويل": {"sadr": [_t1, _t2, _t1, _t_arud], "ajz": [_t1, _t2, _t1, _t_darb]},
    "البسيط": {"sadr": [_b1, _b2, _b1, _b_end], "ajz": [_b1, _b2, _b1, _b_end]},
    "الكامل": {"sadr": [_k, _k, _k], "ajz": [_k, _k, _k_darb]},
    "الوافر": {"sadr": [_w, _w, _w_end], "ajz": [_w, _w, _w_end]},
    "الخفيف": {"sadr": [_f1, _f2, _f_end], "ajz": [_f1, _f2, _f_end]},
}


def _parse(bits, slots, i=0, pos=0):
    if i == len(slots):
        return [] if pos == len(bits) else None
    for var, label in slots[i].items():
        if bits.startswith(var, pos):
            rest = _parse(bits, slots, i + 1, pos + len(var))
            if rest is not None:
                return [(var, label)] + rest
    return None


def scan_line(sadr_bits, ajz_bits, meters=METERS):
    """sadr_bits / ajz_bits: قاموس {"plain": ..., "lengthened": ...} من bits_for.
    يعيد كل المطابقات الممكنة (قد تكون صفرًا)."""
    results = []
    for name, m in meters.items():
        found = False
        for s_mode in ("plain", "lengthened"):
            for a_mode in ("lengthened", "plain"):
                s = _parse(sadr_bits[s_mode], m["sadr"])
                a = _parse(ajz_bits[a_mode], m["ajz"])
                if s is not None and a is not None:
                    results.append({"meter": name, "sadr": s, "ajz": a,
                                    "sadr_end": s_mode, "ajz_end": a_mode})
                    found = True
                    break
            if found:
                break
    return results
