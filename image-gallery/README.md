# LEVANTE Image Gallery

A comprehensive image gallery application for browsing LEVANTE framework assets and screenshots from multiple sources.

## 🎯 Features

### 📁 Assets Tab
- Browse high-resolution assets from LEVANTE cognitive tasks
- Filter by task type, implementation status, and search terms
- Sort by filename, task name, file size, or modification date
- View detailed metadata including core task implementations
- Full-screen image viewing and path copying

### 📸 GitHub Screenshots Tab
- Browse Cypress test screenshots from the LEVANTE core-tasks repository
- Recursive directory scanning to find all image files
- Filter by filename or path
- Sort by filename, path, or file size
- Direct links to GitHub repository files
- Source: [core-tasks/cypress/screenshots](https://github.com/levante-framework/core-tasks/tree/14337ff781dda568b50f09be5f636259bc917245/task-launcher/cypress/screenshots)

### 🌐 Crowdin Screenshots Tab
- Browse screenshots from the LEVANTE translations project on Crowdin
- Requires API token setup (see [CROWDIN_SETUP.md](CROWDIN_SETUP.md))
- Filter by name or tags
- Sort by name, creation date, update date, or strings count
- Integration with Crowdin API for real-time data

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ 
- npm or yarn

### Installation
```cmd
cd image-gallery
npm install
```

### Development
```cmd
npm run dev
```

The app will open at `http://localhost:3001`

### Build for Production
```cmd
npm run build
```

## 📋 Tab Descriptions

### 1. Assets Tab
Displays LEVANTE core task assets with rich metadata including:
- Task implementation status
- Core task mappings
- Item-level information (numbers, variants, conditions)
- Resolution analysis
- GitHub repository links

### 2. GitHub Screenshots Tab
Shows Cypress test screenshots from the core-tasks repository:
- Automatically scans all subdirectories
- Supports common image formats (PNG, JPG, JPEG, GIF, BMP, WebP, SVG)
- Displays file paths and sizes
- Links directly to GitHub repository files

### 3. Crowdin Screenshots Tab
Requires setup to access Crowdin API:
- Browse translation project screenshots
- View tags and string associations
- Requires API token configuration
- See [CROWDIN_SETUP.md](CROWDIN_SETUP.md) for setup instructions

## 🔧 Configuration

### Assets Configuration
Update `../config.js` to point to your GitHub repository:
```javascript
github: {
  owner: 'your-username',
  repo: 'your-repo-name',
  baseUrl: 'https://raw.githubusercontent.com/your-username/your-repo-name/main',
}
```

### GitHub Screenshots Configuration
The GitHub screenshots tab automatically uses:
- Repository: `levante-framework/core-tasks`
- Branch: `14337ff781dda568b50f09be5f636259bc917245`
- Path: `task-launcher/cypress/screenshots`

### Crowdin Configuration
See [CROWDIN_SETUP.md](CROWDIN_SETUP.md) for detailed setup instructions.

## 🛠 Development

### Project Structure
```
src/
├── components/
│   ├── ImageCard.vue          # Asset display component
│   ├── ScreenshotCard.vue     # Crowdin screenshot component
│   ├── GitHubScreenshotCard.vue # GitHub screenshot component
│   └── ResolutionChart.vue    # Resolution analysis chart
├── services/
│   ├── crowdinService.ts      # Crowdin API integration
│   └── githubService.ts       # GitHub API integration
├── config/
│   └── crowdin.ts             # Crowdin configuration
├── types/
│   └── Image.ts               # TypeScript type definitions
└── App.vue                    # Main application component
```

### Available Scripts
- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run type-check` - Run TypeScript type checking

## 🌐 API Integrations

### GitHub API
- Uses GitHub REST API v3
- No authentication required for public repositories
- Recursive directory scanning
- Rate limit: 60 requests/hour for unauthenticated requests

### Crowdin API
- Uses Crowdin API v2
- Requires personal access token
- Supports pagination for large datasets
- Rate limit: Varies by plan

## 📱 Responsive Design

The application is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones

Tab navigation adapts to screen size:
- Desktop: Horizontal tab layout
- Mobile: Vertical tab layout

## 🔒 Security

- API tokens are stored in client-side configuration
- No sensitive data is logged or transmitted unnecessarily
- GitHub API calls use public endpoints only
- Crowdin API requires proper token scoping

## 📚 Additional Resources

- [LEVANTE Framework](https://github.com/levante-framework)
- [Crowdin API Documentation](https://developer.crowdin.com/api/v2/)
- [GitHub API Documentation](https://docs.github.com/en/rest)
- [Vue.js Documentation](https://vuejs.org/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is part of the LEVANTE framework and follows the same licensing terms. 