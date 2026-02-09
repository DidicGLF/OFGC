import flet as ft
from database import Database


class CalendarView(ft.Container):
    def __init__(self, page: ft.Page, db: Database):
        super().__init__()
        self.page = page
        self.db = db
        self.expand = True
        self.bgcolor = ft.colors.with_opacity(0.95, "#0f172a")
        
        self.build_view()
    
    def build_view(self):
        """Construit la vue calendrier"""
        # Header
        header = ft.Container(
            padding=30,
            bgcolor=ft.colors.with_opacity(0.8, "#0f172a"),
            content=ft.Text(
                "Calendrier",
                size=28,
                weight=ft.FontWeight.BOLD,
                color=ft.colors.WHITE,
            ),
        )
        
        # Message temporaire
        placeholder = ft.Container(
            padding=40,
            expand=True,
            content=ft.Column(
                controls=[
                    ft.Icon(
                        ft.icons.CALENDAR_MONTH,
                        size=64,
                        color=ft.colors.BLUE,
                    ),
                    ft.Text(
                        "Vue calendrier",
                        size=24,
                        weight=ft.FontWeight.BOLD,
                        color=ft.colors.WHITE,
                    ),
                    ft.Text(
                        "Cette fonctionnalité affichera toutes vos interventions dans un calendrier interactif.",
                        size=16,
                        color=ft.colors.with_opacity(0.6, ft.colors.WHITE),
                        text_align=ft.TextAlign.CENTER,
                    ),
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=20,
            ),
        )
        
        self.content = ft.Column(
            controls=[header, placeholder],
            spacing=0,
            expand=True,
        )
