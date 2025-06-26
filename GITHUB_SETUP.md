# GitHub Setup for LEVANTE Image Gallery

## 🚀 Quick Setup Instructions

### Step 1: Create GitHub Repository
1. Go to [GitHub](https://github.com) and create a new repository
2. Name it `core-task-assets` (or any name you prefer)
3. Make it **Public** (required for raw file access)
4. Initialize with README

### Step 2: Upload Your Assets

**On Windows (Command Prompt):**
```cmd
# Clone the new repository
git clone https://github.com/YOUR_USERNAME/core-task-assets.git
cd core-task-assets

# Copy your assets to the repository
xcopy "C:\path\to\your\levante\core-task-assets\*" . /E /I

# Commit and push
git add .
git commit -m "Add LEVANTE core task assets"
git push origin main
```

**On Windows (PowerShell):**
```powershell
# Clone the new repository
git clone https://github.com/YOUR_USERNAME/core-task-assets.git
cd core-task-assets

# Copy your assets to the repository
Copy-Item "C:\path\to\your\levante\core-task-assets\*" -Destination . -Recurse

# Commit and push
git add .
git commit -m "Add LEVANTE core task assets"
git push origin main
```

**On Unix/Linux/macOS:**
```bash
# Clone the new repository
git clone https://github.com/YOUR_USERNAME/core-task-assets.git
cd core-task-assets

# Copy your assets to the repository
cp -r /path/to/your/levante/core-task-assets/* .

# Commit and push
git add .
git commit -m "Add LEVANTE core task assets"
git push origin main
```

### Step 3: Update Configuration
Edit `config.js` and replace the GitHub URL:

```javascript
github: {
  baseUrl: 'https://raw.githubusercontent.com/YOUR_USERNAME/core-task-assets/main',
}
```

### Step 4: Regenerate Metadata
```cmd
node generate-enhanced-metadata.js
```

### Step 5: Test Locally
```cmd
cd image-gallery
npm run dev
```

### Step 6: Deploy
```cmd
vercel --prod
```

## 🔗 GitHub Raw URL Format

The raw GitHub URL format is:
```
https://raw.githubusercontent.com/USERNAME/REPOSITORY/BRANCH/PATH_TO_FILE
```

Example:
```
https://raw.githubusercontent.com/johndoe/core-task-assets/main/TROG/original/1-boy.png
```

## ✅ Benefits of GitHub Hosting

- ✨ **Faster deployments** - No need to upload 566 images
- 🌐 **Global CDN** - GitHub serves files from edge locations
- 🔄 **Version control** - Track changes to your assets
- 💰 **Free hosting** - GitHub provides free raw file serving
- 📱 **Smaller app bundle** - Only code gets deployed

## 🛠 Troubleshooting

**Images not loading?**
- Ensure repository is **public**
- Check the GitHub URL in browser
- Verify the file path matches exactly
- Check browser console for CORS errors

**Want to use a different branch?**
- Update the URL in `config.js` to use `/develop` or `/staging`
- Make sure the branch exists and has the assets 