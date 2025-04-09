"""
UI Components module for the PyQt6 desktop application.
Contains reusable UI widgets used across the application.
"""

from PyQt6.QtWidgets import QTextEdit, QVBoxLayout, QFrame
from PyQt6.QtGui import QTextCursor
from PyQt6.QtCore import Qt


class ChatBubble(QFrame):
    """Widget for displaying chat messages in the Document Creator"""

    def __init__(self, message_text: str, is_user: bool, parent=None):
        super().__init__(parent)
        self.setObjectName("ChatBubble")

        # Configure frame appearance
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setFrameShadow(QFrame.Shadow.Raised)
        self.setStyleSheet(
            f"border-radius: 10px; " f"padding: 5px; " f"margin: 0px 5px 0px 5px; "
        )

        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(2, 2, 2, 2)

        # Add message text
        self.message = QTextEdit()
        self.message.setReadOnly(True)
        self.message.setText(message_text)
        self.message.setStyleSheet(
            "background-color: transparent; border: none; color: #222222; padding: 0px;"
        )

        # Adjust height based on content
        self.message.document().documentLayout().documentSizeChanged.connect(
            self.adjust_text_edit_height
        )

        layout.addWidget(self.message)
        self.setLayout(layout)

        # Set maximum width based on parent
        if parent:
            self.setMaximumWidth(int(parent.width() * 0.8))

    def adjust_text_edit_height(self):
        """Adjust QTextEdit height based on content"""
        doc_height = self.message.document().size().height()
        self.message.setFixedHeight(int(doc_height + 5))
