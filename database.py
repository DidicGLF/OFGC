import sqlite3
import os
import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


def get_data_dir():
    """
    Retourne le dossier de données selon l'OS et le mode (dev ou packagé)
    """
    if getattr(sys, 'frozen', False):
        # Mode packagé
        if os.name == 'nt':  # Windows
            data_dir = Path(os.getenv('LOCALAPPDATA')) / 'OrdiFacile'
        elif sys.platform == 'darwin':  # macOS
            data_dir = Path.home() / 'Library' / 'Application Support' / 'OrdiFacile'
        else:  # Linux
            data_dir = Path.home() / '.local' / 'share' / 'OrdiFacile'
    else:
        # Mode développement
        data_dir = Path.cwd()
    
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


class Database:
    def __init__(self, db_name: str = "clientpro.db"):
        db_path = get_data_dir() / db_name
        self.db_name = str(db_path)
        print(f"📁 Base de données : {self.db_name}")
        self.init_database()
    
    def get_connection(self):
        """Crée une connexion à la base de données"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_database(self):
        """Initialise la base de données avec les tables nécessaires"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table Clients (structure simplifiée)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom_prenom TEXT NOT NULL,
                adresse TEXT,
                code_postal TEXT,
                ville TEXT,
                telephone_fixe TEXT,
                telephone_portable TEXT,
                email TEXT,
                statut TEXT DEFAULT 'Particulier',
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actif INTEGER DEFAULT 1
            )
        """)
        
        # Table Interventions (structure simplifiée)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT NOT NULL UNIQUE,
                client_id INTEGER NOT NULL,
                date_intervention DATE NOT NULL,
                heure_debut TEXT,
                heure_fin TEXT,
                lieu TEXT DEFAULT 'Domicile',
                paiement TEXT DEFAULT 'À payer',
                effectuee INTEGER DEFAULT 0,
                resume TEXT,
                detail TEXT,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id)
            )
        """)
        
        conn.commit()
        
        # Ajouter des données de démonstration si la base est vide
        cursor.execute("SELECT COUNT(*) FROM clients")
        if cursor.fetchone()[0] == 0:
            self.add_demo_data()
        
        conn.close()
    
    def add_demo_data(self):
        """Ajoute des données de démonstration"""
        demo_clients = [
            ("Martin Dupont", "15 rue du Commerce", "75001", "Paris", "01 23 45 67 89", "06 12 34 56 78", "martin.dupont@email.com", "Professionnel"),
            ("Sophie Dubois", "28 avenue des Lilas", "69001", "Lyon", "", "06 23 45 67 89", "sophie.d@email.com", "Particulier"),
            ("Jean Lefebvre", "5 place de la Mairie", "13001", "Marseille", "04 91 23 45 67", "06 34 56 78 90", "j.lefebvre@gmail.com", "Particulier"),
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for client in demo_clients:
            cursor.execute("""
                INSERT INTO clients (nom_prenom, adresse, code_postal, ville, telephone_fixe, telephone_portable, email, statut)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, client)
        
        # Interventions de démonstration
        demo_interventions = [
            ("INT-001", 1, "2026-02-09", "09:00", "12:00", "Domicile", "Payé", 1, "Installation réseau", "Installation et configuration du réseau Wi-Fi domestique"),
            ("INT-002", 2, "2026-02-12", "14:00", "16:00", "À distance", "À payer", 0, "Dépannage PC", "Résolution problème de démarrage Windows"),
            ("INT-003", 3, "2026-02-14", "10:00", "11:30", "Domicile", "Gratuit", 0, "Conseil informatique", "Conseils sur le choix d'un nouvel ordinateur"),
        ]
        
        for intervention in demo_interventions:
            cursor.execute("""
                INSERT INTO interventions (numero, client_id, date_intervention, heure_debut, heure_fin, lieu, paiement, effectuee, resume, detail)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, intervention)
        
        conn.commit()
        conn.close()
    
    # === CLIENTS ===
    
    def get_all_clients(self, actif_only: bool = True) -> List[Dict]:
        """Récupère tous les clients"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM clients"
        if actif_only:
            query += " WHERE actif = 1"
        query += " ORDER BY nom_prenom"
        
        cursor.execute(query)
        clients = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return clients
    
    def get_client_by_id(self, client_id: int) -> Optional[Dict]:
        """Récupère un client par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def add_client(self, nom_prenom: str, adresse: str = "", code_postal: str = "",
                   ville: str = "", telephone_fixe: str = "", telephone_portable: str = "",
                   email: str = "", statut: str = "Particulier") -> int:
        """Ajoute un nouveau client"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO clients (nom_prenom, adresse, code_postal, ville, telephone_fixe, telephone_portable, email, statut)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nom_prenom, adresse, code_postal, ville, telephone_fixe, telephone_portable, email, statut))
        
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return client_id
    
    def update_client(self, client_id: int, **kwargs) -> bool:
        """Met à jour un client"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        fields = []
        values = []
        for key, value in kwargs.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(client_id)
        query = f"UPDATE clients SET {', '.join(fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return True
    
    def delete_client(self, client_id: int, soft_delete: bool = True) -> bool:
        """Supprime un client (soft delete par défaut)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if soft_delete:
            cursor.execute("UPDATE clients SET actif = 0 WHERE id = ?", (client_id,))
        else:
            cursor.execute("DELETE FROM clients WHERE id = ?", (client_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def search_clients(self, search_term: str) -> List[Dict]:
        """Recherche des clients"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_pattern = f"%{search_term}%"
        cursor.execute("""
            SELECT * FROM clients 
            WHERE actif = 1 AND (
                nom_prenom LIKE ? OR 
                email LIKE ? OR 
                telephone_fixe LIKE ? OR
                telephone_portable LIKE ? OR
                ville LIKE ?
            )
            ORDER BY nom_prenom
        """, (search_pattern, search_pattern, search_pattern, search_pattern, search_pattern))
        
        clients = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return clients
    
    # === INTERVENTIONS ===
    
    def get_all_interventions(self) -> List[Dict]:
        """Récupère toutes les interventions avec les infos clients"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                i.*,
                c.nom_prenom as client_nom,
                c.email as client_email,
                c.telephone_portable as client_telephone
            FROM interventions i
            JOIN clients c ON i.client_id = c.id
            ORDER BY i.date_intervention DESC
        """)
        
        interventions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return interventions
    
    def get_intervention_by_id(self, intervention_id: int) -> Optional[Dict]:
        """Récupère une intervention par son ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                i.*,
                c.nom_prenom as client_nom,
                c.email as client_email
            FROM interventions i
            JOIN clients c ON i.client_id = c.id
            WHERE i.id = ?
        """, (intervention_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def get_interventions_by_client(self, client_id: int) -> List[Dict]:
        """Récupère toutes les interventions d'un client"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM interventions 
            WHERE client_id = ?
            ORDER BY date_intervention DESC
        """, (client_id,))
        
        interventions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return interventions
    
    def add_intervention(self, numero: str, client_id: int, date_intervention: str,
                        heure_debut: str = "", heure_fin: str = "",
                        lieu: str = "Domicile", paiement: str = "À payer",
                        effectuee: int = 0,
                        resume: str = "", detail: str = "") -> int:
        """Ajoute une nouvelle intervention"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interventions (numero, client_id, date_intervention, heure_debut, heure_fin, lieu, paiement, effectuee, resume, detail)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (numero, client_id, date_intervention, heure_debut, heure_fin, lieu, paiement, effectuee, resume, detail))
        
        intervention_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return intervention_id
    
    def update_intervention(self, intervention_id: int, **kwargs) -> bool:
        """Met à jour une intervention"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        fields = []
        values = []
        for key, value in kwargs.items():
            if key != 'id':
                fields.append(f"{key} = ?")
                values.append(value)
        
        if not fields:
            return False
        
        values.append(intervention_id)
        query = f"UPDATE interventions SET {', '.join(fields)} WHERE id = ?"
        
        cursor.execute(query, values)
        conn.commit()
        conn.close()
        return True
    
    def delete_intervention(self, intervention_id: int) -> bool:
        """Supprime une intervention"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM interventions WHERE id = ?", (intervention_id,))
        conn.commit()
        conn.close()
        return True
    
    def search_interventions(self, search_term: str) -> List[Dict]:
        """Recherche des interventions"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        search_pattern = f"%{search_term}%"
        cursor.execute("""
            SELECT 
                i.*,
                c.nom_prenom as client_nom,
                c.email as client_email
            FROM interventions i
            JOIN clients c ON i.client_id = c.id
            WHERE 
                i.numero LIKE ? OR 
                i.resume LIKE ? OR
                i.detail LIKE ? OR
                c.nom_prenom LIKE ?
            ORDER BY i.date_intervention DESC
        """, (search_pattern, search_pattern, search_pattern, search_pattern))
        
        interventions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return interventions
    
    def get_next_numero(self) -> str:
        """Génère le prochain numéro d'intervention"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT numero FROM interventions ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        conn.close()
        
        if row:
            # Extraire le numéro et incrémenter
            last_num = row['numero']
            if last_num.startswith('INT-'):
                num = int(last_num.split('-')[1]) + 1
                return f"INT-{num:03d}"
        
        return "INT-001"
    
    # === STATISTIQUES ===
    
    def get_stats(self) -> Dict:
        """Récupère les statistiques générales"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total clients actifs
        cursor.execute("SELECT COUNT(*) FROM clients WHERE actif = 1")
        total_clients = cursor.fetchone()[0]
        
        # Total interventions
        cursor.execute("SELECT COUNT(*) FROM interventions")
        total_interventions = cursor.fetchone()[0]
        
        # Interventions à payer
        cursor.execute("SELECT COUNT(*) FROM interventions WHERE paiement = 'À payer'")
        interventions_a_payer = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_clients": total_clients,
            "total_interventions": total_interventions,
            "interventions_a_payer": interventions_a_payer,
        }
