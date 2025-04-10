from django.apps import AppConfig
from django.db import connection
from django.db.migrations.executor import MigrationExecutor

class backendConfig(AppConfig):
    name = 'backend'

    """
    Setuo để run_initial_setup() chạy sau các lệnh migrations và migrate
    """
    def ready(self):
        print("backendConfig ready")
        # Kiểm tra xem đang chạy migrate không
        if self.is_running_migrate():
            return  # Không chạy setup trong quá trình migrate
        # Kiểm tra xem migrations đã áp dụng hết chưa
        if self.migrations_applied():
            from .initial import run_initial_setup
            run_initial_setup()

    def is_running_migrate(self):
        import sys
        return 'migrate' in sys.argv  # Trả về True nếu đang chạy lệnh migrate

    def migrations_applied(self):
        executor = MigrationExecutor(connection)
        plan = executor.migration_plan(executor.loader.graph.leaf_nodes())
        return len(plan) == 0  # Trả về True nếu không còn migrations nào cần áp dụng
