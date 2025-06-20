// -------------------------
// client/src/App.js
// -------------------------
import React, { useState } from 'react';
import axios from 'axios';

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [parsedText, setParsedText] = useState('');
  const [analysis, setAnalysis] = useState('');

  const handleResumeUpload = async () => {
    const formData = new FormData();
    formData.append('resume', resumeFile);

    const res = await axios.post('http://localhost:5000/api/upload-resume', formData);
    setParsedText(res.data.extractedText);
  };

  const handleAnalysis = async () => {
    const res = await axios.post('http://localhost:5000/api/analyze-resume', {
      resumeText: parsedText,
      jobDescription: jobDescription
    });
    setAnalysis(res.data.analysis);
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">AI Resume Analyzer</h1>

      <input
        type="file"
        accept=".pdf,.docx"
        onChange={(e) => setResumeFile(e.target.files[0])}
        className="mb-4"
      />
      <button
        onClick={handleResumeUpload}
        className="px-4 py-2 bg-blue-500 text-white rounded mb-4"
      >
        Upload & Parse Resume
      </button>

      <textarea
        rows={5}
        className="w-full border p-2 mb-4"
        placeholder="Paste Job Description Here..."
        value={jobDescription}
        onChange={(e) => setJobDescription(e.target.value)}
      />
      <button
        onClick={handleAnalysis}
        className="px-4 py-2 bg-green-600 text-white rounded mb-4"
      >
        Analyze Resume
      </button>

      <h2 className="font-semibold text-xl mb-2">Parsed Resume Text:</h2>
      <pre className="whitespace-pre-wrap bg-gray-100 p-3 mb-6">{parsedText}</pre>

      <h2 className="font-semibold text-xl mb-2">AI Analysis Output:</h2>
      <pre className="whitespace-pre-wrap bg-gray-100 p-3">{analysis}</pre>
    </div>
  );
}

export default App;

// -------------------------
// To do next:
// - Create login & register pages (Phase 2)
// - Add chart visualizations (Phase 2 or 3)
// - Style with Tailwind CSS
// - Deploy to Vercel (client) & Render (server)
