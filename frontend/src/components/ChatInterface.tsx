/**
 * Chat interface component for the AI Todo Assistant
 * Handles user input and displays AI responses with conversation history
 */

import React, { useState, useEffect, useRef } from 'react';
import ChatService from '../services/chatService';
import styles from './ChatInterface.module.css';

interface Message {
  id: string;
  role: string;
  content: string;
  timestamp: string;
}

interface Conversation {
  id: string;
  title: string | null;
  createdAt: Date;
  updatedAt: Date;
}

const ChatInterface: React.FC = () => {
  const [inputMessage, setInputMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentUserId, setCurrentUserId] = useState<string | null>(null);
  const [currentConversationId, setCurrentConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [showConversations, setShowConversations] = useState<boolean>(false);

  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load user info and conversations on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const userId = localStorage.getItem('user_id') || localStorage.getItem('current_user_id');

    if (!token || !userId) {
      setError('Please log in to use the chat');
      return;
    }

    setCurrentUserId(userId);

    // Load conversations
    loadConversations(userId);
  }, []);

  // Scroll to bottom when messages change
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const loadConversations = async (userId: string) => {
    try {
      const userConversations = await ChatService.getUserConversations(userId);
      setConversations(userConversations.map(conv => ({
        id: conv.id,
        title: conv.title || 'New Conversation',
        createdAt: new Date(conv.created_at),
        updatedAt: new Date(conv.updated_at)
      })));
    } catch (err) {
      console.error('Error loading conversations:', err);
    }
  };

  const handleSendMessage = async () => {
    if (!inputMessage.trim() || !currentUserId) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputMessage,
      timestamp: new Date().toISOString()
    };

    // Add user message to UI immediately
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await ChatService.sendMessage(
        currentUserId,
        inputMessage,
        currentConversationId || undefined
      );

      // Update conversation ID if it changed
      if (response.conversation_id !== currentConversationId) {
        setCurrentConversationId(response.conversation_id);
        // Reload conversations to reflect the new one
        loadConversations(currentUserId);
      }

      // Add AI response to messages
      const aiMessage: Message = {
        id: `ai-${Date.now()}`,
        role: 'assistant',
        content: response.response,
        timestamp: new Date().toISOString()
      };

      setMessages(prev => [...prev, aiMessage]);

      // Log tool calls if any
      if (response.tool_calls.length > 0) {
        console.log('Tool calls executed:', response.tool_calls);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');

      // Remove the user message if it failed
      setMessages(prev => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const startNewConversation = () => {
    setCurrentConversationId(null);
    setMessages([]);
  };

  const selectConversation = (convId: string) => {
    setCurrentConversationId(convId);
    setShowConversations(false);
    // Load the conversation history
    if (currentUserId) {
      loadConversationDetails(currentUserId, convId);
    }
  };

  const loadConversationDetails = async (userId: string, convId: string) => {
    try {
      const details = await ChatService.getConversationHistory(userId, convId);
      setMessages(details.messages.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: msg.timestamp
      })));
    } catch (err) {
      console.error('Error loading conversation details:', err);
    }
  };

  const formatDate = (date: Date) => {
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className={styles['chat-container']}>
      <div className={styles['chat-header']}>
        <h2>AI Todo Assistant</h2>
        <div className={styles['chat-actions']}>
          <button
            className={`${styles['btn']} ${styles['btn-secondary']}`}
            onClick={() => setShowConversations(!showConversations)}
          >
            {showConversations ? 'Hide Chats' : 'Show Chats'}
          </button>
          <button
            className={`${styles['btn']} ${styles['btn-primary']}`}
            onClick={startNewConversation}
          >
            New Chat
          </button>
        </div>
      </div>

      {showConversations && (
        <div className={styles['conversations-sidebar']}>
          <h3>Your Conversations</h3>
          {conversations.length > 0 ? (
            <ul className={styles['conversation-list']}>
              {conversations.map((conversation) => (
                <li
                  key={conversation.id}
                  className={`${styles['conversation-item']} ${conversation.id === currentConversationId ? styles['active'] : ''}`}
                  onClick={() => selectConversation(conversation.id)}
                >
                  <div className={styles['conversation-title']}>{conversation.title}</div>
                  <div className={styles['conversation-date']}>{formatDate(conversation.updatedAt)}</div>
                </li>
              ))}
            </ul>
          ) : (
            <p>No conversations yet</p>
          )}
        </div>
      )}

      <div className={styles['chat-messages']}>
        {messages.length === 0 ? (
          <div className={styles['welcome-message']}>
            <h3>Hello! I'm your AI Todo Assistant</h3>
            <p>You can ask me to:</p>
            <ul>
              <li>Add tasks: "Add a task to buy groceries"</li>
              <li>List tasks: "Show my tasks"</li>
              <li>Complete tasks: "Mark the grocery task as complete"</li>
              <li>Delete tasks: "Delete the meeting task"</li>
              <li>Update tasks: "Change the title of my task"</li>
              <li>General chat: "Tell me about my productivity"</li>
            </ul>
          </div>
        ) : (
          messages.map((message) => (
            <div
              key={message.id}
              className={`${styles['message']} ${message.role === 'user' ? styles['user-message'] : styles['ai-message']}`}
            >
              <div className={styles['message-content']}>
                {message.content}
              </div>
              <div className={styles['message-meta']}>
                {new Date(message.timestamp).toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div className={`${styles['message']} ${styles['ai-message']}`}>
            <div className={styles['message-content']}>
              <div className={styles['typing-indicator']}>
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {error && (
        <div className={styles['error-message']}>
          {error}
        </div>
      )}

      <div className={styles['chat-input-area']}>
        <textarea
          value={inputMessage}
          onChange={(e) => setInputMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type your message here... (e.g., 'Add a task to buy milk')"
          rows={3}
          disabled={isLoading}
          className={styles['chat-textarea']}
        />
        <button
          onClick={handleSendMessage}
          disabled={isLoading || !inputMessage.trim() || !currentUserId}
          className={styles['send-button']}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;