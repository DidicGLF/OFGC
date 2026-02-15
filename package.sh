#!/bin/bash

# Script de packaging AVEC CONSOLE pour debug

echo "=================================================="
echo "   ClientPro - Packaging DEBUG (avec console)"
echo "=================================================="
echo ""

# Vérifier PyInstaller
if ! command -v pyinstaller &> /dev/null; then
    echo "❌ PyInstaller n'est pas installé"
    echo "Installation : pip install pyinstaller"
    exit 1
fi

echo "🧹 Nettoyage..."
rm -rf build/ dist/ *.spec 2>/dev/null

echo ""
echo "📦 Packaging en mode DEBUG (avec console)..."
echo ""

# SANS --windowed pour voir la console !
pyinstaller --onefile \
            --name ClientPro-Debug \
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

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Package DEBUG créé !"
    echo ""
    echo "📁 Emplacement : dist/ClientPro-Debug"
    echo ""
    echo "🧪 Lancement avec console pour voir les erreurs :"
    echo "   ./dist/ClientPro-Debug"
    echo ""
    echo "Une console s'ouvrira et affichera toutes les erreurs !"
    echo ""
else
    echo ""
    echo "❌ Erreur lors du packaging"
    exit 1
fi
