import flet as ft
from database import Database


class ClientsView(ft.Container):
    def __init__(self, page: ft.Page, db: Database, navigate_callback=None):
        super().__init__()
        self.page = page
        self.db = db
        self.navigate_callback = navigate_callback
        self.expand = True
        self.bgcolor = ft.Colors.with_opacity(0.95, "#0f172a")
        self.search_term = ""
        self.filter_statut = "Tous"
        
        self.build_view()
    
    def build_view(self):
        """Construit la vue des clients"""
        # Header
        header = ft.Container(
            padding=30,
            bgcolor=ft.Colors.with_opacity(0.8, "#0f172a"),
            content=ft.Row(
                controls=[
                    ft.Text(
                        "Gestion des Clients",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.Colors.WHITE,
                    ),
                    ft.ElevatedButton(
                        "➕ Nouveau client",
                        bgcolor=ft.Colors.BLUE,
                        color=ft.Colors.WHITE,
                        on_click=self.open_add_client_dialog,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
        
        # Boutons de filtre
        self.filter_tabs = ft.Row(
            controls=[
                ft.TextButton("Tous", on_click=lambda e: self.change_filter("Tous")),
                ft.TextButton("Particulier", on_click=lambda e: self.change_filter("Particulier")),
                ft.TextButton("Professionnel", on_click=lambda e: self.change_filter("Professionnel")),
            ],
            spacing=10,
        )
        
        filter_bar = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=10),
            content=self.filter_tabs,
        )
        
        # Barre de recherche
        self.search_field = ft.TextField(
            prefix_icon=ft.Icons.SEARCH,
            hint_text="Rechercher par nom, email, téléphone...",
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
            border_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            color=ft.Colors.WHITE,
            on_change=self.on_search_change,
        )
        
        search_bar = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=20),
            content=self.search_field,
        )
        
        # Liste des clients
        self.clients_list = ft.Column(spacing=0)
        self.load_clients()
        
        clients_table = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=0),
            content=ft.Container(
                bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
                border_radius=16,
                content=ft.Column(
                    controls=[
                        # En-tête
                        ft.Container(
                            padding=20,
                            content=ft.Text(
                                "Liste des clients",
                                size=18,
                                weight=ft.FontWeight.W_600,
                                color=ft.Colors.WHITE,
                            ),
                        ),
                        ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                        # Tableau
                        ft.Column(
                            controls=[self.clients_list],
                            scroll=ft.ScrollMode.AUTO,
                            expand=True,
                        ),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ),
            expand=True,
        )
        
        # Contenu principal
        main_content = ft.Column(
            controls=[
                header,
                filter_bar,
                search_bar,
                clients_table,
            ],
            spacing=0,
            expand=True,
        )
        
        self.update_filter_tabs()
        self.content = main_content
    
    def change_filter(self, statut):
        """Change le filtre de statut"""
        self.filter_statut = statut
        self.update_filter_tabs()
        self.load_clients(self.search_term)
    
    def update_filter_tabs(self):
        """Met à jour l'apparence des onglets de filtre"""
        for i, tab in enumerate(self.filter_tabs.controls):
            statuts = ["Tous", "Particulier", "Professionnel"]
            if statuts[i] == self.filter_statut:
                tab.style = ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
            else:
                tab.style = ft.ButtonStyle(bgcolor=None, color=None)
    
    def load_clients(self, search_term: str = ""):
        """Charge la liste des clients"""
        self.clients_list.controls.clear()
        
        # Récupérer les clients
        if search_term:
            clients = self.db.search_clients(search_term)
        else:
            clients = self.db.get_all_clients()
        
        # Appliquer le filtre de statut
        if self.filter_statut != "Tous":
            clients = [c for c in clients if c.get("statut") == self.filter_statut]
        
        if not clients:
            self.clients_list.controls.append(
                ft.Container(
                    padding=40,
                    content=ft.Text(
                        "Aucun client trouvé" if search_term else "Aucun client enregistré",
                        size=16,
                        color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.center,
                )
            )
        else:
            for client in clients:
                self.clients_list.controls.append(self.create_client_row(client))
        
        self.page.update()
    
    def create_client_row(self, client):
        """Crée une ligne de client"""
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=25, vertical=20),
            content=ft.Row(
                controls=[
                    # Nom et statut
                    ft.Container(
                        width=280,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    client["nom_prenom"],
                                    size=15,
                                    weight=ft.FontWeight.W_600,
                                    color=ft.Colors.WHITE,
                                ),
                                ft.Text(
                                    client.get("statut", "Particulier"),
                                    size=13,
                                    color=ft.Colors.ORANGE if client.get("statut") == "Professionnel" else ft.Colors.BLUE,
                                ),
                            ],
                            spacing=2,
                        ),
                    ),
                    # Contact
                    ft.Container(
                        width=250,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    client.get("email", "-"),
                                    size=14,
                                    color=ft.Colors.WHITE,
                                ),
                                # Téléphones avec icônes
                                ft.Column(
                                    controls=[
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.PHONE, size=14, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
                                                ft.Text(
                                                    client.get("telephone_fixe", ""),
                                                    size=13,
                                                    color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                                                ),
                                            ],
                                            spacing=5,
                                        ) if client.get("telephone_fixe") else ft.Container(height=0),
                                        ft.Row(
                                            controls=[
                                                ft.Icon(ft.Icons.SMARTPHONE, size=14, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
                                                ft.Text(
                                                    client.get("telephone_portable", ""),
                                                    size=13,
                                                    color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                                                ),
                                            ],
                                            spacing=5,
                                        ) if client.get("telephone_portable") else ft.Container(height=0),
                                    ],
                                    spacing=2,
                                ),
                            ],
                            spacing=4,
                        ),
                    ),
                    # Localisation
                    ft.Container(
                        width=250,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    client.get("adresse", "-"),
                                    size=14,
                                    color=ft.Colors.WHITE,
                                ),
                                ft.Text(
                                    f"{client.get('code_postal', '')} {client.get('ville', '')}".strip() or "-",
                                    size=13,
                                    color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                                ),
                            ],
                            spacing=2,
                        ),
                    ),
                    # Actions
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.Icons.VISIBILITY,
                                icon_size=18,
                                tooltip="Voir les détails",
                                on_click=lambda e, c=client: self.view_client(c),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.EDIT,
                                icon_size=18,
                                tooltip="Modifier",
                                on_click=lambda e, c=client: self.open_edit_client_dialog(c),
                            ),
                            ft.IconButton(
                                icon=ft.Icons.DELETE,
                                icon_size=18,
                                tooltip="Supprimer",
                                on_click=lambda e, c=client: self.delete_client(c),
                            ),
                        ],
                        spacing=8,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
    
    def on_search_change(self, e):
        """Gère le changement dans la barre de recherche"""
        self.search_term = e.control.value
        self.load_clients(self.search_term)
    
    def open_add_client_dialog(self, e):
        """Ouvre le dialogue d'ajout de client"""
        # Champs du formulaire
        nom_prenom_field = ft.TextField(label="Nom Prénom *", autofocus=True)
        adresse_field = ft.TextField(label="Adresse")
        code_postal_field = ft.TextField(label="Code postal", width=150)
        ville_field = ft.TextField(label="Ville", expand=True)
        telephone_fixe_field = ft.TextField(label="Téléphone fixe")
        telephone_portable_field = ft.TextField(label="Téléphone portable")
        email_field = ft.TextField(label="Email")
        statut_dropdown = ft.Dropdown(
            label="Statut",
            options=[
                ft.dropdown.Option("Particulier"),
                ft.dropdown.Option("Professionnel"),
            ],
            value="Particulier",
        )
        
        def close_dialog(e):
            self.page.close(dialog)
        
        def save_client(e):
            if not nom_prenom_field.value:
                nom_prenom_field.error_text = "Le nom prénom est obligatoire"
                self.page.update()
                return
            
            # Ajouter le client
            self.db.add_client(
                nom_prenom=nom_prenom_field.value,
                adresse=adresse_field.value or "",
                code_postal=code_postal_field.value or "",
                ville=ville_field.value or "",
                telephone_fixe=telephone_fixe_field.value or "",
                telephone_portable=telephone_portable_field.value or "",
                email=email_field.value or "",
                statut=statut_dropdown.value,
            )
            
            # Fermer le dialogue
            self.page.close(dialog)
            
            # Recharger la liste
            self.load_clients()
            
            # Message de succès
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Client ajouté avec succès ✅"),
                bgcolor=ft.Colors.GREEN,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nouveau client"),
            content=ft.Container(
                width=600,
                padding=ft.padding.only(top=20, bottom=10, left=10, right=10),
                content=ft.Column(
                    controls=[
                        nom_prenom_field,
                        statut_dropdown,
                        adresse_field,
                        ft.Row([code_postal_field, ville_field], spacing=15),
                        telephone_fixe_field,
                        telephone_portable_field,
                        email_field,
                    ],
                    spacing=25,
                    scroll=ft.ScrollMode.AUTO,
                    height=500,
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=close_dialog),
                ft.ElevatedButton("Enregistrer", on_click=save_client),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.open(dialog)
    
    def open_edit_client_dialog(self, client):
        """Ouvre le dialogue de modification de client"""
        # Pré-remplir les champs
        nom_prenom_field = ft.TextField(label="Nom Prénom *", value=client["nom_prenom"], autofocus=True)
        adresse_field = ft.TextField(label="Adresse", value=client.get("adresse", ""))
        code_postal_field = ft.TextField(label="Code postal", value=client.get("code_postal", ""), width=150)
        ville_field = ft.TextField(label="Ville", value=client.get("ville", ""), expand=True)
        telephone_fixe_field = ft.TextField(label="Téléphone fixe", value=client.get("telephone_fixe", ""))
        telephone_portable_field = ft.TextField(label="Téléphone portable", value=client.get("telephone_portable", ""))
        email_field = ft.TextField(label="Email", value=client.get("email", ""))
        statut_dropdown = ft.Dropdown(
            label="Statut",
            options=[
                ft.dropdown.Option("Particulier"),
                ft.dropdown.Option("Professionnel"),
            ],
            value=client.get("statut", "Particulier"),
        )
        
        def close_dialog(e):
            self.page.close(dialog)
        
        def save_changes(e):
            if not nom_prenom_field.value:
                nom_prenom_field.error_text = "Le nom prénom est obligatoire"
                self.page.update()
                return
            
            # Mettre à jour le client
            self.db.update_client(
                client["id"],
                nom_prenom=nom_prenom_field.value,
                adresse=adresse_field.value or "",
                code_postal=code_postal_field.value or "",
                ville=ville_field.value or "",
                telephone_fixe=telephone_fixe_field.value or "",
                telephone_portable=telephone_portable_field.value or "",
                email=email_field.value or "",
                statut=statut_dropdown.value,
            )
            
            # Fermer le dialogue
            self.page.close(dialog)
            
            # Recharger la liste
            self.load_clients(self.search_term)
            
            # Message de succès
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Client modifié avec succès ✅"),
                bgcolor=ft.Colors.GREEN,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Modifier le client"),
            content=ft.Container(
                width=600,
                padding=ft.padding.only(top=20, bottom=10, left=10, right=10),
                content=ft.Column(
                    controls=[
                        nom_prenom_field,
                        statut_dropdown,
                        adresse_field,
                        ft.Row([code_postal_field, ville_field], spacing=15),
                        telephone_fixe_field,
                        telephone_portable_field,
                        email_field,
                    ],
                    spacing=25,
                    scroll=ft.ScrollMode.AUTO,
                    height=500,
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=close_dialog),
                ft.ElevatedButton("Enregistrer", on_click=save_changes),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.open(dialog)
    
    def view_client(self, client):
        """Affiche les détails d'un client"""
        interventions = self.db.get_interventions_by_client(client["id"])
        
        def close_dialog(e):
            self.page.close(dialog)
        
        def view_interventions(e):
            close_dialog(e)
            # Naviguer vers la page interventions avec filtre sur ce client
            if self.navigate_callback:
                self.navigate_callback("interventions", filter_client_id=client["id"], filter_client_name=client["nom_prenom"])
            else:
                # Fallback si pas de callback
                self.page.snack_bar = ft.SnackBar(
                    content=ft.Text(f"Navigation vers interventions de {client['nom_prenom']}"),
                    bgcolor=ft.Colors.BLUE,
                )
                self.page.snack_bar.open = True
                self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(client["nom_prenom"], size=20, weight=ft.FontWeight.BOLD),
            content=ft.Container(
                width=550,
                padding=ft.padding.all(10),
                content=ft.Column(
                    controls=[
                        # Statut
                        ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            bgcolor=ft.Colors.ORANGE if client.get("statut") == "Professionnel" else ft.Colors.BLUE,
                            border_radius=6,
                            content=ft.Text(
                                client.get("statut", "Particulier"),
                                size=13,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.W_600,
                            ),
                        ),
                        
                        ft.Divider(height=20),
                        
                        # Contact
                        ft.Text("📧 Contact", weight=ft.FontWeight.BOLD, size=16),
                        ft.Text(f"Email: {client.get('email', '-')}", size=14),
                        ft.Row([
                            ft.Icon(ft.Icons.PHONE, size=16),
                            ft.Text(client.get('telephone_fixe', 'Non renseigné'), size=14),
                        ], spacing=5) if client.get('telephone_fixe') else ft.Container(height=0),
                        ft.Row([
                            ft.Icon(ft.Icons.SMARTPHONE, size=16),
                            ft.Text(client.get('telephone_portable', 'Non renseigné'), size=14),
                        ], spacing=5) if client.get('telephone_portable') else ft.Container(height=0),
                        
                        ft.Divider(height=20),
                        
                        # Adresse
                        ft.Text("📍 Adresse", weight=ft.FontWeight.BOLD, size=16),
                        ft.Text(client.get('adresse', '-'), size=14),
                        ft.Text(f"{client.get('code_postal', '')} {client.get('ville', '')}", size=14),
                        
                        ft.Divider(height=20),
                        
                        # Interventions
                        ft.Container(
                            padding=15,
                            bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.BLUE),
                            border_radius=8,
                            content=ft.Column(
                                controls=[
                                    ft.Row([
                                        ft.Icon(ft.Icons.ASSIGNMENT, color=ft.Colors.BLUE),
                                        ft.Text(
                                            f"Interventions: {len(interventions)}",
                                            weight=ft.FontWeight.BOLD,
                                            size=16,
                                        ),
                                    ], spacing=10),
                                    ft.ElevatedButton(
                                        "📋 Voir toutes les interventions",
                                        bgcolor=ft.Colors.BLUE,
                                        color=ft.Colors.WHITE,
                                        on_click=view_interventions,
                                    ) if len(interventions) > 0 else ft.Text(
                                        "Aucune intervention enregistrée",
                                        size=13,
                                        italic=True,
                                        color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                                    ),
                                ],
                                spacing=10,
                            ),
                        ),
                    ],
                    spacing=8,
                    scroll=ft.ScrollMode.AUTO,
                ),
            ),
            actions=[
                ft.TextButton("Fermer", on_click=close_dialog),
                ft.ElevatedButton("Modifier", on_click=lambda e: (close_dialog(e), self.open_edit_client_dialog(client))),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.open(dialog)
    
    def delete_client(self, client):
        """Supprime un client après confirmation"""
        def close_dialog(e):
            self.page.close(dialog)
        
        def confirm_delete(e):
            self.db.delete_client(client["id"])
            
            # Fermer le dialogue
            self.page.close(dialog)
            
            # Recharger la liste
            self.load_clients(self.search_term)
            
            # Message de succès
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Client supprimé ✅"),
                bgcolor=ft.Colors.GREEN,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmer la suppression"),
            content=ft.Text(f"Êtes-vous sûr de vouloir supprimer le client '{client['nom_prenom']}' ?"),
            actions=[
                ft.TextButton("Annuler", on_click=close_dialog),
                ft.ElevatedButton(
                    "Supprimer",
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    on_click=confirm_delete,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.open(dialog)
