import flet as ft
from database import Database
from views.dashboard import DashboardView
from views.clients import ClientsView
from views.interventions import InterventionsView
from views.calendar import CalendarView


class ClientProApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        self.current_view = "dashboard"
        
        # Configuration de la page
        self.page.title = "ClientPro - Gestion Clients & Interventions"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 1400
        self.page.window_height = 900
        
        # Thème personnalisé
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.colors.BLUE,
                on_primary=ft.colors.WHITE,
                secondary=ft.colors.BLUE_GREY_900,
                background=ft.colors.with_opacity(0.95, "#0f172a"),
                surface=ft.colors.with_opacity(0.95, "#1e293b"),
            )
        )
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Sidebar
        self.sidebar = ft.Container(
            width=280,
            bgcolor=ft.colors.with_opacity(0.95, "#0f172a"),
            content=ft.Column(
                controls=[
                    # Logo
                    ft.Container(
                        padding=30,
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    "Client",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.WHITE,
                                ),
                                ft.Text(
                                    "Pro",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.colors.BLUE,
                                ),
                            ],
                            spacing=0,
                        ),
                    ),
                    ft.Divider(height=1, color=ft.colors.with_opacity(0.1, ft.colors.WHITE)),
                    
                    # Navigation
                    ft.Container(
                        padding=ft.padding.only(top=20),
                        content=ft.Column(
                            controls=[
                                self.create_nav_item("📊", "Tableau de bord", "dashboard"),
                                self.create_nav_item("👥", "Clients", "clients"),
                                self.create_nav_item("🔧", "Interventions", "interventions"),
                                self.create_nav_item("📅", "Calendrier", "calendar"),
                                self.create_nav_item("📈", "Rapports", "reports"),
                                self.create_nav_item("⚙️", "Paramètres", "settings"),
                            ],
                            spacing=8,
                        ),
                    ),
                ],
            ),
        )
        
        # Zone de contenu principal
        self.content_area = ft.Container(
            expand=True,
            bgcolor=ft.colors.with_opacity(0.95, "#0f172a"),
            content=ft.Column(
                expand=True,
                spacing=0,
            ),
        )
        
        # Layout principal
        self.page.add(
            ft.Row(
                controls=[
                    self.sidebar,
                    self.content_area,
                ],
                spacing=0,
                expand=True,
            )
        )
        
        # Charger la vue par défaut
        self.load_view("dashboard")
    
    def create_nav_item(self, icon: str, label: str, view_id: str):
        """Crée un élément de navigation"""
        is_active = self.current_view == view_id
        
        return ft.Container(
            padding=14,
            margin=ft.margin.symmetric(horizontal=15, vertical=4),
            border_radius=12,
            bgcolor=ft.colors.BLUE if is_active else None,
            animate=ft.animation.Animation(200, ft.AnimationCurve.EASE_OUT),
            content=ft.Row(
                controls=[
                    ft.Text(icon, size=20),
                    ft.Text(
                        label,
                        size=15,
                        weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_500,
                        color=ft.colors.WHITE if is_active else ft.colors.with_opacity(0.6, ft.colors.WHITE),
                    ),
                ],
                spacing=14,
            ),
            on_click=lambda e, v=view_id: self.navigate_to(v),
            ink=True,
        )
    
    def navigate_to(self, view_id: str):
        """Navigation vers une vue"""
        if view_id == self.current_view:
            return
            
        self.current_view = view_id
        self.load_view(view_id)
        self.page.update()
    
    def load_view(self, view_id: str):
        """Charge une vue spécifique"""
        # Nettoyer le contenu actuel
        self.content_area.content.controls.clear()
        
        # Charger la nouvelle vue
        if view_id == "dashboard":
            view = DashboardView(self.page, self.db)
        elif view_id == "clients":
            view = ClientsView(self.page, self.db)
        elif view_id == "interventions":
            view = InterventionsView(self.page, self.db)
        elif view_id == "calendar":
            view = CalendarView(self.page, self.db)
        else:
            # Vue par défaut pour les sections non implémentées
            view = ft.Container(
                padding=40,
                content=ft.Column(
                    controls=[
                        ft.Text(
                            f"Section '{view_id}' en cours de développement",
                            size=24,
                            weight=ft.FontWeight.BOLD,
                        ),
                        ft.Text(
                            "Cette fonctionnalité sera disponible prochainement.",
                            size=16,
                            color=ft.colors.with_opacity(0.6, ft.colors.WHITE),
                        ),
                    ],
                    spacing=10,
                ),
            )
        
        self.content_area.content.controls.append(view)
        
        # Reconstruire la sidebar pour mettre à jour l'élément actif
        self.sidebar.content.controls[2].content.controls.clear()
        self.sidebar.content.controls[2].content.controls = [
            self.create_nav_item("📊", "Tableau de bord", "dashboard"),
            self.create_nav_item("👥", "Clients", "clients"),
            self.create_nav_item("🔧", "Interventions", "interventions"),
            self.create_nav_item("📅", "Calendrier", "calendar"),
            self.create_nav_item("📈", "Rapports", "reports"),
            self.create_nav_item("⚙️", "Paramètres", "settings"),
        ]
        
        self.page.update()


def main(page: ft.Page):
    ClientProApp(page)


if __name__ == "__main__":
    ft.app(target=main)
