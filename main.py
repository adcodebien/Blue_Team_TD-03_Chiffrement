import os
import sys
import json
import platform
import subprocess
from datetime import datetime
from getpass import getpass

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.scrypt import Scrypt
from cryptography.hazmat.primitives import constant_time

from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64
import paramiko
from tqdm import tqdm
import secrets

KEY_DIR = "./keys"
LAB_DIR = "./lab_data"


def verification_dependance():
    print("Vérification des dépendances...")

    if sys.version_info < (3, 8):
        print("Python 3.8+ requis.")
        sys.exit(1)

    try:
        import cryptography
        import paramiko
        print("✓ Toutes les dépendances sont installées.")
    except ImportError:
        print("Dépendances manquantes. Installation...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])


def generation_de_la_cle(algo, longeur):
    if algo == "AES":
        return secrets.token_bytes(longeur // 8)

    elif algo == "PBKDF2":
        mot_de_passe = getpass("Mot de passe maître : ").encode()
        salt = os.urandom(16)
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            longeur=longeur // 8,
            salt=salt,
            iterations=390000,
        )
        return kdf.derive(mot_de_passe)

    else:
        raise ValueError("Algorithme non supporté.")


def sauvegarde_de_la_cle(clé):
    os.makedirs(KEY_DIR, exist_ok=True)

    filename = f"cle_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    path = os.path.join(KEY_DIR, filename)

    with open(path, "w") as f:
        json.dump({"cle": base64.b64encode(clé).decode()}, f)

    os.chmod(path, 0o600)
    print(f"✓ Clé sauvegardée : {path}")
    return path


def envoie_sftp(local_path):
    host = input("Host : ")
    username = input("Username : ")
    mot_de_passe = input("Password : ")
    remote_path = input("Remote path : ")

    try:
        transport = paramiko.Transport((host, 22))
        transport.connect(username=username, password=mot_de_passe)
        sftp = paramiko.SFTPClient.from_transport(transport)

        sftp.put(local_path, remote_path)
        sftp.close()
        transport.close()
        print("✓ Transfert réussi.")
    except Exception as e:
        print(f"Erreur SFTP : {e}")


def encryption_du_fichier(filepath, clé):

    with open(filepath, "rb") as f:
        data = f.read()

    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(clé), modes.CBC(iv))
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    with open(filepath, "wb") as f:
        f.write(iv + encrypted)


def selection_du_fichier():
    print("[1] Fichier unique")
    print("[2] Dossier complet")
    choice = input("Choix : ")

    if choice == "1":
        return [input("Chemin fichier : ")]

    elif choice == "2":
        folder = input("Chemin dossier : ")
        files = []
        for root, _, filenames in os.walk(folder):
            for file in filenames:
                files.append(os.path.join(root, file))
        return files

    return []


def main():
    verification_dependance()

    while True:
        print("""
==============================
Système de Chiffrement - TP3
==============================
1. Générer une clé
2. Envoyer une clé via SFTP
3. Chiffrer fichiers (LAB ONLY)
4. Déchiffrement du fichier
5. Vérifier dépendances
6. Quitter
""")

        choice = input("Choix : ")

        if choice == "1":
            algo = input("Algorithme (AES/PBKDF2) : ")
            longeur = int(input("Longueur (128/192/256) : "))
            cle = generation_de_la_cle(algo, longeur)
            sauvegarde_de_la_cle(cle)

        elif choice == "2":
            path = input("Chemin clé locale : ")
            envoie_sftp(path)

        elif choice == "3":
            key_path = input("Chemin clé : ")
            with open(key_path) as f:
                cle = base64.b64decode(json.load(f)["cle"])

            files = selection_du_fichier()

            print(f"Chiffrement de {len(files)} fichiers...")
            for file in tqdm(files):
                encryption_du_fichier(file, cle)

            print("✓ Terminé.")

        elif choice == "4":
            key_path = input("Chemin clé : ")
            with open(key_path) as f:
                cle = base64.b64decode(json.load(f)["cle"])

            files = selection_du_fichier()

            print(f"Chiffrement de {len(files)} fichiers...")
            for file in tqdm(files):
                dechiffrement_du_fichier(file, cle)

            print("✓ Terminé.")

        elif choice == "5":
            verification_dependance()

        elif choice == "6":
            break

        else:
            print("Choix invalide.")

def dechiffrement_du_fichier(filepath, cle):
    with open(filepath, "rb") as f:
        data = f.read()

    iv = data[:16]
    encrypted_data = data[16:]

    cipher = Cipher(algorithms.AES(cle), modes.CBC(iv))
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

    with open(filepath, "wb") as f:
        f.write(decrypted)

if __name__ == "__main__":
    main()