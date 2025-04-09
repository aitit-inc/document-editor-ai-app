"""
Document models module for the PyQt6 desktop application.
Contains data models used in document processing.
"""

from enum import Enum
from pydantic import BaseModel, Field


class ProcessingMode(str, Enum):
    """Enum for processing modes"""

    ASK = "ask"
    EDIT = "edit"


class DocumentRequest(BaseModel):
    """
    Request model for document processing
    """

    mode: ProcessingMode
    prompt: str
    content: str = Field(default="")
