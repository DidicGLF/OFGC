# 📦 Guide de Packaging - MISE À JOUR

## ⚠️ Problème connu : Calendrier et Rapports ne s'ouvrent pas

Si après packaging, les pages Calendrier et Rapports ne s'affichent pas, c'est parce que PyInstaller ne trouve pas automatiquement tous les modules `views/`.

## ✅ Solution

### Méthode 1 : Utiliser le script mis à jour

```bash
./package.sh
```

Le script a été mis à jour pour inclure tous les hidden imports.

### Méthode 2 : Commande manuelle complète

```bash
pyinstaller --onefile \
            --windowed \
            --name ClientPro \
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
```

### Méthode 3 : Utiliser le .spec

```bash
pyinstaller clientpro.spec
```

Le fichier .spec a aussi été mis à jour.

## 🔍 Vérification après packaging

Pour vérifier que tout est bien inclus :

```bash
# Lancer l'exécutable
./dist/ClientPro

# Tester CHAQUE page :
# ✅ Dashboard
# ✅ Clients
# ✅ Interventions
# ✅ Calendrier ← Doit s'afficher !
# ✅ Rapports ← Doit s'afficher !
```

## 🐛 Diagnostic si ça ne marche toujours pas

### 1. Vérifier les imports dans l'exécutable

Lancez l'exécutable depuis le terminal pour voir les erreurs :

```bash
./dist/ClientPro
```

Cherchez des erreurs comme :
```
ModuleNotFoundError: No module named 'views.calendar'
ModuleNotFoundError: No module named 'views.reports'
```

### 2. Vérifier la structure du package

```bash
# Extraire et inspecter (sur Linux)
7z x dist/ClientPro
# Cherchez si views/ est inclus
```

### 3. Mode debug

Utilisez `--debug all` pour plus d'infos :

```bash
pyinstaller --debug all \
            --onefile \
            --windowed \
            --name ClientPro \
            --add-data "views:views" \
            --hidden-import views.calendar \
            --hidden-import views.reports \
            app.py
```

## 📋 Checklist avant packaging

- [ ] Tous les fichiers views/ sont présents
  ```bash
  ls views/
  # __init__.py  calendar.py  clients.py  dashboard.py  interventions.py  reports.py
  ```

- [ ] Le fichier __init__.py existe dans views/
  ```bash
  touch views/__init__.py
  ```

- [ ] L'application fonctionne en mode dev
  ```bash
  python app.py
  # Tester TOUTES les pages
  ```

- [ ] PyInstaller est installé
  ```bash
  pip install pyinstaller
  ```

- [ ] Nettoyer les anciens builds
  ```bash
  rm -rf build/ dist/ *.spec
  ```

## 🎯 Commande recommandée finale

```bash
# 1. Nettoyer
rm -rf build/ dist/ __pycache__ views/__pycache__

# 2. Vérifier la structure
ls views/  # Doit montrer tous les .py

# 3. Packager avec tous les imports
pyinstaller --onefile \
            --windowed \
            --name ClientPro \
            --add-data "views:views" \
            --hidden-import views.dashboard \
            --hidden-import views.clients \
            --hidden-import views.interventions \
            --hidden-import views.calendar \
            --hidden-import views.reports \
            app.py

# 4. Tester
./dist/ClientPro
```

## 💡 Alternative : Mode --onedir

Si --onefile pose problème, utilisez --onedir :

```bash
pyinstaller --onedir \
            --windowed \
            --name ClientPro \
            --add-data "views:views" \
            --hidden-import views.calendar \
            --hidden-import views.reports \
            app.py

# L'exécutable sera dans dist/ClientPro/ClientPro
```

Avantage : Plus rapide au démarrage, debug plus facile.

## 📦 Distribution

Une fois que tout fonctionne :

```bash
# Créer une archive
tar -czf ClientPro-Linux-v1.0.tar.gz -C dist ClientPro

# Ou avec un installer (optionnel)
# Voir PACKAGING_GUIDE.md pour créer un .deb
```

---

**La clé : TOUJOURS inclure les hidden-imports pour chaque nouveau fichier views/ !**
