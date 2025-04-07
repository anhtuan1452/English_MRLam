from django.apps import AppConfig

class DocumentManagementConfig(AppConfig):  # Đổi tên class
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'DocumentManagement'  # Đảm bảo tên app đúng
    verbose_name = "Quản lý tài liệu"