# Commit-Strategie

Die Commit-Strategie richtet sich nach Scope, Veroeffentlichungsgrad und Repo-Konvention.

## Grundregeln

- Nie blind alles stagen
- Nie unrelated User-Aenderungen mitnehmen
- Nie Secrets, Keys, `.env` oder Build-Artefakte committen
- Repo-Konvention vor eigener Vorliebe
- Veroeffentlichte History respektieren

## Entscheidungslogik

### Fall A: Dirty Worktree, keine lokalen Commits

Aktion:

- passende Checks laufen lassen
- nur in-scope Dateien stagen
- Commit erstellen

### Fall B: Dirty Worktree, letzter Commit lokal und unpushed, gleicher Scope

Aktion:

- Amend ist erlaubt, wenn:
  - dieselbe fachliche Einheit betroffen ist
  - noch kein PR-Review auf diesem Stand haengt
  - kein anderer Mensch auf genau dieser History aufsetzt

Sonst:

- neuer Follow-up-Commit

### Fall C: Dirty Worktree, Commit bereits gepusht oder PR offen

Aktion:

- neuer Follow-up-Commit
- keine leichtfertige History-Umschreibung

### Fall D: Clean Worktree, lokale Commits ahead of upstream

Aktion:

- pushen
- danach PR erstellen oder vorhandenen PR aktualisieren

### Fall E: Clean Worktree, PR offen, keine lokalen Aenderungen

Aktion:

- nicht neu committen
- Reviews, Checks, Auto-Merge oder Merge Queue bearbeiten

## Mehrere Change-Sets

Wenn die Working Tree Aenderungen nicht zu einer einzigen Aufgabe gehoeren:

- wenn sauber trennbar: nur den relevanten Teil stagen
- wenn nicht sauber trennbar: stoppen und Optionen nennen

## Commit-Message

Bevorzuge:

- Repo-eigenen Stil, wenn er erkennbar ist
- sonst kurze, praezise Message mit Nutzer- oder Systemwirkung

Conventional Commits nur wenn:

- das Repo sie sichtbar nutzt
- oder der User sie explizit erwartet

## History-Rewrite

Nur mit hoher Huerde:

- erlaubt auf eigenem Feature-Branch
- nur wenn keine gemeinsame Nutzung / kein Review-Schaden entsteht
- nur mit `--force-with-lease`, nie mit blindem `--force`

Nicht geeignet fuer:

- shared branches
- geschuetzte Branches
- reviewte oeffentliche History ohne klaren Mehrwert

## Squash-Merge-Kontext

Wenn das Repo squash merge bevorzugt, ist eine perfekte lokale Zwischen-History weniger wichtig als:

- gut lesbarer PR-Kontext
- sinnvolle Commit-Grenzen waehrend der Arbeit
- nachvollziehbare Review-Fixes
