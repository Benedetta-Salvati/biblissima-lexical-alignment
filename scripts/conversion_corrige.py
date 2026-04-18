import os
import pandas as pd
from bs4 import BeautifulSoup


def get_text_list(parent, tag_names):
    """
    Retourne la liste des textes pour tous les tags donnés, dans l'ordre d'apparition.
    tag_names: str ou list[str]
    """
    if isinstance(tag_names, str):
        tag_names = [tag_names]
    out = []
    for tname in tag_names:
        for node in parent.find_all(tname):
            txt = node.get_text(strip=True)
            if txt:
                out.append(txt)
    return out


def unique_or_empty(lst):
    """Déduplique en conservant l'ordre, enlève les chaînes vides."""
    seen = set()
    out = []
    for x in lst:
        if not x:
            continue
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out


def extract_equivalences_from_art(art):
    """
    À partir d'un <ART>, extrait :
    DMF (LEM), TL (TL.RENVOI ou TL/*), GD, GDC, AND, DECT.
    Retourne une liste de dicts (une ou plusieurs lignes).
    """
    # DMF
    dmf_list = get_text_list(art, "LEM")
    dmf = dmf_list[0] if dmf_list else ""

    # TL : soit TL.RENVOI, sinon TL (SLEMME / SLEMMEVSPE / LEMME)
    tl_values = []
    tl_renvoi = get_text_list(art, "TL.RENVOI")
    if tl_renvoi:
        # parfois plusieurs TL.RENVOI : on garde tout
        tl_values.extend(tl_renvoi)
    else:
        for tl_node in art.find_all("TL"):
            # dans TL, on peut trouver SLEMME, SLEMMEVSPE, ou LEMME
            tl_values.extend(get_text_list(tl_node, "SLEMME"))
            tl_values.extend(get_text_list(tl_node, "SLEMMEVSPE"))
            tl_values.extend(get_text_list(tl_node, "LEMME"))

    tl_values = unique_or_empty(tl_values)

    # GD
    gd_values = []
    for gd_node in art.find_all("GD"):
        gd_values.extend(get_text_list(gd_node, "LEMME"))
    gd_values = unique_or_empty(gd_values)

    # GDC
    gdc_values = []
    for gdc_node in art.find_all("GDC"):
        gdc_values.extend(get_text_list(gdc_node, "LEMME"))
    gdc_values = unique_or_empty(gdc_values)

    # AND : LEMME et LEMMEAND
    and_values = []
    for and_node in art.find_all("AND"):
        and_values.extend(get_text_list(and_node, "LEMME"))
        and_values.extend(get_text_list(and_node, "LEMMEAND"))
    and_values = unique_or_empty(and_values)

    # DECT
    dect_values = []
    for dect_node in art.find_all("DECT"):
        dect_values.extend(get_text_list(dect_node, "LEMME"))
    dect_values = unique_or_empty(dect_values)

    # Si l'article ne contient aucun de ces champs, on ne crée rien
    if not (tl_values or gd_values or gdc_values or and_values or dect_values or dmf):
        return []

    # Pour rester proche du script d'origine :
    # s'il n'y a pas de valeurs pour un champ, on met "" (une seule option)
    # sinon on fait une ligne par combinaison des listes.
    def opts(values):
        return values if values else [""]

    rows = []
    for tl in opts(tl_values):
        for gd in opts(gd_values):
            for gdc in opts(gdc_values):
                for and_ in opts(and_values):
                    for dect in opts(dect_values):
                        rows.append(
                            {"TL": tl, "DMF": dmf, "GD": gd, "GDC": gdc, "AND": and_, "DECT": dect}
                        )

    return rows


def main():
    # Chemins (adaptés à ton dossier actuel)
    xml_path = "DICT_2024-05-29-corr.xml"
    out_dir = "output"
    out_path = os.path.join(out_dir, "data_df_lemmes.tsv")

    if not os.path.exists(xml_path):
        raise FileNotFoundError(
            f"Fichier XML introuvable: {xml_path}\n"
            f"Place DICT_2024-05-29-corr.xml dans le même dossier que ce script, "
            f"ou modifie xml_path."
        )

    os.makedirs(out_dir, exist_ok=True)

    # Lecture + parsing XML
    with open(xml_path, "r", encoding="ISO-8859-1") as f:
        data = f.read()

    soup = BeautifulSoup(data, "xml")
    arts = soup.find_all("ART")

    rows = []
    for art in arts:
        rows.extend(extract_equivalences_from_art(art))

    df_lemmes = pd.DataFrame(rows, columns=["TL", "DMF", "GD", "GDC", "AND", "DECT"])

    # Export TSV
    df_lemmes.to_csv(out_path, sep="\t", encoding="utf-8", index=False, header=True)

    print(f"OK: {len(df_lemmes):,} lignes écrites dans {out_path}")


if __name__ == "__main__":
    main()