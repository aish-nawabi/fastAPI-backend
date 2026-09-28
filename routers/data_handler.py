from fastapi import APIRouter, UploadFile, File, HTTPException, Query
import uuid as uuid_pkg
import os

from src.data_store import data_store

from src.utils.pdf_processor import extract_text_from_pdf

from src.utils.llm_client import get_llm_response

router = APIRouter()

UPLOAD_DIR = "/tmp/cag_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload/{uuid}", status_code=201)
def upload_pdf(uuid: uuid_pkg.UUID, file: UploadFile = File(...)):
    """
    Uploads a PDF file associated with a specific UUID.
    Extracts text from the PDF and stores it in the data store.
    If the UUID already exists, it raises an error (use PUT to update).
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. Only PDF files are accepted."
        )
    uuid_str = str(uuid)
    if uuid_str in data_store:
        raise HTTPException(
            status_code=400,
            detail=F"UUID  {uuid_str}  already exists. Use PUT /API/V1/update/{uuid_str} to append data.",
        )
    file_path = os.path.join(UPLOAD_DIR, f"{uuid_str}_{file.filename}")
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        extracted_text = extract_text_from_pdf(file_path)
        if extracted_text is None:
            raise HTTPException(
                status_code=500, detail="Failed to extract text from PDF."
            )
        data_store[uuid_str] = extracted_text
        return {
            "message": "File uploaded and text extracted successfully",
            "uuid":uuid_str,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occured during file processing: {str(e)}",
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@router.put("/update/{uuid}")
def update_pdf_data(uuid: uuid_pkg.UUID, file: UploadFile = File(...)):
    """
    Appends text extracted from a new PDF file to the existing data for a given uuid.
    If the UUID does not exist, it raises an error.
    """
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400, detail="Invalid file type. only PDF files are accepted"
        )
    uuid_str = str(uuid)
    if uuid_str not in data_store:
        raise HTTPException(
            status_code=404,
            detail=f"UUID {uuid_str} not found. use POST /api/v1/upload/{uuid_str} to create it first.",
        )
    file_path = os.path.join(UPLOAD_DIR, f"{uuid_str}_update_{file.filename}")
    try:
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())
        new_text = extract_text_from_pdf(file_path)

        if new_text is None:
            raise HTTPException(
                status_code=500, detail="Failed to extract text from PDF."
            )
        data_store[uuid_str] += "/n/n" + new_text
        return {"message": "Data appended succesfully", "uuid": uuid_str}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occured during file processing: {str(e)}",
        )
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)

@router.get("/query/{uuid}")
def querry_data(uuid: uuid_pkg.UUID, query: str = Query(..., min_length=1)):
    """
    Retrives the stored text for a given UUID And sends it along with a querry
    to a paceholder LLM service.
    Returns the placeholder response.
    """
    uuid_str = str(uuid)
    if uuid_str not in data_store:
        raise HTTPException(
            status_code=404, detail=f"UUID (uuid_str) not found."
        )
    stored_text = data_store[uuid_str]
    llm_response = get_llm_response(context=stored_text, query=query)
    return {"uuid": uuid_str, "query": query, "llm_response": llm_response}

@router.delete("/data/{uuid}", status_code=200)
def delete_data(uuid: uuid_pkg.UUID):
    """
    Deletes the data associated with a specific UUID from the data store.
    """

    uuid_str = str(uuid)
    if uuid_str not in data_store:
        raise HTTPException(
            status_code=404, detail=f"UUID {uuid_str} not found."
        )
    del data_store[uuid_str]
    return {"message":f"Data for UUID {uuid_str} deleted succesfully."}

@router.get("/list_uuids")
def list_all_uuid():
     """
     Returns a list of all UUIDs currently stored.
     """
     return {"uuids":list(data_store.keys())}    




