"""
certify_vault.py — Certificazione Digitale per il Vault Obsidian
===============================================================
Basato sul Capitolo 4 di "Art Between Matter and Code" di G. Moioli
Caso pratico per la tesi di laurea in Scultura, Accademia di Brera

Funzionalita:
  1. Scansiona tutti i file .md, genera hash SHA-256
  2. Produce un certificato digitale in formato JSON
  3. Supporta la verifica a catena (chain verification)
  4. Modalita verifica: confronta lo stato attuale con l'ultimo certificato

Utilizzo:
  python certify_vault.py           Crea un nuovo certificato
  python certify_vault.py --verify  Verifica l'integrita dei file
  python certify_vault.py --list    Mostra la cronologia dei certificati
"""

import os
import json
import hashlib
import argparse
import time
import sys
import io
from datetime import datetime

# Compatibilita terminale Windows (codifica UTF-8)
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

# ============================================================
# Configurazione
# ============================================================
VAULT_PATH = os.path.dirname(os.path.abspath(__file__))
CERT_DIR = os.path.join(VAULT_PATH, "_certificates")
VAULT_NAME = "Il Mio Archivio della Conoscenza"

# ============================================================
# Funzioni principali
# ============================================================

def sha256_file(filepath):
    """Calcola l'hash SHA-256 di un file"""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def scan_md_files(vault_path):
    """Scansiona tutti i file .md nel vault, restituisce percorsi relativi"""
    md_files = []
    vault_norm = os.path.normpath(vault_path)
    for root, dirs, files in os.walk(vault_path):
        # Salta directory .obsidian e _certificates
        dirs[:] = [d for d in dirs if d not in (".obsidian", "_certificates")]
        for f in files:
            if f.endswith(".md"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, vault_norm)
                md_files.append(rel_path)
    return sorted(md_files)


def load_latest_certificate():
    """Carica l'ultimo certificato"""
    if not os.path.isdir(CERT_DIR):
        return None
    certs = [f for f in os.listdir(CERT_DIR) if f.endswith(".json")]
    if not certs:
        return None
    latest = sorted(certs)[-1]
    with open(os.path.join(CERT_DIR, latest), "r", encoding="utf-8") as f:
        return json.load(f)


def compute_vault_hash(file_hashes):
    """Calcola l'hash radice del vault (root hash)"""
    combined = "".join(
        f"{entry['path']}:{entry['sha256']}" for entry in file_hashes
    )
    return hashlib.sha256(combined.encode()).hexdigest()


def create_certificate():
    """Crea un nuovo certificato digitale"""
    os.makedirs(CERT_DIR, exist_ok=True)

    print("=" * 60)
    print("  CERTIFICAZIONE DIGITALE DEL VAULT OBSIDIAN")
    print("=" * 60)
    print()
    print(f"  Vault: {VAULT_NAME}")
    print(f"  Percorso: {VAULT_PATH}")
    print()

    # Scansione file
    md_files = scan_md_files(VAULT_PATH)
    print(f"  Trovati {len(md_files)} file .md")
    print()

    # Calcolo hash per ogni file
    file_hashes = []
    for rel_path in md_files:
        full_path = os.path.join(VAULT_PATH, rel_path)
        file_hash = sha256_file(full_path)
        file_hashes.append({
            "path": rel_path.replace("\\", "/"),
            "sha256": file_hash
        })

    # Carica certificato precedente (per la catena)
    prev_cert = load_latest_certificate()
    prev_hash = prev_cert["certificate"]["root_hash"] if prev_cert else None
    prev_id = prev_cert["certificate"]["id"] if prev_cert else None

    # Genera ID certificato
    timestamp = datetime.now()
    cert_id = timestamp.strftime("CERT-%Y%m%d-%H%M%S")

    # Calcola root hash
    root_hash = compute_vault_hash(file_hashes)

    # Costruisce il certificato
    certificate = {
        "vault": {
            "nome": VAULT_NAME,
            "percorso": VAULT_PATH,
            "totale_file": len(file_hashes)
        },
        "certificato": {
            "id": cert_id,
            "data_creazione": timestamp.isoformat(),
            "timestamp": int(time.time()),
            "algoritmo": "SHA-256",
            "root_hash": root_hash,
            "certificato_precedente_id": prev_id,
            "root_hash_precedente": prev_hash,
            "lunghezza_catena": (prev_cert["certificate"]["lunghezza_catena"] + 1) if prev_cert else 1
        },
        "file": file_hashes
    }

    # Salva certificato
    cert_filename = f"{cert_id}.json"
    cert_path = os.path.join(CERT_DIR, cert_filename)
    with open(cert_path, "w", encoding="utf-8") as f:
        json.dump(certificate, f, ensure_ascii=False, indent=2)

    print(f"  Certificato creato: {cert_filename}")
    print(f"  Root hash: {root_hash[:20]}...")
    print(f"  Lunghezza catena: {certificate['certificato']['lunghezza_catena']}")
    if prev_id:
        print(f"  Certificato precedente: {prev_id}")
    print()
    print("-" * 60)
    print(f"  CERTIFICATO DIGITALE")
    print(f"  Vault: {VAULT_NAME}")
    print(f"  File certificati: {len(file_hashes)}")
    print(f"  Data: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  ID: {cert_id}")
    print(f"  Root hash SHA-256: {root_hash}")
    print("-" * 60)

    return certificate


def verify_files():
    """Verifica l'integrita dei file rispetto all'ultimo certificato"""
    prev_cert = load_latest_certificate()

    if prev_cert is None:
        print("Nessun certificato trovato. Creane uno prima (python certify_vault.py)")
        return

    cert_info = prev_cert["certificato"]
    print(f"Certificato di riferimento: {cert_info['id']}")
    print(f"Creato il: {cert_info['data_creazione']}")
    print(f"Lunghezza catena: {cert_info['lunghezza_catena']}")
    print()

    # Riscansione dei file correnti
    current_files = scan_md_files(VAULT_PATH)

    # Dizionario dei file nel certificato
    cert_files = {entry["path"]: entry["sha256"] for entry in prev_cert["file"]}

    modificati = []
    aggiunti = []
    rimossi = []
    invariati = 0

    # Verifica file correnti
    for rel_path in current_files:
        cert_path_key = rel_path.replace("\\", "/")
        full_path = os.path.join(VAULT_PATH, rel_path)
        current_hash = sha256_file(full_path)

        if cert_path_key in cert_files:
            if current_hash == cert_files[cert_path_key]:
                invariati += 1
            else:
                modificati.append(cert_path_key)
        else:
            aggiunti.append(cert_path_key)

    # Verifica file eliminati
    for cert_path_key in cert_files:
        local_path = os.path.join(VAULT_PATH, cert_path_key)
        if not os.path.exists(local_path):
            rimossi.append(cert_path_key)

    # Report
    print("RISULTATO VERIFICA:")
    print(f"  Invariati: {invariati}")
    print(f"  Modificati: {len(modificati)}")
    print(f"  Aggiunti: {len(aggiunti)}")
    print(f"  Rimossi: {len(rimossi)}")
    print()

    if modificati:
        print("File modificati:")
        for f in modificati:
            print(f"    ~ {f}")
        print()

    if aggiunti:
        print("File aggiunti:")
        for f in aggiunti:
            print(f"    + {f}")
        print()

    if rimossi:
        print("File rimossi:")
        for f in rimossi:
            print(f"    - {f}")
        print()

    # Verifica root hash
    current_hashes = []
    for rel_path in current_files:
        full_path = os.path.join(VAULT_PATH, rel_path)
        file_hash = sha256_file(full_path)
        current_hashes.append({
            "path": rel_path.replace("\\", "/"),
            "sha256": file_hash
        })
    current_root = compute_vault_hash(current_hashes)

    if current_root == cert_info["root_hash"]:
        print("VERIFICA SUPERATA — Il root hash corrisponde.")
        print("L'integrita del vault e confermata.")
    else:
        print("VERIFICA FALLITA — Il root hash non corrisponde.")
        print("Il vault e stato modificato dall'ultimo certificato.")
        print(f"  Root hash registrato: {cert_info['root_hash'][:20]}...")
        print(f"  Root hash attuale:    {current_root[:20]}...")


def list_certificates():
    """Mostra la cronologia dei certificati"""
    if not os.path.isdir(CERT_DIR):
        print("Nessun certificato trovato.")
        return

    cert_files = sorted([f for f in os.listdir(CERT_DIR) if f.endswith(".json")])

    if not cert_files:
        print("Nessun certificato trovato.")
        return

    print(f"Cronologia certificati ({len(cert_files)} totali):")
    print()

    for i, cf in enumerate(cert_files):
        with open(os.path.join(CERT_DIR, cf), "r", encoding="utf-8") as f:
            cert = json.load(f)
        ci = cert["certificato"]
        marker = " <-- ultimo" if i == len(cert_files) - 1 else ""
        print(f"  [{i+1}] {ci['id']}{marker}")
        print(f"      Data: {ci['data_creazione']}")
        print(f"      File: {cert['vault']['totale_file']}")
        print(f"      Root hash: {ci['root_hash'][:20]}...")
        if ci["certificato_precedente_id"]:
            print(f"      Precedente: {ci['certificato_precedente_id']}")
        print()


# ============================================================
# Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description=f"Certificazione digitale per il vault Obsidian: {VAULT_NAME}"
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="Modalita verifica: confronta i file con l'ultimo certificato"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="Mostra la cronologia dei certificati"
    )
    args = parser.parse_args()

    if args.list:
        list_certificates()
    elif args.verify:
        verify_files()
    else:
        create_certificate()


if __name__ == "__main__":
    main()
