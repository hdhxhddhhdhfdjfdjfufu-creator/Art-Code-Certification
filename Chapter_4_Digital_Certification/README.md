# Capitolo 4 — Certificazione Digitale per Vault Obsidian

## Descrizione

Questo script implementa un sistema di certificazione digitale per un vault
Obsidian, basato sui concetti del Capitolo 4 di *"Art Between Matter and Code"*
di Gianpiero Moioli.

## Funzionalita

- Scansione di tutti i file `.md` del vault
- Calcolo hash SHA-256 per ogni file
- Generazione di un certificato digitale in formato JSON
- Verifica a catena (chain verification)
- Modalita di verifica dell'integrita

## Script

- `scripts/certify_vault.py` — script principale di certificazione

## Output

I certificati vengono salvati in `_certificates/` all'interno del vault.
Ogni certificato contiene:

- ID univoco e timestamp
- Root hash SHA-256 dell'intero vault
- Hash individuale per ogni file
- Collegamento al certificato precedente (catena)

## Esempio

```bash
python scripts/certify_vault.py
```
