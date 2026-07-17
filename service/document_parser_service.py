from io import BytesIO
from fastapi import UploadFile
import fitz
from docx import Document

from core.constants import constants

class DocumentParser:

    @staticmethod
    async def extract_text(file: UploadFile) -> str:
        extension = constants.DOT + file.filename.split(constants.DOT)[-1].lower()

        if extension not in constants.ALLOWED_EXT:
            raise ValueError(
                f"Unsupported file type: {extension}.\nAllowed types: {constants.ALLOWED_EXT}"
            )
        
        content = await file.read()

        if extension == constants.TXT_EXT:
            return content.decode(constants.UTF)
        
        if extension == constants.PDF_EXT:
            pdf = fitz.open(stream=content, filetype=constants.PDF)
            text = ""
            for page in pdf:
                text += page.get_text()

            pdf.close()
            return text
        
        if extension == constants.DOCX_EXT:
            document = Document(BytesIO(content))

            return "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
                if paragraph.text.strip()
            )
