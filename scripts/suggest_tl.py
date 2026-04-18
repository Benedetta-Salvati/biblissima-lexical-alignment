import re
import unicodedata
from pathlib import Path
import pandas as pd
from difflib import get_close_matches


# Normalisation


SUPERSCRIPTS = str.maketrans({
    "¹": "1", "²": "2", "³": "3", "⁴": "4", "⁵": "5",
    "⁶": "6", "⁷": "7", "⁸": "8", "⁹": "9", "⁰": "0",
})

def norm_basic(s: str) -> str:
    if s is None:
        return ""
    s = str(s).strip()
    s = re.sub(r"\s+", " ", s)
    return unicodedata.normalize("NFC", s)

def norm_loose(s: str) -> str:
    """
    Normalisation agressive :
    accents/diacritiques, ç, chiffres/exposants
    """
    s = norm_basic(s)
    if not s:
        return ""
    s = s.translate(SUPERSCRIPTS)
    s = s.lower()

    s = s.replace("ſ", "s").replace("æ", "ae").replace("œ", "oe")

    s = unicodedata.normalize("NFD", s)
    s = "".join(ch for ch in s if unicodedata.category(ch) != "Mn")
    s = unicodedata.normalize("NFC", s)

    s = re.sub(r"[·•’'`´\-_/]", "", s)
    s = re.sub(r"\d+", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def tokenize_lemma(s: str):
    s = norm_basic(s)
    if not s:
        return []
    return [t for t in re.split(r"\s+", s) if t]



# Lecture fichiers


def read_missing_tsv(path: Path):
    df = pd.read_csv(path, sep="\t", dtype=str, keep_default_na=False)
    col = df.columns[0]
    return [norm_basic(x) for x in df[col].tolist() if norm_basic(x)]

def read_tllemma_txt(path: Path):
    lemmes = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line:
            continue
        if "\t" in line:
            lemma = line.split("\t")[0].strip()
        elif ";" in line:
            lemma = line.split(";")[0].strip()
        else:
            lemma = line
        if lemma:
            lemmes.append(lemma)
    return lemmes



# Suggestions


def build_index(tl_lemmes):
    idx = {}
    for lem in tl_lemmes:
        k = norm_loose(lem)
        if k:
            idx.setdefault(k, set()).add(norm_basic(lem))
    return idx, sorted(idx.keys())

def suggest_one(missing_lemma, idx, keys):
    raw = norm_basic(missing_lemma)
    if not raw or raw.upper() == "FALSE":
        return ""

    toks = tokenize_lemma(raw)
    suggestions = []

    for tok in toks:
        k = norm_loose(tok)
        if not k:
            continue

        if k in idx:
            suggestions.append(sorted(idx[k])[0])
        else:
            close = get_close_matches(k, keys, n=1, cutoff=0.90)
            if close:
                suggestions.append(sorted(idx[close[0]])[0])

    if not suggestions:
        return ""
    if len(set(suggestions)) == 1:
        return suggestions[0]
    return " ".join(suggestions)



# Main


def main():
    ROOT = Path.cwd()

    missing_path = ROOT / "reports" / "dmf_tl_absent_tl.tsv"
    tllemma_path = ROOT / "tllemma" / "tllemma.txt"
    out_path = ROOT / "suggestions_dmf_absent_vs_tl.tsv"

    if not missing_path.exists():
        raise FileNotFoundError(f"Introuvable: {missing_path}")
    if not tllemma_path.exists():
        raise FileNotFoundError(f"Introuvable: {tllemma_path}")

    missing = read_missing_tsv(missing_path)
    tl_lemmes = read_tllemma_txt(tllemma_path)

    idx, keys = build_index(tl_lemmes)

    rows = []
    for m in missing:
        rows.append({
            "dmf_tl_absent": m,
            "suggestion_tl": suggest_one(m, idx, keys)
        })

    df = pd.DataFrame(rows)
    df.to_csv(out_path, sep="\t", index=False, encoding="utf-8")

    print(f"OK — {len(df)} lignes écrites dans {out_path}")

if __name__ == "__main__":
    main()