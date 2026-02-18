import flet as ft
from database import Database
import shutil
import os
from pathlib import Path
from datetime import datetime


class SettingsView(ft.Container):
    def __init__(self, page: ft.Page, db: Database):
        super().__init__()
        self.page = page
        self.db = db
        self.expand = True
        self.bgcolor = ft.Colors.with_opacity(0.95, "#0f172a")
        
        self.build_view()
    
    def build_view(self):
        """Construit la vue des paramètres"""
        header = ft.Container(
            padding=30,
            bgcolor=ft.Colors.with_opacity(0.8, "#0f172a"),
            content=ft.Row(
                controls=[
                    ft.Text("Paramètres", size=28, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
        )
        
        # Informations base de données
        db_path = self.db.db_name
        db_size = self.get_db_size()
        
        db_info_section = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=20),
            content=ft.Container(
                padding=25,
                bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
                border_radius=16,
                content=ft.Column(
                    controls=[
                        ft.Text("💾 Base de données", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Divider(height=20, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                        
                        ft.Row([
                            ft.Text("Emplacement :", weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(str(db_path), size=13, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                        ], spacing=10),
                        
                        ft.Row([
                            ft.Text("Taille :", weight=ft.FontWeight.BOLD, size=14),
                            ft.Text(db_size, size=13, color=ft.Colors.with_opacity(0.7, ft.Colors.WHITE)),
                        ], spacing=10),
                        
                        ft.Divider(height=20, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                        
                        ft.Row([
                            ft.ElevatedButton(
                                "💾 Sauvegarder la base de données",
                                icon=ft.Icons.SAVE,
                                bgcolor=ft.Colors.BLUE,
                                color=ft.Colors.WHITE,
                                on_click=self.backup_database,
                            ),
                            ft.ElevatedButton(
                                "📥 Restaurer depuis un fichier",
                                icon=ft.Icons.UPLOAD_FILE,
                                bgcolor=ft.Colors.GREEN,
                                color=ft.Colors.WHITE,
                                on_click=self.restore_database,
                            ),
                        ], spacing=15),
                    ],
                    spacing=15,
                ),
            ),
        )
        
        # Section À propos
        about_section = ft.Container(
            padding=ft.padding.symmetric(horizontal=40, vertical=20),
            content=ft.Container(
                padding=25,
                bgcolor=ft.Colors.with_opacity(0.95, "#1e293b"),
                border_radius=16,
                content=ft.Column(
                    controls=[
                        ft.Text("ℹ️ À propos", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
                        ft.Divider(height=20, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                        
                        ft.Row([
                            ft.Icon(ft.Icons.COMPUTER, size=48, color=ft.Colors.BLUE),
                            ft.Column([
                                ft.Text("OrdiFacile", size=22, weight=ft.FontWeight.BOLD),
                                ft.Text("Gestion Clients & Interventions", size=14, color=ft.Colors.with_opacity(0.6, ft.Colors.WHITE)),
                                ft.Text("Version 1.0.0", size=13, italic=True),
                            ], spacing=5),
                        ], spacing=20),
                        
                        ft.Divider(height=20, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                        
                        ft.Text("© 2026 OrdiFacile - Tous droits réservés", size=12, color=ft.Colors.with_opacity(0.5, ft.Colors.WHITE)),
                    ],
                    spacing=15,
                ),
            ),
        )
        
        main_content = ft.Column(
            controls=[header, db_info_section, about_section],
            spacing=0,
            expand=True,
            scroll=ft.ScrollMode.AUTO,
        )
        
        self.content = main_content
    
    def get_db_size(self):
        """Récupère la taille de la base de données"""
        try:
            size_bytes = os.path.getsize(self.db.db_name)
            if size_bytes < 1024:
                return f"{size_bytes} octets"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.2f} Ko"
            else:
                return f"{size_bytes / (1024 * 1024):.2f} Mo"
        except:
            return "Inconnu"
    
    def backup_database(self, e):
        """Sauvegarde la base de données"""
        try:
            # Nom du fichier de sauvegarde avec timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"ordifacile_backup_{timestamp}.db"
            
            # Demander où sauvegarder
            def on_file_picker_result(e: ft.FilePickerResultEvent):
                if e.path:
                    try:
                        # Copier la base de données
                        shutil.copy2(self.db.db_name, e.path)
                        
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"✅ Sauvegarde créée : {Path(e.path).name}"),
                            bgcolor=ft.Colors.GREEN,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                    except Exception as ex:
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"❌ Erreur lors de la sauvegarde : {str(ex)}"),
                            bgcolor=ft.Colors.RED,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
            
            # Créer le file picker
            file_picker = ft.FilePicker(on_result=on_file_picker_result)
            self.page.overlay.append(file_picker)
            self.page.update()
            
            # Ouvrir le dialogue de sauvegarde
            file_picker.save_file(
                dialog_title="Sauvegarder la base de données",
                file_name=backup_name,
                allowed_extensions=["db"],
            )
            
        except Exception as ex:
            self.page.snack_bar = ft.SnackBar(
                content=ft.Text(f"❌ Erreur : {str(ex)}"),
                bgcolor=ft.Colors.RED,
            )
            self.page.snack_bar.open = True
            self.page.update()
    
    def restore_database(self, e):
        """Restaure la base de données depuis un fichier"""
        def on_file_picker_result(e: ft.FilePickerResultEvent):
            if e.files and len(e.files) > 0:
                source_path = e.files[0].path
                
                # Demander confirmation
                def confirm_restore(e):
                    try:
                        # Créer une sauvegarde de sécurité avant de restaurer
                        backup_safety = str(self.db.db_name) + ".before_restore"
                        shutil.copy2(self.db.db_name, backup_safety)
                        
                        # Copier le fichier de restauration
                        shutil.copy2(source_path, self.db.db_name)
                        
                        self.page.close(confirm_dialog)
                        
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text("✅ Base de données restaurée ! Redémarrez l'application."),
                            bgcolor=ft.Colors.GREEN,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                        
                    except Exception as ex:
                        self.page.close(confirm_dialog)
                        self.page.snack_bar = ft.SnackBar(
                            content=ft.Text(f"❌ Erreur lors de la restauration : {str(ex)}"),
                            bgcolor=ft.Colors.RED,
                        )
                        self.page.snack_bar.open = True
                        self.page.update()
                
                def cancel_restore(e):
                    self.page.close(confirm_dialog)
                
                confirm_dialog = ft.AlertDialog(
                    modal=True,
                    title=ft.Text("⚠️ Confirmer la restauration"),
                    content=ft.Text(
                        "Êtes-vous sûr de vouloir restaurer cette base de données ?\n\n"
                        "ATTENTION : Toutes les données actuelles seront remplacées !\n"
                        "Une sauvegarde de sécurité sera créée automatiquement.",
                        size=14,
                    ),
                    actions=[
                        ft.TextButton("Annuler", on_click=cancel_restore),
                        ft.ElevatedButton(
                            "Restaurer",
                            bgcolor=ft.Colors.ORANGE,
                            color=ft.Colors.WHITE,
                            on_click=confirm_restore,
                        ),
                    ],
                    actions_alignment=ft.MainAxisAlignment.END,
                )
                
                self.page.open(confirm_dialog)
        
        # Créer le file picker
        file_picker = ft.FilePicker(on_result=on_file_picker_result)
        self.page.overlay.append(file_picker)
        self.page.update()
        
        # Ouvrir le dialogue de sélection
        file_picker.pick_files(
            dialog_title="Choisir une sauvegarde à restaurer",
            allowed_extensions=["db"],
            allow_multiple=False,
        )
