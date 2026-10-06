import os
import tempfile
import pandas as pd

from fastapi import UploadFile
from io import BytesIO

from langchain_community.document_loaders import (
    CSVLoader,
    Docx2txtLoader,
    PyMuPDFLoader,
    TextLoader,
    UnstructuredExcelLoader,
)
from langchain_core.documents import Document
from core.constants import constants


class DocumentParser:

    LOADERS = {
        constants.TXT_EXT: TextLoader,
        constants.CSV_EXT: CSVLoader,
        constants.PDF_EXT: PyMuPDFLoader,
        constants.DOCX_EXT: Docx2txtLoader,
        constants.XLS_EXT: UnstructuredExcelLoader,
    }

    @staticmethod
    async def extract_documents(file: UploadFile):
        """
        Extract documents using LangChain document loaders.

        Returns:
            list[Document]
        """

        if not file.filename:
            return ValueError(constants.INVALID_FILE)

        extension = (
            constants.DOT
            + file.filename.split(
                constants.DOT
            )[-1].lower()
        )

        if extension not in constants.ALLOWED_EXT:
            return ValueError(
                f"Unsupported file type: {extension}.\n"
                f"Allowed types: {constants.ALLOWED_EXT}"
            )

        loader_class = DocumentParser.LOADERS.get(extension)

        if not loader_class:
            return ValueError(f"No loader configured for: {extension}")

        content = await file.read()
        temp_path = None
        try:
            suffix = extension
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
                temp_file.write(content)
                temp_path = temp_file.name

            if extension == constants.TXT_EXT:
                loader = loader_class(temp_path, encoding=constants.UTF)

            elif extension == constants.CSV_EXT:
                loader = loader_class(temp_path, encoding=constants.UTF)

            elif extension in (constants.XLS_EXT):
                excel = pd.ExcelFile(BytesIO(content))
                documents = []
                for sheet_name in excel.sheet_names:
                    df = pd.read_excel(excel, sheet_name=sheet_name)
                    text = df.to_string(index=False)

                    if text.strip():
                        documents.append(
                            Document(
                                page_content=text,
                                metadata={
                                    constants.FILE_NAME: file.filename,
                                    constants.TYPE: constants.EXCEL,
                                    constants.SHEET: sheet_name
                                }
                            )
                        )

                return documents

            else:
                loader = loader_class(temp_path)

            documents = loader.load()

            for document in documents:
                document.metadata[constants.FILE_NAME] = file.filename
                document.metadata[constants.FILE_EXT] = extension

            return documents

        finally:
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
