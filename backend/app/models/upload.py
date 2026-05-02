from pydantic import BaseModel

class UploadStagingResponse(BaseModel):
    file_id: str
    original_filename: str
    size_bytes: int
    message: str

class UploadToFolderResponse(BaseModel):
    folder_id: str
    original_filename: str
    size_bytes: int
    message: str
