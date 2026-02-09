import sqlite3
from datetime import datetime
from typing import List, Dict, Optional


class Database:
    def __init__(self, db_name: str = "clientpro.db"):
        self.db_name = db_name
        self.init_database()
    
    def get_connection(self):
        """Crée une connexion à la base de données"""
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row  # Pour accéder aux colonnes par nom
        return conn
    
    def init_database(self):
        """Initialise la base de données avec les tables nécessaires"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Table Clients
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nom TEXT NOT NULL,
                email TEXT,
                telephone TEXT,
                adresse TEXT,
                ville TEXT,
                code_postal TEXT,
                type_client TEXT DEFAULT 'Particulier',
                notes TEXT,
                date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                actif INTEGER DEFAULT 1
            )
        """)
        
        # Table Interventions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS interventions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER NOT NULL,
                titre TEXT NOT NULL,
                description TEXT,
                type_intervention TEXT,
                date_intervention DATE NOT NULL,
                heure_debut TIME,
                heure_fin TIME,
                statut TEXT DEFAULT 'Planifié',
                priorite TEXT DEFAULT 'Normal',
                cout REAL DEFAULT 0,
                notes TEXT,
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
            ("Entreprise Martin SARL", "contact@martin-sarl.fr", "06 12 34 56 78", "15 rue du Commerce", "Paris", "75001", "Entreprise", "Client important"),
            ("Sophie Dubois", "sophie.d@email.com", "06 23 45 67 89", "28 avenue des Lilas", "Lyon", "69001", "Particulier", ""),
            ("Tech Solutions Inc", "admin@techsolutions.fr", "01 23 45 67 89", "10 boulevard Innovation", "Toulouse", "31000", "Entreprise", "Client VIP"),
            ("Jean Lefebvre", "j.lefebvre@gmail.com", "06 34 56 78 90", "5 place de la Mairie", "Marseille", "13001", "Particulier", ""),
            ("Cabinet Médical du Centre", "secretariat@cabinet-centre.fr", "04 56 78 90 12", "42 rue de la Santé", "Nice", "06000", "Entreprise", "Contrat annuel"),
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        for client in demo_clients:
            cursor.execute("""
                INSERT INTO clients (nom, email, telephone, adresse, ville, code_postal, type_client, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, client)
        
        # Interventions de démonstration
        demo_interventions = [
            (1, "Maintenance serveur", "Vérification et mise à jour du serveur principal", "Maintenance", "2026-02-09", "09:00", "12:00", "Terminé", "Normal", 350.00),
            (2, "Installation réseau", "Installation du réseau Wi-Fi et câblage", "Installation", "2026-02-08", "14:00", "17:00", "En cours", "Élevé", 450.00),
            (3, "Audit sécurité", "Audit complet de la sécurité informatique", "Audit", "2026-02-07", "10:00", "16:00", "En cours", "Élevé", 800.00),
            (4, "Dépannage PC", "Réparation ordinateur portable", "Dépannage", "2026-02-05", "15:00", "16:30", "Terminé", "Normal", 120.00),
            (5, "Mise à jour logiciel", "Mise à jour urgente du logiciel métier", "Mise à jour", "2026-02-04", "08:00", "10:00", "Urgent", "Urgent", 200.00),
        ]
        
        for intervention in demo_interventions:
            cursor.execute("""
                INSERT INTO interventions 
                (client_id, titre, description, type_intervention, date_intervention, 
                 heure_debut, heure_fin, statut, priorite, cout)
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
        query += " ORDER BY nom"
        
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
    
    def add_client(self, nom: str, email: str = "", telephone: str = "", 
                   adresse: str = "", ville: str = "", code_postal: str = "",
                   type_client: str = "Particulier", notes: str = "") -> int:
        """Ajoute un nouveau client"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO clients (nom, email, telephone, adresse, ville, code_postal, type_client, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nom, email, telephone, adresse, ville, code_postal, type_client, notes))
        
        client_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return client_id
    
    def update_client(self, client_id: int, **kwargs) -> bool:
        """Met à jour un client"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Construire la requête dynamiquement
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
                nom LIKE ? OR 
                email LIKE ? OR 
                telephone LIKE ? OR
                ville LIKE ?
            )
            ORDER BY nom
        """, (search_pattern, search_pattern, search_pattern, search_pattern))
        
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
                c.nom as client_nom,
                c.email as client_email,
                c.telephone as client_telephone
            FROM interventions i
            JOIN clients c ON i.client_id = c.id
            ORDER BY i.date_intervention DESC, i.heure_debut DESC
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
                c.nom as client_nom,
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
    
    def add_intervention(self, client_id: int, titre: str, description: str = "",
                        type_intervention: str = "", date_intervention: str = "",
                        heure_debut: str = "", heure_fin: str = "",
                        statut: str = "Planifié", priorite: str = "Normal",
                        cout: float = 0, notes: str = "") -> int:
        """Ajoute une nouvelle intervention"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO interventions 
            (client_id, titre, description, type_intervention, date_intervention,
             heure_debut, heure_fin, statut, priorite, cout, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (client_id, titre, description, type_intervention, date_intervention,
              heure_debut, heure_fin, statut, priorite, cout, notes))
        
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
                c.nom as client_nom,
                c.email as client_email
            FROM interventions i
            JOIN clients c ON i.client_id = c.id
            WHERE 
                i.titre LIKE ? OR 
                i.description LIKE ? OR
                i.type_intervention LIKE ? OR
                c.nom LIKE ?
            ORDER BY i.date_intervention DESC
        """, (search_pattern, search_pattern, search_pattern, search_pattern))
        
        interventions = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return interventions
    
    # === STATISTIQUES ===
    
    def get_stats(self) -> Dict:
        """Récupère les statistiques générales"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total clients actifs
        cursor.execute("SELECT COUNT(*) FROM clients WHERE actif = 1")
        total_clients = cursor.fetchone()[0]
        
        # Interventions actives (en cours ou planifiées)
        cursor.execute("""
            SELECT COUNT(*) FROM interventions 
            WHERE statut IN ('En cours', 'Planifié')
        """)
        interventions_actives = cursor.fetchone()[0]
        
        # Interventions en attente
        cursor.execute("""
            SELECT COUNT(*) FROM interventions 
            WHERE statut = 'Planifié'
        """)
        interventions_attente = cursor.fetchone()[0]
        
        # Interventions urgentes
        cursor.execute("""
            SELECT COUNT(*) FROM interventions 
            WHERE priorite = 'Urgent' AND statut != 'Terminé'
        """)
        interventions_urgentes = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            "total_clients": total_clients,
            "interventions_actives": interventions_actives,
            "interventions_attente": interventions_attente,
            "interventions_urgentes": interventions_urgentes,
        }
