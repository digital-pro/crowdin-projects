# Crowdin Editor Button App

A custom Crowdin app that adds interactive buttons to the editor interface, enhancing the translation workflow with custom functionality.

## Features

- 🎯 Custom buttons integrated into Crowdin editor
- 🚀 Modern, responsive UI with smooth animations
- 📡 RESTful API for handling button actions
- 🔧 Easy to customize and extend
- 📱 Mobile-friendly design

## Project Structure

```
editor-button-app/
├── manifest.json          # Crowdin app configuration
├── package.json          # Node.js dependencies and scripts
├── index.js             # Express server (main entry point)
├── public/
│   └── editor-button.html # Frontend interface
└── README.md           # This file
```

## Setup Instructions

### 1. Install Dependencies

```bash
cd editor-button-app
npm install
```

### 2. Run the Application

For development (with auto-restart):
```bash
npm run dev
```

For production:
```bash
npm start
```

The app will be available at:
- Main app: `http://localhost:3000`
- Manifest: `http://localhost:3000/manifest.json`
- Editor button: `http://localhost:3000/editor-button`
- Health check: `http://localhost:3000/health`

## Crowdin Integration

### 1. Install the App in Crowdin

1. Go to your Crowdin project settings
2. Navigate to "Apps" section
3. Click "Install Custom App"
4. Enter your app's manifest URL: `http://your-domain.com/manifest.json`
5. Follow the installation prompts

### 2. Configure Your Domain

For production deployment, update the `manifest.json` file:
- Replace `your-website.com` with your actual domain
- Update the author email address
- Modify the app description if needed

## Customization

### Adding New Button Actions

1. **Frontend (editor-button.html)**: Add new buttons in the `button-group` div
2. **Backend (index.js)**: Handle new actions in the `/api/button-action` endpoint

Example of adding a new button:

```html
<button class="custom-button" onclick="performAction('new-action')">
    <span class="button-text">New Action</span>
</button>
```

Then handle it in the server:

```javascript
app.post('/api/button-action', (req, res) => {
  const { action } = req.body;
  
  switch(action) {
    case 'new-action':
      // Your custom logic here
      break;
    // ... other cases
  }
});
```

### Styling Customization

The CSS in `editor-button.html` uses CSS custom properties and modern styling. You can:
- Change color schemes by modifying the gradient backgrounds
- Adjust button sizes and spacing
- Add new button variants with different classes

### API Integration

The app is designed to integrate with external APIs. Common use cases:
- Translation validation services
- Quality assurance tools
- Custom translation memory lookups
- Automated terminology checks

## Deployment Options

### 1. Local Development
- Use `npm run dev` for development
- Access via `http://localhost:3000`

### 2. Cloud Deployment
Popular options include:
- **Heroku**: Easy deployment with git integration
- **Vercel**: Great for Node.js apps
- **Railway**: Simple deployment platform
- **DigitalOcean App Platform**: Scalable hosting

### 3. Self-Hosted
- Deploy on your own server
- Use PM2 for process management
- Set up reverse proxy with Nginx

## Environment Variables

You can configure the app using environment variables:

```bash
PORT=3000                    # Server port (default: 3000)
NODE_ENV=production         # Environment mode
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/manifest.json` | GET | App manifest for Crowdin |
| `/editor-button` | GET | Main editor interface |
| `/api/button-action` | POST | Handle button actions |
| `/health` | GET | Health check endpoint |

## Development Tips

1. **Testing**: Use the browser's developer tools to test the interface
2. **Debugging**: Check the server console for API request logs
3. **CORS**: The app includes CORS middleware for cross-origin requests
4. **Security**: Add authentication for production use

## Troubleshooting

### Common Issues

1. **App not loading in Crowdin**
   - Check that your server is accessible from the internet
   - Verify the manifest.json URL is correct
   - Ensure CORS is properly configured

2. **Button actions not working**
   - Check browser console for JavaScript errors
   - Verify the API endpoint is responding
   - Check network connectivity

3. **Styling issues**
   - Clear browser cache
   - Check for CSS conflicts
   - Verify responsive design on different screen sizes

## Contributing

To contribute to this project:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the ISC License.

## Support

For questions or issues:
- Check the troubleshooting section above
- Review Crowdin's app development documentation
- Create an issue in the project repository

---

**Happy translating! 🌍✨** 