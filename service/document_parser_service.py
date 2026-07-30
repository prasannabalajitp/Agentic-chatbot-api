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
            text = constants.EMPTY_STRING
            for page in pdf:
                text += page.get_text()

            pdf.close()
            return text
        
        if extension == constants.DOCX_EXT:
            document = Document(BytesIO(content))
            text = []
            # Normal paragraphs
            for p in document.paragraphs:
                if p.text.strip():
                    text.append(p.text.strip())

            # Tables
            for table in document.tables:
                for row in table.rows:
                    for cell in row.cells:
                        cell_text = cell.text.strip()
                        if cell_text:
                            text.append(cell_text)

            return "\n".join(text)
