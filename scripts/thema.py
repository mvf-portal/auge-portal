#!/usr/bin/env python3
"""Alles Themenspezifische der taeglichen Studienauswahl — und sonst nichts.

Diese Datei ist die EINZIGE unter scripts/, die sich von Portal zu Portal
inhaltlich unterscheidet. `update_studies.py` bleibt in allen Portalen
wortgleich und importiert von hier. Wer die Auswahl aendern will, aendert
Text in dieser Datei — keinen Code.

Erzeugt von neues-portal.py aus dem Themenprofil `themen/auge.json`.
Weiterentwickelt wird danach hier, nicht im Profil.
"""
from __future__ import annotations

import os

# --------------------------------------------------------------- Kennungen
# NCBI bittet bei automatisierten Zugriffen um eine Tool-Kennung.
NCBI_TOOL = "auge-portal"

# ----------------------------------------------------------- Die Suchabfrage
# Zwei Bloecke, die BEIDE zutreffen muessen. Ohne den zweiten spuelt die Abfrage
# Arbeiten herein, die das Thema nur streifen; ohne den ersten kommt beliebige
# Versorgungsliteratur.
#
# Zur Feldwahl: [MeSH Terms] fasst breit, [Majr] verlangt das Haupt-Schlagwort,
# [Title/Abstract] fasst am breitesten, [Title] am engsten. Faustregel aus den
# Schwesterportalen: Steht ein Begriff in fremden Abstracts als blosses Werkzeug
# oder Beiwerk, ist [Title/Abstract] untauglich — dann [Majr]/[Title]. Im
# KI-Portal sank die Trefferzahl dadurch von 605.000 auf 321.000, und erst die
# kleinere Menge handelte tatsaechlich vom Thema.
#
# Vor dem Livegang die Trefferzahl in PubMed nachsehen und hier notieren, damit
# spaetere Aenderungen messbar bleiben.
_THEMA = (
    '((("Eye Diseases"[Majr] OR "Ophthalmology"[Majr] OR "Macular '
    'Degeneration"[Majr] OR "Glaucoma"[Majr] OR "Cataract"[Majr] OR '
    '"Retinal Diseases"[Majr] OR "Vision Disorders"[Majr] OR "Visually '
    'Impaired Persons"[Majr] OR "Refractive Errors"[Majr] OR "Corneal '
    'Diseases"[Majr] OR "Dry Eye Syndromes"[Majr] OR "Uveitis"[Majr] '
    'OR "Blindness"[Majr] OR "Vision, Low"[Majr] OR "Eye '
    'Injuries"[Majr] OR "Myopia"[Majr] OR "Retinopathy of '
    'Prematurity"[Majr] OR "Macular Edema"[Majr] OR "Ophthalmologic '
    'Surgical Procedures"[Majr] OR "Intravitreal Injections"[Majr] OR '
    '"Lenses, Intraocular"[Majr] OR "Visual Acuity"[Majr] OR '
    'glaucoma[Title] OR cataract[Title] OR "macular '
    'degeneration"[Title] OR retinopathy[Title] OR "dry eye"[Title] OR '
    'keratoconus[Title] OR "visual impairment"[Title] OR "visual '
    'acuity"[Title] OR intravitreal[Title] OR ophthalm*[Title] OR '
    'myopia[Title] OR "retinal detachment"[Title] OR uveitis[Title] OR '
    '"age-related macular"[Title]) OR ("Diabetic Retinopathy"[Majr] OR '
    '"diabetic retinopathy"[Title] OR "diabetic macular '
    'edema"[Title])) NOT ("Artificial Intelligence"[Majr] OR "Machine '
    'Learning"[Majr] OR "Deep Learning"[Majr] OR "Telemedicine"[Majr] '
    'OR "Medical Informatics"[Majr] OR "Nursing"[Majr] OR "Nursing '
    'Care"[Majr] OR "Long-Term Care"[Majr] OR "Nursing Homes"[Majr] OR '
    '"Aging"[Majr] OR "Longevity"[Majr] OR "Frailty"[Majr] OR '
    '"Geriatrics"[Majr] OR "Health Literacy"[Majr] OR "Patient '
    'Education as Topic"[Majr] OR "Climate Change"[Majr] OR "Air '
    'Pollution"[Majr] OR "Vaccination"[Majr] OR "Vaccines"[Majr] OR '
    '"Multimorbidity"[Majr] OR "Patient Safety"[Majr] OR "Medical '
    'Errors"[Majr] OR "Cross Infection"[Majr] OR "Mental Health '
    'Services"[Majr]))'
)
_KONTEXT = (
    '(hasabstract NOT (Comment[Publication Type] OR '
    'Editorial[Publication Type] OR Letter[Publication Type] OR '
    'News[Publication Type] OR "Published Erratum"[Publication Type] '
    'OR "Retraction of Publication"[Publication Type] OR "Case '
    'Reports"[Publication Type]))'
)
# OHNE "Humans"[MeSH]: Dieses Portal zeigt bewusst auch Grundlagenforschung.
# Tier- und Laborarbeiten kommen damit in den Pool - der Prompt muss sie ordnen.
# Zweiter Grund, den Filter hier wegzulassen: Frisch in PubMed aufgenommene
# Datensaetze sind noch nicht verschlagwortet. In der Woche vom 29.08.2026 trugen
# nur 37 bis 40 Prozent der neuen Datensaetze ueberhaupt "Humans"[MeSH] - ueber
# das ganze Jahr sind es 56 bis 67. Der Filter siebt also auch nach
# Bearbeitungsstand der NLM, nicht nur nach Inhalt.
TERM = os.environ.get(
    "SEARCH_TERM",
    f'(({_THEMA} AND {_KONTEXT}))',
)
# Zweite Abfrage, damit Arbeiten mit Deutschland- und Europabezug den
# Kandidatenpool sicher erreichen. Ueber MeSH und Autorenadresse, nicht ueber
# Journalnamen - deutschsprachige Journale liefern kaum Treffer.
TERM_DE = os.environ.get(
    "SEARCH_TERM_DE",
    f"{TERM} AND (Germany[MeSH Terms] OR Germany[Affiliation] "
    "OR Europe[MeSH Terms] OR Europe[Affiliation])",
)

# Groesse des Kandidatenpools. Europa steht vorn und stellt die Mehrheit -
# ein Sprachmodell gewichtet, was es zuerst liest. Wer das umdreht, bekommt
# eine Auswahl ohne Bezug zu hiesigen Verhaeltnissen; im Klima-Portal ist
# genau das passiert.
POOL_EUROPA = 10
POOL_ALLGEMEIN = 45
# Welche Abfrage vorn steht. True ist der Regelfall und die Lehre aus dem
# Klima-Portal: Steht die allgemeine Abfrage vorn, kommt eine Auswahl ohne
# Bezug zu hiesigen Verhaeltnissen heraus. Das Versorgungsforschungs-Portal
# arbeitet historisch andersherum (40 allgemein + 15 deutsch) - dort steht
# hier False, damit der Anschluss an die Vorlage nichts an seiner taeglichen
# Auswahl geaendert hat. Umstellen ist eine redaktionelle Entscheidung.
EUROPA_ZUERST = True

# Wie viele Studien taeglich erscheinen. SOLL wird im Prompt verlangt und beim
# Kappen verwendet; ueber MAX wird gekappt, unter MIN bricht der Lauf ab.
# **Nicht ins JSON-Schema schreiben** - die Anthropic-API lehnt minItems > 1
# und maxItems ab (am 17.08.2026 zweimal mit HTTP 400 belegt).
ANZAHL_SOLL = 6
ANZAHL_MAX = 7
ANZAHL_MIN = 1
# True: zu viele Studien werden auf ANZAHL_SOLL gekuerzt (die Auswahl ist nach
# Relevanz geordnet, die vorderen sind brauchbar). False: zu viele lassen den
# Lauf scheitern - so hielt es das Versorgungsforschungs-Portal von Anfang an.
KAPPEN = True

# ------------------------------------------------------------------- Prompts
SYSTEM = (
    "Du bist Fachredakteur fuer Augenheilkunde. "
    "Aus einer Liste von PubMed-Abstracts waehlst du die relevantesten "
    "aktuellen Studien aus und fasst sie praezise auf Deutsch zusammen. "
    "Deine Leserschaft arbeitet im deutschen Gesundheitswesen: "
    "Augenarztpraxen, Augenkliniken, Kostentraeger, Selbstverwaltung, "
    "Selbsthilfe und Gesundheitspolitik. "
    "Sie erwartet beides - was die Forschung ueber das Auge "
    "herausfindet und was davon bei den Behandelten ankommt."
)

USER_TEMPLATE = """Unten stehen aktuelle PubMed-Abstracts (nach Datum sortiert).

Waehle GENAU 6 Studien aus, die (a) Diagnostik, Therapie, Operation, Rehabilitation oder Versorgung bei Augenerkrankungen betreffen - oder die Grundlagen, auf denen sie beruhen UND (b) im
Abstract ein BENENNBARES ERGEBNIS berichten. Bei quantitativen Arbeiten heisst
das: konkrete Zahlen (Prozentwerte, Effektstaerken, Odds/Hazard Ratios, Zeit-
oder Kostenwirkungen, Fallzahlen, p-Werte) - und die gehoeren dann auch in die
Zusammenfassung. Qualitative Studien (Interviews, Fokusgruppen) und
Expertenpapiere sind ausdruecklich zugelassen; bei ihnen tritt an die Stelle
der Zahl die klar benannte Kernaussage - welche Faktoren, welche Bedingungen,
welche Empfehlung. Was NICHT genuegt, ist ein Abstract, der nur ankuendigt,
was untersucht wurde, ohne zu sagen, was dabei herauskam.
Ueberspringe Studien ohne Abstract oder ohne benennbares Ergebnis. Achte auf
thematische Vielfalt und mische quantitative und qualitative Arbeiten.

THEMATISCHE RANGFOLGE - in dieser Reihenfolge bevorzugen:
  1. Praxisveraendernde Evidenz: Ergebnisse, die eine Leitlinie, eine
     Therapieentscheidung oder ein Versorgungsangebot veraendern koennen -
     randomisierte Studien, Metaanalysen, Leitlinien, Nutzenbewertungen.
  2. Harte Endpunkte: Erblindung, bleibender Sehverlust, Operation,
     Rezidiv, Lebensqualitaet, Selbststaendigkeit im Alltag. Was daran
     etwas aendert, wiegt schwerer als eine Verbesserung im Messwert.
  3. Versorgung und Ergebnis: Screening, Zugang, Wartezeit, Mengen,
     Nachsorge, Rehabilitation und Teilhabe bei Sehbehinderung -
     gemessen an Folgen fuer die Behandelten.
  4. Grundlagenforschung mit erkennbarem Weg in die Klinik: Mechanismus,
     Zielstruktur, Gentherapie, Modell - wenn die Arbeit selbst sagt,
     wohin es fuehrt. Molekulare Befunde ohne diesen Weg gehoeren nicht
     in die Auswahl, auch wenn die Zeitschrift renommiert ist.

NICHT in die Auswahl gehoeren:
Reine Tiermodelle und Zellversuche ohne erkennbaren Bezug zum Menschen, tiermedizinische Arbeiten (Augenerkrankungen bei Hund, Katze, Pferd oder Nutztier - dieser Hub filtert nicht nach Zeitschrift, deshalb erreichen sie den Pool), Phase-I-Studien, Bioaequivalenzstudien, Fallberichte und Fallserien unter zehn Augen, bibliometrische Arbeiten, Editorials und Kommentare.

HARTE REGELN ZUR ZUSAMMENSETZUNG (sie gehen der thematischen Rangfolge vor):
  1. MINDESTENS 2 der sechs Studien muessen aus Europa stammen oder
     ein europaeisches Gesundheitssystem betreffen. Der Europa-Anteil des
     Suchraums liegt hier bei 7 Prozent (gemessen 11.11.2026) - noch
     niedriger als bei den uebrigen Indikations-Hubs. Mehr zu verlangen
     hiesse, den Pool leerzuraeumen.
  2. HOECHSTENS ZWEI der sechs duerfen reine Grundlagenarbeiten sein
     (Zellsystem, Tiermodell, molekularer Mechanismus). Sie gehoeren
     ausdruecklich dazu - dieses Portal zeigt auch, woher das Wissen
     kommt -, aber die Mehrheit der Ausgabe muss am Menschen gemessen sein.
  3. HOECHSTENS EINE darf eine digitale Anwendung oder ein Verfahren des
     maschinellen Lernens im Mittelpunkt haben. Die Abfrage schliesst solche
     Arbeiten bereits aus, wenn sie dort Hauptthema sind; diese Quote faengt
     die uebrigen. Sie gehoeren nach ki.m-vf.de. Die Augenheilkunde ist das
     Fach mit den meisten Bilderkennungsarbeiten ueberhaupt - ohne diese
     Quote bestuende die Ausgabe aus Netzhautbild-Algorithmen.
  4. HOECHSTENS EINE darf die diabetische Retinopathie oder das diabetische
     Makulaoedem im Mittelpunkt haben. Dieses Gebiet ist bewusst NICHT aus
     der Abfrage ausgeschlossen - es gehoert fachlich in beide Portale -,
     aber 77,5 Prozent dieser Arbeiten liegen schon im Diabetes-Hub
     (gemessen 29.10.2026). Die Teilung: Steht das Auge im Mittelpunkt
     (Screening, intravitreale Therapie, Verlauf der Sehschaerfe), gehoert
     die Arbeit hierher. Steht die Stoffwechseleinstellung im Mittelpunkt,
     gehoert sie nach diabetes.m-vf.de.
  5. HOECHSTENS ZWEI der sechs duerfen ausschliesslich einen Messwert
     berichten (Sehschaerfe in logMAR oder Buchstaben, zentrale
     Netzhautdicke, Augeninnendruck in mmHg, Hornhauttopografie) ohne einen
     Endpunkt, den die Behandelten merken. Diese Arbeiten sagen, dass sich
     eine Zahl bewegt, nicht, dass jemand besser sieht oder zurechtkommt.
  6. HOECHSTENS ZWEI duerfen eine Operationstechnik oder ein
     Bildgebungsverfahren im Mittelpunkt haben. Das Fach publiziert darin
     reichlich, und eine Ausgabe aus sechs Techniknachrichten erreicht die
     Leserschaft dieses Verlags nicht.

ZWEITES AUSWAHLKRITERIUM - Übertragbarkeit auf Deutschland:
Bei sonst gleicher Qualität hat die übertragbare Studie IMMER Vorrang vor der
aktuelleren.

  Hoch:    Deutschland und deutschsprachiger Raum, vergleichbare Sozial-
           versicherungssysteme.
  Mittel:  Übriges Europa, Kanada, Australien - andere Ausgangslage,
           ähnlicher Versorgungsauftrag.
  Gering:  USA und Länder mit grundlegend anderer Finanzierung oder
           Ressourcenlage. Nur nehmen, wenn die Fragestellung davon
           unabhängig ist.

Besonderheit dieses Themenfeldes: Zwischen Studienlage und Versorgung stehen in Deutschland drei Dinge. Erstens die intravitreale Therapie, die ueber den EBM, die ambulante spezialfachaerztliche Versorgung und Selektivvertraege geregelt ist - was dort nicht vorgesehen ist, findet in der Flaeche kaum statt. Zweitens die Kataraktoperation als Leistung des ambulanten Operierens, bei der Menge, Wartezeit und Zusatzleistungen die eigentlichen Versorgungsfragen sind. Drittens die Sehhilfen, die seit 2017 nur bei schwerer Sehbeeintraechtigung von der gesetzlichen Krankenversicherung getragen werden. Dazu kommt, dass die Glaukom-Frueherkennung in Deutschland keine Leistung der gesetzlichen Krankenversicherung ist, sondern von den Versicherten selbst bezahlt wird - Screening-Studien aus Laendern mit organisiertem Programm sind deshalb nur eingeschraenkt uebertragbar. Ordne eine Arbeit immer daran ein, ob und wie ihr Befund hier ankommen kann - und sage es, wenn er das absehbar nicht kann. Nenne bei internationalen Arbeiten das Gesundheitssystem, in dem sie entstanden sind.

Fuer jede Studie:
- journal: Journalname genau so, wie er in der Kopfzeile des Abstracts steht -
  Abkuerzung nicht aufloesen, nichts ergaenzen. (Wird ohnehin durch die Angabe
  aus PubMed ersetzt; rate hier nichts.)
- year: Erscheinungsjahr, z. B. "2026"
- pmid: die PubMed-ID
- title: praegnanter deutscher Titel, **hoechstens 160 Zeichen**. Der
  Torwaechter lehnt alles ueber 200 Zeichen ab und stoppt damit die ganze
  Ausgabe - Methode und Population gehoeren nicht in den Titel, sie stehen
  in sum und transfer.
  **Er MUSS das Ergebnis nennen, nicht nur die Massnahme.** Und er darf
  sich NICHT auf den Messwert beschraenken: Eine Differenz von Buchstaben
  auf der Sehtafel oder von Mikrometern Netzhautdicke ist der
  Zwischenschritt, nicht das Ziel. Wo eine Arbeit einen Endpunkt berichtet,
  den die Behandelten merken - Erblindung, bleibender Sehverlust, zweite
  Operation, Lesefaehigkeit, Sturz, Selbststaendigkeit -, gehoert dieser in
  den Titel.
- sum: 1 Satz auf Deutsch, was die Studie untersucht hat. Wenn der genannte
  Anlassfall nur das Material ist, an dem gerechnet wurde, sage das
  ausdruecklich - sonst haelt die Leserschaft ihn fuer den Gegenstand.
- result: Deutsch, die konkreten Zahlen/Befunde + ein kurzer Einordnungssatz.
  Deutsches Zahlenformat mit Komma (z. B. 0,63). **Der Einordnungssatz darf
  nicht behaupten, was die Autoren selbst ablehnen.** Wo ein Abstract eine
  Deutung ausdruecklich zurueckweist, diese Einschraenkung uebernehmen statt
  sie zu ueberschreiben. Ein Rechercheportal referiert, es wertet nicht auf.
- transfer: EIN Halbsatz (höchstens 12 Wörter), warum das Ergebnis für Deutschland
  taugt - oder wo die Grenze liegt. Nenne Land bzw. System und Datengrundlage.
  Keine ganzen Sätze, keine Wiederholung des Titels.
  Gut:      "Deutsche Klinikdaten, vergleichbare Dokumentationspflichten"
            "Niederlande, vergleichbares Versicherungssystem"
            "USA - nur der Sicherheitsbefund ist übertragbar"
  Schlecht: "Diese Studie ist gut übertragbar." (sagt nichts)

WICHTIG - Fachterminologie: Etablierte englische Fachbegriffe NICHT eindeutschen.
Sie sind auch im deutschen Fachdeutsch stehende Begriffe; eine woertliche
Uebersetzung wirkt unprofessionell und erschwert das Wiederfinden.
Englisch bleiben: Screening, Outcome, Baseline, Setting, Follow-up, Hazard Ratio, Odds Ratio, OCT, logMAR, Anti-VEGF, Dry Eye, Real-World-Evidenz, Patient-Reported Outcomes, Shared Decision Making. Deutsch: intravitreale Injektion, Kataraktoperation, Augeninnendruck, Sehschaerfe, Gesichtsfeld, Netzhautabloesung, Hornhauttransplantation, Frueherkennung. Uebersetze alles, wofuer es einen eingefuehrten deutschen Ausdruck gibt.
Faustregel: Wuerde eine deutsche Fachzeitschrift wie Monitor Versorgungsforschung
den Begriff englisch stehen lassen, dann tue es auch. Im Zweifel englisch
belassen und bei Bedarf eine kurze deutsche Erlaeuterung in Klammern ergaenzen.

Gib ausschliesslich das geforderte JSON zurueck.

=== ABSTRACTS ===
{abstracts}
"""

# ------------------------------------------------- Newsfeed
# Wonach dieser Hub im MVF-Archiv sucht (scripts/newsfeed.py). Deutsche,
# versorgungsnahe Begriffe - das Archiv ist deutsch, englische Begriffe
# treffen dort hoechstens zufaellig.
#
# Warum eine eigene Liste und nicht die Schnellwahlbegriffe der Seite: Chips
# sind fuer Datenbankabfragen gemacht. Am 29.08.2026 im Gender-Hub gemessen -
# dort stehen "Herzinfarkt" und "Arzneimittelsicherheit" als Chips, weil deren
# geschlechtsspezifische Seite das Thema ist; im Archiv holten dieselben
# Woerter allgemeine Herz- und Arzneimittelmeldungen. Fehlt NEWS_SUCHE, faellt
# newsfeed.py auf die Chips zurueck - das geht, ist aber die schlechtere Wahl.
#
# Neue Begriffe VOR dem Eintragen messen:
#     py scripts/newsfeed.py --probe
NEWS_SUCHE = [
    "Augenheilkunde",
    "Augenarzt",
    "Augenaerzte",
    "Glaukom",
    "Grauer Star",
    "Makuladegeneration",
    "Netzhaut",
    "Sehbehinderung",
    "Erblindung",
    "Intravitreale Injektion",
]

# Der Ausschreibungsradar steht NICHT mehr hier. Er laeuft seit dem 28.08.2026
# einmal zentral im Versorgungsforschungs-Portal; die zwoelf Themengebiete,
# ihre Auswahlregeln und Suchbegriffe stehen dort in scripts/radar_themen.py.
# Dieser Hub holt sich mit scripts/radar_hinweis.py nur die Zahl seines
# Gebiets.
