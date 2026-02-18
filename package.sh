#!/bin/bash

# Script de packaging avec PyInstaller
# Plus compatible que flet build, surtout avec Nix

echo "=================================================="
echo "   OrdiFacile - Packaging avec PyInstaller"
echo "=================================================="
echo ""

# Vérifier si PyInstaller est installé
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller n'est pas installé"
    echo ""
    echo "Installation :"
    echo "  pip install pyinstaller"
    echo ""
    exit 1
fi

echo "🧹 Nettoyage des anciens builds..."
rm -rf build/ dist/ 2>/dev/null

echo ""
echo "📦 Création du package..."
echo ""

# Option 1 : Commande simple (un seul fichier)
pyinstaller --onefile \
            --windowed \
            --name OrdiFacile \
            --add-data "views:views" \
            --add-data "database.py:." \
            --hidden-import views.dashboard \
            --hidden-import views.clients \
            --hidden-import views.interventions \
            --hidden-import views.calendar \
            --hidden-import views.reports \
            --hidden-import flet \
            --hidden-import sqlite3 \
            --exclude-module matplotlib \
            --exclude-module numpy \
            --exclude-module pandas \
            app.py

# Option 2 : Avec le fichier .spec (décommentez si vous préférez)
# pyinstaller ordifacile.spec

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Package créé avec succès !"
    echo ""
    echo "📁 Emplacement : dist/OrdiFacile"
    echo ""
    echo "🧪 Test de l'exécutable :"
    echo "   ./dist/OrdiFacile"
    echo ""
    echo "📤 Distribution :"
    echo "   tar -czf OrdiFacile-Linux-x64.tar.gz -C dist OrdiFacile"
    echo ""
else
    echo ""
    echo "❌ Erreur lors du packaging"
    echo ""
    exit 1
fi
