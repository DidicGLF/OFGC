import flet as ft
from database import Database
from datetime import datetime
from date_picker_custom import create_custom_date_picker


class InterventionsView(ft.Container):
    def __init__(self, page: ft.Page, db: Database, filter_client_id=None, filter_client_name=None):
        super().__init__()
        self.page = page
        self.db = db
        self.expand = True
        self.bgcolor = ft.Colors.with_opacity(0.95, "#0f172a")
        self.search_term = ""
        self.filter_paiement = "Toutes"
        self.filter_client_id = filter_client_id
        self.filter_client_name = filter_client_name
        
        self.build_view()
    
    def build_view(self):
        """Construit la vue des interventions"""
        header = ft.Container(
            padding=30,
            bgcolor=ft.Colors.with_opacity(0.8, "#0f172a"),
            content=ft.Row(
                controls=[
                    ft.Column(
                        controls=[
                            ft.Text("Gestion des Interventions", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                            ft.Container(
                                content=ft.Row(
                                    controls=[
                                        ft.Icon(ft.Icons.FILTER_ALT, size=16, color=ft.Colors.BLUE),
                                        ft.Text(f"Client: {self.filter_client_name}", size=14, color=ft.Colors.BLUE),
                                        ft.IconButton(
                                            icon=ft.Icons.CLOSE,
                                            icon_size=16,
                                            tooltip="Retirer le filtre",
                                            on_click=self.clear_client_filter,
                                        ),
                                    ],
                                    spacing=5,
                                ),
                                visible=self.filter_client_id is not None,
                            ),
                        ],
                        spacing=5,
                    ),
                    ft.ElevatedButton("➕ Nouvelle intervention", bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE, on_click=self.open_add_intervention_dialog),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
        
        self.filter_tabs = ft.Row(
            controls=[
                ft.TextButton("Toutes", on_click=lambda e: self.change_filter("Toutes")),
                ft.TextButton("Payé", on_click=lambda e: self.change_filter("Payé")),
                ft.TextButton("À payer", on_click=lambda e: self.change_filter("À payer")),
                ft.TextButton("Gratuit", on_click=lambda e: self.change_filter("Gratuit")),
            ],
            spacing=10,
        )
        
        filter_bar = ft.Container(padding=ft.padding.symmetric(horizontal=40, vertical=10), content=self.filter_tabs)
        
        self.search_field = ft.TextField(
            prefix_icon=ft.Icons.SEARCH,
            hint_text="Rechercher une intervention...",
            border_radius=12,
            filled=True,
            bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
            border_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
            color=ft.Colors.WHITE,
            on_change=self.on_search_change,
        )
        
        search_bar = ft.Container(padding=ft.padding.symmetric(horizontal=40, vertical=10), content=self.search_field)
        
        self.interventions_list = ft.Column(spacing=0)
        self.update_filter_tabs()
        self.load_interventions()
        
        interventions_table = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=0),
            content=ft.Container(
                bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
                border_radius=16,
                content=ft.Column(
                    controls=[
                        ft.Container(padding=20, content=ft.Text("Liste des interventions", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
                        ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                        ft.Column(controls=[self.interventions_list], scroll=ft.ScrollMode.AUTO, expand=True),
                    ],
                    spacing=0,
                    expand=True,
                ),
            ),
            expand=True,
        )
        
        main_content = ft.Column(controls=[header, filter_bar, search_bar, interventions_table], spacing=0, expand=True)
        self.content = main_content
    
    def change_filter(self, paiement):
        self.filter_paiement = paiement
        self.update_filter_tabs()
        self.load_interventions()
    
    def update_filter_tabs(self):
        for i, tab in enumerate(self.filter_tabs.controls):
            paiements = ["Toutes", "Payé", "À payer", "Gratuit"]
            if paiements[i] == self.filter_paiement:
                tab.style = ft.ButtonStyle(bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE)
            else:
                tab.style = ft.ButtonStyle(bgcolor=None, color=None)
    
    def load_interventions(self):
        self.interventions_list.controls.clear()
        
        if self.search_term:
            interventions = self.db.search_interventions(self.search_term)
        else:
            interventions = self.db.get_all_interventions()
        
        # Filtre par client si actif
        if self.filter_client_id:
            interventions = [i for i in interventions if i["client_id"] == self.filter_client_id]
        
        # Filtre par paiement
        if self.filter_paiement != "Toutes":
            interventions = [i for i in interventions if i["paiement"] == self.filter_paiement]
        
        if not interventions:
            self.interventions_list.controls.append(
                ft.Container(
                    padding=40,
                    content=ft.Text("Aucune intervention trouvée", size=16, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE), text_align=ft.TextAlign.CENTER),
                    alignment=ft.alignment.center,
                )
            )
        else:
            for intervention in interventions:
                self.interventions_list.controls.append(self.create_intervention_row(intervention))
        
        self.page.update()
    
    def clear_client_filter(self, e):
        """Retire le filtre client"""
        self.filter_client_id = None
        self.filter_client_name = None
        self.build_view()
        self.page.update()
    
    def format_date_display(self, date_str):
        """Convertit YYYY-MM-DD en JJ/MM/AAAA pour affichage"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except:
            return date_str
    
    def create_intervention_row(self, intervention):
        if intervention.get("effectuee"):
            badge_color, badge_bgcolor = ft.Colors.GREEN, ft.Colors.with_opacity(0.15, ft.Colors.GREEN)
            badge_text = "✅ Effectuée"
        else:
            badge_color, badge_bgcolor = ft.Colors.ORANGE, ft.Colors.with_opacity(0.15, ft.Colors.ORANGE)
            badge_text = "⏳ À venir"
        
        heures = ""
        if intervention.get("heure_debut") and intervention.get("heure_fin"):
            heures = f"{intervention['heure_debut']} - {intervention['heure_fin']}"
        
        date_display = self.format_date_display(intervention["date_intervention"])
        
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=25, vertical=20),
            content=ft.Row(
                controls=[
                    ft.Container(width=100, content=ft.Text(intervention["numero"], size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
                    ft.Container(width=180, content=ft.Column(controls=[ft.Text(intervention["client_nom"], size=14, color=ft.Colors.WHITE), ft.Text(heures, size=12, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE))], spacing=2)),
                    ft.Container(width=100, content=ft.Text(date_display, size=14, color=ft.Colors.WHITE)),
                    ft.Container(width=80, content=ft.Text(intervention.get("lieu", "-"), size=14, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE))),
                    ft.Container(width=120, content=ft.Container(padding=ft.padding.symmetric(horizontal=12, vertical=6), bgcolor=badge_bgcolor, border_radius=6, content=ft.Text(badge_text, size=12, weight=ft.FontWeight.W_600, color=badge_color))),
                    ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.Icons.VISIBILITY, icon_size=18, tooltip="Voir", on_click=lambda e, i=intervention: self.view_intervention(i)),
                            ft.IconButton(icon=ft.Icons.EDIT, icon_size=18, tooltip="Modifier", on_click=lambda e, i=intervention: self.open_edit_intervention_dialog(i)),
                            ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, tooltip="Supprimer", on_click=lambda e, i=intervention: self.delete_intervention(i)),
                        ],
                        spacing=8,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
    
    def on_search_change(self, e):
        self.search_term = e.control.value
        self.load_interventions()
    
    def open_add_intervention_dialog(self, e):
        clients = self.db.get_all_clients()
        if not clients:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Aucun client. Créez d'abord un client."), bgcolor=ft.Colors.RED)
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        client_options = [ft.dropdown.Option(key=str(c["id"]), text=c["nom_prenom"]) for c in clients]
        
        numero_field = ft.TextField(label="Numéro *", hint_text="Ex: INT-001")
        client_dropdown = ft.Dropdown(label="Client *", options=client_options, autofocus=True)
        
        # Date picker intégré (pas de dialog séparé)
        selected_date = [datetime.now()]  # Liste pour garder la référence
        date_field = ft.TextField(label="Date *", value=selected_date[0].strftime("%d/%m/%Y"), read_only=True)
        
        # Mini calendrier intégré
        calendar_visible = [False]
        
        def on_date_selected(date_obj):
            selected_date[0] = date_obj
            date_field.value = date_obj.strftime("%d/%m/%Y")
            calendar_container.visible = False
            check_time_conflict()  # Vérifier les conflits après changement de date
            self.page.update()
        
        def toggle_calendar(e):
            calendar_container.visible = not calendar_container.visible
            self.page.update()
        
        # Importer la fonction de calendrier
        from date_picker_custom import create_inline_calendar
        calendar_widget = create_inline_calendar(self.page, selected_date[0], on_date_selected)
        
        calendar_container = ft.Container(
            content=calendar_widget,
            visible=False,
            padding=10,
            bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
            border_radius=8,
        )
        
        date_button = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, tooltip="Choisir", on_click=toggle_calendar)
        
        # Option toute la journée
        all_day_checkbox = ft.Checkbox(label="Toute la journée (pas d'horaire précis)", value=False)
        
        heure_debut_field = ft.TextField(label="Heure début", value="09:00", width=100, hint_text="HH:MM")
        heure_fin_field = ft.TextField(label="Heure fin", value="10:00", width=100, hint_text="HH:MM")
        conflict_warning = ft.Text("", color=ft.Colors.ORANGE, size=12, visible=False)
        
        def on_all_day_change(e):
            """Désactive/active les champs horaires selon l'option toute la journée"""
            is_all_day = all_day_checkbox.value
            heure_debut_field.disabled = is_all_day
            heure_fin_field.disabled = is_all_day
            heure_debut_field.visible = not is_all_day
            heure_fin_field.visible = not is_all_day
            conflict_warning.visible = False
            if is_all_day:
                heure_debut_field.value = ""
                heure_fin_field.value = ""
            else:
                if not heure_debut_field.value:
                    heure_debut_field.value = "09:00"
                if not heure_fin_field.value:
                    heure_fin_field.value = "10:00"
            self.page.update()
        
        def check_time_conflict(e=None):
            """Vérifie s'il y a un conflit horaire"""
            if all_day_checkbox.value or not heure_debut_field.value or not heure_fin_field.value or not date_field.value:
                conflict_warning.visible = False
                self.page.update()
                return
            
            try:
                # Convertir la date
                date_obj = datetime.strptime(date_field.value, "%d/%m/%Y")
                date_iso = date_obj.strftime("%Y-%m-%d")
                
                # Récupérer toutes les interventions du même jour
                all_interventions = self.db.get_all_interventions()
                same_day = [i for i in all_interventions if i["date_intervention"] == date_iso]
                
                # Vérifier les conflits
                debut = heure_debut_field.value
                fin = heure_fin_field.value
                
                conflicts = []
                for interv in same_day:
                    if interv.get("heure_debut") and interv.get("heure_fin"):
                        # Vérifier le chevauchement
                        if not (fin <= interv["heure_debut"] or debut >= interv["heure_fin"]):
                            conflicts.append(f"{interv['numero']} ({interv['heure_debut']}-{interv['heure_fin']})")
                
                if conflicts:
                    conflict_warning.value = f"⚠️ Conflit avec: {', '.join(conflicts)}"
                    conflict_warning.visible = True
                else:
                    conflict_warning.visible = False
                
                self.page.update()
            except:
                conflict_warning.visible = False
                self.page.update()
        
        all_day_checkbox.on_change = on_all_day_change
        heure_debut_field.on_change = check_time_conflict
        heure_fin_field.on_change = check_time_conflict
        
        lieu_dropdown = ft.Dropdown(label="Lieu", options=[ft.dropdown.Option("Domicile"), ft.dropdown.Option("À distance")], value="Domicile")
        paiement_dropdown = ft.Dropdown(label="Paiement", options=[ft.dropdown.Option("Payé"), ft.dropdown.Option("À payer"), ft.dropdown.Option("Gratuit")], value="À payer")
        effectuee_checkbox = ft.Checkbox(label="Intervention effectuée", value=False)
        resume_field = ft.TextField(label="Résumé", multiline=True, min_lines=2)
        detail_field = ft.TextField(label="Détail", multiline=True, min_lines=3)
        
        def close_dialog(e):
            self.page.close(dialog)
        
        def save(e):
            # Générer le numéro automatiquement si vide
            if not numero_field.value:
                numero_field.value = self.db.get_next_numero()
            
            if not numero_field.value or not client_dropdown.value or not date_field.value:
                if not numero_field.value:
                    numero_field.error_text = "Numéro obligatoire"
                if not client_dropdown.value:
                    client_dropdown.error_text = "Client obligatoire"
                if not date_field.value:
                    date_field.error_text = "Date obligatoire"
                self.page.update()
                return
            
            # Vérifier que le numéro n'existe pas déjà
            all_interventions = self.db.get_all_interventions()
            if any(i["numero"] == numero_field.value for i in all_interventions):
                numero_field.error_text = "Ce numéro existe déjà"
                self.page.update()
                return
            
            try:
                date_obj = datetime.strptime(date_field.value, "%d/%m/%Y")
                date_iso = date_obj.strftime("%Y-%m-%d")
            except:
                date_field.error_text = "Date invalide"
                self.page.update()
                return
            
            self.db.add_intervention(
                numero=numero_field.value,
                client_id=int(client_dropdown.value),
                date_intervention=date_iso,
                heure_debut=heure_debut_field.value or "",
                heure_fin=heure_fin_field.value or "",
                lieu=lieu_dropdown.value,
                paiement=paiement_dropdown.value,
                effectuee=1 if effectuee_checkbox.value else 0,
                resume=resume_field.value or "",
                detail=detail_field.value or "",
            )
            
            self.page.close(dialog)
            self.load_interventions()
            
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Intervention ajoutée ✅"), bgcolor=ft.Colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nouvelle intervention"),
            content=ft.Container(
                width=600,
                padding=ft.padding.only(top=20, bottom=10, left=20, right=20),
                content=ft.Column(
                    controls=[
                        numero_field,
                        client_dropdown,
                        ft.Row([date_field, date_button], spacing=5),
                        calendar_container,  # Calendrier intégré
                        all_day_checkbox,
                        ft.Row([heure_debut_field, heure_fin_field], spacing=15),
                        conflict_warning,
                        lieu_dropdown,
                        paiement_dropdown,
                        effectuee_checkbox,
                        resume_field,
                        detail_field,
                    ],
                    spacing=25,
                    scroll=ft.ScrollMode.AUTO,
                    height=550,
                ),
            ),
            actions=[ft.TextButton("Annuler", on_click=close_dialog), ft.ElevatedButton("Enregistrer", on_click=save)],
        )
        
        self.page.open(dialog)
    
    def open_edit_intervention_dialog(self, intervention):
        clients = self.db.get_all_clients()
        client_options = [ft.dropdown.Option(key=str(c["id"]), text=c["nom_prenom"]) for c in clients]
        
        numero_field = ft.TextField(label="Numéro *", value=intervention["numero"])
        client_dropdown = ft.Dropdown(label="Client *", options=client_options, value=str(intervention["client_id"]))
        
        date_display = self.format_date_display(intervention["date_intervention"])
        date_field = ft.TextField(label="Date *", value=date_display, read_only=True)
        
        try:
            current_date = datetime.strptime(intervention["date_intervention"], "%Y-%m-%d")
        except:
            current_date = datetime.now()
        
        def on_date_selected(date_obj):
            date_field.value = date_obj.strftime("%d/%m/%Y")
            self.page.update()
        
        def pick_date(e):
            picker = create_custom_date_picker(self.page, current_date, on_date_selected)
            self.page.open(picker)
        
        date_button = ft.IconButton(icon=ft.Icons.CALENDAR_MONTH, tooltip="Choisir", on_click=pick_date)
        
        # Option toute la journée (cochée si pas d'horaires)
        is_all_day = not intervention.get("heure_debut") and not intervention.get("heure_fin")
        all_day_checkbox = ft.Checkbox(label="Toute la journée (pas d'horaire précis)", value=is_all_day)
        
        heure_debut_field = ft.TextField(label="Heure début", value=intervention.get("heure_debut", ""), width=100, hint_text="HH:MM", disabled=is_all_day, visible=not is_all_day)
        heure_fin_field = ft.TextField(label="Heure fin", value=intervention.get("heure_fin", ""), width=100, hint_text="HH:MM", disabled=is_all_day, visible=not is_all_day)
        conflict_warning = ft.Text("", color=ft.Colors.ORANGE, size=12, visible=False)
        
        def on_all_day_change(e):
            is_all_day = all_day_checkbox.value
            heure_debut_field.disabled = is_all_day
            heure_fin_field.disabled = is_all_day
            heure_debut_field.visible = not is_all_day
            heure_fin_field.visible = not is_all_day
            conflict_warning.visible = False
            if is_all_day:
                heure_debut_field.value = ""
                heure_fin_field.value = ""
            self.page.update()
        
        def check_time_conflict(e=None):
            if all_day_checkbox.value or not heure_debut_field.value or not heure_fin_field.value or not date_field.value:
                conflict_warning.visible = False
                self.page.update()
                return
            
            try:
                date_obj = datetime.strptime(date_field.value, "%d/%m/%Y")
                date_iso = date_obj.strftime("%Y-%m-%d")
                
                all_interventions = self.db.get_all_interventions()
                # Exclure l'intervention en cours de modification
                same_day = [i for i in all_interventions if i["date_intervention"] == date_iso and i["id"] != intervention["id"]]
                
                debut = heure_debut_field.value
                fin = heure_fin_field.value
                
                conflicts = []
                for interv in same_day:
                    if interv.get("heure_debut") and interv.get("heure_fin"):
                        if not (fin <= interv["heure_debut"] or debut >= interv["heure_fin"]):
                            conflicts.append(f"{interv['numero']} ({interv['heure_debut']}-{interv['heure_fin']})")
                
                if conflicts:
                    conflict_warning.value = f"⚠️ Conflit avec: {', '.join(conflicts)}"
                    conflict_warning.visible = True
                else:
                    conflict_warning.visible = False
                
                self.page.update()
            except:
                conflict_warning.visible = False
                self.page.update()
        
        all_day_checkbox.on_change = on_all_day_change
        heure_debut_field.on_change = check_time_conflict
        heure_fin_field.on_change = check_time_conflict
        
        # Vérification initiale des conflits (pour mode édition)
        self.page.update()
        check_time_conflict()
        
        lieu_dropdown = ft.Dropdown(label="Lieu", options=[ft.dropdown.Option("Domicile"), ft.dropdown.Option("À distance")], value=intervention.get("lieu"))
        paiement_dropdown = ft.Dropdown(label="Paiement", options=[ft.dropdown.Option("Payé"), ft.dropdown.Option("À payer"), ft.dropdown.Option("Gratuit")], value=intervention["paiement"])
        effectuee_checkbox = ft.Checkbox(label="Intervention effectuée", value=bool(intervention.get("effectuee")))
        resume_field = ft.TextField(label="Résumé", multiline=True, min_lines=2, value=intervention.get("resume", ""))
        detail_field = ft.TextField(label="Détail", multiline=True, min_lines=3, value=intervention.get("detail", ""))
        
        def close_dialog(e):
            self.page.close(dialog)
        
        def save(e):
            # Vérifier que le numéro n'est pas déjà utilisé par une AUTRE intervention
            all_interventions = self.db.get_all_interventions()
            if any(i["numero"] == numero_field.value and i["id"] != intervention["id"] for i in all_interventions):
                numero_field.error_text = "Ce numéro existe déjà"
                self.page.update()
                return
            
            try:
                date_obj = datetime.strptime(date_field.value, "%d/%m/%Y")
                date_iso = date_obj.strftime("%Y-%m-%d")
            except:
                return
            
            self.db.update_intervention(
                intervention["id"],
                numero=numero_field.value,
                client_id=int(client_dropdown.value),
                date_intervention=date_iso,
                heure_debut=heure_debut_field.value or "",
                heure_fin=heure_fin_field.value or "",
                lieu=lieu_dropdown.value,
                paiement=paiement_dropdown.value,
                effectuee=1 if effectuee_checkbox.value else 0,
                resume=resume_field.value or "",
                detail=detail_field.value or "",
            )
            
            self.page.close(dialog)
            self.load_interventions()
            
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Intervention modifiée ✅"), bgcolor=ft.Colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Modifier l'intervention"),
            content=ft.Container(
                width=600,
                padding=ft.padding.only(top=20, bottom=10, left=20, right=20),
                content=ft.Column(
                    controls=[
                        numero_field,
                        client_dropdown,
                        ft.Row([date_field, date_button], spacing=5),
                        all_day_checkbox,
                        ft.Row([heure_debut_field, heure_fin_field], spacing=15),
                        conflict_warning,
                        lieu_dropdown,
                        paiement_dropdown,
                        effectuee_checkbox,
                        resume_field,
                        detail_field,
                    ],
                    spacing=25,
                    scroll=ft.ScrollMode.AUTO,
                    height=550,
                ),
            ),
            actions=[ft.TextButton("Annuler", on_click=close_dialog), ft.ElevatedButton("Enregistrer", on_click=save)],
        )
        
        self.page.open(dialog)
    
    def view_intervention(self, intervention):
        def close_dialog(e):
            self.page.close(dialog)
        
        heures = ""
        if intervention.get("heure_debut") and intervention.get("heure_fin"):
            heures = f"{intervention['heure_debut']} - {intervention['heure_fin']}"
        
        date_display = self.format_date_display(intervention["date_intervention"])
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Intervention {intervention['numero']}"),
            content=ft.Container(
                width=550,
                padding=ft.padding.all(10),
                content=ft.Column(
                    controls=[
                        ft.Text(f"Client: {intervention['client_nom']}", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Date: {date_display}", size=14),
                        ft.Text(f"Horaire: {heures if heures else '-'}", size=14),
                        ft.Text(f"Lieu: {intervention.get('lieu', '-')}", size=14),
                        ft.Text(f"Paiement: {intervention['paiement']}", size=14),
                        ft.Text(f"Statut: {'✅ Effectuée' if intervention.get('effectuee') else '⏳ À venir'}", size=14),
                        ft.Divider(),
                        ft.Text("Résumé:", weight=ft.FontWeight.BOLD),
                        ft.Text(intervention.get('resume', '-'), size=14),
                        ft.Text("Détail:", weight=ft.FontWeight.BOLD),
                        ft.Text(intervention.get('detail', '-'), size=14),
                    ],
                    spacing=10,
                    scroll=ft.ScrollMode.AUTO,
                    height=400,
                ),
            ),
            actions=[
                ft.TextButton("Fermer", on_click=close_dialog),
                ft.ElevatedButton(
                    "🗑️ Supprimer",
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: (close_dialog(e), self.delete_intervention(intervention)),
                ),
            ],
        )
        
        self.page.open(dialog)
    
    def delete_intervention(self, intervention):
        def close_dialog(e):
            self.page.close(dialog)
        
        def confirm_delete(e):
            self.db.delete_intervention(intervention["id"])
            self.page.close(dialog)
            self.load_interventions()
            
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Intervention supprimée ✅"), bgcolor=ft.Colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text("Confirmer la suppression"),
            content=ft.Text(f"Supprimer l'intervention '{intervention['numero']}' ?"),
            actions=[
                ft.TextButton("Annuler", on_click=close_dialog),
                ft.ElevatedButton("Supprimer", bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, on_click=confirm_delete),
            ],
        )
        
        self.page.open(dialog)
