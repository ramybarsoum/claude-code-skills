# Repo Detection und Policy Snapshot

Baue vor Commit, Push, PR oder Merge einen kompakten Policy-Snapshot.

## 1. Repo-Struktur lesen

Pruefe gezielt auf:

- `.github/workflows/`
- `.github/CODEOWNERS`
- `.github/PULL_REQUEST_TEMPLATE*`
- `package.json`, `pnpm-lock.yaml`, `package-lock.json`, `yarn.lock`, `bun.lockb`
- `pyproject.toml`, `requirements.txt`, `tox.ini`, `noxfile.py`
- `Makefile`, `justfile`, `Taskfile.yml`
- `turbo.json`, `nx.json`
- `go.mod`, `Cargo.toml`, `pom.xml`, `Gemfile`
- Repo-Dokumente mit Build-/Release-Konventionen

## 2. Git-Zustand lesen

Ermittle mindestens:

- aktueller Branch
- upstream gesetzt oder nicht
- ahead/behind
- staged / unstaged / untracked
- lokale Commits seit Base
- ob bereits ein PR fuer den Branch existiert
- ob die Arbeit versehentlich direkt auf `main` / `master` / Release-Branch liegt

## 3. GitHub-Policy lesen

Wenn `gh` verfuegbar und authentifiziert ist, ermittle:

- Default-Branch
- erlaubte Merge-Methoden
- Auto-Merge moeglich oder aktiv
- Merge Queue vorhanden oder erforderlich
- Review-Decision
- offene Threads / requested changes
- required status checks
- required deployments
- Branch-Protection / Rulesets soweit sichtbar

Wenn `gh` fehlt oder nicht authentifiziert ist:

- falle auf einen lokalen Vorbereitungsmodus zurueck
- fuehre nur lokale Validierung, Branch-Sicherung und Commit-Entscheidungen aus
- gib einen klaren Handover aus, was fuer Push, PR oder Merge noch extern noetig ist

Das ist kein Grund fuer einen fruehen Komplettabbruch, solange lokale Arbeit sinnvoll vorbereitet werden kann.

## 3a. Base-Branch robust bestimmen

Bestimme die Base nicht blind ueber den Default-Branch.

Prioritaet:

1. wenn bereits ein PR existiert: dessen echte Base verwenden
2. wenn der Branch sauber von einem Tracking-Branch oder Upstream ableitbar ist: diesen Kontext nutzen
3. sonst Repo-Default-Branch verwenden
4. bei Forks pruefen, ob `origin` der Fork und ein anderer Remote das eigentliche Ziel ist

Wenn Base oder Zielrepo trotz dieser Schritte unklar bleibt, ist das ein Risikosignal und kann einen Stop erfordern.

## 4. Repo-native Checks ableiten

Nutze nicht generische Standardbefehle. Leite Checks aus dem Repo ab:

- Node: Package-Manager aus Lockfile, Skripte aus `package.json`
- Python: Tooling aus `pyproject.toml`, `tox`, `nox`, `pytest`, `ruff`, `mypy`
- Monorepo: betroffene Pakete / Apps / Targets statt Vollgas auf alles
- CI: lies die echten Workflow-Jobs und priorisiere die Checks, die spaeter required sind
- Release-/Deploy-Repos: beachte Preview-, Staging- oder Deployment-Gates wenn sie merge-relevant sind

## 5. Installationen nur wenn noetig

Fuehre keine mutierenden Installationen blind aus.

Regel:

- Wenn vorhandene Umgebung fuer belastbare Checks reicht: keine Neuinstallation
- Wenn das Repo klar einen Install-Schritt erwartet: gezielt und mit passendem Tool
- Wenn der Install-Schritt selbst Dateien aendern wuerde: Risiko bewusst abwaegen und dokumentieren
- Wenn Install oder Codegen nur Seiteneffekte wie Lockfile- oder Artefakt-Diffs erzeugt: nur mitnehmen, wenn das Repo dies erwartet oder die Aenderung fachlich notwendig ist

## 6. Snapshot in Worte fassen

Verdichte den Zustand intern in wenige Entscheidungen:

- Was ist bereits erledigt
- Was fehlt noch bis zu einem guten Endzustand
- Welche Repo-Regel steuert den naechsten Schritt
- Welche Checks sind wirklich relevant
- Ob Draft PR, Ready PR, Auto-Merge oder Queue der richtige Modus ist
