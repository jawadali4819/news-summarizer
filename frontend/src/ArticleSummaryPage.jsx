import { useState, useEffect } from 'react';
import { Send, Trash2, ExternalLink, ChevronUp, AlertCircle, CheckCircle } from 'lucide-react';

// Internal Alert Component
const Alert = ({ children, variant = 'default' }) => {
  const styles = {
    default: 'bg-blue-50 text-blue-700 border-blue-200',
    success: 'bg-green-50 text-green-700 border-green-200',
    error: 'bg-red-50 text-red-700 border-red-200'
  };

  return (
    <div className={`flex items-center p-4 rounded-lg border ${styles[variant]}`}>
      {variant === 'success' && <CheckCircle className="h-5 w-5 mr-2" />}
      {variant === 'error' && <AlertCircle className="h-5 w-5 mr-2" />}
      <div className="ml-1">{children}</div>
    </div>
  );
};

const ArticleSummaryPage = () => {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [articles, setArticles] = useState([]);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState('');
  const [isInputExpanded, setIsInputExpanded] = useState(false);

  useEffect(() => {
    fetchArticles();
  }, []);

  const fetchArticles = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/articles');
      if (!response.ok) throw new Error('Failed to fetch articles');
      const data = await response.json();
      setArticles(data.reverse());
    } catch (err) {
      setError('Failed to load articles');
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setSuccess('');
    
    try {
      const response = await fetch('http://127.0.0.1:8000/articles', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url }),
      });
      
      if (!response.ok) throw new Error('Failed to fetch summary');
      
      const data = await response.json();
      setArticles(prev => [data, ...prev]);
      setUrl('');
      setIsInputExpanded(false);
      setSuccess('Article successfully summarized!');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (articleUrl) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/articles?url=${encodeURIComponent(articleUrl)}`, {
        method: 'DELETE',
      });
      
      if (!response.ok) throw new Error('Failed to delete article');
      await fetchArticles(); // Reload the articles
      setSuccess('Article successfully deleted!');
      
      // Clear success message after 3 seconds
      setTimeout(() => setSuccess(''), 3000);
    } catch (err) {
      setError('Failed to delete article');
    }
  };

  const formatText = (text) => {
    const lines = text.split('\n');
    const formattedContent = [];
    let currentSection = null;
    
    lines.forEach(line => {
      if (line.trim().startsWith('**')) {
        if (currentSection) formattedContent.push(currentSection);
        const headingText = line.trim().replace(/^\*\*|\*\*$/g, '');
        currentSection = { heading: headingText, content: [] };
      } else if (line.trim().startsWith('* ')) {
        if (currentSection) {
          currentSection.content.push({
            type: 'bullet',
            text: line.trim().substring(2)
          });
        }
      } else if (line.trim()) {
        if (currentSection) {
          currentSection.content.push({
            type: 'text',
            text: line.trim()
          });
        }
      }
    });
    
    if (currentSection) formattedContent.push(currentSection);
    
    return formattedContent.map((section, idx) => (
      <div key={idx} className="mb-6">
        <h2 className="text-xl font-bold text-gray-800 mb-3">
          {section.heading}
        </h2>
        <div className="space-y-3">
          {section.content.map((item, contentIdx) => {
            if (item.type === 'bullet') {
              return (
                <ul key={contentIdx} className="list-disc pl-6">
                  <li className="text-gray-700">{item.text}</li>
                </ul>
              );
            }
            return (
              <p key={contentIdx} className="text-gray-700 leading-relaxed">
                {item.text}
              </p>
            );
          })}
        </div>
      </div>
    ));
  };

  return (
    <div className="min-h-screen bg-gray-50 pb-24">
      {/* Header */}
      <div className="bg-white shadow-sm sticky top-0 z-10">
        <div className="max-w-5xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Article Summarizer</h1>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-5xl mx-auto px-4 py-6">
        {/* Notifications */}
        {error && (
          <div className="mb-6">
            <Alert variant="error">{error}</Alert>
          </div>
        )}
        
        {success && (
          <div className="mb-6">
            <Alert variant="success">{success}</Alert>
          </div>
        )}

        {/* Articles Grid */}
        <div className="grid gap-6">
          {articles.map((article, idx) => (
            <div key={idx} className="bg-white rounded-xl shadow-sm overflow-hidden border border-gray-100 hover:shadow-md transition-shadow">
              {/* Image Section */}
              {article.image && (
                <div className="w-full h-48 md:h-64 relative">
                  <img
                    src={article.image}
                    alt="Article thumbnail"
                    className="w-full h-full object-cover"
                  />
                  <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent" />
                </div>
              )}
              
              {/* Content Section */}
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h2 className="text-lg font-semibold text-gray-900 flex-1 pr-4">
                    {article.url.split('/').pop() || 'Article Summary'}
                  </h2>
                  <div className="flex gap-3">
                    <button
                      onClick={() => window.open(article.url, '_blank')}
                      className="p-2 rounded-full hover:bg-gray-100 text-gray-500 hover:text-blue-600 transition-colors"
                      title="Open original article"
                    >
                      <ExternalLink className="h-5 w-5" />
                    </button>
                    <button
                      onClick={() => handleDelete(article.url)}
                      className="p-2 rounded-full hover:bg-gray-100 text-gray-500 hover:text-red-600 transition-colors"
                      title="Delete summary"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
                {formatText(article.summary)}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Fixed Input Section */}
      <div className="fixed bottom-0 left-0 right-0 bg-white shadow-lg border-t border-gray-200">
        <div className="max-w-5xl mx-auto px-4">
          <div className={`transform transition-all duration-300 ${isInputExpanded ? 'py-6' : 'py-4'}`}>
            <button
              onClick={() => setIsInputExpanded(!isInputExpanded)}
              className="absolute -top-10 right-4 bg-white rounded-t-lg px-4 py-2 shadow-lg border border-gray-200 border-b-0 text-gray-600 hover:text-gray-900"
            >
              <ChevronUp className={`h-5 w-5 transform transition-transform ${isInputExpanded ? 'rotate-180' : ''}`} />
            </button>
            
            <form onSubmit={handleSubmit} className={`transition-all duration-300 ${isInputExpanded ? 'opacity-100' : 'opacity-90'}`}>
              <div className="flex gap-4">
                <input
                  type="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="Enter article URL to summarize..."
                  required
                  className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-500 focus:outline-none"
                />
                <button
                  type="submit"
                  disabled={loading}
                  className="inline-flex items-center px-6 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 transition-colors"
                >
                  {loading ? (
                    'Processing...'
                  ) : (
                    <>
                      Summarize
                      <Send className="ml-2 h-4 w-4" />
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ArticleSummaryPage;