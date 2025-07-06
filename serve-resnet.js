const http = require('http');
const https = require('https');
const fs = require('fs');
const path = require('path');
const url = require('url');

const port = 8080;

const server = http.createServer((req, res) => {
    const parsedUrl = url.parse(req.url, true);
    
    console.log('Request URL:', req.url, 'Pathname:', parsedUrl.pathname);
    
    // Test endpoint
    if (parsedUrl.pathname === '/test') {
        res.writeHead(200, { 
            'Content-Type': 'text/html',
            'Access-Control-Allow-Origin': '*'
        });
        res.end(`
            <h1>Server Test</h1>
            <p>Server is working!</p>
            <p>Time: ${new Date().toISOString()}</p>
            <p><a href="/real-imagenet-resnet.html">Go to ResNet App</a></p>
        `);
        return;
    }
    
    // CORS proxy endpoint
    if (parsedUrl.pathname === '/proxy') {
        const targetUrl = parsedUrl.query.url;
        if (!targetUrl) {
            res.writeHead(400, { 'Content-Type': 'text/plain' });
            res.end('Missing url parameter');
            return;
        }
        
        console.log('Proxying request to:', targetUrl);
        
        const protocol = targetUrl.startsWith('https:') ? https : http;
        const request = protocol.get(targetUrl, (proxyRes) => {
            // Add CORS headers
            res.writeHead(proxyRes.statusCode, {
                ...proxyRes.headers,
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            });
            proxyRes.pipe(res);
        });
        
        request.on('error', (error) => {
            console.error('Proxy error:', error);
            res.writeHead(500, { 'Content-Type': 'text/plain' });
            res.end('Proxy error: ' + error.message);
        });
        
        return;
    }
    
    // Regular file serving
    let filePath = '.' + parsedUrl.pathname;
    if (filePath === './' || filePath === './') {
        filePath = './real-imagenet-resnet.html';
    }
    
    console.log('Serving file:', filePath);

    const extname = path.extname(filePath).toLowerCase();
    const mimeTypes = {
        '.html': 'text/html',
        '.js': 'text/javascript',
        '.css': 'text/css',
        '.json': 'application/json',
        '.png': 'image/png',
        '.jpg': 'image/jpg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.wav': 'audio/wav',
        '.mp4': 'video/mp4',
        '.woff': 'application/font-woff',
        '.ttf': 'application/font-ttf',
        '.eot': 'application/vnd.ms-fontobject',
        '.otf': 'application/font-otf',
        '.wasm': 'application/wasm',
        '.txt': 'text/plain'
    };

    const contentType = mimeTypes[extname] || 'application/octet-stream';

    fs.readFile(filePath, (error, content) => {
        if (error) {
            if (error.code === 'ENOENT') {
                res.writeHead(404, { 'Content-Type': 'text/html' });
                res.end('<h1>404 Not Found</h1>', 'utf-8');
            } else {
                res.writeHead(500);
                res.end(`Server Error: ${error.code}`, 'utf-8');
            }
        } else {
            // Add CORS headers
            res.writeHead(200, { 
                'Content-Type': contentType,
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            });
            res.end(content, 'utf-8');
        }
    });
});

server.listen(port, () => {
    console.log(`Server running at http://localhost:${port}/`);
    console.log(`Open http://localhost:${port}/real-imagenet-resnet.html in your browser`);
    console.log(`CORS proxy available at http://localhost:${port}/proxy?url=<target_url>`);
}); 