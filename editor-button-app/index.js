const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Serve the manifest file
app.get('/manifest.json', (req, res) => {
  res.sendFile(path.join(__dirname, 'manifest.json'));
});

// Main editor button route
app.get('/editor-button', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'editor-button.html'));
});

// API endpoint for button actions
app.post('/api/button-action', (req, res) => {
  console.log('Button action received:', req.body);
  
  // Here you can add your custom logic
  // For example, interact with Crowdin API, process translations, etc.
  
  res.json({
    success: true,
    message: 'Button action processed successfully!',
    timestamp: new Date().toISOString()
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`Crowdin Editor Button App running on port ${PORT}`);
  console.log(`Manifest available at: http://localhost:${PORT}/manifest.json`);
  console.log(`Editor button at: http://localhost:${PORT}/editor-button`);
});

module.exports = app; 