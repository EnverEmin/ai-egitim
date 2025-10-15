import { useState, useEffect, useRef } from 'react';
import '@/App.css';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [stats, setStats] = useState(null);
  const [concepts, setConcepts] = useState([]);
  const [phase, setPhase] = useState('offline');
  const [loading, setLoading] = useState(false);
  const [showStats, setShowStats] = useState(false);
  const messagesEndRef = useRef(null);

  // İlk yüklemede stats ve concepts getir
  useEffect(() => {
    fetchStats();
    fetchConcepts();
    fetchPhase();
  }, []);

  // Mesajlar güncellendiğinde scroll yap
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchStats = async () => {
    try {
      const response = await axios.get(`${API}/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('Stats fetch error:', error);
    }
  };

  const fetchConcepts = async () => {
    try {
      const response = await axios.get(`${API}/concepts`);
      setConcepts(response.data);
    } catch (error) {
      console.error('Concepts fetch error:', error);
    }
  };

  const fetchPhase = async () => {
    try {
      const response = await axios.get(`${API}/phase`);
      setPhase(response.data.phase);
    } catch (error) {
      console.error('Phase fetch error:', error);
    }
  };

  const togglePhase = async () => {
    try {
      const newPhase = phase === 'offline' ? 'online' : 'offline';
      await axios.post(`${API}/phase`, { phase: newPhase });
      setPhase(newPhase);
      
      // Bilgilendirme mesajı ekle
      setMessages(prev => [...prev, {
        role: 'system',
        content: `Sistem şu anda ${newPhase === 'offline' ? 'Kapalı Sistem (Offline)' : 'Açık Sistem (Online)'} moduna geçti.`,
        timestamp: new Date().toISOString()
      }]);
    } catch (error) {
      console.error('Phase toggle error:', error);
    }
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    
    if (!input.trim()) return;

    const userMessage = {
      role: 'user',
      content: input,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await axios.post(`${API}/chat`, {
        message: input,
        session_id: sessionId
      });

      const aiMessage = {
        role: 'assistant',
        content: response.data.response,
        timestamp: new Date().toISOString(),
        concepts: response.data.concepts_learned || []
      };

      setMessages(prev => [...prev, aiMessage]);
      
      if (!sessionId) {
        setSessionId(response.data.session_id);
      }

      // Stats ve concepts güncelle
      if (response.data.concepts_learned && response.data.concepts_learned.length > 0) {
        fetchStats();
        fetchConcepts();
      }
    } catch (error) {
      console.error('Send message error:', error);
      const errorMessage = {
        role: 'error',
        content: 'Üzgünüm, bir hata oluştu. Lütfen tekrar deneyin.',
        timestamp: new Date().toISOString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const formatTime = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="app-container" data-testid="app-container">
      {/* Header */}
      <header className="app-header" data-testid="app-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo" data-testid="app-logo">
              <span className="logo-icon">🧠</span>
              <div className="logo-text">
                <h1>Monoque Intelligence</h1>
                <p>Adaptive Learning Core</p>
              </div>
            </div>
          </div>
          
          <div className="header-right">
            <div className="phase-toggle" data-testid="phase-toggle">
              <span className="phase-label">Faz:</span>
              <button 
                className={`phase-button ${phase}`}
                onClick={togglePhase}
                data-testid="phase-button"
              >
                {phase === 'offline' ? '🔒 Kapalı Sistem' : '🌐 Açık Sistem'}
              </button>
            </div>
            
            <button 
              className="stats-button"
              onClick={() => setShowStats(!showStats)}
              data-testid="stats-toggle-button"
            >
              📊 İstatistikler
            </button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <div className="main-content">
        {/* Chat Area */}
        <div className="chat-container" data-testid="chat-container">
          <div className="messages-area" data-testid="messages-area">
            {messages.length === 0 ? (
              <div className="welcome-message" data-testid="welcome-message">
                <h2>👋 Merhaba!</h2>
                <p>Ben Monoque Intelligence, sizin kişisel öğrenme asistanınızım.</p>
                <div className="welcome-features">
                  <div className="feature">
                    <span>✅</span>
                    <p>Sizden öğreniyorum</p>
                  </div>
                  <div className="feature">
                    <span>🧩</span>
                    <p>Kavramları kaydediyorum</p>
                  </div>
                  <div className="feature">
                    <span>🌍</span>
                    <p>Türkçe ve İngilizce biliyorum</p>
                  </div>
                </div>
              </div>
            ) : (
              messages.map((msg, idx) => (
                <div 
                  key={idx} 
                  className={`message ${msg.role}`}
                  data-testid={`message-${msg.role}-${idx}`}
                >
                  <div className="message-content">
                    <div className="message-header">
                      <span className="message-role">
                        {msg.role === 'user' ? '👤 Siz' : 
                         msg.role === 'assistant' ? '🧠 Monoque' : 
                         msg.role === 'system' ? 'ℹ️ Sistem' : '⚠️ Hata'}
                      </span>
                      <span className="message-time">{formatTime(msg.timestamp)}</span>
                    </div>
                    <div className="message-text">{msg.content}</div>
                    {msg.concepts && msg.concepts.length > 0 && (
                      <div className="concepts-learned" data-testid="concepts-learned">
                        <h4>📚 Yeni Kavramlar Öğrenildi:</h4>
                        {msg.concepts.map((concept, i) => (
                          <div key={i} className="concept-item">
                            <strong>{concept.concept}</strong>: {concept.definition}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))
            )}
            {loading && (
              <div className="message assistant loading" data-testid="loading-message">
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-role">🧠 Monoque</span>
                  </div>
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <form className="input-area" onSubmit={sendMessage} data-testid="message-form">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Bir şey öğret veya sor..."
              disabled={loading}
              className="message-input"
              data-testid="message-input"
            />
            <button 
              type="submit" 
              disabled={loading || !input.trim()}
              className="send-button"
              data-testid="send-button"
            >
              {loading ? '⏳' : '🚀'} Gönder
            </button>
          </form>
        </div>

        {/* Stats Sidebar */}
        {showStats && (
          <div className="stats-sidebar" data-testid="stats-sidebar">
            <div className="stats-header">
              <h3>📊 İstatistikler</h3>
              <button 
                onClick={() => setShowStats(false)}
                className="close-button"
                data-testid="close-stats-button"
              >
                ✕
              </button>
            </div>

            {stats && (
              <div className="stats-content">
                <div className="stat-item">
                  <span className="stat-label">📚 Toplam Kavram</span>
                  <span className="stat-value" data-testid="stat-total-concepts">{stats.total_concepts}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">💬 Toplam Mesaj</span>
                  <span className="stat-value" data-testid="stat-total-messages">{stats.total_messages}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">✅ Doğrulanmış Bilgi</span>
                  <span className="stat-value" data-testid="stat-verified-knowledge">{stats.verified_knowledge}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">🌐 İnternet Bilgisi</span>
                  <span className="stat-value" data-testid="stat-internet-knowledge">{stats.internet_knowledge}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-label">🎯 Mevcut Faz</span>
                  <span className={`stat-value phase-${stats.current_phase}`} data-testid="stat-current-phase">
                    {stats.current_phase === 'offline' ? 'Kapalı' : 'Açık'}
                  </span>
                </div>
              </div>
            )}

            <div className="concepts-list">
              <h4>🧩 Öğrenilen Kavramlar</h4>
              <div className="concepts-scroll" data-testid="concepts-list">
                {concepts.length === 0 ? (
                  <p className="no-concepts">Henüz kavram öğrenilmedi</p>
                ) : (
                  concepts.map((concept, idx) => (
                    <div key={idx} className="concept-card" data-testid={`concept-card-${idx}`}>
                      <h5>{concept.concept}</h5>
                      <p>{concept.definition}</p>
                      <span className="concept-status">
                        {concept.verified ? '✅ Doğrulandı' : '⏳ Bekliyor'}
                      </span>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;