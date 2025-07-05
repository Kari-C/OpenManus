import React, { useState, useEffect, useRef } from 'react';
import LottiePlayer from './components/LottiePlayer';

const App: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [streamingResponse, setStreamingResponse] = useState<string[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);
  const responseEndRef = useRef<HTMLDivElement>(null);

  // Clean up event source on unmount
  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, []);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    if (responseEndRef.current) {
      responseEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [streamingResponse]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    if (!prompt.trim()) {
      return;
    }

    // Clear previous responses
    setStreamingResponse([]);
    setIsProcessing(true);

    try {
      // Close any existing connection
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }

      // Send the prompt to the backend
      const response = await fetch('http://localhost:8000/process/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ prompt }),
      });

      // Check if the response is a streaming response
      const contentType = response.headers.get('content-type');

      if (contentType && contentType.includes('text/event-stream')) {
        // Create a reader to process the stream
        const reader = response.body?.getReader();
        const decoder = new TextDecoder();

        if (reader) {
          while (true) {
            const { done, value } = await reader.read();

            if (done) {
              break;
            }

            const chunk = decoder.decode(value);
            // Process SSE format (data: message\n\n)
            const lines = chunk
              .split('\n\n')
              .filter(line => line.startsWith('data: '))
              .map(line => line.replace('data: ', ''));

            if (lines.length > 0) {
              setStreamingResponse(prev => [...prev, ...lines]);
            }
          }
        }
      } else {
        // Handle regular JSON response
        const data = await response.json();
        setStreamingResponse([data.message]);
      }
    } catch (error) {
      console.error('Error processing request:', error);
      setStreamingResponse(prev => [...prev, 'Error processing request']);
    } finally {
      setIsProcessing(false);
    }
  };

  // Function to format the message with proper styles
  const formatMessage = (message: string) => {
    // Check if this is a tool result message
    if (message.includes('🎯 Tool') && message.includes('Result:')) {
      const [toolHeader, resultContent] = message.split('Result:');

      return (
        <>
          <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>{toolHeader}</div>
          <div style={{
            whiteSpace: 'pre-wrap',
            backgroundColor: '#e6f7ff',
            padding: '10px',
            borderRadius: '4px',
            border: '1px solid #91d5ff',
            fontFamily: 'monospace'
          }}>
            {resultContent.trim()}
          </div>
        </>
      );
    }

    // Check if this is a thought message
    if (message.includes('✨ Manus\'s thoughts:')) {
      return (
        <div style={{
          backgroundColor: '#f6ffed',
          padding: '10px',
          borderRadius: '4px',
          border: '1px solid #b7eb8f'
        }}>
          {message}
        </div>
      );
    }

    // Check if this message contains data/output that should be displayed as terminal output
    // This includes stock data, tables, CSV data, or any multi-line data
    const isDataOutput =
      message.includes('Stock History') ||
      message.includes('Date,') ||
      message.includes('Open,High,Low,Close') ||
      message.includes('\n') ||  // Any multi-line output
      /\d{4}-\d{2}-\d{2}/.test(message) || // Contains dates in YYYY-MM-DD format
      message.includes('|') || // Potential table format
      (message.includes(',') && message.split(',').length > 3); // Potential CSV data

    if (isDataOutput) {
      return (
        <div style={{
          whiteSpace: 'pre-wrap',
          backgroundColor: '#f5f5f5',
          padding: '10px',
          borderRadius: '4px',
          border: '1px solid #d9d9d9',
          fontFamily: 'monospace',
          overflowX: 'auto'
        }}>
          {message}
        </div>
      );
    }

    // Regular message
    return message;
  };

  return (
    <div style={{ maxWidth: '80%', margin: 'auto' }}>
      <form onSubmit={handleSubmit} >
        <div>
          {/* <label style={{ display: 'block', marginBottom: '5px', fontWeight: 'bold' }}>
            Enter your prompt:
          </label> */}
          <textarea
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            style={{
              width: '100%',
              height: '100px',
              padding: '8px',
              borderRadius: '4px',
              border: '1px solid #ccc'
            }}
            disabled={isProcessing}
            placeholder="Type your prompt here..."
          />
        </div>
        <div style={{ display: 'flex', flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <button
            type="submit"
            disabled={isProcessing || !prompt.trim()}
            style={{
              padding: '8px 16px',
              backgroundColor: isProcessing || !prompt.trim() ? '#cccccc' : '#063970',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              cursor: isProcessing || !prompt.trim() ? 'not-allowed' : 'pointer',
            }}
          >
            {isProcessing ? 'Processing...' : 'DoTask'}
          </button>
          <LottiePlayer src="dragon" width={55} height={55} loop={isProcessing} speed={1} autoplay={isProcessing} />
        </div>
      </form >

      <div style={{
        border: streamingResponse.length > 0 ? '1px solid #ddd' : 'none',
        borderRadius: '4px',
        padding: streamingResponse.length > 0 ? '16px' : '0',
        backgroundColor: '#f9f9f9',
        maxHeight: '500px',
        overflow: 'auto'
      }}>
        <h2 style={{ margin: '0 0 16px 0', display: streamingResponse.length > 0 ? 'block' : 'none' }}>Response:</h2>
        {streamingResponse.map((message, index) => (
          <div key={index} style={{
            marginBottom: '8px',
            padding: '8px',
            backgroundColor: 'white',
            borderRadius: '4px',
            border: '1px solid #eee'
          }}>
            {formatMessage(message)}
          </div>
        ))}
        <div ref={responseEndRef} />
      </div>
    </div >
  );
};

export default App;
