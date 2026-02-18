#!/bin/bash

echo "🧹 Nettoyage complet des builds..."

# Supprimer build et dist
rm -rf build/ dist/
echo "✅ build/ et dist/ supprimés"

# Supprimer les anciens .spec
if [ -f "clientpro.spec" ]; then
    rm -f clientpro.spec
    echo "✅ clientpro.spec supprimé"
fi

# Supprimer les caches Python
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.pyc" -delete 2>/dev/null
echo "✅ Caches Python nettoyés"

echo ""
echo "✨ Prêt pour un build propre !"
echo "   Lancez maintenant : ./package.sh"
