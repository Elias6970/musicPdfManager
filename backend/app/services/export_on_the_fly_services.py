from sqlmodel import Session

from backend.app.models.export_on_the_fly.export_on_the_fly import ExportOnTheFly, ExportOnTheFlyCreate, ExportOnTheFlyRequest

def create_export_on_the_fly(session: Session, user_id:int, request: ExportOnTheFlyRequest):
    pass