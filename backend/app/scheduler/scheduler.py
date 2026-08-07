from apscheduler.schedulers.background import BackgroundScheduler

# --------------------------------------------------------------------------------------
# Scheduler global utilizado para registrar y ejecutar tareas programadas.
# Todas las fechas se manejan internamente en UTC.
# --------------------------------------------------------------------------------------
scheduler: BackgroundScheduler = BackgroundScheduler(
    timezone="UTC"
)