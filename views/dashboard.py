import flet as ft
from database import Database


class DashboardView(ft.Container):
    def __init__(self, page: ft.Page, db: Database, navigate_callback=None):
        super().__init__()
        self.page = page
        self.db = db
        self.navigate_callback = navigate_callback
        self.expand = True
        self.bgcolor = ft.Colors.with_opacity(0.95, "#0f172a")
        
        self.build_view()
    
    def format_date_display(self, date_str):
        """Convertit YYYY-MM-DD en JJ/MM/AAAA pour affichage"""
        try:
            from datetime import datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            return date_obj.strftime("%d/%m/%Y")
        except:
            return date_str
    
    def build_view(self):
        """Construit la vue du tableau de bord"""
        stats = self.db.get_stats()
        interventions = self.db.get_all_interventions()[:5]
        
        header = ft.Container(
            padding=30,
            bgcolor=ft.Colors.with_opacity(0.8, "#0f172a"),
            content=ft.Row(
                controls=[
                    ft.Text("Tableau de bord", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton("📤 Exporter", bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"), color=ft.Colors.WHITE),
                            ft.ElevatedButton("➕ Nouvelle intervention", bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE, on_click=self.open_new_intervention),
                        ],
                        spacing=15,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
        
        search_bar = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=0),
            content=ft.TextField(
                prefix_icon=ft.Icons.SEARCH,
                hint_text="Rechercher un client, une intervention...",
                border_radius=12,
                filled=True,
                bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
                border_color=ft.Colors.with_opacity(0.2, ft.Colors.WHITE),
                color=ft.Colors.WHITE,
            ),
        )
        
        stats_cards = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=20),
            content=ft.Row(
                controls=[
                    self.create_stat_card("Total clients", str(stats["total_clients"]), "👥", ft.Colors.BLUE, "+12 ce mois"),
                    self.create_stat_card("Total interventions", str(stats["total_interventions"]), "🔧", ft.Colors.GREEN, "Toutes périodes"),
                    self.create_stat_card("À payer", str(stats["interventions_a_payer"]), "💰", ft.Colors.ORANGE, "Nécessite attention"),
                ],
                spacing=20,
                expand=True,
            ),
        )
        
        interventions_table = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=0),
            content=ft.Container(
                bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
                border_radius=16,
                content=ft.Column(
                    controls=[
                        ft.Container(padding=20, content=ft.Text("Interventions récentes", size=18, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
                        ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                        *[self.create_intervention_row(intervention) for intervention in interventions],
                    ],
                    spacing=0,
                ),
            ),
        )
        
        main_content = ft.Column(controls=[header, search_bar, stats_cards, interventions_table], spacing=20, scroll=ft.ScrollMode.AUTO, expand=True)
        self.content = main_content
    
    def create_stat_card(self, label, value, icon, color, change):
        """Crée une carte de statistique"""
        return ft.Container(
            expand=True,
            padding=24,
            bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
            border_radius=16,
            border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(label, size=14, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE), weight=ft.FontWeight.W_500),
                            ft.Container(
                                width=40,
                                height=40,
                                bgcolor=ft.Colors.with_opacity(0.15, color),
                                border_radius=10,
                                content=ft.Text(icon, size=18, text_align=ft.TextAlign.CENTER),
                                alignment=ft.alignment.center,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(value, size=32, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Text(change, size=13, color=ft.Colors.GREEN, weight=ft.FontWeight.W_500),
                ],
                spacing=8,
            ),
        )
    
    def create_intervention_row(self, intervention):
        """Crée une ligne d'intervention"""
        if intervention["paiement"] == "Payé":
            badge_color, badge_bgcolor = ft.Colors.GREEN, ft.Colors.with_opacity(0.15, ft.Colors.GREEN)
        elif intervention["paiement"] == "À payer":
            badge_color, badge_bgcolor = ft.Colors.ORANGE, ft.Colors.with_opacity(0.15, ft.Colors.ORANGE)
        else:
            badge_color, badge_bgcolor = ft.Colors.BLUE, ft.Colors.with_opacity(0.15, ft.Colors.BLUE)
        
        date_display = self.format_date_display(intervention["date_intervention"])
        
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=25, vertical=20),
            content=ft.Row(
                controls=[
                    ft.Container(width=100, content=ft.Text(intervention["numero"], size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE)),
                    ft.Container(width=250, content=ft.Column(controls=[ft.Text(intervention["client_nom"], size=14, weight=ft.FontWeight.W_600, color=ft.Colors.WHITE), ft.Text(intervention.get("client_email", ""), size=13, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE))], spacing=2)),
                    ft.Container(width=120, content=ft.Text(date_display, size=14, color=ft.Colors.WHITE)),
                    ft.Container(width=120, content=ft.Container(padding=ft.padding.symmetric(horizontal=12, vertical=6), bgcolor=badge_bgcolor, border_radius=6, content=ft.Text(intervention["paiement"], size=12, weight=ft.FontWeight.W_600, color=badge_color))),
                    ft.Row(
                        controls=[
                            ft.IconButton(icon=ft.Icons.VISIBILITY, icon_size=18, icon_color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE), on_click=lambda e, i=intervention: self.view_intervention(i)),
                            ft.IconButton(icon=ft.Icons.EDIT, icon_size=18, icon_color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE), on_click=lambda e, i=intervention: self.navigate_to_interventions(e)),
                            ft.IconButton(icon=ft.Icons.DELETE, icon_size=18, icon_color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE), on_click=lambda e, i=intervention: self.delete_intervention(i)),
                        ],
                        spacing=8,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
    
    def navigate_to_interventions(self, e):
        """Navigue vers la page des interventions"""
        if self.navigate_callback:
            self.navigate_callback("interventions")
    
    def open_new_intervention(self, e):
        """Navigue vers interventions et ouvre le dialog de création"""
        if self.navigate_callback:
            self.navigate_callback("interventions", open_new=True)
    
    def view_intervention(self, intervention):
        """Affiche les détails d'une intervention"""
        def close_dialog(e):
            self.page.close(dialog)
        
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
                        ft.Text(f"Lieu: {intervention.get('lieu', '-')}", size=14),
                        ft.Text(f"Paiement: {intervention['paiement']}", size=14),
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
            actions=[ft.TextButton("Fermer", on_click=close_dialog)],
        )
        
        self.page.open(dialog)
    
    def delete_intervention(self, intervention):
        """Supprime une intervention après confirmation"""
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
            actions_alignment=ft.MainAxisAlignment.END,
        )
        
        self.page.open(dialog)
