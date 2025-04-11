"""
AI Agent module for the PyQt6 desktop application.
Provides AI functionality powered by LangGraph and OpenAI.
Handles conversation flow and model interaction.
"""

import os
import re
from typing import List, Dict, Any, Optional, Tuple, Union

# LangGraph imports
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, END

# Pydantic imports
from pydantic import BaseModel

# Import app config
from modules.config import config


class DocumentResponse(BaseModel):
    """
    Response model for document processing
    """

    message: str
    edited_content: Optional[str] = None


class DocumentAIAgent:
    """
    AI Agent class that provides AI functionality using
    LangGraph and OpenAI for document processing.
    Handles conversation flow and model interaction.
    Returns a structured response with both message and edited content.
    """

    def __init__(self):
        """
        Initialize the AI Agent.
        """
        # Create message queue for chat history
        self.messages = []
        self.model = None
        self.agent = None

        # Store current configuration values for change detection
        self._current_api_key = None
        self._current_model_name = None

        # Initialize with current settings
        self._update_configuration()

        # Initialize message history
        self.initialize_history()

    def _update_configuration(self) -> bool:
        """
        Check and update configuration if settings have changed.

        Returns:
            bool: True if configuration was updated, False otherwise
        """
        # Get current settings from config
        api_key = config.OPEN_AI_API_KEY
        model_name = config.AI_MODEL_NAME

        # Check if settings have changed
        if api_key == self._current_api_key and model_name == self._current_model_name:
            return False  # No changes

        # Store new settings
        self._current_api_key = api_key
        self._current_model_name = model_name

        # Reset model
        self.model = None
        self.agent = None

        if not api_key:
            print(
                "Warning: OPEN_AI_API_KEY is not set in config. AI chat functionality will be limited."
            )
            return True

        try:
            # Initialize the model using config values
            self.model = ChatOpenAI(
                api_key=api_key,
                model=model_name,
                temperature=0.7,
            )

            self.model = self.model.with_structured_output(DocumentResponse)

            # Setup LangGraph for conversation management
            self._setup_langgraph()
            return True
        except Exception as e:
            print(f"Error setting up AI agent: {e}")
            self.model = None
            return True

    def initialize_history(self):
        """
        Initialize the message history with a system message.
        """
        self.messages = [
            SystemMessage(
                content="あなたは優秀な社会保険労務士です。ユーザーの指示に従って、質問対応や書類作成・編集を行います。"
            )
        ]

    def _setup_langgraph(self):
        """Set up LangGraph for conversation flow"""
        # Define state schema
        workflow = StateGraph(MessagesState)

        # Define the model calling function
        def call_model(state):
            messages = state["messages"]
            if not self.model:
                return {
                    "messages": [
                        AIMessage(
                            content="APIキーが設定されていないため、応答できません。"
                        )
                    ]
                }

            response = self.model.invoke(messages)
            return {"messages": [response]}

        # Add nodes and edges
        workflow.add_node("agent", call_model)
        workflow.set_entry_point("agent")
        workflow.add_edge("agent", END)

        # Compile graph
        self.agent = workflow.compile()

    def process_document_request(
        self, prompt: str, content: str, is_edit_mode: bool
    ) -> DocumentResponse:
        """
        Process document request and return a structured response.

        Args:
            prompt: The user's prompt/instruction
            content: The current document content
            is_edit_mode: Whether this is an edit request (True) or question (False)

        Returns:
            DocumentResponse containing message and optionally edited content
        """
        # Check for configuration updates before processing
        self._update_configuration()

        if not self.model:
            return DocumentResponse(
                message="APIキーが設定されていないため、応答できません。設定画面でAPIキーを設定してください。",
                edited_content=None,
            )

        try:
            # Prepare system message based on mode
            #             if is_edit_mode:
            #                 system_message = SystemMessage(
            #                     content="""あなたは書類作成アシスタントです。ユーザーの指示に従って提供されたテキストを編集してください。
            #
            # 回答形式:
            # 1. 最初に編集内容の説明を記載してください。
            # 2. その後に明確な区切り「===編集後のテキスト===」を入れてください。
            # 3. その後に編集後のテキスト全体を記載してください。
            #
            # 例:
            # 「文章を簡潔にしました。また、誤字を修正し、段落を整理しました。」
            #
            # ===編集後のテキスト===
            # （編集後のテキスト全体）
            # """
            #                 )
            #             else:
            #                 system_message = SystemMessage(
            #                     content="あなたは書類作成アシスタントです。ユーザーが提供したテキストについての質問に答えてください。"
            #                 )

            # Prepare user message with content
            if is_edit_mode:
                user_instruction = "指示に基づいてテキストを編集してください。"
            else:
                user_instruction = "質問に答えてください（テキスト編集は不要）。"

            user_input = f"{user_instruction}\n\n{prompt}\n\n【テキスト】\n{content}"
            user_message = HumanMessage(content=user_input)
            user_message_hor_history = HumanMessage(content=prompt)

            # Get response
            input_to_ai = [*self.messages, user_message]
            # print(f"Input to AI: {input_to_ai}")
            response = self.model.invoke(input_to_ai)

            # チャット履歴にはユーザーが入力したプロンプトのみ追加
            self.messages.append(user_message_hor_history)

            message, edited_content = response.message, response.edited_content
            if is_edit_mode:
                # # Parse response for edit mode
                # message, edited_content = self._parse_edit_response(
                #     response.content, content
                # )
                # Only add the 'message' part to history

                self.messages.append(AIMessage(content=message))
                return response
            else:
                if edited_content:
                    print(
                        f"WARNING: Edited content was returned in question mode: {edited_content}"
                    )

                # For question mode, just return the response
                self.messages.append(AIMessage(content=message))
                return DocumentResponse(message=message, edited_content=None)

        except Exception as e:
            print(f"Error processing document request: {e}")
            return DocumentResponse(
                message=f"エラーが発生しました: {str(e)}", edited_content=None
            )

    def _parse_edit_response(
        self, response: str, original_content: str
    ) -> Tuple[str, str]:
        """
        Parse the AI response to extract the message and edited content.

        Args:
            response: The full AI response
            original_content: The original document content

        Returns:
            Tuple of (message, edited_content)
        """
        # Look for the separator
        separator = "===編集後のテキスト==="

        if separator in response:
            # Split by the separator
            parts = response.split(separator, 1)
            message = parts[0].strip()
            edited_content = parts[1].strip()
        else:
            # If no separator found, treat whole response as the edited content
            # but also add a note in the message
            message = (
                "編集を行いました。（注：AIの回答形式が標準形式ではありませんでした）"
            )
            edited_content = response

        return message, edited_content
