import flet as ft
from datetime import datetime, timedelta
import calendar as cal


def create_custom_date_picker(page, initial_date, on_date_selected):
    """
    Crée un date picker personnalisé amélioré
    """
    current_date = initial_date if initial_date else datetime.now()
    selected_date = current_date
    
    def close_picker(e):
        page.close(dialog)
    
    def select_date(date_obj):
        nonlocal selected_date
        selected_date = date_obj
        on_date_selected(date_obj)
        page.close(dialog)
    
    def on_year_change(e):
        nonlocal current_date
        current_date = datetime(int(year_dropdown.value), current_date.month, 1)
        update_calendar()
    
    def on_month_change(e):
        nonlocal current_date
        current_date = datetime(current_date.year, int(month_dropdown.value), 1)
        update_calendar()
    
    def create_calendar_grid():
        """Crée la grille du calendrier"""
        month_cal = cal.monthcalendar(current_date.year, current_date.month)
        
        # En-têtes jours
        headers = ft.Row(
            controls=[
                ft.Container(
                    width=35,
                    height=25,
                    content=ft.Text(day, size=11, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    alignment=ft.alignment.center,
                )
                for day in ["Lu", "Ma", "Me", "Je", "Ve", "Sa", "Di"]
            ],
            spacing=2,
        )
        
        # Grille des jours
        rows = []
        today = datetime.now().date()
        
        for week in month_cal:
            day_buttons = []
            for day in week:
                if day == 0:
                    day_buttons.append(ft.Container(width=35, height=35))
                else:
                    date_obj = datetime(current_date.year, current_date.month, day)
                    is_today = date_obj.date() == today
                    is_selected = (selected_date and 
                                 date_obj.year == selected_date.year and 
                                 date_obj.month == selected_date.month and 
                                 date_obj.day == selected_date.day)
                    
                    if is_selected:
                        bg_color = ft.Colors.BLUE
                        text_color = ft.Colors.WHITE
                    elif is_today:
                        bg_color = ft.Colors.with_opacity(0.2, ft.Colors.BLUE)
                        text_color = ft.Colors.WHITE
                    else:
                        bg_color = None
                        text_color = ft.Colors.WHITE
                    
                    day_buttons.append(
                        ft.Container(
                            width=35,
                            height=35,
                            bgcolor=bg_color,
                            border_radius=17,
                            content=ft.TextButton(
                                text=str(day),
                                on_click=lambda e, d=date_obj: select_date(d),
                                style=ft.ButtonStyle(color=text_color, padding=0),
                            ),
                            alignment=ft.alignment.center,
                        )
                    )
            
            rows.append(ft.Row(controls=day_buttons, spacing=2))
        
        return ft.Column(controls=[headers] + rows, spacing=3)
    
    # Dropdowns pour année et mois
    current_year = datetime.now().year
    years = list(range(current_year - 10, current_year + 5))
    
    year_dropdown = ft.Dropdown(
        width=100,
        value=str(current_date.year),
        options=[ft.dropdown.Option(str(y)) for y in years],
        on_change=on_year_change,
        text_size=14,
    )
    
    months = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ]
    
    month_dropdown = ft.Dropdown(
        width=130,
        value=str(current_date.month),
        options=[ft.dropdown.Option(str(i+1), text=months[i]) for i in range(12)],
        on_change=on_month_change,
        text_size=14,
    )
    
    header = ft.Row(
        controls=[month_dropdown, year_dropdown],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )
    
    calendar_grid = create_calendar_grid()
    
    calendar_container = ft.Column(
        controls=[header, calendar_grid],
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
    )
    
    def update_calendar():
        year_dropdown.value = str(current_date.year)
        month_dropdown.value = str(current_date.month)
        calendar_container.controls[1] = create_calendar_grid()
        page.update()
    
    dialog = ft.AlertDialog(
        modal=True,
        title=ft.Text("Choisir une date", size=16),
        content=ft.Container(
            content=calendar_container,
            padding=10,
            width=280,
        ),
        actions=[ft.TextButton("Annuler", on_click=close_picker)],
        actions_alignment=ft.MainAxisAlignment.CENTER,
    )
    
    return dialog


def create_inline_calendar(page, initial_date, on_date_selected):
    """
    Crée un calendrier intégré (pas un dialog) pour être affiché inline
    """
    current_date = [initial_date if initial_date else datetime.now()]
    selected_date = current_date[0]
    
    def select_date(date_obj):
        on_date_selected(date_obj)
    
    def on_year_change(e):
        current_date[0] = datetime(int(year_dropdown.value), current_date[0].month, 1)
        update_calendar()
    
    def on_month_change(e):
        current_date[0] = datetime(current_date[0].year, int(month_dropdown.value), 1)
        update_calendar()
    
    def create_calendar_grid():
        month_cal = cal.monthcalendar(current_date[0].year, current_date[0].month)
        
        headers = ft.Row(
            controls=[
                ft.Container(
                    width=35,
                    height=25,
                    content=ft.Text(day, size=11, weight=ft.FontWeight.BOLD, text_align=ft.TextAlign.CENTER),
                    alignment=ft.alignment.center,
                )
                for day in ["Lu", "Ma", "Me", "Je", "Ve", "Sa", "Di"]
            ],
            spacing=2,
        )
        
        rows = []
        today = datetime.now().date()
        
        for week in month_cal:
            day_buttons = []
            for day in week:
                if day == 0:
                    day_buttons.append(ft.Container(width=35, height=35))
                else:
                    date_obj = datetime(current_date[0].year, current_date[0].month, day)
                    is_today = date_obj.date() == today
                    
                    if is_today:
                        bg_color = ft.Colors.with_opacity(0.2, ft.Colors.BLUE)
                        text_color = ft.Colors.WHITE
                    else:
                        bg_color = None
                        text_color = ft.Colors.WHITE
                    
                    day_buttons.append(
                        ft.Container(
                            width=35,
                            height=35,
                            bgcolor=bg_color,
                            border_radius=17,
                            content=ft.TextButton(
                                text=str(day),
                                on_click=lambda e, d=date_obj: select_date(d),
                                style=ft.ButtonStyle(color=text_color, padding=0),
                            ),
                            alignment=ft.alignment.center,
                        )
                    )
            
            rows.append(ft.Row(controls=day_buttons, spacing=2))
        
        return ft.Column(controls=[headers] + rows, spacing=3)
    
    current_year = datetime.now().year
    years = list(range(current_year - 10, current_year + 5))
    
    year_dropdown = ft.Dropdown(
        width=100,
        value=str(current_date[0].year),
        options=[ft.dropdown.Option(str(y)) for y in years],
        on_change=on_year_change,
        text_size=14,
    )
    
    months = [
        "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
        "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
    ]
    
    month_dropdown = ft.Dropdown(
        width=130,
        value=str(current_date[0].month),
        options=[ft.dropdown.Option(str(i+1), text=months[i]) for i in range(12)],
        on_change=on_month_change,
        text_size=14,
    )
    
    header = ft.Row(
        controls=[month_dropdown, year_dropdown],
        alignment=ft.MainAxisAlignment.CENTER,
        spacing=10,
    )
    
    calendar_grid_container = ft.Container(content=create_calendar_grid())
    
    def update_calendar():
        year_dropdown.value = str(current_date[0].year)
        month_dropdown.value = str(current_date[0].month)
        calendar_grid_container.content = create_calendar_grid()
        page.update()
    
    return ft.Column(
        controls=[header, calendar_grid_container],
        spacing=15,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
        width=280,
    )
