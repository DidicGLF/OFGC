import flet as ft
from database import Database
from datetime import datetime


class InterventionsView(ft.Container):
    def __init__(self, page: ft.Page, db: Database):
        super().__init__()
        self.page = page
        self.db = db
        self.expand = True
        self.bgcolor = ft.colors.with_opacity(0.95, "#0f172a")
        self.search_term = ""
        self.filter_status = "Toutes"
        
        self.build_view()
    
    def build_view(self):
        """Construit la vue des interventions"""
        # Header
        header = ft.Container(
            padding=30,
            bgcolor=ft.colors.with_opacity(0.8, "#0f172a"),
            content=ft.Row(
                controls=[
                    ft.Text(
                        "Gestion des Interventions",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                    ),
                    ft.ElevatedButton(
                        "➕ Nouvelle intervention",
                        style=ft.ButtonStyle(
                            bgcolor=ft.colors.BLUE,
                            color=ft.colors.WHITE,
                        ),
                        on_click=self.open_add_intervention_dialog,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
        
        # Barre de recherche
        self.search_field = ft.TextField(
            prefix_icon=ft.icons.SEARCH,
            hint_text="Rechercher une intervention...",
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
        
        # Filtres
        self.filter_tabs = ft.Row(
            controls=[
                ft.TextButton("Toutes", on_click=lambda e: self.set_filter("Toutes")),
                ft.TextButton("En cours", on_click=lambda e: self.set_filter("En cours")),
                ft.TextButton("Planifié", on_click=lambda e: self.set_filter("Planifié")),
                ft.TextButton("Terminé", on_click=lambda e: self.set_filter("Terminé")),
                ft.TextButton("Urgent", on_click=lambda e: self.set_filter("Urgent")),
            ],
            spacing=10,
        )
        
        # Liste des interventions
        self.interventions_list = ft.Column(spacing=0)
        self.load_interventions()
        
        interventions_table = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=0),
            content=ft.Container(
                bgcolor=ft.colors.with_opacity(0.95, "#1e293b"),
                border_radius=16,
                content=ft.Column(
                    controls=[
                        # En-tête
                        ft.Container(
                            padding=20,
                            content=ft.Row(
                                controls=[
                                    ft.Text(
                                        "Liste des interventions",
                                        size=18,
                                        weight=ft.FontWeight.W_600,
                                        color=ft.colors.WHITE,
                                    ),
                                    self.filter_tabs,
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ),
                        ft.Divider(height=1, color=ft.colors.with_opacity(0.1, ft.colors.WHITE)),
                        # Tableau
                        ft.Column(
                            controls=[self.interventions_list],
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
                interventions_table,
            ],
            spacing=0,
            expand=True,
        )
        
        self.content = main_content
        self.update_filter_tabs()
    
    def load_interventions(self):
        """Charge la liste des interventions"""
        self.interventions_list.controls.clear()
        
        # Récupérer les interventions
        if self.search_term:
            interventions = self.db.search_interventions(self.search_term)
        else:
            interventions = self.db.get_all_interventions()
        
        # Appliquer le filtre de statut
        if self.filter_status != "Toutes":
            if self.filter_status == "Urgent":
                interventions = [i for i in interventions if i.get("priorite") == "Urgent"]
            else:
                interventions = [i for i in interventions if i.get("statut") == self.filter_status]
        
        if not interventions:
            self.interventions_list.controls.append(
                ft.Container(
                    padding=40,
                    content=ft.Text(
                        "Aucune intervention trouvée",
                        size=16,
                        color=ft.colors.with_opacity(0.6, ft.colors.WHITE),
                        text_align=ft.TextAlign.CENTER,
                    ),
                    alignment=ft.alignment.center,
                )
            )
        else:
            for intervention in interventions:
                self.interventions_list.controls.append(self.create_intervention_row(intervention))
        
        self.page.update()
    
    def create_intervention_row(self, intervention):
        """Crée une ligne d'intervention"""
        # Déterminer la couleur du badge selon le statut
        if intervention["statut"] == "Terminé":
            badge_color = ft.colors.GREEN
            badge_bgcolor = ft.colors.with_opacity(0.15, ft.colors.GREEN)
        elif intervention["statut"] == "En cours":
            badge_color = ft.colors.ORANGE
            badge_bgcolor = ft.colors.with_opacity(0.15, ft.colors.ORANGE)
        elif intervention.get("priorite") == "Urgent":
            badge_color = ft.colors.RED
            badge_bgcolor = ft.colors.with_opacity(0.15, ft.colors.RED)
        else:
            badge_color = ft.colors.BLUE
            badge_bgcolor = ft.colors.with_opacity(0.15, ft.colors.BLUE)
        
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=25, vertical=20),
            content=ft.Row(
                controls=[
                    # Client
                    ft.Container(
                        width=220,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    intervention["client_nom"],
                                    size=14,
                                    weight=ft.FontWeight.W_600,
                                    color=ft.colors.WHITE,
                                ),
                                ft.Text(
                                    intervention.get("client_email", ""),
                                    size=13,
                                    color=ft.colors.with_opacity(0.6, ft.colors.WHITE),
                                ),
                            ],
                            spacing=2,
                        ),
                    ),
                    # Titre
                    ft.Container(
                        width=200,
                        content=ft.Column(
                            controls=[
                                ft.Text(
                                    intervention["titre"],
                                    size=14,
                                    weight=ft.FontWeight.W_500,
                                    color=ft.colors.WHITE,
                                ),
                                ft.Text(
                                    intervention.get("type_intervention", "-"),
                                    size=13,
                                    color=ft.colors.with_opacity(0.6, ft.colors.WHITE),
                                ),
                            ],
                            spacing=2,
                        ),
                    ),
                    # Date
                    ft.Container(
                        width=100,
                        content=ft.Text(
                            intervention["date_intervention"],
                            size=14,
                            color=ft.colors.WHITE,
                        ),
                    ),
                    # Statut
                    ft.Container(
                        width=100,
                        content=ft.Container(
                            padding=ft.padding.symmetric(horizontal=12, vertical=6),
                            bgcolor=badge_bgcolor,
                            border_radius=6,
                            content=ft.Text(
                                intervention["statut"],
                                size=12,
                                weight=ft.FontWeight.W_600,
                                color=badge_color,
                            ),
                        ),
                    ),
                    # Coût
                    ft.Container(
                        width=80,
                        content=ft.Text(
                            f"{intervention.get('cout', 0):.2f}€",
                            size=14,
                            color=ft.colors.WHITE,
                            weight=ft.FontWeight.W_600,
                        ),
                    ),
                    # Actions
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.VISIBILITY,
                                icon_size=18,
                                tooltip="Voir les détails",
                                on_click=lambda e, i=intervention: self.view_intervention(i),
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                icon_size=18,
                                tooltip="Modifier",
                                on_click=lambda e, i=intervention: self.open_edit_intervention_dialog(i),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_size=18,
                                tooltip="Supprimer",
                                on_click=lambda e, i=intervention: self.delete_intervention(i),
                            ),
                        ],
                        spacing=8,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
    
    def set_filter(self, status):
        """Définit le filtre de statut"""
        self.filter_status = status
        self.update_filter_tabs()
        self.load_interventions()
    
    def update_filter_tabs(self):
        """Met à jour l'apparence des onglets de filtre"""
        for i, tab in enumerate(self.filter_tabs.controls):
            statuses = ["Toutes", "En cours", "Planifié", "Terminé", "Urgent"]
            if statuses[i] == self.filter_status:
                tab.style = ft.ButtonStyle(bgcolor=ft.colors.BLUE)
            else:
                tab.style = ft.ButtonStyle(bgcolor=None)
    
    def on_search_change(self, e):
        """Gère le changement dans la barre de recherche"""
        self.search_term = e.control.value
        self.load_interventions()
    
    def open_add_intervention_dialog(self, e):
        """Ouvre le dialogue d'ajout d'intervention"""
        # Récupérer la liste des clients pour le dropdown
        clients = self.db.get_all_clients()
        client_options = [ft.dropdown.Option(key=str(c["id"]), text=c["nom"]) for c in clients]
        
        # Champs du formulaire
        client_dropdown = ft.Dropdown(
            label="Client *",
            options=client_options,
            autofocus=True,
        )
        titre_field = ft.TextField(label="Titre *")
        description_field = ft.TextField(label="Description", multiline=True, min_lines=2)
        type_dropdown = ft.Dropdown(
            label="Type d'intervention",
            options=[
                ft.dropdown.Option("Maintenance"),
                ft.dropdown.Option("Installation"),
                ft.dropdown.Option("Dépannage"),
                ft.dropdown.Option("Audit"),
                ft.dropdown.Option("Formation"),
                ft.dropdown.Option("Consultation"),
            ],
        )
        date_field = ft.TextField(
            label="Date *",
            hint_text="AAAA-MM-JJ",
            value=datetime.now().strftime("%Y-%m-%d"),
        )
        heure_debut_field = ft.TextField(label="Heure début", hint_text="HH:MM")
        heure_fin_field = ft.TextField(label="Heure fin", hint_text="HH:MM")
        statut_dropdown = ft.Dropdown(
            label="Statut",
            options=[
                ft.dropdown.Option("Planifié"),
                ft.dropdown.Option("En cours"),
                ft.dropdown.Option("Terminé"),
                ft.dropdown.Option("Annulé"),
            ],
            value="Planifié",
        )
        priorite_dropdown = ft.Dropdown(
            label="Priorité",
            options=[
                ft.dropdown.Option("Normal"),
                ft.dropdown.Option("Élevé"),
                ft.dropdown.Option("Urgent"),
            ],
            value="Normal",
        )
        cout_field = ft.TextField(label="Coût (€)", value="0", keyboard_type=ft.KeyboardType.NUMBER)
        notes_field = ft.TextField(label="Notes", multiline=True, min_lines=2)
        
        def save_intervention(e):
            if not client_dropdown.value or not titre_field.value or not date_field.value:
                if not client_dropdown.value:
                    client_dropdown.error_text = "Client obligatoire"
                if not titre_field.value:
                    titre_field.error_text = "Titre obligatoire"
                if not date_field.value:
                    date_field.error_text = "Date obligatoire"
                self.page.update()
                return
            
            # Ajouter l'intervention
            self.db.add_intervention(
                client_id=int(client_dropdown.value),
                titre=titre_field.value,
                description=description_field.value,
                type_intervention=type_dropdown.value or "",
                date_intervention=date_field.value,
                heure_debut=heure_debut_field.value,
                heure_fin=heure_fin_field.value,
                statut=statut_dropdown.value,
                priorite=priorite_dropdown.value,
                cout=float(cout_field.value) if cout_field.value else 0,
                notes=notes_field.value,
            )
            
            # Fermer le dialogue et recharger la liste
            dialog.open = False
            self.page.update()
            self.load_interventions()
            
            # Message de succès
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Intervention ajoutée avec succès ✅"),
                bgcolor=ft.colors.GREEN,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Nouvelle intervention"),
            content=ft.Container(
                width=550,
                content=ft.Column(
                    controls=[
                        client_dropdown,
                        titre_field,
                        type_dropdown,
                        description_field,
                        ft.Row([date_field, heure_debut_field, heure_fin_field], spacing=10),
                        ft.Row([statut_dropdown, priorite_dropdown], spacing=10),
                        cout_field,
                        notes_field,
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                    height=450,
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.ElevatedButton("Enregistrer", on_click=save_intervention),
            ],
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.dialog = dialog
        dialog.open = True
        self.page.update()
    
    def open_edit_intervention_dialog(self, intervention):
        """Ouvre le dialogue de modification d'intervention"""
        # Récupérer la liste des clients
        clients = self.db.get_all_clients()
        client_options = [ft.dropdown.Option(key=str(c["id"]), text=c["nom"]) for c in clients]
        
        # Pré-remplir les champs
        client_dropdown = ft.Dropdown(
            label="Client *",
            options=client_options,
            value=str(intervention["client_id"]),
        )
        titre_field = ft.TextField(label="Titre *", value=intervention["titre"])
        description_field = ft.TextField(
            label="Description",
            multiline=True,
            min_lines=2,
            value=intervention.get("description", "")
        )
        type_dropdown = ft.Dropdown(
            label="Type d'intervention",
            options=[
                ft.dropdown.Option("Maintenance"),
                ft.dropdown.Option("Installation"),
                ft.dropdown.Option("Dépannage"),
                ft.dropdown.Option("Audit"),
                ft.dropdown.Option("Formation"),
                ft.dropdown.Option("Consultation"),
            ],
            value=intervention.get("type_intervention"),
        )
        date_field = ft.TextField(
            label="Date *",
            value=intervention["date_intervention"]
        )
        heure_debut_field = ft.TextField(
            label="Heure début",
            value=intervention.get("heure_debut", "")
        )
        heure_fin_field = ft.TextField(
            label="Heure fin",
            value=intervention.get("heure_fin", "")
        )
        statut_dropdown = ft.Dropdown(
            label="Statut",
            options=[
                ft.dropdown.Option("Planifié"),
                ft.dropdown.Option("En cours"),
                ft.dropdown.Option("Terminé"),
                ft.dropdown.Option("Annulé"),
            ],
            value=intervention["statut"],
        )
        priorite_dropdown = ft.Dropdown(
            label="Priorité",
            options=[
                ft.dropdown.Option("Normal"),
                ft.dropdown.Option("Élevé"),
                ft.dropdown.Option("Urgent"),
            ],
            value=intervention.get("priorite", "Normal"),
        )
        cout_field = ft.TextField(
            label="Coût (€)",
            value=str(intervention.get("cout", 0)),
            keyboard_type=ft.KeyboardType.NUMBER
        )
        notes_field = ft.TextField(
            label="Notes",
            multiline=True,
            min_lines=2,
            value=intervention.get("notes", "")
        )
        
        def save_changes(e):
            if not client_dropdown.value or not titre_field.value or not date_field.value:
                self.page.update()
                return
            
            # Mettre à jour l'intervention
            self.db.update_intervention(
                intervention["id"],
                client_id=int(client_dropdown.value),
                titre=titre_field.value,
                description=description_field.value,
                type_intervention=type_dropdown.value or "",
                date_intervention=date_field.value,
                heure_debut=heure_debut_field.value,
                heure_fin=heure_fin_field.value,
                statut=statut_dropdown.value,
                priorite=priorite_dropdown.value,
                cout=float(cout_field.value) if cout_field.value else 0,
                notes=notes_field.value,
            )
            
            # Fermer et recharger
            dialog.open = False
            self.page.update()
            self.load_interventions()
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Intervention modifiée avec succès ✅"),
                bgcolor=ft.colors.GREEN,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Modifier l'intervention"),
            content=ft.Container(
                width=550,
                content=ft.Column(
                    controls=[
                        client_dropdown,
                        titre_field,
                        type_dropdown,
                        description_field,
                        ft.Row([date_field, heure_debut_field, heure_fin_field], spacing=10),
                        ft.Row([statut_dropdown, priorite_dropdown], spacing=10),
                        cout_field,
                        notes_field,
                    ],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                    height=450,
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
    
    def view_intervention(self, intervention):
        """Affiche les détails d'une intervention"""
        dialog = ft.AlertDialog(
            title=ft.Text(intervention["titre"]),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    controls=[
                        ft.Text(f"Client: {intervention['client_nom']}", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Email: {intervention.get('client_email', '-')}", size=14),
                        ft.Divider(),
                        ft.Text(f"Type: {intervention.get('type_intervention', '-')}", size=14),
                        ft.Text(f"Date: {intervention['date_intervention']}", size=14),
                        ft.Text(f"Horaire: {intervention.get('heure_debut', '-')} - {intervention.get('heure_fin', '-')}", size=14),
                        ft.Text(f"Statut: {intervention['statut']}", size=14),
                        ft.Text(f"Priorité: {intervention.get('priorite', 'Normal')}", size=14),
                        ft.Text(f"Coût: {intervention.get('cout', 0):.2f}€", size=14, weight=ft.FontWeight.BOLD),
                        ft.Divider(),
                        ft.Text("Description:", weight=ft.FontWeight.BOLD),
                        ft.Text(intervention.get('description', '-'), size=14),
                        ft.Text("Notes:", weight=ft.FontWeight.BOLD),
                        ft.Text(intervention.get('notes', '-'), size=14),
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
    
    def delete_intervention(self, intervention):
        """Supprime une intervention après confirmation"""
        def confirm_delete(e):
            self.db.delete_intervention(intervention["id"])
            dialog.open = False
            self.page.update()
            self.load_interventions()
            
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text("Intervention supprimée ✅"),
                bgcolor=ft.colors.GREEN,
            )
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            title=ft.Text("Confirmer la suppression"),
            content=ft.Text(f"Êtes-vous sûr de vouloir supprimer l'intervention '{intervention['titre']}' ?"),
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
