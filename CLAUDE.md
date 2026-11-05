# liederbuecher.com – Projektwissen für Claude

Statische Website (reines HTML/CSS/JS, kein Framework) für die Reihe „Liederbücher für Alt und Jung“ (Schott Music). Live unter **https://liederbuecher.com**, gehostet auf GitHub Pages (Branch `main`, Repo-Root). Repo: `bpm1416-ops/bmpubl`.

Diese Datei ersetzt das lokale Claude-Gedächtnis auf Rechnern, auf denen es nicht vorhanden ist (z. B. MacBook). Aktuelle Details immer im Code/`git log` prüfen.

## Menschen
- **Bernhard Müller** betreut Marketing, Promotion und Website. Technisch nicht erfahren: Technik-Entscheidungen trifft Claude, erklärt aber verständlich auf Deutsch.
- Autor/Komponist der Bücher ist sein Sohn **Sebastian Müller** (siehe `autor.html`). Autorentexte immer um Sebastian herum formulieren. Verlag ist Schott; in Texten nie „Bernhard Mueller Publishing“ nennen.
- Bernhard mag warme Designs. Farben: Header `#5c2418`, Akzent `#c8832a`, Hintergrund `#faf6f0`.

## Arbeitsregeln
- **Nie pushen ohne ausdrückliches OK** („Ja, pushen“). Commit-Nachrichten mit Co-Authored-By-Zeile. GitHub Pages braucht 1–2 Min.
- Alle internen Links und Canonicals zeigen auf `https://liederbuecher.com/...`. `bmpubl.com` und `liederbuecher.info` sind alte Adressen: Treffer korrigieren.
- Großformat-Ausgaben (XXL und Klavier) sind **23 × 30 cm**, nicht 23 × 31.
- Instrumenten-Verfügbarkeit nie aus FAQ-Texten übernehmen, sondern aus der `versions-table` der jeweiligen Buchseite prüfen (FAQ-Texte waren schon falsch).
- Liedtexte oder Noten aus `Beispielseiten/` nie abschreiben oder wiedergeben.
- Wichtige neue Erkenntnisse nach getaner Arbeit in dieser Datei festhalten.

## Seitenstruktur
- Echte Seiten im Root: `index`, `fetenbuch`, `rock-pop`, `rock-pop-2`, `weihnachten`, `kinderliederbuch`, `schlagerbuch`, `folk`, `autor`, `blog`, `kontakt`, `impressum`, `datenschutz`, dazu `gitarre`, `ukulele`, `klavier`, `weitere-instrumente`, `404`.
- Ordner wie `45-2/`, `fb/`, `kinder/`, `vl/`, `wb/`, `weihnachten/` usw. sind **reine Redirect-Stubs** für alte URLs. Nicht bearbeiten, immer die Root-`.html` editieren. Kurzlinks (z. B. `/geige`) sind ebenfalls Stubs.
- Blog: `blog/*.html` (generiert), Index `blog/articles.json`, Bilder `images/blog/`. Buchcover `images/covers/`.
- `google7751d9d8b49c7dba.html` im Root **nicht löschen** (Search-Console-Verifizierung).
- Tracking: nur **Umami** (cookielos). Google Analytics wurde am 2026-11-04 bewusst entfernt (Datenschutz). Umami-Snippet steht in jedem `<head>` und in `HEAD_TEMPLATE` von `scripts/generate_blog.py`. Kein Clarity/keine Session-Recordings.
- CSS-Cache bei GitHub Pages ~4 h: Bei CSS-Änderungen, die sofort sichtbar sein müssen, `?v=YYYYMMDD` an den `style.css`-Link der betroffenen Seite hängen.

## Blogbeitrag schreiben (fester Ablauf)
Nur nach Thema und Hauptprodukt fragen, den Rest ohne Rückfrage abarbeiten:
1. Stil prüfen: letzte Beiträge über `blog/articles.json` lesen. Hausstil ist „du“ (Ausnahme: sensible Pflege-/Demenzthemen dürfen „Sie“), deutsche Anführungszeichen „…“.
2. Aufbau: fetter Einstieg, direkt danach CTA-Box `.blog-cta--cover` (Cover + ein Satz mit Fakten von der Produktseite + Button), nützliche Tipps mit einigen externen Links, Vorteile des passenden Buchs, FAQ mit 8 H3-Fragen. Zusammenfassung von Hand schreiben (~140–160 Zeichen, „Titel – konkrete Aussage“).
3. **CTA-Box zeigt immer das XXL-Cover** (`weihnachten.jpg`, `schlagerbuch.jpg`, `kinderliederbuch.jpg`, `fetenbuch.jpg`), Text nennt „XXL“ (23 × 30 cm, Spiralbindung). Ausnahmen: Ukulele-Themen mit Ukulele-Cover, Klavier-Weihnachtsthemen mit `weihnachten-klavier.jpg`.
4. Entwurf als `.txt` in `blogentwürfe/`: Titelzeile, Leerzeile, `Zusammenfassung: …`, Leerzeile, HTML-Body.
5. Vorschau als temporäre Seite in `blog/` zeigen, danach löschen. Bernhard gibt dort Textfeedback.
6. Hero-Bild: Bernhard bevorzugt Canva-generierte Bilder (Details prüfen, z. B. Zahl der Kerzen). Das Original lädt Bernhard selbst aus Canva herunter (über das Tool gibt es nur ein 200-px-Vorschaubild) und legt es mit dem Dateinamen des Entwurfs in `blogentwürfe/` ab. Bei „no hero image found“: Dateiname liegt evtl. in NFD-Unicode vor (ü), per Python `os.rename` auf den exakten Entwurfsnamen umbenennen.
7. Erzeugen: `python3 scripts/generate_blog.py`. Danach prüfen: Slug (wird bei ~60 Zeichen abgeschnitten, ggf. von Hand kürzen in html, webp, articles.json, blog.html, sitemap.xml), `git diff sitemap.xml` (lastmod-Werte werden zurückgesetzt, alte per Regex aus `git show HEAD:sitemap.xml` wiederherstellen, neuer Eintrag bekommt das heutige Datum), Akzente im Titel (Generator behandelt nur ä/ö/ü/ß, ein „é“ würde den Slug kappen).
8. Entwurf und Hero-Bild nach `blogentwürfe/veröffentlicht/` verschieben.
9. Erst auf Bernhards OK pushen, danach Live-Seite prüfen lassen.

Entwürfe von außen (z. B. alte byclaire-Entwürfe) vor dem Generieren inhaltlich prüfen: Dateiname passt zum Inhalt? Veraltete `bmpubl.com`-Links? byclaire-CTA-Reste (`app.byclaire.co`, `data-claire-slot`) entfernen. `.rtf` vorher mit `textutil -convert txt -stdout` umwandeln. Anzahl im Titel mit den tatsächlich gelisteten Liedern abgleichen.

## Wichtige Fakten zu Produkten
- Klavier-Ausgaben gibt es nur für Kinderliederbuch, Weihnachtsliederbuch und Fetenbuch (ED 23953, 26,50 €, 23 × 30 cm, Spiralbindung). C-Stimme/Blockflöte und Violine gibt es nur beim Weihnachtsliederbuch (Violine: kompakte Ausgabe „45 Weihnachtslied-Klassiker“, 48 S., 23 × 30 cm, 18,50 €).
- Fetenbuch-Inhalt: aktuelle Ausgabe ohne „Guantanamera“, mit „Aber bitte mit Sahne“ und „Griechischer Wein“. Die Website schreibt „Alle Lieder“ statt „100 Lieder“.
- Pro Ausgabe gibt es eine Schott-ED-Nummer. Beim Weihnachtsliederbuch: Gitarre 22935, Ukulele 22936, XXL 22802, Klavier 23646.

## SEO-Stand (Nov 2026)
- Erledigt: Canonicals, Meta-Descriptions, Sitemap-lastmod, Blog aktiv, Titel ohne Brand-Suffix (unter 70 Zeichen), 404-Seite, Redirect-Stubs für fehlerhafte URL-Varianten.
- Offen: Backlink-Strategie (VLB, Schott-Produktseiten-Link, Musikverlags-Verzeichnisse, später Chorverband, Kita-/Altenpflege-Portale), FAQ-JSON-LD, Alt-Texte/Bildnamen, Verifikation der alten Redirects in der Search Console.
- Search Console (3 Monate bis 2026-11-03): 284 Klicks. Die meisten Klicks kommen von Blogposts über Senioren, Schlager und Advent. Produktseiten bekommen kaum Klicks, daher interne Links und CTA-Boxen. CTA-Boxen fehlen noch in ca. 19 älteren Posts (Kinderlieder, Lagerfeuer, Gitarre/Ukulele lernen, Liederbuch-Vergleiche, Demenz, Party, Senioren-Liederbücher), geplant ab Woche vom 2026-11-09.
- Datenschutztext sollte noch juristisch geprüft werden (z. B. eRecht24). Kein Rechtsrat.

## Außerhalb des Repos (nur auf dem Mac mini)
Im übergeordneten Ordner `BMPUBL/` liegen Quellmaterialien, die nicht in Git sind:
`Produktinfos/` (Word-Doku pro Buch, maßgebliche Produkttexte), `Beispielseiten/` (Scans nach ED-Nummer), `Low Res/` (PDF-Proofs), `Spotify/` (Playlist-Links), `Promotion/` (Kampagnenmaterial). Auf einem anderen Rechner fehlen sie. Dann Bernhard um die benötigte Datei bitten.
