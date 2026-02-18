import flet as ft
from database import Database
from views.dashboard import DashboardView
from views.clients import ClientsView
from views.interventions import InterventionsView
from views.calendar import CalendarView
from views.reports import ReportsView
from views.settings import SettingsView


class OrdiFacileApp:
    def __init__(self, page: ft.Page):
        self.page = page
        self.db = Database()
        self.current_view = "dashboard"
        
        # Configuration de la page
        self.page.title = "OrdiFacile - Gestion Clients & Interventions"
        self.page.theme_mode = ft.ThemeMode.DARK
        self.page.padding = 0
        self.page.window_width = 1400
        self.page.window_height = 900
        
        # Thème personnalisé
        self.page.theme = ft.Theme(
            color_scheme=ft.ColorScheme(
                primary=ft.Colors.BLUE,
                on_primary=ft.Colors.WHITE,
                secondary=ft.Colors.BLUE_GREY_900,
                background=ft.Colors.with_opacity(0.95, "#0f172a"),
                surface=ft.Colors.with_opacity(0.95, "#1e293b"),
            )
        )
        
        self.setup_ui()
        
    def setup_ui(self):
        """Configure l'interface utilisateur"""
        # Sidebar
        self.sidebar = ft.Container(
            width=280,
            bgcolor=ft.Colors.with_opacity(0.95, "#0f172a"),
            content=ft.Column(
                controls=[
                    # Logo
                    ft.Container(
                        padding=30,
                        content=ft.Row(
                            controls=[
                                ft.Text(
                                    "Ordi",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.WHITE,
                                ),
                                ft.Text(
                                    "Facile",
                                    size=24,
                                    weight=ft.FontWeight.BOLD,
                                    color=ft.Colors.BLUE,
                                ),
                            ],
                            spacing=0,
                        ),
                    ),
                    ft.Divider(height=1, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                    
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
            bgcolor=ft.Colors.with_opacity(0.95, "#0f172a"),
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
            bgcolor=ft.Colors.BLUE if is_active else None,
            animate=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
            content=ft.Row(
                controls=[
                    ft.Text(icon, size=20),
                    ft.Text(
                        label,
                        size=15,
                        weight=ft.FontWeight.W_600 if is_active else ft.FontWeight.W_500,
                        color=ft.Colors.WHITE if is_active else ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
                    ),
                ],
                spacing=14,
            ),
            on_click=lambda e, v=view_id: self.navigate_to(v),
            ink=True,
        )
    
    def navigate_to(self, view_id: str, **kwargs):
        """Navigation vers une vue"""
        if view_id == self.current_view and not kwargs:
            return
            
        self.current_view = view_id
        self.load_view(view_id, **kwargs)
        self.page.update()
    
    def load_view(self, view_id: str, **kwargs):
        """Charge une vue spécifique"""
        # Nettoyer le contenu actuel
        self.content_area.content.controls.clear()
        
        # Charger la nouvelle vue
        if view_id == "dashboard":
            view = DashboardView(self.page, self.db, navigate_callback=self.navigate_to)
        elif view_id == "clients":
            view = ClientsView(self.page, self.db, navigate_callback=self.navigate_to)
        elif view_id == "interventions":
            view = InterventionsView(
                self.page, 
                self.db,
                filter_client_id=kwargs.get("filter_client_id"),
                filter_client_name=kwargs.get("filter_client_name"),
            )
            # Si open_new=True, ouvrir le dialog automatiquement
            if kwargs.get("open_new"):
                # Attendre que la vue soit chargée
                self.page.update()
                view.open_add_intervention_dialog(None)
        elif view_id == "calendar":
            print(f"DEBUG: Loading calendar view")
            try:
                view = CalendarView(self.page, self.db)
                print(f"DEBUG: Calendar view created successfully")
            except Exception as e:
                print(f"ERROR: Failed to create CalendarView: {e}")
                import traceback
                traceback.print_exc()
                raise
        elif view_id == "reports":
            print(f"DEBUG: Loading reports view")
            try:
                view = ReportsView(self.page, self.db)
                print(f"DEBUG: Reports view created successfully")
            except Exception as e:
                print(f"ERROR: Failed to create ReportsView: {e}")
                import traceback
                traceback.print_exc()
                raise
        elif view_id == "settings":
            view = SettingsView(self.page, self.db)
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
                            color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE),
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
    OrdiFacileApp(page)


if __name__ == "__main__":
    ft.app(target=main)
