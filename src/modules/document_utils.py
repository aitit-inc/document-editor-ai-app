"""
Document utilities module for the PyQt6 desktop application.
Contains utility functions for document processing and handling.
"""

from PyQt6.QtWidgets import QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QTextCursor


def add_chat_message(chat_history: QTextEdit, text: str, is_user: bool):
    """
    Add a message to the chat history with appropriate styling

    Args:
        chat_history: The QTextEdit widget containing chat history
        text: Message content to add
        is_user: True if message is from the user, False if from AI
    """
    # Create cursor for inserting text
    cursor = chat_history.textCursor()
    cursor.movePosition(QTextCursor.MoveOperation.End)

    # Set alignment based on who's sending the message
    format = cursor.blockFormat()
    if is_user:
        format.setAlignment(Qt.AlignmentFlag.AlignRight)
    else:
        format.setAlignment(Qt.AlignmentFlag.AlignLeft)
    cursor.setBlockFormat(format)

    # Create message bubble with styling
    if is_user:
        bubble_style = "border: 2px solid #007bff; border-radius: 10px; padding: 5px; white-space: pre-wrap;"
    else:
        bubble_style = "border: 2px solid #6c757d; border-radius: 10px; padding: 5px; white-space: pre-wrap;"
    message_html = f"""
    <div style="{bubble_style}; margin: 5px; display: inline-block; max-width: 80%; text-align: left;">
        {text}
    </div>
    """

    # Insert HTML and a new line
    cursor.insertHtml(message_html)
    cursor.insertBlock()

    # Set cursor position to the end
    chat_history.setTextCursor(cursor)

    # Scroll to bottom
    chat_history.verticalScrollBar().setValue(
        chat_history.verticalScrollBar().maximum()
    )
