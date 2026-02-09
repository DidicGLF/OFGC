import flet as ft
from database import Database


class ClientsView(ft.Container):
    def __init__(self, page: ft.Page, db: Database):
        super().__init__()
        self.page = page
        self.db = db
        self.expand = True
        self.bgcolor = ft.colors.with_opacity(0.95, "#0f172a")
        self.search_term = ""
        
        self.build_view()
    
    def build_view(self):
        """Construit la vue des clients"""
        # Header
        header = ft.Container(
            padding=30,
            bgcolor=ft.colors.with_opacity(0.8, "#0f172a"),
            content=ft.Row(
                controls=[
                    ft.Text(
                        "Gestion des Clients",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                    ),
                    ft.ElevatedButton(
                        "➕ Nouveau client",
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE,
                            color=ft.colors.WHITE,
                        ),
                        on_click=self.open_add_client_dialog,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
        
        # Barre de recherche
        self.search_field = ft.TextField(
            prefix_icon=ft.icons.SEARCH,
            hint_text="Rechercher par nom, email, téléphone ou ville...",
            border_radius=12,
            filled=True,
            bgcolor=ft.colors.with_opacity(0.95, "#1e293b"),
            border_color=ft.colors.with_opacity(0.2, ft.colors.WHITE),
            color=ft.colors.WHITE,
            on_change=self.on_search_change,
        )
        
        search_bar = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=20),
            content=self.search_field,
        )
        
        # Liste des clients (DataTable)
        self.clients_list = ft.Column(spacing=0)
        self.load_clients()
        
        clients_table = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=0),
            content=ft.Container(
                bgcolor=ft.colors.with_opacity(0.95, "#1e293b"),
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
                                color=ft.colors.WHITE,
                            ),
                        ),
                        ft.Divider(height=1, color=ft.colors.with_opacity(0.1, ft.colors.WHITE)),
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
                search_bar,
                clients_table,
            ],
            spacing=0,
            expand=True,
        )
        
        self.content = main_content
    
    def load_clients(self, search_term: str = ""):
        """Charge la liste des clients"""
        self.clients_list.controls.clear()
        
        # Récupérer les clients
        if search_term:
            clients = self.db.search_clients(search_term)
        else:
            clients = self.db.get_all_clients()
        
        if not clients:
            self.clients_list.controls.append(
                ft.Container(
                    padding=40,
                    content=ft.Text(
                        "Aucun client trouvé" if search_term else "Aucun client enregistré",
                        size=16,
                        color=ft.colors.with_opacity(0.6, ft.colors.WHITE),
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
                    # Nom et type
                    ft.Container(
                        width=280,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    client["nom"],
                                    size=15,
                                    weight=ft.FontWeight.W_600,
                                    color=ft.colors.WHITE,
                                ),
                                ft.Text(
                                    client.get("type_client", "Particulier"),
                                    size=13,
                                    color=ft.colors.BLUE,
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
                                    color=ft.colors.WHITE,
                                ),
                                ft.Text(
                                    client.get("telephone", "-"),
                                    size=13,
                                    color=ft.colors.with_opacity(0.6, ft.colors.WHITE),
                                ),
                            ],
                            spacing=2,
                        ),
                    ),
                    # Localisation
                    ft.Container(
                        width=200,
                        content=ft.Text(
                            f"{client.get('ville', '-')} {client.get('code_postal', '')}".strip(),
                            size=14,
                            color=ft.colors.WHITE,
                        ),
                    ),
                    # Actions
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.VISIBILITY,
                                icon_size=18,
                                tooltip="Voir les détails",
                                on_click=lambda e, c=client: self.view_client(c),
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                icon_size=18,
                                tooltip="Modifier",
                                on_click=lambda e, c=client: self.open_edit_client_dialog(c),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
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
        nom_field = ft.TextField(label="Nom *", autofocus=True)
        email_field = ft.TextField(label="Email")
        telephone_field = ft.TextField(label="Téléphone")
        adresse_field = ft.TextField(label="Adresse")
        ville_field = ft.TextField(label="Ville")
        code_postal_field = ft.TextField(label="Code postal")
        type_client_dropdown = ft.Dropdown(
            label="Type de client",
            options=[
                ft.dropdown.Option("Particulier"),
                ft.dropdown.Option("Entreprise"),
            ],
            value="Particulier",
        )
        notes_field = ft.TextField(label="Notes", multiline=True, min_lines=3)
        
        def save_client(e):
            if not nom_field.value:
                nom_field.error_text = "Le nom est obligatoire"
                self.page.update()
                return
            
            # Ajouter le client
            self.db.add_client(
                nom=nom_field.value,
                email=email_field.value,
                telephone=telephone_field.value,
                adresse=adresse_field.value,
                ville=ville_field.value,
                code_postal=code_postal_field.value,
                type_client=type_client_dropdown.value,
                notes=notes_field.value,
            )
            
            # Fermer le dialogue et recharger la liste
            dialog.open = False
            self.page.update()
            self.load_clients()
            
            # Message de succès
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Client ajouté avec succès ✅"),
                bgcolor=ft.colors.GREEN,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Nouveau client"),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    controls=[
                        nom_field,
                        type_client_dropdown,
                        email_field,
                        telephone_field,
                        adresse_field,
                        ft.Row([ville_field, code_postal_field], spacing=10),
                        notes_field,
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                    height=400,
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Enregistrer", on_click=save_client),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def open_edit_client_dialog(self, client):
        """Ouvre le dialogue de modification de client"""
        # Pré-remplir les champs avec les données existantes
        nom_field = ft.TextField(label="Nom *", value=client["nom"], autofocus=True)
        email_field = ft.TextField(label="Email", value=client.get("email", ""))
        telephone_field = ft.TextField(label="Téléphone", value=client.get("telephone", ""))
        adresse_field = ft.TextField(label="Adresse", value=client.get("adresse", ""))
        ville_field = ft.TextField(label="Ville", value=client.get("ville", ""))
        code_postal_field = ft.TextField(label="Code postal", value=client.get("code_postal", ""))
        type_client_dropdown = ft.Dropdown(
            label="Type de client",
            options=[
                ft.dropdown.Option("Particulier"),
                ft.dropdown.Option("Entreprise"),
            ],
            value=client.get("type_client", "Particulier"),
        )
        notes_field = ft.TextField(label="Notes", multiline=True, min_lines=3, value=client.get("notes", ""))
        
        def save_changes(e):
            if not nom_field.value:
                nom_field.error_text = "Le nom est obligatoire"
                self.page.update()
                return
            
            # Mettre à jour le client
            self.db.update_client(
                client["id"],
                nom=nom_field.value,
                email=email_field.value,
                telephone=telephone_field.value,
                adresse=adresse_field.value,
                ville=ville_field.value,
                code_postal=code_postal_field.value,
                type_client=type_client_dropdown.value,
                notes=notes_field.value,
            )
            
            # Fermer le dialogue et recharger la liste
            dialog.open = False
            self.page.update()
            self.load_clients(self.search_term)
            
            # Message de succès
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Client modifié avec succès ✅"),
                bgcolor=ft.colors.GREEN,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Modifier le client"),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    controls=[
                        nom_field,
                        type_client_dropdown,
                        email_field,
                        telephone_field,
                        adresse_field,
                        ft.Row([ville_field, code_postal_field], spacing=10),
                        notes_field,
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                    height=400,
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Enregistrer", on_click=save_changes),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def view_client(self, client):
        """Affiche les détails d'un client"""
        interventions = self.db.get_interventions_by_client(client["id"])
        
        dialog = ft.AlertDialog(
            title=ft.Text(client["nom"]),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    controls=[
                        ft.Text(f"Type: {client.get('type_client', 'Particulier')}", size=14),
                        ft.Divider(),
                        ft.Text("Contact", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Email: {client.get('email', '-')}", size=14),
                        ft.Text(f"Téléphone: {client.get('telephone', '-')}", size=14),
                        ft.Divider(),
                        ft.Text("Adresse", weight=ft.FontWeight.BOLD),
                        ft.Text(f"{client.get('adresse', '-')}", size=14),
                        ft.Text(f"{client.get('ville', '-')} {client.get('code_postal', '')}", size=14),
                        ft.Divider(),
                        ft.Text(f"Interventions: {len(interventions)}", weight=ft.FontWeight.BOLD),
                        ft.Text(f"Notes: {client.get('notes', '-')}", size=14),
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                    height=400,
                ),
            ),
            actions=[
                ft.TextButton("Fermer", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
            ],
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def delete_client(self, client):
        """Supprime un client après confirmation"""
        def confirm_delete(e):
            self.db.delete_client(client["id"])
            dialog.open = False
            self.page.update()
            self.load_clients(self.search_term)
            
            # Message de succès
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Client supprimé ✅"),
                bgcolor=ft.colors.GREEN,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmer la suppression"),
            content=ft.Text(f"Êtes-vous sûr de vouloir supprimer le client '{client['nom']}' ?"),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton(
                    "Supprimer",
                    bgcolor=ft.colors.RED,
                    color=ft.colors.WHITE,
                    on_click=confirm_delete,
                ),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
