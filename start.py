#!/usr/bin/env python3
"""
Script de démarrage automatique pour OrdiFacile

Ce script :
1. Nettoie automatiquement les anciens processus Flet/Flutter
2. Nettoie le cache Python
3. Lance l'application
4. Ferme proprement tout à la fin

Usage : python start.py
"""

import subprocess
import time
import sys
import os

def kill_processes():
    """Tue les anciens processus Flet/Flutter"""
    print("🧹 Nettoyage des anciens processus...")
    try:
        subprocess.run(['pkill', '-f', 'flet'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        subprocess.run(['pkill', '-f', 'flutter'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        time.sleep(2)
    except Exception as e:
        print(f"⚠️  Avertissement lors du nettoyage : {e}")

def clean_cache():
    """Nettoie le cache Python"""
    print("🗑️  Nettoyage du cache...")
    try:
        subprocess.run(['find', '.', '-type', 'd', '-name', '__pycache__', 
                       '-exec', 'rm', '-rf', '{}', '+'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
    except Exception as e:
        print(f"⚠️  Avertissement lors du nettoyage du cache : {e}")

def main():
    print("=" * 50)
    print("    OrdiFacile - Gestion Clients & Interventions")
    print("=" * 50)
    print()
    
    # Nettoyage
    kill_processes()
    clean_cache()
    
    print()
    print("🚀 Lancement de l'application...")
    print("   (Utilisez Ctrl+C pour quitter proprement)")
    print()
    
    try:
        # Lancer l'application
        subprocess.run(['python', 'app.py'])
    except KeyboardInterrupt:
        print("\n")
        print("👋 Fermeture en cours...")
        kill_processes()
        print("✅ Application fermée proprement")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Erreur : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
