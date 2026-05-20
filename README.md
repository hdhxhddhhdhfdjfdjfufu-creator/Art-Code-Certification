# Art-Code-Certification

Certificazione digitale per vault Obsidian.
Caso pratico per tesi di laurea in Scultura, Accademia di Belle Arti di Brera.

Basato sul Capitolo 4 di *"Art Between Matter and Code"* di Gianpiero Moioli.

## Sistema a 3 Livelli

| Livello | Descrizione |
|---------|-------------|
| 1 | Metadati interni (embedding) |
| 2 | Certificato SHA-256 + JSON con verifica a catena |
| 3 | Ancoraggio blockchain Bitcoin via OpenTimestamps |

## Struttura

```
Chapter_4_Digital_Certification/
├── README.md              ← panoramica del capitolo
├── scripts/
│   └── certify_vault.py   ← script di certificazione digitale
├── images/                ← schermate e diagrammi
├── docs/                  ← documentazione
└── media/                 ← video e animazioni
```

## Utilizzo

```bash
# Livello 2: certificato digitale
python Chapter_4_Digital_Certification/scripts/certify_vault.py

# Livello 2: verifica
python Chapter_4_Digital_Certification/scripts/certify_vault.py --verify

# Livello 3: ancoraggio blockchain Bitcoin
python Chapter_4_Digital_Certification/scripts/certify_vault.py --stamp

# Livello 3: verifica ancoraggio
python Chapter_4_Digital_Certification/scripts/certify_vault.py --verify-stamp
```

## Licenza

CC BY-NC 4.0 — vedi [LICENSE](LICENSE).
