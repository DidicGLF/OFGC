# ClientPro - Application de Gestion de Clients et d'Interventions

Application moderne de gestion de clients et d'interventions développée avec **Flet** et **SQLite**.

## 🚀 Fonctionnalités

### ✅ Implémentées
- **Tableau de bord** avec statistiques en temps réel
- **Gestion des clients** (CRUD complet)
  - Ajout, modification, suppression
  - Recherche par nom, email, téléphone, ville
  - Informations détaillées (contact, adresse, notes)
  - Types de clients (Particulier/Entreprise)
  
- **Gestion des interventions** (CRUD complet)
  - Création avec formulaire détaillé
  - Modification et suppression
  - Filtres par statut (Toutes, En cours, Planifié, Terminé, Urgent)
  - Recherche globale
  - Gestion des priorités et coûts
  
- **Base de données SQLite**
  - Structure optimisée avec relations
  - Données de démonstration incluses
  - Soft delete pour les clients

### 🔄 En développement
- Vue calendrier interactive
- Rapports et statistiques avancées
- Export de données
- Paramètres de l'application

## 📋 Prérequis

- Python 3.8 ou supérieur
- pip (gestionnaire de paquets Python)

## 🔧 Installation

1. **Cloner ou télécharger les fichiers**
   ```bash
   # Si vous avez Git
   git clone <votre-repo>
   cd clientpro
   ```

2. **Installer Flet**
   ```bash
   pip install flet
   ```

3. **Lancer l'application**
   ```bash
   python app.py
   ```

## 📁 Structure du projet

```
clientpro/
│
├── app.py                    # Point d'entrée de l'application
├── database.py               # Gestion de la base de données SQLite
├── clientpro.db             # Base de données (créée automatiquement)
│
└── views/                    # Vues de l'application
    ├── dashboard.py         # Tableau de bord
    ├── clients.py           # Gestion des clients
    ├── interventions.py     # Gestion des interventions
    └── calendar.py          # Vue calendrier (en développement)
```

## 💾 Base de données

L'application utilise **SQLite** avec la structure suivante :

### Table `clients`
- id (PRIMARY KEY)
- nom, email, telephone
- adresse, ville, code_postal
- type_client (Particulier/Entreprise)
- notes
- date_creation
- actif (soft delete)

### Table `interventions`
- id (PRIMARY KEY)
- client_id (FOREIGN KEY)
- titre, description, type_intervention
- date_intervention, heure_debut, heure_fin
- statut, priorite
- cout
- notes
- date_creation

## 🎨 Personnalisation

### Thème
Le thème sombre est défini dans `app.py`. Vous pouvez le modifier :

```python
self.page.theme = ft.Theme(
    color_scheme=ft.ColorScheme(
        primary=ft.colors.BLUE,        # Couleur principale
        secondary=ft.colors.BLUE_GREY_900,
        background=...,
        surface=...,
    )
)
```

### Données de démonstration
Les données de démonstration sont ajoutées automatiquement au premier lancement.
Pour les désactiver, commentez dans `database.py` :

```python
# self.add_demo_data()
```

## 🔑 Utilisation

### Tableau de bord
- Vue d'ensemble avec statistiques
- 5 dernières interventions
- Accès rapide aux actions

### Clients
- **Ajouter** : Cliquer sur "➕ Nouveau client"
- **Rechercher** : Taper dans la barre de recherche
- **Modifier** : Cliquer sur l'icône ✏️
- **Voir détails** : Cliquer sur l'icône 👁
- **Supprimer** : Cliquer sur l'icône 🗑️

### Interventions
- **Ajouter** : Cliquer sur "➕ Nouvelle intervention"
- **Filtrer** : Utiliser les onglets (Toutes, En cours, etc.)
- **Rechercher** : Taper dans la barre de recherche
- **Modifier/Supprimer** : Mêmes actions que pour les clients

## 🐛 Résolution de problèmes

### L'application ne démarre pas
```bash
# Vérifier que Flet est bien installé
pip install --upgrade flet

# Vérifier la version de Python
python --version  # Doit être >= 3.8
```

### Erreurs de base de données
```bash
# Supprimer la base de données et relancer
rm clientpro.db
python app.py
```

## 🚀 Améliorations futures

- [ ] Vue calendrier complète
- [ ] Export PDF/Excel
- [ ] Envoi d'emails aux clients
- [ ] Notifications de rappel
- [ ] Gestion des documents (factures, devis)
- [ ] Statistiques avancées
- [ ] Mode multi-utilisateurs
- [ ] Synchronisation cloud

## 📝 Notes

- La base de données SQLite est un fichier local (`clientpro.db`)
- Les suppressions de clients sont "soft" (le client reste en base mais est marqué comme inactif)
- L'application est conçue pour être utilisée sur desktop (adaptabilité mobile à venir)

## 🤝 Contribution

Cette application est un projet de départ. N'hésitez pas à :
- Ajouter de nouvelles fonctionnalités
- Améliorer l'interface
- Corriger des bugs
- Partager vos suggestions

## 📄 Licence

Projet libre d'utilisation et de modification.

---

**Développé avec ❤️ en Python + Flet**
