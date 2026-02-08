"""
Cohere Chat Agent Service for processing user messages with natural language understanding.
Handles intent detection and MCP tool calling based on user input.
"""
import os
import logging
from typing import Dict, Any, List, Optional
from enum import Enum
import re
from uuid import UUID
from sqlmodel import Session
import cohere
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IntentType(Enum):
    """Types of intents that the chat agent can detect."""
    ADD_TASK = "add_task"
    LIST_TASKS = "list_tasks"
    COMPLETE_TASK = "complete_task"
    DELETE_TASK = "delete_task"
    UPDATE_TASK = "update_task"
    GENERAL_CHAT = "general_chat"

class CohereChatAgent:
    """
    AI agent that processes user messages using Cohere and calls appropriate MCP tools.
    Handles natural language understanding and intent detection for task operations.
    """

    def __init__(self, db_session: Session):
        self.db_session = db_session
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            raise ValueError("COHERE_API_KEY environment variable is not set")
        self.co = cohere.Client(api_key)

        # Import tool executor
        from ..services.tool_executor import ToolExecutor
        self.tool_executor = ToolExecutor(db_session)

        # Compile regex patterns for intent detection
        self.intent_patterns = {
            IntentType.ADD_TASK: [
                r'\b(add|create|make|new)\s+(a\s+)?(task|todo|item|to-do|work)\b',
                r'\b(make|create)\s+.*\b(for|to|that)\b',
                r'\b(want|need)\s+to\s+(do|complete|finish|buy|get|go)\b',
                r'\b(remind|remember)\s+me\s+to\b',
            ],
            IntentType.LIST_TASKS: [
                r'\b(list|show|display|view|see|get)\s+(my\s+)?(tasks|todos|items|to-dos)\b',
                r'\b(what|which)\s+(tasks|todos|items)\s+do\s+i\s+have\b',
                r'\b(show|list)\s+(all|my|current)\s+(tasks|todos)\b',
                r'\b(check|look\s+at)\s+(my\s+)?(tasks|todos)\b',
            ],
            IntentType.COMPLETE_TASK: [
                r'\b(complete|finish|done|mark\s+as\s+done|accomplish|check|tick)\s+(task|todo|item)\b',
                r'\b(mark|set)\s+(as\s+)?(complete|finished|done)\b',
                r'\b(done|completed|finished)\s+(task|todo|item)\b',
            ],
            IntentType.DELETE_TASK: [
                r'\b(delete|remove|eliminate|cancel|trash|erase)\s+(task|todo|item)\b',
                r'\b(get\s+rid\s+of|remove|clear)\s+(task|todo)\b',
            ],
            IntentType.UPDATE_TASK: [
                r'\b(update|change|modify|edit|adjust|revise)\s+(task|todo|item)\b',
                r'\b(change|modify|update)\s+(the\s+)?(title|description|details?)\s+of\b',
                r'\b(rename|reword)\s+(task|todo)\b',
            ]
        }

        # Pattern to extract title and description from user input
        self.title_desc_pattern = r'(?:to\s+)?(["\']?)([^"\'.!?]+?)\1(?:\s+(?:for|that|which|where|when)\s+([^"\'.!?\n]+))?'

    def detect_intent(self, message: str) -> IntentType:
        """
        Detect the intent of the user's message using regex patterns.

        Args:
            message: The user's message

        Returns:
            Detected intent type
        """
        message_lower = message.lower().strip()

        # Check each intent type
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    logger.info(f"Detected intent: {intent_type.value} for message: {message}")
                    return intent_type

        # Default to general chat if no specific intent is detected
        return IntentType.GENERAL_CHAT

    def extract_task_details(self, message: str) -> tuple[str, Optional[str]]:
        """
        Extract task title and description from user message.

        Args:
            message: The user's message

        Returns:
            Tuple of (title, description)
        """
        # Look for quoted strings first
        quoted_match = re.search(r'["\']([^"\']+?)["\']', message)
        if quoted_match:
            title = quoted_match.group(1).strip()
            # Look for additional description after the quote
            remaining_text = message[quoted_match.end():].strip()
            if remaining_text.startswith('for ') or remaining_text.startswith('that ') or remaining_text.startswith('which '):
                desc_match = re.search(r'(?:for|that|which|where|when)\s+(.+)', remaining_text, re.IGNORECASE)
                description = desc_match.group(1).strip() if desc_match else None
            else:
                description = None
            return title, description

        # If no quotes, try to extract the main action/task
        message_lower = message.lower()

        # Remove common prefixes
        prefixes_to_remove = [
            r'^\s*(add|create|make|new|want to|need to|please|can you|could you|would you)\s+',
            r'\s+(for|to|that|which)\s+.*$'
        ]

        cleaned_message = message
        for prefix in prefixes_to_remove:
            cleaned_message = re.sub(prefix, '', cleaned_message, flags=re.IGNORECASE).strip()

        # Take the first sentence as title
        sentences = re.split(r'[.!?]', cleaned_message)
        title = sentences[0].strip() if sentences else message[:50]  # Fallback to first 50 chars

        # Remove common task-related words from title to get cleaner title
        common_words = ['task', 'todo', 'item', 'to do', 'to-do']
        for word in common_words:
            title = re.sub(r'\b' + word + r'\b', '', title, flags=re.IGNORECASE).strip()

        # If we have more sentences, treat them as description
        description = '. '.join(sentences[1:]).strip() if len(sentences) > 1 else None

        # Clean up the title
        title = re.sub(r'^\s*[\'"]|[\'"]\s*$', '', title).strip()

        return title, description if description else None

    def call_cohere_for_general_response(self, message: str, conversation_history: List[Dict[str, str]]) -> str:
        """
        Call Cohere to generate a general chat response.

        Args:
            message: The user's message
            conversation_history: Previous conversation history

        Returns:
            Generated response from Cohere
        """
        try:
            # Format conversation history for Cohere
            chat_history = []
            for msg in conversation_history[-10:]:  # Use last 10 messages
                role = "USER" if msg.get('role') == 'user' else "CHATBOT"
                chat_history.append({
                    "user_name": role,
                    "text": msg.get('content', '')
                })

            response = self.co.chat(
                message=message,
                chat_history=chat_history,
                preamble="You are a helpful AI assistant that helps users manage their tasks. Respond naturally and professionally.",
                temperature=0.7
            )

            return response.text
        except Exception as e:
            logger.error(f"Error calling Cohere for general response: {str(e)}")
            return "I'm sorry, I encountered an issue processing your message. Could you try again?"

    async def process_message(self, user_id: str, message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Process a user message and return appropriate response and tool calls.

        Args:
            user_id: The ID of the user
            message: The user's message
            conversation_history: Previous conversation history

        Returns:
            Dictionary with response and tool calls
        """
        if not conversation_history:
            conversation_history = []

        intent = self.detect_intent(message)
        logger.info(f"Processing message with intent: {intent.value}")

        tool_calls = []
        response = ""

        try:
            if intent == IntentType.ADD_TASK:
                title, description = self.extract_task_details(message)

                if not title or not title.strip():
                    # Try to extract from the original message
                    title = message.strip()[:100]  # Use first 100 chars as title

                result = await self.tool_executor.execute_add_task(
                    user_id=user_id,
                    title=title,
                    description=description
                )

                tool_calls.append({
                    "name": "add_task",
                    "arguments": {"title": title, "description": description},
                    "result": result
                })

                response = f"I've added the task '{title}' to your list. It has been created with ID {result['task_id']}."

            elif intent == IntentType.LIST_TASKS:
                # Check if user specified a status filter
                status_filter = None
                message_lower = message.lower()
                if 'completed' in message_lower:
                    status_filter = 'completed'
                elif 'pending' in message_lower or 'incomplete' in message_lower or 'active' in message_lower:
                    status_filter = 'pending'

                result = await self.tool_executor.execute_list_tasks(
                    user_id=user_id,
                    status_filter=status_filter
                )

                tool_calls.append({
                    "name": "list_tasks",
                    "arguments": {"status_filter": status_filter},
                    "result": result
                })

                if result['task_count'] == 0:
                    response = "You don't have any tasks in your list."
                else:
                    response = f"You have {result['task_count']} tasks:\n"
                    for task in result['tasks']:
                        status = "✓ Completed" if task['is_completed'] else "○ Pending"
                        response += f"- [{status}] {task['title']} (ID: {task['id']})\n"

            elif intent == IntentType.COMPLETE_TASK:
                # Try to extract task ID from message
                task_id = None
                # Look for UUID pattern
                uuid_match = re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', message, re.IGNORECASE)
                if uuid_match:
                    task_id = uuid_match.group()

                # If no UUID found, look for numbered task (1, 2, 3, etc.)
                if not task_id:
                    num_match = re.search(r'(task|number|no\.?)\s*(\d+)', message, re.IGNORECASE)
                    if num_match:
                        task_num = int(num_match.group(2))
                        # Get the task by sequence number (would need to implement this logic)
                        # For now, we'll need to list tasks first to map numbers to IDs
                        pass

                if not task_id:
                    # If we can't find a specific task ID, ask user for clarification
                    response = "Could you please specify which task you'd like to mark as complete? You can provide the task ID or describe the task."
                else:
                    result = await self.tool_executor.execute_complete_task(
                        user_id=user_id,
                        task_id=task_id
                    )

                    tool_calls.append({
                        "name": "complete_task",
                        "arguments": {"task_id": task_id},
                        "result": result
                    })

                    response = f"I've marked the task '{result['title']}' as completed."

            elif intent == IntentType.DELETE_TASK:
                # Similar logic to complete_task
                task_id = None
                uuid_match = re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', message, re.IGNORECASE)
                if uuid_match:
                    task_id = uuid_match.group()

                if not task_id:
                    response = "Could you please specify which task you'd like to delete? You can provide the task ID or describe the task."
                else:
                    result = await self.tool_executor.execute_delete_task(
                        user_id=user_id,
                        task_id=task_id
                    )

                    tool_calls.append({
                        "name": "delete_task",
                        "arguments": {"task_id": task_id},
                        "result": result
                    })

                    response = f"I've deleted the task '{result['title']}'."

            elif intent == IntentType.UPDATE_TASK:
                # Extract task ID and new details
                task_id = None
                uuid_match = re.search(r'[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}', message, re.IGNORECASE)
                if uuid_match:
                    task_id = uuid_match.group()

                # Extract new title and description if mentioned
                new_title, new_description = self.extract_task_details(message)

                if not task_id:
                    response = "Could you please specify which task you'd like to update? You can provide the task ID or describe the task."
                else:
                    update_args = {}
                    if new_title and new_title.strip():
                        update_args["title"] = new_title
                    if new_description:
                        update_args["description"] = new_description

                    result = await self.tool_executor.execute_update_task(
                        user_id=user_id,
                        task_id=task_id,
                        **update_args
                    )

                    tool_calls.append({
                        "name": "update_task",
                        "arguments": {"task_id": task_id, **update_args},
                        "result": result
                    })

                    response = f"I've updated the task '{result['title']}' successfully."

            else:  # GENERAL_CHAT
                response = self.call_cohere_for_general_response(message, conversation_history)

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            response = f"I encountered an error while processing your request: {str(e)}"

        return {
            "response": response,
            "tool_calls": tool_calls
        }