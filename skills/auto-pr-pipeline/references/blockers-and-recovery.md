# Blocker und Recovery

Stoppe nur bei echtem Risiko. Kleine Reibung ist kein Grund fuer Abbruch.

## Hard Blocker

Ein Hard Blocker liegt vor bei:

- Secret-, Token-, Key- oder Push-Protection-Fund
- potenzieller Datenverlust oder riskanter Migration ohne klare Absicherung
- fehlender Auth oder fehlender Berechtigung fuer einen erforderlichen GitHub-Schritt
- Merge-Konflikt mit fachlicher Richtungsentscheidung
- mehreren unrelated Change-Sets, die sich nicht sicher trennen lassen, besonders im selben Dateibereich
- unklarer Produkt- oder Architekturentscheidung mit deutlich unterschiedlichen Folgen
- required checks schlagen nach fokussiertem Versuch weiter fehl und die Ursache ist nicht belastbar klar
- riskanter Workflow-, Infra- oder Release-Eingriff ohne ausreichende Schutzmechanismen
- unklarem Fork- oder Upstream-Ziel, wenn dadurch der falsche Branch oder das falsche Repo betroffen sein koennte

## Soft Blocker

Weiterarbeiten ist meist moeglich bei:

- optionales Tool fehlt lokal
- nicht-required Preview fehlt
- Stil- oder Nit-Kommentar
- einzelne flaky, nicht-required Checks
- fehlende kleine Kontextinformation ohne Sicherheits- oder Architekturfolgen
- fehlender `gh`-Login, solange lokale Vorbereitungen noch sinnvoll erledigt werden koennen

## Recovery-Budget

Nicht stumpf "dreimal alles". Arbeite fokussiert:

- 1 Diagnose-Durchlauf
- 1 gezielter Reparaturversuch
- 1 Verifikation

Wenn das Signal danach klar ist, handle entsprechend weiter. Wenn es danach weiterhin unklar oder riskant ist, stoppe.

## Blocker-Ausgabeformat

Wenn du stoppen musst, liefere genau dieses Format:

`BLOCKER`

- Was blockiert gerade?

`FAKTEN`

- Welche beobachtbaren Fakten fuehren dazu?

`RISIKO`

- Warum waere autonomes Weiterarbeiten riskant?

`OPTION A`

- konservativster sichere Weg

`OPTION B`

- pragmatischer Weg mit erklaertem Trade-off

`OPTION C`

- schneller, aber riskanter Weg nur wenn passend

`EMPFEHLUNG`

- welche Option ist fachlich am saubersten und warum

## Resume nach Blocker

Bei Wiederaufnahme:

- alten Zustand nicht blind annehmen
- neuen Snapshot bauen
- pruefen, ob der Blocker wirklich beseitigt ist
- dann an der passenden Stelle weitermachen, nicht am Anfang
- wenn zwischenzeitlich Queue oder Auto-Merge schon armed wurde, diesen Zustand respektieren
