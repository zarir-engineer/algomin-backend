# routes/html_to_audio_api.py
from fastapi import APIRouter, UploadFile, Form
from tools.html_to_audio import extract_selected_text_from_html, text_to_audio

router = APIRouter()

@router.post("/html-to-audio/")
async def html_to_audio(file: UploadFile, selectors: str = Form(...)):
    content = await file.read()
    selectors_list = selectors.split(',')
    text = extract_selected_text_from_html(content.decode(), selectors_list)
    output_path = text_to_audio(text)
    return {"message": "Success", "output_file": output_path}
