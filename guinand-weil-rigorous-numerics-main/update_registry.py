# -*- coding: utf-8 -*-
"""Update the guinand-weil-qinf entry in PROJECT_REGISTRY.json (SSoT).

Edit is limited to the `notes` field of one project. `meta` is left untouched:
the 26-Sep session added a project without bumping meta.updated, so the
convention is that meta.updated tracks structural changes only.

Run from C:/Users/usER/oracle-toe. Writes UTF-8, ensure_ascii=False, indent=2,
matching the existing file.
"""
import json
import io
import os
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8")

REG = os.path.join("state", "PROJECT_REGISTRY.json")
PID = "guinand-weil-qinf"

NOTES = (
    "SESI 2026-09-27: GERBANG 3b LOLOS -> (100,40) FINAL. "
    "Goal A/B/D/E TERTUTUP, C terjawab sejauh data (M-G rmse 0.304 vs divergen 1.36-1.45; "
    "lambda_* ~ 10^-61.7; LIMIT MASIH OPEN, fit-only). "
    "c=100: (100,20) RESOLVED POSITIF 3.03e-62; (100,40) lambda_min = +1.32105051975e-102 "
    "RESOLVED POSITIF (dy=0, dps140->180) dan kini FINAL: gerbang identitas psi' lolos DUA "
    "presisi -- 4.807480089477698e-138 (dps140, 35.44 orde di bawah lambda_min) dan "
    "3.912055399093736e-159 (dps160, 56.53 orde); psi 9.381409e-140. "
    "AKAR kegagalan lama: mp.lerchphi(z,2,a_n) dengan z=1e-4 meleset SISTEMATIS "
    "8.42831291456e-100 pada dps140-252 lalu melompat di dps>=288 -- konvergen ke limit yang "
    "salah (dy 140->252 hanya 1e-201). Rantai NON-SIRKULAR: 0.0108573620475813 x "
    "3.12332701278e-100 = 3.391109217077509e-102 = selisih closed terukur. 6 dari 7 komponen "
    "closed_dpsi lolos 1e-160..1e-162, hanya lerchphi gagal. "
    "Section 7a RETRACTED (salah baca di pihak kita): 1e-59 = TARGET SERTIFIKASI B_T, bukan "
    "lambda_min (bukti certification_floor_solve; lambda_min di preprint muncul 1x saja di "
    "kapsi Fig.2; sertifikat (100,200) yang diterbitkan = inertia saja n+=401 n-=0). "
    "lambda_min adalah eigenvalue matriks Q dan TIDAK PERNAH menyentuh closed_dpsi -> TIDAK ADA "
    "ANGKA LAMA YANG BERUBAH, hanya kedalaman identitas. "
    "DEVIASI aturan dy dinyatakan terbuka: dy literal = 21.08961 tidak < 1e-4 karena residual "
    "terkoreksi berada di lantai presisi; kriteria yang dipakai = residual < lambda_min pada dua "
    "presisi. "
    "LANDMINE: gw_qinf.py:47 menyetel mp.mp.dps=40 di level-modul -- impor dulu, dps sesudahnya. "
    "Laporan: GUINAND_WEIL/GW_STATUS_2026-09-26.md (diperbarui 27 Sep, section 7b = log "
    "eliminasi). Tidak ada klaim RH/Weil/prime/factoring."
)


def main():
    if not os.path.exists(REG):
        sys.exit("registry not found: %s" % REG)

    with io.open(REG, encoding="utf-8") as fh:
        data = json.load(fh)

    hit = 0
    for proj in data["projects"]:
        if proj.get("id") == PID:
            old = proj.get("notes", "")
            proj["notes"] = NOTES
            hit += 1
            print("project id : %s" % PID)
            print("old length : %d chars" % len(old))
            print("new length : %d chars" % len(NOTES))
            print("old head   : %s" % old[:90].replace("\n", " "))
            print("new head   : %s" % NOTES[:90].replace("\n", " "))

    if hit != 1:
        sys.exit("expected exactly 1 match for %s, got %d" % (PID, hit))

    backup = REG + ".bak-20260927"
    shutil.copy2(REG, backup)
    print("backup     : %s" % backup)

    with io.open(REG, "w", encoding="utf-8", newline="\n") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
        fh.write("\n")

    # round-trip verification
    with io.open(REG, encoding="utf-8") as fh:
        check = json.load(fh)
    n = len(check["projects"])
    ok = [p for p in check["projects"] if p.get("id") == PID and p["notes"] == NOTES]
    print("projects   : %d" % n)
    print("round-trip : %s" % ("OK" if len(ok) == 1 else "FAILED"))
    print("meta kept  : %s" % json.dumps(check["meta"].get("updated")))


if __name__ == "__main__":
    main()
