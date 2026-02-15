import flet as ft
from database import Database
from datetime import datetime, timedelta
from collections import defaultdict


class ReportsView(ft.Container):
    def __init__(self, page: ft.Page, db: Database):
        super().__init__()
        self.page = page
        self.db = db
        self.expand = True
        self.bgcolor = ft.Colors.with_opacity(0.95, "#0f172a")
        
        # Période par défaut : ce mois
        today = datetime.now()
        self.start_date = datetime(today.year, today.month, 1)
        self.end_date = today
        self.period_label = "Ce mois"
        
        self.build_view()
    
    def build_view(self):
        """Construit la vue des rapports"""
        header = ft.Container(
            padding=30,
            bgcolor=ft.Colors.with_opacity(0.8, "#0f172a"),
            content=ft.Row(
                controls=[
                    ft.Text("Rapports & Statistiques", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton("Ce mois", on_click=lambda e: self.change_period("month")),
                            ft.ElevatedButton("Année", on_click=lambda e: self.change_period("year")),
                            ft.ElevatedButton("📤 Export PDF", bgcolor=ft.Colors.BLUE, color=ft.Colors.WHITE, on_click=self.export_pdf),
                        ],
                        spacing=10,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
        
        # Période sélectionnée
        period_info = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=10),
            content=ft.Text(
                f"📅 Période : {self.period_label} ({self.start_date.strftime('%d/%m/%Y')} - {self.end_date.strftime('%d/%m/%Y')})",
                size=16,
                color=ft.Colors.BLUE,
                weight=ft.FontWeight.W_500,
            ),
        )
        
        # Récupérer les statistiques
        stats = self.get_period_stats()
        
        # Cartes statistiques
        stats_cards = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=20),
            content=ft.Row(
                controls=[
                    self.create_stat_card("Total interventions", str(stats["total_interventions"]), "📋", ft.Colors.BLUE),
                    self.create_stat_card("Effectuées", str(stats["effectuees"]), "✅", ft.Colors.GREEN),
                    self.create_stat_card("À payer", str(stats["a_payer"]), "💰", ft.Colors.ORANGE),
                    self.create_stat_card("Clients uniques", str(stats["clients_uniques"]), "👥", ft.Colors.PURPLE),
                ],
                spacing=20,
            ),
        )
        
        # Graphiques et listes
        charts_row = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=10),
            content=ft.Row(
                controls=[
                    self.create_monthly_chart(stats["monthly_data"]),
                    self.create_payment_pie(stats["payment_breakdown"]),
                ],
                spacing=20,
            ),
        )
        
        # Top 5 clients
        top_clients = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=10),
            content=self.create_top_clients_list(stats["top_clients"]),
        )
        
        # Détails des interventions
        interventions_list = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=10),
            content=self.create_interventions_list(stats["interventions"]),
        )
        
        main_content = ft.Column(
            controls=[header, period_info, stats_cards, charts_row, top_clients, interventions_list],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        self.content = main_content
    
    def get_period_stats(self):
        """Calcule les statistiques pour la période sélectionnée"""
        all_interventions = self.db.get_all_interventions()
        
        # Filtrer par période
        period_interventions = []
        for interv in all_interventions:
            interv_date = datetime.strptime(interv["date_intervention"], "%Y-%m-%d")
            if self.start_date <= interv_date <= self.end_date:
                period_interventions.append(interv)
        
        # Statistiques de base
        total = len(period_interventions)
        effectuees = sum(1 for i in period_interventions if i.get("effectuee"))
        a_payer = sum(1 for i in period_interventions if i["paiement"] == "À payer")
        clients_uniques = len(set(i["client_id"] for i in period_interventions))
        
        # Répartition par paiement
        payment_breakdown = {"Payé": 0, "À payer": 0, "Gratuit": 0}
        for interv in period_interventions:
            payment_breakdown[interv["paiement"]] += 1
        
        # Interventions par mois (6 derniers mois)
        monthly_data = self.get_monthly_data()
        
        # Top 5 clients
        client_counts = defaultdict(int)
        client_names = {}
        for interv in period_interventions:
            client_counts[interv["client_id"]] += 1
            client_names[interv["client_id"]] = interv["client_nom"]
        
        top_clients = sorted(client_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        top_clients = [(client_names[cid], count) for cid, count in top_clients]
        
        return {
            "total_interventions": total,
            "effectuees": effectuees,
            "a_payer": a_payer,
            "clients_uniques": clients_uniques,
            "payment_breakdown": payment_breakdown,
            "monthly_data": monthly_data,
            "top_clients": top_clients,
            "interventions": period_interventions,
        }
    
    def get_monthly_data(self):
        """Récupère les données des 6 derniers mois"""
        all_interventions = self.db.get_all_interventions()
        monthly_counts = defaultdict(int)
        
        for interv in all_interventions:
            interv_date = datetime.strptime(interv["date_intervention"], "%Y-%m-%d")
            month_key = interv_date.strftime("%Y-%m")
            monthly_counts[month_key] += 1
        
        # 6 derniers mois
        today = datetime.now()
        months = []
        for i in range(5, -1, -1):
            month = today - timedelta(days=30*i)
            month_key = month.strftime("%Y-%m")
            month_label = month.strftime("%b %Y")
            count = monthly_counts.get(month_key, 0)
            months.append((month_label, count))
        
        return months
    
    def create_stat_card(self, label, value, icon, color):
        """Crée une carte de statistique"""
        return ft.Container(
            expand=True,
            padding=24,
            bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
            border_radius=16,
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(label, size=14, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
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
                ],
                spacing=8,
            ),
        )
    
    def create_monthly_chart(self, monthly_data):
        """Crée un graphique en barres (simulé)"""
        max_value = max([count for _, count in monthly_data]) if monthly_data else 1
        
        bars = []
        for month_label, count in monthly_data:
            bar_height = (count / max_value * 100) if max_value > 0 else 0
            bars.append(
                ft.Column(
                    controls=[
                        ft.Container(
                            width=50,
                            height=120,
                            content=ft.Column(
                                controls=[
                                    ft.Container(expand=True),
                                    ft.Container(
                                        width=50,
                                        height=bar_height,
                                        bgcolor=ft.Colors.BLUE,
                                        border_radius=4,
                                    ),
                                ],
                                spacing=0,
                            ),
                        ),
                        ft.Text(str(count), size=12, color=ft.Colors.WHITE, text_align=ft.TextAlign.CENTER),
                        ft.Text(month_label, size=10, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE), text_align=ft.TextAlign.CENTER),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=5,
                )
            )
        
        return ft.Container(
            expand=True,
            padding=20,
            bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
            border_radius=16,
            content=ft.Column(
                controls=[
                    ft.Text("Interventions par mois", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Row(controls=bars, spacing=10, alignment=ft.MainAxisAlignment.CENTER),
                ],
                spacing=15,
            ),
        )
    
    def create_payment_pie(self, payment_breakdown):
        """Crée un camembert (simulé avec barres)"""
        total = sum(payment_breakdown.values())
        
        items = []
        colors = {"Payé": ft.Colors.GREEN, "À payer": ft.Colors.ORANGE, "Gratuit": ft.Colors.BLUE}
        
        for status, count in payment_breakdown.items():
            percentage = (count / total * 100) if total > 0 else 0
            items.append(
                ft.Row(
                    controls=[
                        ft.Container(width=15, height=15, bgcolor=colors[status], border_radius=3),
                        ft.Text(status, size=14, color=ft.Colors.WHITE),
                        ft.Text(f"{count} ({percentage:.1f}%)", size=14, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
                    ],
                    spacing=10,
                )
            )
        
        return ft.Container(
            expand=True,
            padding=20,
            bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
            border_radius=16,
            content=ft.Column(
                controls=[
                    ft.Text("Répartition paiements", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Column(controls=items, spacing=10),
                ],
                spacing=15,
            ),
        )
    
    def create_top_clients_list(self, top_clients):
        """Crée la liste des top clients"""
        if not top_clients:
            return ft.Container(
                padding=20,
                bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
                border_radius=16,
                content=ft.Text("Aucune donnée", color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
            )
        
        items = []
        for i, (client_name, count) in enumerate(top_clients, 1):
            items.append(
                ft.Row(
                    controls=[
                        ft.Text(f"#{i}", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.BLUE),
                        ft.Text(client_name, size=14, color=ft.Colors.WHITE, expand=True),
                        ft.Text(f"{count} intervention{'s' if count > 1 else ''}", size=14, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
                    ],
                    spacing=15,
                )
            )
        
        return ft.Container(
            padding=20,
            bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
            border_radius=16,
            content=ft.Column(
                controls=[
                    ft.Text("🏆 Top 5 Clients", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Column(controls=items, spacing=10),
                ],
                spacing=15,
            ),
        )
    
    def create_interventions_list(self, interventions):
        """Crée la liste détaillée des interventions"""
        if not interventions:
            return ft.Container()
        
        rows = []
        for interv in interventions[:10]:  # Limiter à 10 pour ne pas surcharger
            rows.append(
                ft.Container(
                    padding=15,
                    content=ft.Row(
                        controls=[
                            ft.Text(interv["numero"], size=13, color=ft.Colors.WHITE, width=80),
                            ft.Text(interv["client_nom"], size=13, color=ft.Colors.WHITE, expand=True),
                            ft.Text(interv["date_intervention"], size=13, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE), width=100),
                            ft.Text(interv["paiement"], size=12, color=ft.Colors.GREEN if interv["paiement"] == "Payé" else ft.Colors.ORANGE, width=80),
                        ],
                    ),
                )
            )
        
        return ft.Container(
            padding=20,
            bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
            border_radius=16,
            content=ft.Column(
                controls=[
                    ft.Text(f"📋 Détail des interventions ({len(interventions)} total)", size=16, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                    ft.Column(controls=rows, spacing=5, scroll=ft.ScrollMode.AUTO, height=300),
                ],
                spacing=15,
            ),
        )
    
    def change_period(self, period_type):
        """Change la période affichée"""
        today = datetime.now()
        
        if period_type == "month":
            self.start_date = datetime(today.year, today.month, 1)
            self.end_date = today
            self.period_label = "Ce mois"
        elif period_type == "year":
            self.start_date = datetime(today.year, 1, 1)
            self.end_date = today
            self.period_label = "Cette année"
        
        self.build_view()
        self.page.update()
    
    def export_pdf(self, e):
        """Export en PDF (placeholder)"""
        self.page.snack_bar = ft.SnackBar(
            content=ft.Text("Fonctionnalité d'export PDF à venir ! 📄"),
            bgcolor=ft.Colors.BLUE,
        )
        self.page.snack_bar.open = True
        self.page.update()
