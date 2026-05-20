# Capitolo 4 — Certificazione Digitale per Vault Obsidian

## Descrizione

Questo script implementa un sistema di certificazione digitale a tre livelli
per un vault Obsidian, basato sui concetti del Capitolo 4 di
*"Art Between Matter and Code"* di Gianpiero Moioli.

## Livelli di Certificazione

| Livello | Descrizione | Tecnologia |
|---------|-------------|------------|
| Livello 1 | Metadati interni | Proprieta personalizzate |
| Livello 2 | Certificato digitale esterno | SHA-256 + JSON |
| Livello 3 | Ancoraggio blockchain | OpenTimestamps + Bitcoin |

## Funzionalita

- Scansione di tutti i file `.md` del vault
- Calcolo hash SHA-256 per ogni file
- Generazione di un certificato digitale in formato JSON
- Verifica a catena (chain verification)
- Ancoraggio blockchain Bitcoin via OpenTimestamps

## Script

- `scripts/certify_vault.py` — script principale di certificazione

## Output

I certificati vengono salvati in `_certificates/` all'interno del vault.
Ogni certificato contiene:

- ID univoco e timestamp
- Root hash SHA-256 dell'intero vault
- Hash individuale per ogni file
- Collegamento al certificato precedente (catena)
- File `.ots` per ancoraggio blockchain (Livello 3)

## Esempi

```bash
# Livello 2: crea certificato digitale
python scripts/certify_vault.py

# Livello 2: verifica integrita
python scripts/certify_vault.py --verify

# Livello 3: crea certificato + ancoraggio blockchain
python scripts/certify_vault.py --stamp

# Livello 3: verifica ancoraggio blockchain
python scripts/certify_vault.py --verify-stamp

# Cronologia certificati
python scripts/certify_vault.py --list
```

## Esempio di output

In `docs/` sono disponibili un certificato di esempio e il relativo file
`.ots` di ancoraggio blockchain.
