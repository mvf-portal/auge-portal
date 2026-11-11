#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Baut aus mvf-logo.png die Negativfassung fuer dunkle Flaechen.

Das Hauslogo besteht aus genau zwei Farben auf durchsichtigem Grund: der
Schriftzug in Hausblau #00529F, das Quadrat in Gold #BE9E53. Auf dem blauen
Balken des Newsletter-Banners verschwindet der Schriftzug - er hat dieselbe
Farbe wie der Untergrund.

Ein CSS-Filter (brightness(0) invert(1)) macht alles Sichtbare weiss und
nimmt dabei auch dem Quadrat sein Gold. Deshalb wird hier pixelweise
umgefaerbt: Blau wird Weiss, Gold bleibt Gold. Die Kanten sind weich
(Alphakanal), die Zuordnung laeuft deshalb ueber den Abstand zu den beiden
Farben, nicht ueber Gleichheit.
"""
from __future__ import annotations

import pathlib

import numpy as np
from PIL import Image

HIER = pathlib.Path(__file__).resolve().parent
BLAU = (0, 82, 159)
GOLD = (190, 158, 85)
ERSATZ_BLAU = (255, 255, 255)      # Schriftzug auf dunklem Grund

quelle = Image.open(HIER / "mvf-logo.png").convert("RGBA")
d = np.asarray(quelle).astype(np.int16)
rgb, alpha = d[..., :3], d[..., 3]

nah_blau = np.abs(rgb - np.array(BLAU)).sum(axis=-1)
nah_gold = np.abs(rgb - np.array(GOLD)).sum(axis=-1)
ist_blau = (nah_blau <= nah_gold) & (alpha > 0)

neu = d.copy()
neu[ist_blau, :3] = ERSATZ_BLAU
neu[~ist_blau & (alpha > 0), :3] = GOLD

ziel = HIER / "mvf-logo-negativ.png"
Image.fromarray(neu.astype(np.uint8), "RGBA").save(ziel, "PNG", optimize=True)
print(f"  {ziel.name}: {quelle.width}x{quelle.height}, "
      f"{ziel.stat().st_size:,} Byte".replace(",", "."))
