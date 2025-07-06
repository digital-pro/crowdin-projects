const https = require('https');
const http = require('http');
const { URL } = require('url');

export default function handler(req, res) {
  // Set CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
  
  // Handle preflight requests
  if (req.method === 'OPTIONS') {
    res.status(200).end();
    return;
  }
  
  // Only allow GET requests
  if (req.method !== 'GET') {
    res.status(405).json({ error: 'Method not allowed' });
    return;
  }
  
  const { url: targetUrl } = req.query;
  
  if (!targetUrl) {
    res.status(400).json({ error: 'Missing url parameter' });
    return;
  }
  
  try {
    const parsedUrl = new URL(targetUrl);
    
    // Only allow HTTPS URLs for security
    if (parsedUrl.protocol !== 'https:') {
      res.status(400).json({ error: 'Only HTTPS URLs are allowed' });
      return;
    }
    
    console.log('Proxying request to:', targetUrl);
    
    const protocol = parsedUrl.protocol === 'https:' ? https : http;
    const request = protocol.get(targetUrl, (proxyRes) => {
      // Forward status code and headers
      res.status(proxyRes.statusCode);
      
      // Forward relevant headers
      Object.keys(proxyRes.headers).forEach(key => {
        if (!key.toLowerCase().startsWith('access-control-')) {
          res.setHeader(key, proxyRes.headers[key]);
        }
      });
      
      // Pipe the response
      proxyRes.pipe(res);
    });
    
    request.on('error', (error) => {
      console.error('Proxy error:', error);
      res.status(500).json({ error: 'Proxy error: ' + error.message });
    });
    
    // Set timeout
    request.setTimeout(30000, () => {
      request.abort();
      res.status(504).json({ error: 'Request timeout' });
    });
    
  } catch (error) {
    console.error('URL parsing error:', error);
    res.status(400).json({ error: 'Invalid URL: ' + error.message });
  }
} 