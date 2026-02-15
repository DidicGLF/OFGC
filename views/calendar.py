import flet as ft
from database import Database
from datetime import datetime, timedelta


class CalendarView(ft.Container):
    def __init__(self, page: ft.Page, db: Database):
        super().__init__()
        print("DEBUG: CalendarView __init__ called")
        self.page = page
        self.db = db
        self.expand = True
        self.bgcolor = ft.Colors.with_opacity(0.95, "#0f172a")
        
        self.current_date = datetime.now()
        self.start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        self.dragged_intervention = None
        
        print("DEBUG: About to call build_view")
        self.build_view()
        print("DEBUG: build_view completed")
    
    def build_view(self):
        """Construit la vue calendrier"""
        header = ft.Container(
            padding=30,
            bgcolor=ft.Colors.with_opacity(0.8, "#0f172a"),
            content=ft.Row(
                controls=[
                    ft.Text("Calendrier", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, tooltip="Semaine précédente", on_click=self.prev_week),
                            ft.Container(width=250, content=ft.Text(self.get_week_text(), size=18, color=ft.Colors.WHITE, weight=ft.FontWeight.W_500, text_align=ft.TextAlign.CENTER)),
                            ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, tooltip="Semaine suivante", on_click=self.next_week),
                            ft.ElevatedButton("Aujourd'hui", on_click=self.goto_today),
                        ],
                        spacing=5,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
        
        legend = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=10),
            content=ft.Row(
                controls=[
                    ft.Row([ft.Container(width=15, height=15, bgcolor=ft.Colors.GREEN, border_radius=3), ft.Text("✅ Effectuée", size=13)], spacing=5),
                    ft.Row([ft.Container(width=15, height=15, bgcolor=ft.Colors.ORANGE, border_radius=3), ft.Text("⏳ À venir", size=13)], spacing=5),
                    ft.Row([ft.Text("🏠", size=16), ft.Text("Domicile", size=13)], spacing=5),
                    ft.Row([ft.Text("💻", size=16), ft.Text("À distance", size=13)], spacing=5),
                    ft.Text("💡 Clic sur case vide = Créer | Appui long = Modifier", size=12, italic=True, color=ft.Colors.BLUE),
                ],
                spacing=20,
            ),
        )
        
        self.calendar_grid = ft.Container()
        self.build_calendar_grid()
        
        main_content = ft.Column(controls=[header, legend, self.calendar_grid], spacing=10, expand=True, scroll=ft.ScrollMode.AUTO)
        self.content = main_content
    
    def get_week_text(self):
        end_of_week = self.start_of_week + timedelta(days=6)
        return f"Semaine du {self.start_of_week.strftime('%d/%m')} au {end_of_week.strftime('%d/%m/%Y')}"
    
    def format_date_display(self, date_str):
        """Convertit YYYY-MM-DD en JJ/MM/AAAA pour affichage"""
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except:
            return date_str
    
    def prev_week(self, e):
        self.start_of_week -= timedelta(days=7)
        self.build_view()
        self.page.update()
    
    def next_week(self, e):
        self.start_of_week += timedelta(days=7)
        self.build_view()
        self.page.update()
    
    def goto_today(self, e):
        self.current_date = datetime.now()
        self.start_of_week = self.current_date - timedelta(days=self.current_date.weekday())
        self.build_view()
        self.page.update()
    
    def build_calendar_grid(self):
        interventions = self.get_week_interventions()
        
        days_header = ft.Row(
            controls=[ft.Container(width=60, content=ft.Text("", size=12))] + [
                ft.Container(
                    expand=True,
                    padding=10,
                    bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
                    border_radius=8,
                    content=ft.Column(
                        controls=[
                            ft.Text(self.get_day_name(i), size=14, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                            ft.Text((self.start_of_week + timedelta(days=i)).strftime("%d/%m"), size=12, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE), text_align=ft.TextAlign.CENTER),
                        ],
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        spacing=2,
                    ),
                )
                for i in range(7)
            ],
            spacing=5,
        )
        
        hours_grid = ft.Column(spacing=0)
        
        for hour in range(8, 20):
            hour_row = ft.Row(
                controls=[
                    ft.Container(width=60, padding=5, content=ft.Text(f"{hour:02d}:00", size=12, color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE))),
                ] + [self.create_hour_cell(i, hour, interventions) for i in range(7)],
                spacing=5,
            )
            hours_grid.controls.append(hour_row)
        
        self.calendar_grid.content = ft.Column(controls=[days_header, hours_grid], spacing=10)
        self.calendar_grid.padding = ft.padding.symmetric(horizontal=40, vertical=10)
    
    def get_day_name(self, day_index):
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        return days[day_index]
    
    def get_week_interventions(self):
        all_interventions = self.db.get_all_interventions()
        week_interventions = []
        
        for intervention in all_interventions:
            interv_date = datetime.strptime(intervention["date_intervention"], "%Y-%m-%d")
            if self.start_of_week <= interv_date < self.start_of_week + timedelta(days=7):
                week_interventions.append(intervention)
        
        return week_interventions
    
    def create_hour_cell(self, day_index, hour, interventions):
        current_day = self.start_of_week + timedelta(days=day_index)
        current_date_str = current_day.strftime("%Y-%m-%d")
        
        cell_interventions = []
        for intervention in interventions:
            if intervention["date_intervention"] == current_date_str:
                if intervention.get("heure_debut"):
                    start_hour = int(intervention["heure_debut"].split(":")[0])
                    if start_hour == hour:
                        cell_interventions.append(intervention)
        
        # Cellule vide - clic pour créer
        if not cell_interventions:
            return ft.Container(
                expand=True,
                height=60,
                bgcolor=ft.Colors.with_opacity(0.3, "#1e293b"),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                on_click=lambda e: self.create_intervention_at(current_date_str, hour),
                ink=True,
            )
        
        # Cellule avec interventions
        intervention_cards = []
        for intervention in cell_interventions:
            bg_color = ft.Colors.GREEN if intervention.get("effectuee") else ft.Colors.ORANGE
            icon = "🏠" if intervention.get("lieu") == "Domicile" else "💻"
            
            heure_debut = intervention.get("heure_debut", "")
            heure_fin = intervention.get("heure_fin", "")
            horaire_text = f"{heure_debut} - {heure_fin}" if heure_debut and heure_fin else ""
            
            card = ft.Container(
                padding=5,
                bgcolor=ft.Colors.with_opacity(0.9, bg_color),
                border_radius=6,
                content=ft.Column(
                    controls=[
                        ft.Row(controls=[ft.Text(icon, size=12), ft.Text(horaire_text, size=11, color=ft.Colors.WHITE, weight=ft.FontWeight.BOLD)], spacing=3),
                        ft.Text(intervention["client_nom"], size=12, color=ft.Colors.WHITE, weight=ft.FontWeight.W_600, overflow=ft.TextOverflow.ELLIPSIS),
                    ],
                    spacing=2,
                    tight=True,
                ),
                on_click=lambda e, i=intervention: self.view_intervention(i),
                on_long_press=lambda e, i=intervention: self.edit_intervention(i),
            )
            intervention_cards.append(card)
        
        return ft.Container(
            expand=True,
            padding=2,
            content=ft.Column(controls=intervention_cards, spacing=2, scroll=ft.ScrollMode.AUTO),
            bgcolor=ft.Colors.with_opacity(0.3, "#1e293b"),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
        )
    
    def create_intervention_at(self, date_str, hour):
        """Crée une intervention avec date et heure pré-remplies"""
        clients = self.db.get_all_clients()
        if not clients:
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Aucun client disponible. Créez d'abord un client."), bgcolor=ft.Colors.RED)
            self.page.snack_bar.open = True
            self.page.update()
            return
        
        client_options = [ft.dropdown.Option(key=str(c["id"]), text=c["nom_prenom"]) for c in clients]
        
        numero_field = ft.TextField(label="Numéro *", value=self.db.get_next_numero())
        client_dropdown = ft.Dropdown(label="Client *", options=client_options, autofocus=True)
        date_field = ft.TextField(label="Date *", value=date_str, read_only=True)
        heure_debut_field = ft.TextField(label="Heure début *", value=f"{hour:02d}:00")
        heure_fin_field = ft.TextField(label="Heure fin *", value=f"{hour+1:02d}:00")
        lieu_dropdown = ft.Dropdown(label="Lieu", options=[ft.dropdown.Option("Domicile"), ft.dropdown.Option("À distance")], value="Domicile")
        paiement_dropdown = ft.Dropdown(label="Paiement", options=[ft.dropdown.Option("Payé"), ft.dropdown.Option("À payer"), ft.dropdown.Option("Gratuit")], value="À payer")
        effectuee_checkbox = ft.Checkbox(label="Intervention effectuée", value=False)
        resume_field = ft.TextField(label="Résumé", multiline=True, min_lines=2)
        detail_field = ft.TextField(label="Détail", multiline=True, min_lines=2)
        
        def close_dialog(e):
            self.page.close(dialog)
        
        def save(e):
            if not numero_field.value or not client_dropdown.value:
                self.page.update()
                return
            
            self.db.add_intervention(
                numero=numero_field.value,
                client_id=int(client_dropdown.value),
                date_intervention=date_field.value,
                heure_debut=heure_debut_field.value or "",
                heure_fin=heure_fin_field.value or "",
                lieu=lieu_dropdown.value,
                paiement=paiement_dropdown.value,
                effectuee=1 if effectuee_checkbox.value else 0,
                resume=resume_field.value or "",
                detail=detail_field.value or "",
            )
            
            self.page.close(dialog)
            self.build_view()
            self.page.update()
            
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Intervention créée ✅"), bgcolor=ft.Colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Nouvelle intervention - {date_str} à {hour:02d}:00"),
            content=ft.Container(
                width=550,
                padding=ft.padding.only(top=10, bottom=10),
                content=ft.Column(
                    controls=[numero_field, client_dropdown, date_field, ft.Row([heure_debut_field, heure_fin_field], spacing=10), lieu_dropdown, paiement_dropdown, effectuee_checkbox, resume_field, detail_field],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                    height=500,
                ),
            ),
            actions=[ft.TextButton("Annuler", on_click=close_dialog), ft.ElevatedButton("Enregistrer", on_click=save)],
        )
        
        self.page.open(dialog)
    
    def edit_intervention(self, intervention):
        """Modifie une intervention (long press)"""
        clients = self.db.get_all_clients()
        client_options = [ft.dropdown.Option(key=str(c["id"]), text=c["nom_prenom"]) for c in clients]
        
        numero_field = ft.TextField(label="Numéro *", value=intervention["numero"])
        client_dropdown = ft.Dropdown(label="Client *", options=client_options, value=str(intervention["client_id"]))
        date_field = ft.TextField(label="Date *", value=intervention["date_intervention"])
        heure_debut_field = ft.TextField(label="Heure début", value=intervention.get("heure_debut", ""))
        heure_fin_field = ft.TextField(label="Heure fin", value=intervention.get("heure_fin", ""))
        lieu_dropdown = ft.Dropdown(label="Lieu", options=[ft.dropdown.Option("Domicile"), ft.dropdown.Option("À distance")], value=intervention.get("lieu"))
        paiement_dropdown = ft.Dropdown(label="Paiement", options=[ft.dropdown.Option("Payé"), ft.dropdown.Option("À payer"), ft.dropdown.Option("Gratuit")], value=intervention["paiement"])
        effectuee_checkbox = ft.Checkbox(label="Intervention effectuée", value=bool(intervention.get("effectuee")))
        resume_field = ft.TextField(label="Résumé", multiline=True, min_lines=2, value=intervention.get("resume", ""))
        detail_field = ft.TextField(label="Détail", multiline=True, min_lines=2, value=intervention.get("detail", ""))
        
        def close_dialog(e):
            self.page.close(dialog)
        
        def save(e):
            self.db.update_intervention(
                intervention["id"],
                numero=numero_field.value,
                client_id=int(client_dropdown.value),
                date_intervention=date_field.value,
                heure_debut=heure_debut_field.value or "",
                heure_fin=heure_fin_field.value or "",
                lieu=lieu_dropdown.value,
                paiement=paiement_dropdown.value,
                effectuee=1 if effectuee_checkbox.value else 0,
                resume=resume_field.value or "",
                detail=detail_field.value or "",
            )
            
            self.page.close(dialog)
            self.build_view()
            self.page.update()
            
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Intervention modifiée ✅"), bgcolor=ft.Colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Modifier {intervention['numero']}"),
            content=ft.Container(
                width=550,
                padding=ft.padding.only(top=10, bottom=10),
                content=ft.Column(
                    controls=[numero_field, client_dropdown, date_field, ft.Row([heure_debut_field, heure_fin_field], spacing=10), lieu_dropdown, paiement_dropdown, effectuee_checkbox, resume_field, detail_field],
                    spacing=15,
                    scroll=ft.ScrollMode.AUTO,
                    height=500,
                ),
            ),
            actions=[ft.TextButton("Annuler", on_click=close_dialog), ft.ElevatedButton("Enregistrer", on_click=save)],
        )
        
        self.page.open(dialog)
    
    def view_intervention(self, intervention):
        """Affiche les détails (simple clic)"""
        def close_dialog(e):
            self.page.close(dialog)
        
        heure_debut = intervention.get("heure_debut", "")
        heure_fin = intervention.get("heure_fin", "")
        heures = f"{heure_debut} - {heure_fin}" if heure_debut and heure_fin else "-"
        
        date_display = self.format_date_display(intervention["date_intervention"])
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Intervention {intervention['numero']}"),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    controls=[
                        ft.Text(f"Client: {intervention['client_nom']}", size=14, weight=ft.FontWeight.BOLD),
                        ft.Text(f"Date: {date_display}", size=14),
                        ft.Text(f"Horaire: {heures}", size=14),
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
                ft.ElevatedButton("Modifier", on_click=lambda e: (close_dialog(e), self.edit_intervention(intervention))),
            ],
        )
        
        self.page.open(dialog)
