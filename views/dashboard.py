import flet as ft
from database import Database


class DashboardView(ft.Container):
    def __init__(self, page: ft.Page, db: Database):
        super().__init__()
        self.page = page
        self.db = db
        self.expand = True
        self.bgcolor = ft.colors.with_opacity(0.95, "#0f172a")
        
        self.build_view()
    
    def build_view(self):
        """Construit la vue du tableau de bord"""
        # Récupérer les statistiques
        stats = self.db.get_stats()
        
        # Récupérer les interventions récentes
        interventions = self.db.get_all_interventions()[:5]  # 5 dernières
        
        # Header
        header = ft.Container(
            padding=30,
            bgcolor=ft.colors.with_opacity(0.8, "#0f172a"),
            content=ft.Row(
                controls=[
                    ft.Text(
                        "Tableau de bord",
                        size=28,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                    ),
                    ft.Row(
                        controls=[
                            ft.ElevatedButton(
                                "📤 Exporter",
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.with_opacity(0.95, "#1e293b"),
                                    color=ft.colors.WHITE,
                                ),
                            ),
                            ft.ElevatedButton(
                                "➕ Nouvelle intervention",
                                style=ft.ButtonStyle(
                                    bgcolor=ft.colors.BLUE,
                                    color=ft.colors.WHITE,
                                ),
                            ),
                        ],
                        spacing=15,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
        
        # Barre de recherche
        search_bar = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=0),
            content=ft.TextField(
                prefix_icon=ft.icons.SEARCH,
                hint_text="Rechercher un client, une intervention...",
                border_radius=12,
                filled=True,
                bgcolor=ft.colors.with_opacity(0.95, "#1e293b"),
                border_color=ft.colors.with_opacity(0.2, ft.colors.WHITE),
                color=ft.colors.WHITE,
            ),
        )
        
        # Cartes de statistiques
        stats_cards = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=20),
            content=ft.Row(
                controls=[
                    self.create_stat_card(
                        "Total clients",
                        str(stats["total_clients"]),
                        "👥",
                        ft.colors.BLUE,
                        "+12 ce mois"
                    ),
                    self.create_stat_card(
                        "Interventions actives",
                        str(stats["interventions_actives"]),
                        "🔧",
                        ft.colors.GREEN,
                        "+5 aujourd'hui"
                    ),
                    self.create_stat_card(
                        "En attente",
                        str(stats["interventions_attente"]),
                        "⏳",
                        ft.colors.ORANGE,
                        "Nécessite attention"
                    ),
                ],
                spacing=20,
                expand=True,
            ),
        )
        
        # Tableau des interventions récentes
        interventions_table = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=0),
            content=ft.Container(
                bgcolor=ft.colors.with_opacity(0.95, "#1e293b"),
                border_radius=16,
                content=ft.Column(
                    controls=[
                        # En-tête du tableau
                        ft.Container(
                            padding=20,
                            content=ft.Row(
                                controls=[
                                    ft.Text(
                                        "Interventions récentes",
                                        size=18,
                                        weight=ft.FontWeight.W_600,
                                        color=ft.colors.WHITE,
                                    ),
                                    ft.Row(
                                        controls=[
                                            ft.TextButton("Toutes", style=ft.ButtonStyle(bgcolor=ft.colors.BLUE)),
                                            ft.TextButton("En cours"),
                                            ft.TextButton("Terminées"),
                                        ],
                                        spacing=10,
                                    ),
                                ],
                                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                            ),
                        ),
                        ft.Divider(height=1, color=ft.colors.with_opacity(0.1, ft.colors.WHITE)),
                        # Lignes du tableau
                        *[self.create_intervention_row(intervention) for intervention in interventions],
                    ],
                    spacing=0,
                ),
            ),
        )
        
        # Contenu principal scrollable
        main_content = ft.Column(
            controls=[
                header,
                search_bar,
                stats_cards,
                interventions_table,
            ],
            spacing=20,
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        self.content = main_content
    
    def create_stat_card(self, label: str, value: str, icon: str, color, change: str):
        """Crée une carte de statistique"""
        return ft.Container(
            expand=True,
            padding=24,
            bgcolor=ft.colors.with_opacity(0.95, "#1e293b"),
            border_radius=16,
            border=ft.border.all(1, ft.colors.with_opacity(0.1, ft.colors.WHITE)),
            content=ft.Column(
                controls=[
                    ft.Row(
                        controls=[
                            ft.Text(
                                label,
                                size=14,
                                color=ft.colors.with_opacity(0.6, ft.colors.WHITE),
                                weight=ft.FontWeight.W_500,
                            ),
                            ft.Container(
                                width=40,
                                height=40,
                                bgcolor=ft.colors.with_opacity(0.15, color),
                                border_radius=10,
                                content=ft.Text(
                                    icon,
                                    size=18,
                                    text_align=ft.TextAlign.CENTER,
                                ),
                                alignment=ft.alignment.center,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Text(
                        value,
                        size=32,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                    ),
                    ft.Text(
                        change,
                        size=13,
                        color=ft.colors.GREEN,
                        weight=ft.FontWeight.W_500,
                    ),
                ],
                spacing=8,
            ),
        )
    
    def create_intervention_row(self, intervention):
        """Crée une ligne d'intervention"""
        # Déterminer la couleur du badge selon le statut
        if intervention["statut"] == "Terminé":
            badge_color = ft.colors.GREEN
            badge_bgcolor = ft.colors.with_opacity(0.15, ft.colors.GREEN)
        elif intervention["statut"] == "En cours":
            badge_color = ft.colors.ORANGE
            badge_bgcolor = ft.colors.with_opacity(0.15, ft.colors.ORANGE)
        else:
            badge_color = ft.colors.RED
            badge_bgcolor = ft.colors.with_opacity(0.15, ft.colors.RED)
        
        return ft.Container(
            padding=ft.padding.symmetric(horizontal=25, vertical=20),
            content=ft.Row(
                controls=[
                    # Client
                    ft.Container(
                        width=250,
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
                    # Type
                    ft.Container(
                        width=180,
                        content=ft.Text(
                            intervention.get("type_intervention", ""),
                            size=14,
                            color=ft.colors.WHITE,
                        ),
                    ),
                    # Date
                    ft.Container(
                        width=120,
                        content=ft.Text(
                            intervention["date_intervention"],
                            size=14,
                            color=ft.colors.WHITE,
                        ),
                    ),
                    # Statut
                    ft.Container(
                        width=120,
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
                    # Actions
                    ft.Row(
                        controls=[
                            ft.IconButton(
                                icon=ft.icons.VISIBILITY,
                                icon_size=18,
                                icon_color=ft.colors.with_opacity(0.6, ft.colors.WHITE),
                            ),
                            ft.IconButton(
                                icon=ft.icons.EDIT,
                                icon_size=18,
                                icon_color=ft.colors.with_opacity(0.6, ft.colors.WHITE),
                            ),
                            ft.IconButton(
                                icon=ft.icons.DELETE,
                                icon_size=18,
                                icon_color=ft.colors.with_opacity(0.6, ft.colors.WHITE),
                            ),
                        ],
                        spacing=8,
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
