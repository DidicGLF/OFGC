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
        # Dropdowns pour navigation rapide
        current_year = datetime.now().year
        years = list(range(2020, current_year + 2))  # 2020 à année actuelle + 1
        
        year_dropdown = ft.Dropdown(
            width=100,
            value=str(self.start_of_week.year),
            options=[ft.dropdown.Option(str(y)) for y in years],
            on_change=self.on_year_change,
            text_size=14,
        )
        
        months = [
            "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
            "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
        ]
        
        month_dropdown = ft.Dropdown(
            width=130,
            value=str(self.start_of_week.month),
            options=[ft.dropdown.Option(str(i+1), text=months[i]) for i in range(12)],
            on_change=self.on_month_change,
            text_size=14,
        )
        
        header = ft.Container(
            padding=30,
            bgcolor=ft.Colors.with_opacity(0.8, "#0f172a"),
            content=ft.Row(
                controls=[
                    ft.Text("Calendrier", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.Icons.CHEVRON_LEFT, tooltip="Semaine précédente", on_click=self.prev_week),
                            month_dropdown,
                            year_dropdown,
                            ft.IconButton(icon=ft.Icons.CHEVRON_RIGHT, tooltip="Semaine suivante", on_click=self.next_week),
                            ft.ElevatedButton("Aujourd'hui", on_click=self.goto_today),
                        ],
                        spacing=10,
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
    
    def on_year_change(self, e):
        """Changement d'année via dropdown"""
        try:
            new_year = int(e.control.value)
            # Garder le même mois mais changer l'année
            self.start_of_week = datetime(new_year, self.start_of_week.month, 1)
            # Ajuster au début de la semaine
            self.start_of_week = self.start_of_week - timedelta(days=self.start_of_week.weekday())
            self.build_view()
            self.page.update()
        except:
            pass
    
    def on_month_change(self, e):
        """Changement de mois via dropdown"""
        try:
            new_month = int(e.control.value)
            # Garder la même année mais changer le mois
            self.start_of_week = datetime(self.start_of_week.year, new_month, 1)
            # Ajuster au début de la semaine
            self.start_of_week = self.start_of_week - timedelta(days=self.start_of_week.weekday())
            self.build_view()
            self.page.update()
        except:
            pass
    
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
        
        # Ligne pour les événements "Toute la journée"
        all_day_row = ft.Row(
            controls=[
                ft.Container(width=60, padding=5, content=ft.Text("Toute la\njournée", size=10, color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE))),
            ] + [self.create_all_day_cell(i, interventions) for i in range(7)],
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
        
        self.calendar_grid.content = ft.Column(controls=[days_header, all_day_row, hours_grid], spacing=10)
        self.calendar_grid.padding = ft.padding.symmetric(horizontal=40, vertical=10)
    
    def get_day_name(self, day_index):
        days = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
        return days[day_index]
    
    def get_week_interventions(self):
        all_interventions = self.db.get_all_interventions()
        print(f"DEBUG Calendar: Total interventions dans la base: {len(all_interventions)}")
        week_interventions = []
        
        # Convertir en dates pures (sans heures)
        start_date = self.start_of_week.date()
        end_date = (self.start_of_week + timedelta(days=7)).date()
        
        print(f"DEBUG: Cherche interventions entre {start_date} et {end_date}")
        
        for intervention in all_interventions:
            interv_date_str = intervention["date_intervention"]
            interv_date = datetime.strptime(interv_date_str, "%Y-%m-%d").date()
            
            print(f"DEBUG: Check {intervention['numero']}: {interv_date} (entre {start_date} et {end_date}?)")
            
            if start_date <= interv_date < end_date:
                week_interventions.append(intervention)
                print(f"DEBUG: ✅ Intervention {intervention['numero']} ajoutée pour {interv_date_str}")
            else:
                print(f"DEBUG: ❌ Intervention {intervention['numero']} EXCLUE ({interv_date} pas dans la semaine)")
        
        print(f"DEBUG Calendar: {len(week_interventions)} interventions pour la semaine du {start_date}")
        return week_interventions
    
    def create_all_day_cell(self, day_index, interventions):
        """Crée une cellule pour les événements 'Toute la journée'"""
        current_day = self.start_of_week + timedelta(days=day_index)
        current_date_str = current_day.strftime("%Y-%m-%d")
        
        # Trouver les interventions sans horaire pour ce jour
        all_day_interventions = []
        for intervention in interventions:
            if intervention["date_intervention"] == current_date_str:
                # Intervention sans horaire = toute la journée
                if not intervention.get("heure_debut") or not intervention.get("heure_fin"):
                    all_day_interventions.append(intervention)
                    print(f"DEBUG AllDay: {intervention['numero']} pour {current_date_str} (pas d'horaire)")
        
        if not all_day_interventions:
            return ft.Container(
                expand=True,
                height=40,
                bgcolor=ft.Colors.with_opacity(0.2, "#1e293b"),
                border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            )
        
        print(f"DEBUG AllDay: {len(all_day_interventions)} interventions toute la journée pour {current_date_str}")
        
        # Afficher les interventions toute la journée
        items = []
        for interv in all_day_interventions:
            color = ft.Colors.GREEN if interv.get("effectuee") else ft.Colors.ORANGE
            icon = "🏠" if interv.get("lieu") == "Domicile" else "💻"
            items.append(
                ft.Container(
                    padding=ft.padding.symmetric(horizontal=4, vertical=2),
                    bgcolor=ft.Colors.with_opacity(0.25, color),
                    border=ft.border.all(1, color),
                    border_radius=3,
                    content=ft.Row(
                        controls=[
                            ft.Text(icon, size=10),
                            ft.Text(
                                f"{interv['client_nom']}",
                                size=10,
                                color=ft.Colors.WHITE,
                                weight=ft.FontWeight.BOLD,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=1,
                                expand=True,
                            ),
                        ],
                        spacing=3,
                    ),
                    on_click=lambda e, i=interv: self.view_intervention(i),
                    on_long_press=lambda e, i=interv: self.edit_intervention(i),
                )
            )
        
        return ft.Container(
            expand=True,
            height=max(35, len(all_day_interventions) * 28),  # Hauteur adaptative
            bgcolor=ft.Colors.with_opacity(0.2, "#1e293b"),
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            padding=2,
            content=ft.Column(
                controls=items,
                spacing=2,
                scroll=ft.ScrollMode.AUTO,
            ),
        )
    
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
                        print(f"DEBUG HourCell: {intervention['numero']} à {hour}:00 pour {current_date_str}")
        
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
        
        numero_field = ft.TextField(label="Numéro *", hint_text="Ex: INT-001")
        client_dropdown = ft.Dropdown(label="Client *", options=client_options, autofocus=True)
        
        # Convertir YYYY-MM-DD en DD/MM/YYYY
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            date_display = date_obj.strftime("%d/%m/%Y")
        except:
            date_display = date_str
        
        date_field = ft.TextField(label="Date *", value=date_display, read_only=True)
        
        # Option toute la journée
        all_day_checkbox = ft.Checkbox(label="Toute la journée (pas d'horaire précis)", value=False)
        
        heure_debut_field = ft.TextField(label="Heure début", value=f"{hour:02d}:00", width=100, hint_text="HH:MM")
        heure_fin_field = ft.TextField(label="Heure fin", value=f"{hour+1:02d}:00", width=100, hint_text="HH:MM")
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
            else:
                if not heure_debut_field.value:
                    heure_debut_field.value = f"{hour:02d}:00"
                if not heure_fin_field.value:
                    heure_fin_field.value = f"{hour+1:02d}:00"
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
                same_day = [i for i in all_interventions if i["date_intervention"] == date_iso]
                
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
            
            if not numero_field.value or not client_dropdown.value:
                if not numero_field.value:
                    numero_field.error_text = "Numéro obligatoire"
                if not client_dropdown.value:
                    client_dropdown.error_text = "Client obligatoire"
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
            self.build_view()
            self.page.update()
            
            self.page.snack_bar = ft.SnackBar(content=ft.Text("Intervention créée ✅"), bgcolor=ft.Colors.GREEN)
            self.page.snack_bar.open = True
            self.page.update()
        
        dialog = ft.AlertDialog(
            modal=True,
            title=ft.Text(f"Nouvelle intervention - {date_display} à {hour:02d}:00"),
            content=ft.Container(
                width=600,
                padding=ft.padding.only(top=20, bottom=10, left=20, right=20),
                content=ft.Column(
                    controls=[
                        numero_field,
                        client_dropdown,
                        date_field,
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
                ft.ElevatedButton(
                    "🗑️ Supprimer",
                    bgcolor=ft.Colors.RED,
                    color=ft.Colors.WHITE,
                    on_click=lambda e: (close_dialog(e), self.delete_intervention_calendar(intervention)),
                ),
            ],
        )
        
        self.page.open(dialog)
    
    def delete_intervention_calendar(self, intervention):
        """Supprime une intervention depuis le calendrier"""
        def close_dialog(e):
            self.page.close(dialog)
        
        def confirm_delete(e):
            self.db.delete_intervention(intervention["id"])
            self.page.close(dialog)
            self.build_view()
            self.page.update()
            
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
