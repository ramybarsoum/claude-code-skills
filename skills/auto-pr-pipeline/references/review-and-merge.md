# Review und Merge

Arbeite Reviews nach Wirkung ab, nicht nach Lautstaerke.

## Prioritaet

1. failing required checks
2. requested changes von Menschen
3. Security-, Dependency- oder Deployment-Signale
4. echte Bugs und fehlende Tests
5. Maintainability mit realem Impact
6. Stil, Nits, Kosmetik

## Review-Fixes

- Sammle zusammengehoerige Fixes
- Fuehre passende Regression-Checks aus
- Push in sinnvollen Batches
- Antworte knapp und nachvollziehbar

Wenn bereits Commits gepusht und kommentiert wurden:

- bevorzuge Follow-up-Commits statt Amend oder Rebase
- halte den Review-Verlauf nachvollziehbar

## Threads

Resolve einen Thread nur wenn:

- der Punkt wirklich behoben wurde
- oder eine klare, fachlich tragfaehige Begruendung dokumentiert wurde

Antworte nicht mechanisch mit "fixed". Benenne kurz:

- was geaendert wurde
- in welchem Commit oder Push es steckt
- warum etwas bewusst nicht umgesetzt wurde

## Draft, Ready, Auto-Merge, Queue

Bevorzuge diesen Ablauf:

- Draft PR fuer sichtbare, aber noch nicht reviewfertige Arbeit
- Ready PR wenn die lokalen Hochrisiko-Themen bereinigt sind
- Auto-Merge wenn nur noch formale Gates offen sind
- Merge Queue wenn das Repo sie verwendet oder verlangt
- wenn Auto-Merge oder Queue bereits armed ist und der Head unveraendert bleibt: nicht unnoetig eingreifen

## Flaky oder infrastrukturelle Checks

Behandle flaky Checks anders als echte Produktfehler:

- rerun statt sofort Code aendern, wenn die Fehlerspur klar nach Infra oder Timing aussieht
- bei required Checks nicht endlos loopen
- wenn der Check merge-kritisch bleibt, kommuniziere den externen Blocker klar

## Merge-Methode

Folge zuerst der Repo-Policy:

- squash wenn das Repo oder der Flow auf einen sauberen Einzel-Merge optimiert
- merge commit wenn die Commit-History selbst wertvoll ist
- rebase nur wenn das Repo es klar bevorzugt

Wenn unklar:

- squash ist fuer einzelne Feature-Arbeit meist der sichere Default

## Stale-Head-Schutz

Wenn ueber CLI gemerged wird, bevorzuge Schutz gegen Race Conditions, z. B. Merge nur fuer den erwarteten Head-Commit.

## Nicht endlos babysitten

Wenn die Plattform den Rest uebernehmen kann, ist ein guter Endzustand:

- Auto-Merge armed
- Merge Queue armed
- Ready PR mit allen Fakten dokumentiert

Das ist oft professioneller als manuelles Dauer-Polling.
