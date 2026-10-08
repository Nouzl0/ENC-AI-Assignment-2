# Pravidla pro agenty

Platí pro celý tento repozitář.

## Git: pouze main

- Veškerou práci, změny a commity prováděj výhradně na větvi `main`.
- Nevytvářej ani nepoužívej jiné lokální nebo vzdálené větve, včetně `codex/*`.
  Nepracuj v detached HEAD ani ve worktree na jiné větvi.
- Před úpravami ověř `git status --short --branch`. Pokud nejsi na `main`, přepni
  na ni pouze bezpečně, bez přepsání či přenosu cizích rozpracovaných změn.
- Při čistém pracovním stromu před zahájením práce proveď `git pull --ff-only origin main`.
- Každou dokončenou změnu nebo etapu po odpovídajících kontrolách commitni na
  `main` a proveď `git push origin main`. Nenechávej hotovou práci pouze lokálně.
- Commituj jen změny patřící k aktuálnímu úkolu; cizí změny nemaž ani nevracej.
- Nepoužívej force push ani nepřepisuj již publikovanou historii.
- Při konfliktu nebo zamítnutém pushi nezakládej náhradní větev a nepřepisuj historii;
  problém vyřeš bezpečně, případně jej oznam uživateli. Neúspěšný push nevydávej za hotový.
