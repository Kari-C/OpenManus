import React, { useState } from 'react';


const App: React.FC = () => {
    const [prompt, setPrompt] = useState('');
    const [response, setResponse] = useState('');

    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault();

        try {
            const res = await fetch('http://localhost:8000/process/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ prompt }),
            });

            const data = await res.json();
            setResponse(data.message);
        } catch (error) {
            console.error('Error processing request:', error);
            setResponse('Error processing request');
        }
    };

    return (
        <div>
            <form onSubmit={handleSubmit}>
                <label>
                    Enter your prompt:
                    <input
                        type="text"
                        value={prompt}
                        onChange={(e) => setPrompt(e.target.value)}
                    />
                </label>
                <button type="submit">Submit</button>
            </form>

            {response && <p>{response}</p>}
        </div>
    );
};

export default App;
