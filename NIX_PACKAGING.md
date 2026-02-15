# 📦 Packaging avec Nix/NixOS

## Problème avec flet build

Sur Nix, `flet` et `flet-cli` sont séparés, ce qui cause l'erreur :
```
ModuleNotFoundError: No module named 'flet_cli'
```

## ✅ Solutions recommandées

### Option 1 : PyInstaller (Recommandé pour Nix)

PyInstaller fonctionne mieux avec Nix et donne un contrôle total.

#### Installation

```bash
# Avec pip
pip install pyinstaller

# Ou avec nix-shell
nix-shell -p python3Packages.pyinstaller
```

#### Packaging simple

```bash
# Méthode automatique (script fourni)
./package.sh

# Ou manuellement
pyinstaller --onefile \
            --windowed \
            --name OrdiFacile \
            --add-data "views:views" \
            app.py
```

#### Résultat

```
dist/ClientPro  ← Exécutable standalone
```

### Option 2 : Installer flet-cli

Si vous voulez vraiment utiliser `flet build` :

```bash
# Avec pip
pip install flet-cli

# Puis
flet build linux
```

### Option 3 : Packaging Nix natif

Créer un derivation Nix pour une vraie intégration NixOS.

Créez `default.nix` :

```nix
{ pkgs ? import <nixpkgs> {} }:

pkgs.python3Packages.buildPythonApplication rec {
  pname = "ordifacile";
  version = "1.0.0";

  src = ./.;

  propagatedBuildInputs = with pkgs.python3Packages; [
    flet
  ];

  meta = with pkgs.lib; {
    description = "Application de gestion de clients et interventions";
    homepage = "https://github.com/votre-username/clientpro";
    license = licenses.mit;
  };
}
```

Puis :

```bash
nix-build
./result/bin/ordifacile
```

## 🎯 Recommandation

Pour **Nix/NixOS**, utilisez **PyInstaller** avec le script `package.sh` fourni :

1. Simple et rapide
2. Compatible avec toutes les distros Linux
3. Pas de dépendances Nix à gérer
4. Fichier unique facile à distribuer

## 📋 Checklist packaging sur Nix

```bash
# 1. Installer PyInstaller
pip install pyinstaller

# 2. Packager
./package.sh

# 3. Tester
./dist/OrdiFacile

# 4. Distribuer
tar -czf OrdiFacile-Linux-x64.tar.gz -C dist OrdiFacile
```

## 🐛 Dépannage Nix

**Erreur "flet_cli not found"**
```bash
pip install flet-cli
# ou
nix-shell -p python3Packages.flet-cli
```

**PyInstaller ne trouve pas les modules**
```bash
# Utiliser le fichier .spec fourni
pyinstaller ordifacile.spec
```

**Problème avec les dépendances système**
```bash
# Créer un shell.nix
nix-shell -p python3 python3Packages.pip python3Packages.pyinstaller
```

## 📦 Avantages PyInstaller sur Nix

- ✅ Fonctionne out-of-the-box
- ✅ Pas de conflit avec flet/flet-cli
- ✅ Exécutable portable (fonctionne sur Ubuntu, Debian, Fedora, etc.)
- ✅ Pas besoin de Nix sur la machine cible
- ✅ Contrôle total sur ce qui est inclus

## 🚀 Workflow complet sur Nix

```bash
# Développement
python start.py

# Packaging
./package.sh

# Test
./dist/OrdiFacile

# Distribution
tar -czf OrdiFacile-v1.0-linux-x64.tar.gz -C dist OrdiFacile

# Installation utilisateur final (aucune dépendance)
tar -xzf OrdiFacile-v1.0-linux-x64.tar.gz
./OrdiFacile
```

---

**Pour Nix/NixOS : utilisez PyInstaller, pas `flet build` !** 🎯
