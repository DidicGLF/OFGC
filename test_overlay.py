import flet as ft
from datetime import datetime

def main(page: ft.Page):
    page.title = "Test Intervention Dialog"
    page.theme_mode = ft.ThemeMode.DARK
    
    def open_intervention_dialog(e):
        print("Opening intervention dialog...")
        
        # Formulaire minimal
        client_dropdown = ft.Dropdown(
            label="Client",
            options=[
                ft.dropdown.Option(key="1", text="Client Test 1"),
                ft.dropdown.Option(key="2", text="Client Test 2"),
            ],
        )
        
        titre_field = ft.TextField(label="Titre")
        date_field = ft.TextField(
            label="Date",
            value=datetime.now().strftime("%Y-%m-%d"),
        )
        
        def close_dlg(e):
            print("Closing dialog")
            page.close(dlg)
        
        def save(e):
            print(f"Saving: {titre_field.value}")
            page.close(dlg)
        
        dlg = ft.AlertDialog(
            modal=True,
            title=ft.Text("Nouvelle intervention"),
            content=ft.Container(
                width=500,
                content=ft.Column(
                    controls=[
                        client_dropdown,
                        titre_field,
                        date_field,
                    ],
                    spacing=15,
                ),
            ),
            actions=[
                ft.TextButton("Annuler", on_click=close_dlg),
                ft.ElevatedButton("Enregistrer", on_click=save),
            ],
        )
        
        print("Calling page.open(dlg)")
        page.open(dlg)
        print("Dialog should be open")
    
    page.add(
        ft.Container(
            padding=30,
            content=ft.Column(
                controls=[
                    ft.Text("Test Intervention", size=24),
                    ft.ElevatedButton(
                        "➕ Nouvelle intervention",
                        bgcolor=ft.Colors.BLUE,
                        color=ft.Colors.WHITE,
                        on_click=open_intervention_dialog,
                    ),
                ],
            ),
        )
    )

ft.app(target=main)
