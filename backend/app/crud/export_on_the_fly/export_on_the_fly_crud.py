
from sqlmodel import Session
from backend.app.models.export_on_the_fly.export_on_the_fly import ExportOnTheFly, ExportOnTheFlyCreate


def save_export_on_the_fly(session: Session, export_on_the_fly: ExportOnTheFlyCreate) -> ExportOnTheFly:
    """
    Save a new export on the fly record to the database.

    Args:
        session (Session): The database session.
        export_on_the_fly (ExportOnTheFlyCreate): The export on the fly data to save.

    Returns:
        ExportOnTheFly: The saved export on the fly record.
    """
    db_obj = ExportOnTheFly.model_validate(export_on_the_fly)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def get_export_on_the_fly_by_id(session: Session, export_id: int) -> ExportOnTheFly | None:
    """
    Retrieve an export on the fly record by its ID.

    Args:
        session (Session): The database session.
        export_id (int): The ID of the export on the fly record.

    Returns:
        ExportOnTheFly | None: The export on the fly record if found, otherwise None.
    """
    return session.get(ExportOnTheFly, export_id)


def delete_export_on_the_fly(session: Session, export_id: int) -> bool:
    """
    Delete an export on the fly record by its ID.

    Args:
        session (Session): The database session.
        export_id (int): The ID of the export on the fly record to delete.

    Returns:
        bool: True if the record was deleted, False if not found.
    """
    export_on_the_fly = session.get(ExportOnTheFly, export_id)
    if not export_on_the_fly:
        return False
    session.delete(export_on_the_fly)
    session.commit()
    return True


def update_export_on_the_fly(session: Session, export_id: int, export_data: ExportOnTheFlyCreate) -> ExportOnTheFly | None:
    """
    Update an existing export on the fly record.

    Args:
        session (Session): The database session.
        export_id (int): The ID of the export on the fly record to update.
        export_data (ExportOnTheFlyCreate): The new data for the export on the fly record.

    Returns:
        ExportOnTheFly | None: The updated export on the fly record if found, otherwise None.
    """
    db_obj = session.get(ExportOnTheFly, export_id)
    if not db_obj:
        return None
    updated_data = export_data.model_dump(exclude_unset=True)
    for key, value in updated_data.items():
        setattr(db_obj, key, value)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj
