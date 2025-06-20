// Root directory structure:
// AI-Resume-Analyzer-Project/
// ├── client/    --> React Frontend
// └── server/    --> Node.js Backend

// -------------------------
// server/server.js
// -------------------------
const express = require('express');
const cors = require('cors');
const dotenv = require('dotenv');
const mongoose = require('mongoose');
const multer = require('multer');
const pdfParse = require('pdf-parse');
const mammoth = require('mammoth');
const { GoogleGenerativeAI } = require('@google/generative-ai');

dotenv.config();
const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// MongoDB connection
mongoose.connect(process.env.MONGO_URI, {
  useNewUrlParser: true,
  useUnifiedTopology: true,
}).then(() => console.log('MongoDB Connected'))
  .catch(err => console.error('MongoDB Error:', err));

// File upload setup
const storage = multer.memoryStorage();
const upload = multer({ storage });

// Upload endpoint
app.post('/api/upload-resume', upload.single('resume'), async (req, res) => {
  try {
    let text = '';
    const file = req.file;

    if (file.mimetype === 'application/pdf') {
      const data = await pdfParse(file.buffer);
      text = data.text;
    } else if (file.mimetype === 'application/vnd.openxmlformats-officedocument.wordprocessingml.document') {
      const data = await mammoth.extractRawText({ buffer: file.buffer });
      text = data.value;
    } else {
      return res.status(400).json({ error: 'Unsupported file type.' });
    }

    res.json({ extractedText: text });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'File parsing failed.' });
  }
});

// Gemini API Integration
const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

app.post('/api/analyze-resume', async (req, res) => {
  try {
    const { resumeText, jobDescription } = req.body;
    const prompt = `Analyze this resume text: \n${resumeText}\nFor this job: ${jobDescription}. Give me keywords, skills match, and suggestions.`;

    const model = genAI.getGenerativeModel({ model: 'gemini-pro' });
    const result = await model.generateContent(prompt);
    const response = await result.response;
    const text = response.text();

    res.json({ analysis: text });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Analysis failed.' });
  }
});

app.listen(PORT, () => console.log(`Server running on port ${PORT}`));

// -------------------------
// To do next:
// - Create frontend in React (client/ folder)
// - Connect Axios POST requests to /api/upload-resume and /api/analyze-resume
// - Add authentication and history saving (Phase 2)
// - Add detailed charts and UI refinement (Phase 3)
