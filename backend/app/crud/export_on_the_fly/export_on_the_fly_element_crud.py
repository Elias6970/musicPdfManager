from sqlmodel import Session

from backend.app.models.export_on_the_fly.export_on_the_fly_element import ExportOnTheFlyElement, ExportOnTheFlyElementCreate


def save_export_on_the_fly_element(session: Session, element_data: ExportOnTheFlyElementCreate) -> ExportOnTheFlyElement:
    """
    Save a new export on the fly element record to the database.

    Args:
        session (Session): The database session.
        element_data (ExportOnTheFlyElementCreate): The export on the fly element data to save.

    Returns:
        ExportOnTheFlyElement: The saved export on the fly element record.
    """
    db_obj = ExportOnTheFlyElement.model_validate(element_data)
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj

def save_export_on_the_fly_elements(session: Session, elements_data: list[ExportOnTheFlyElementCreate]) -> list[ExportOnTheFlyElement]:
    """
    Save multiple export on the fly element records to the database.

    Args:
        session (Session): The database session.
        elements_data (list[ExportOnTheFlyElementCreate]): A list of export on the fly element data to save.

    Returns:
        list[ExportOnTheFlyElement]: A list of saved export on the fly element records.
    """
    db_objs = [ExportOnTheFlyElement.model_validate(element) for element in elements_data]
    session.add_all(db_objs)
    session.commit()
    for db_obj in db_objs:
        session.refresh(db_obj)
    return db_objs

def get_export_on_the_fly_element_by_id(session: Session, element_id: int) -> ExportOnTheFlyElement | None:
    """
    Retrieve an export on the fly element record by its ID.

    Args:
        session (Session): The database session.
        element_id (int): The ID of the export on the fly element record.

    Returns:
        ExportOnTheFlyElement | None: The export on the fly element record if found, otherwise None.
    """
    return session.get(ExportOnTheFlyElement, element_id)

def delete_export_on_the_fly_element(session: Session, element_id: int) -> bool:
    """
    Delete an export on the fly element record by its ID.

    Args:
        session (Session): The database session.
        element_id (int): The ID of the export on the fly element record to delete.

    Returns:
        bool: True if the record was deleted, False if not found.
    """
    element = session.get(ExportOnTheFlyElement, element_id)
    if not element:
        return False
    session.delete(element)
    session.commit()
    return True

def update_export_on_the_fly_element(session: Session, element_id: int, element_data: ExportOnTheFlyElementCreate) -> ExportOnTheFlyElement | None:
    """
    Update an existing export on the fly element record.

    Args:
        session (Session): The database session.
        element_id (int): The ID of the export on the fly element record to update.
        element_data (ExportOnTheFlyElementCreate): The new data for the export on the fly element.

    Returns:
        ExportOnTheFlyElement | None: The updated export on the fly element record if found, otherwise None.
    """
    element = session.get(ExportOnTheFlyElement, element_id)
    if not element:
        return None

    # Update fields if provided
    for field, value in element_data.model_dump(exclude_unset=True).items():
        setattr(element, field, value)

    session.add(element)
    session.commit()
    session.refresh(element)
    return element