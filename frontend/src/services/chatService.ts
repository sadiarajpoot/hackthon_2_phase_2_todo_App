/**
 * Service for handling chat API calls
 */
import axios from 'axios';

interface ChatRequest {
  conversation_id?: string;
  message: string;
}

interface ToolCall {
  name: string;
  arguments: Record<string, any>;
  result?: Record<string, any>;
}

interface ChatResponse {
  conversation_id: string;
  response: string;
  tool_calls: ToolCall[];
}

interface Conversation {
  id: string;
  title: string | null;
  created_at: string;
  updated_at: string;
}

interface Message {
  id: string;
  role: string;
  content: string;
  timestamp: string;
}

class ChatService {
  private baseUrl: string;

  constructor() {
    this.baseUrl = process.env.NEXT_PUBLIC_CHAT_API_BASE_URL || process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001';
  }

  /**
   * Send a message to the chat API
   */
  async sendMessage(userId: string, message: string, conversationId?: string): Promise<ChatResponse> {
    try {
      const token = localStorage.getItem('access_token');

      const response = await axios.post<ChatResponse>(
        `${this.baseUrl}/api/${userId}/chat`,
        {
          conversation_id: conversationId || undefined, // Use undefined instead of null to exclude from request if not provided
          message: message
        },
        {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error sending message:', error);
      throw error;
    }
  }

  /**
   * Get conversation history
   */
  async getConversationHistory(userId: string, conversationId: string): Promise<{
    conversation_id: string;
    title: string | null;
    created_at: string;
    updated_at: string;
    messages: Message[];
  }> {
    try {
      const token = localStorage.getItem('access_token');

      const response = await axios.get(
        `${this.baseUrl}/api/${userId}/conversations/${conversationId}`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error getting conversation history:', error);
      throw error;
    }
  }

  /**
   * Get list of user conversations
   */
  async getUserConversations(userId: string): Promise<Conversation[]> {
    try {
      const token = localStorage.getItem('access_token');

      const response = await axios.get<Conversation[]>(
        `${this.baseUrl}/api/${userId}/conversations`,
        {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        }
      );

      return response.data;
    } catch (error) {
      console.error('Error getting user conversations:', error);
      throw error;
    }
  }
}

export default new ChatService();