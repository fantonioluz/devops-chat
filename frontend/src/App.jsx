import React, { useState, useRef, useEffect } from 'react';
import { useGoogleLogin } from '@react-oauth/google';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';
import { Send, BookOpen, Loader2, LogOut, History, Settings, Trash2 } from 'lucide-react';
import { useAuth } from './contexts/AuthContext';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const { user, loginWithGoogle, logout, loading: authLoading } = useAuth();
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: '👋 Olá! Sou seu professor de DevOps. Estou aqui para ajudar você a aprender sobre práticas, ferramentas e conceitos de DevOps. Pode me perguntar sobre CI/CD, Docker, Kubernetes, Cloud, automação e muito mais!'
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
  const [availableModels, setAvailableModels] = useState([]);
  const [conversations, setConversations] = useState([]);
  const [currentConversationId, setCurrentConversationId] = useState(null);
  const [showSidebar, setShowSidebar] = useState(false);
  const [showModelSelector, setShowModelSelector] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    const saved = localStorage.getItem('darkMode');
    return saved ? JSON.parse(saved) : true;
  });
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    fetchModels();
  }, []);

  useEffect(() => {
    if (user) {
      fetchConversations();
    }
  }, [user]);

  useEffect(() => {
    localStorage.setItem('darkMode', JSON.stringify(darkMode));
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  const fetchModels = async () => {
    try {
      const response = await axios.get(`${API_URL}/models`);
      setAvailableModels(response.data);
    } catch (error) {
      console.error('Error fetching models:', error);
    }
  };

  const fetchConversations = async () => {
    try {
      const response = await axios.get(`${API_URL}/conversations`);
      setConversations(response.data);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const loadConversation = async (conversationId) => {
    try {
      const response = await axios.get(`${API_URL}/conversations/${conversationId}`);
      const conv = response.data;
      setCurrentConversationId(conv.id);
      setSelectedModel(conv.model);
      setMessages(conv.messages.map(msg => ({
        role: msg.role,
        content: msg.content
      })));
      setShowSidebar(false);
    } catch (error) {
      console.error('Error loading conversation:', error);
    }
  };

  const deleteConversation = async (conversationId, e) => {
    e.stopPropagation();
    if (!confirm('Deletar esta conversa?')) return;
    
    try {
      await axios.delete(`${API_URL}/conversations/${conversationId}`);
      fetchConversations();
      if (currentConversationId === conversationId) {
        startNewConversation();
      }
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const startNewConversation = () => {
    setCurrentConversationId(null);
    setMessages([
      {
        role: 'assistant',
        content: '👋 Olá! Sou seu professor de DevOps. Como posso ajudar você hoje?'
      }
    ]);
    setShowSidebar(false);
  };

  const googleLogin = useGoogleLogin({
    onSuccess: async (tokenResponse) => {
      try {
        // Get user info from Google using the access token
        const userInfoResponse = await axios.get(
          'https://www.googleapis.com/oauth2/v3/userinfo',
          {
            headers: { Authorization: `Bearer ${tokenResponse.access_token}` }
          }
        );
        
        // Send to our backend
        const response = await axios.post(`${API_URL}/auth/google`, {
          google_data: userInfoResponse.data
        });
        
        const { access_token, user } = response.data;
        localStorage.setItem('token', access_token);
        axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
        window.location.reload();
      } catch (error) {
        console.error('Login error:', error);
        alert('Erro no login. Tente novamente.');
      }
    },
    onError: () => {
      alert('Erro no login com Google');
    },
  });

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input.trim()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await axios.post(`${API_URL}/chat`, {
        messages: [...messages, userMessage],
        model: selectedModel,
        conversation_id: currentConversationId
      });

      setMessages(prev => [...prev, {
        role: 'assistant',
        content: response.data.response
      }]);

      if (response.data.conversation_id && !currentConversationId) {
        setCurrentConversationId(response.data.conversation_id);
        if (user) {
          fetchConversations();
        }
      }
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: '❌ Desculpe, ocorreu um erro ao processar sua mensagem. Por favor, tente novamente.'
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const suggestedQuestions = [
    'O que é DevOps?',
    'Como funciona CI/CD?',
    'O que é Docker?',
    'Explique Kubernetes'
  ];

  if (authLoading) {
    return (
      <div className="app loading-screen">
        <Loader2 className="spinner" size={48} />
        <p>Carregando...</p>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <div className="header-content">
          <div className="header-left">
            <BookOpen size={32} />
            <div>
              <h1>DevOps Learning Chat</h1>
              <p>Aprenda DevOps de forma interativa</p>
            </div>
          </div>
          
          <div className="header-right">
            {!user ? (
              <button onClick={googleLogin} className="login-button">
                <img src="https://www.google.com/favicon.ico" alt="Google" width="20" />
                Login com Google
              </button>
            ) : (
              <>
                <button 
                  onClick={() => setDarkMode(!darkMode)} 
                  className="theme-button"
                  title={darkMode ? 'Modo claro' : 'Modo escuro'}
                >
                  {darkMode ? '☀️' : '🌙'}
                </button>

                <button onClick={() => setShowModelSelector(!showModelSelector)} className="model-button">
                  <Settings size={20} />
                  {availableModels.find(m => m.id === selectedModel)?.name || 'Selecione Modelo'}
                </button>
                
                {user && (
                  <button onClick={() => setShowSidebar(!showSidebar)} className="history-button">
                    <History size={20} />
                  </button>
                )}
                
                <div className="user-menu">
                  <img src={user.picture} alt={user.name} className="user-avatar" />
                  <span className="user-name">{user.name}</span>
                  <button onClick={logout} className="logout-button" title="Sair">
                    <LogOut size={20} />
                  </button>
                </div>
              </>
            )}
          </div>
        </div>

        {showModelSelector && (
          <div className="model-selector-dropdown">
            <h3>Escolha o Modelo de IA</h3>
            <div className="models-grid">
              {availableModels.map(model => (
                <button
                  key={model.id}
                  className={`model-option ${selectedModel === model.id ? 'active' : ''}`}
                  onClick={() => {
                    setSelectedModel(model.id);
                    setShowModelSelector(false);
                  }}
                >
                  <strong>{model.name}</strong>
                  <span className="model-provider">{model.provider}</span>
                  <span className="model-description">{model.description}</span>
                </button>
              ))}
            </div>
          </div>
        )}
      </header>

      {showSidebar && user && (
        <>
          <div className="sidebar-overlay" onClick={() => setShowSidebar(false)} />
          <div className="sidebar">
            <div className="sidebar-header">
              <h2>Suas Conversas</h2>
              <button onClick={startNewConversation} className="new-chat-button">
                + Nova Conversa
              </button>
            </div>
            <div className="conversations-list">
              {conversations.length === 0 ? (
                <p className="empty-state">Nenhuma conversa ainda</p>
              ) : (
                conversations.map(conv => (
                  <div
                    key={conv.id}
                    className={`conversation-item ${conv.id === currentConversationId ? 'active' : ''}`}
                    onClick={() => loadConversation(conv.id)}
                  >
                    <div className="conversation-info">
                      <strong>{conv.title}</strong>
                      <span className="conversation-meta">
                        {conv.message_count} mensagens • {new Date(conv.updated_at).toLocaleDateString()}
                      </span>
                    </div>
                    <button
                      className="delete-conversation"
                      onClick={(e) => deleteConversation(conv.id, e)}
                      title="Deletar"
                    >
                      <Trash2 size={16} />
                    </button>
                  </div>
                ))
              )}
            </div>
          </div>
        </>
      )}

      <div className="chat-container">
        <div className="messages-container">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-avatar">
                {message.role === 'assistant' ? '🤖' : user?.name?.charAt(0) || 'U'}
              </div>
              <div className="message-content">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar">🤖</div>
              <div className="message-content">
                <Loader2 className="spinner" size={20} />
                <span> Pensando...</span>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div className="input-form">
          <div className="input-container">
            <div className="input-wrapper">
              <textarea
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    sendMessage(e);
                  }
                }}
                placeholder="Digite sua pergunta sobre DevOps..."
                className="chat-input"
                disabled={isLoading}
                rows={1}
              />
            </div>
            <button
              onClick={sendMessage}
              className="send-button"
              disabled={isLoading || !input.trim()}
            >
              {isLoading ? <Loader2 className="spinner" size={20} /> : <Send size={20} />}
              {!isLoading && 'Enviar'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
