import argparse, json, sys
from .prosodic import bits_for
from .meters import scan_line


def _both(text):
    return {"plain": bits_for(text), "lengthened": bits_for(text, lengthen_end=True)}


def _fmt(feet):
    return " | ".join(f"{label} ({bits})" for bits, label in feet)


def scan(sadr, ajz):
    sb, ab = _both(sadr), _both(ajz)
    return sb, ab, scan_line(sb, ab)


def main():
    p = argparse.ArgumentParser(prog="arudh", description="تقطيع عروضي (مسودة للمراجعة)")
    p.add_argument("sadr", nargs="?", help="صدر البيت مشكولًا")
    p.add_argument("ajz", nargs="?", help="عجز البيت مشكولًا")
    p.add_argument("--corpus", help="ملف JSON للنماذج، مثل data/jahili_samples.json")
    a = p.parse_args()

    if a.corpus:
        data = json.load(open(a.corpus, encoding="utf-8"))
        items = data["verses"]
    elif a.sadr and a.ajz:
        items = [{"poet": "-", "poem": "-", "sadr": a.sadr, "ajz": a.ajz, "meter_attributed": None}]
    else:
        p.error("أعطني الصدر والعجز، أو --corpus")

    for v in items:
        sb, ab, res = scan(v["sadr"], v["ajz"])
        print(f"\n{v['poet']} — {v['poem']}")
        print(f"  {v['sadr']}  ***  {v['ajz']}")
        print(f"  نمط الصدر: {sb['plain']}   (بإشباع: {sb['lengthened']})")
        print(f"  نمط العجز: {ab['plain']}   (بإشباع: {ab['lengthened']})")
        if not res:
            print("  النتيجة: لا مطابقة في الجداول الحالية — للمراجعة")
        for r in res:
            print(f"  مطابقة محتملة: {r['meter']}  [نهاية الصدر: {r['sadr_end']}، نهاية العجز: {r['ajz_end']}]")
            print(f"    صدر: {_fmt(r['sadr'])}")
            print(f"    عجز: {_fmt(r['ajz'])}")
        att = v.get("meter_attributed")
        if att:
            found = {r["meter"] for r in res}
            tag = "يوافق" if att in found else "يخالف/غير محسوم"
            print(f"  المنسوب تقليديًا: {att} ← {tag} (بانتظار حكم صاحب الاختصاص)")


if __name__ == "__main__":
    sys.exit(main())
