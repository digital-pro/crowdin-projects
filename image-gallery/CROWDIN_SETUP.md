# Crowdin Screenshots Integration Setup

This guide explains how to set up the Crowdin screenshots integration for the LEVANTE Image Gallery.

## 🔑 Getting Your Crowdin API Token

1. **Log in to Crowdin**
   - Go to [Crowdin](https://crowdin.com) and sign in to your account
   - Navigate to your profile settings

2. **Generate API Token**
   - Go to **Account Settings** → **API** → **Personal Access Tokens**
   - Click **Create Token**
   - Give it a name like "LEVANTE Image Gallery"
   - Select the necessary scopes (at minimum, you need `screenshots:read`)
   - Copy the generated token (you won't be able to see it again!)

## ⚙️ Configuring the App

1. **Update the Configuration**
   - Open `src/config/crowdin.ts`
   - Replace the empty `apiToken` with your actual token:

```typescript
export const crowdinConfig: CrowdinConfig = {
  apiToken: 'your-actual-api-token-here', // ← Add your token here
  projectId: 'levantetranslations',
  baseUrl: 'https://api.crowdin.com/api/v2'
};
```

2. **Verify Project Access**
   - Ensure you have access to the `levantetranslations` project
   - The project ID should match your Crowdin project

## 🚀 Testing the Integration

1. **Start the Development Server**
   ```cmd
   npm run dev
   ```

2. **Navigate to Screenshots Tab**
   - Click on the "📸 Screenshots" tab
   - If configured correctly, you should see screenshots loading
   - If not, check the browser console for error messages

## 🔧 Troubleshooting

### "Crowdin API is not configured" Error
- Make sure you've added your API token to `src/config/crowdin.ts`
- Verify the token is not empty or contains extra spaces

### "401 Unauthorized" Error
- Check that your API token is valid and not expired
- Ensure you have the correct permissions for the project

### "404 Not Found" Error
- Verify the project ID is correct (`levantetranslations`)
- Make sure you have access to the project

### No Screenshots Loading
- Check if the project has any screenshots uploaded
- Verify your API token has the `screenshots:read` scope

## 📋 API Scopes Required

For the screenshots integration to work, your API token needs these scopes:
- `screenshots:read` - To read screenshot metadata and URLs

## 🔒 Security Notes

- **Never commit your API token to version control**
- Consider using environment variables for production
- Regularly rotate your API tokens
- Use the minimum required scopes for security

## 🌐 Direct Access

If you prefer to access screenshots directly:
- Visit: [https://crowdin.com/project/levantetranslations/screenshots](https://crowdin.com/project/levantetranslations/screenshots)
- This requires manual login and navigation

## 📚 Additional Resources

- [Crowdin API Documentation](https://developer.crowdin.com/api/v2/)
- [Crowdin Screenshots API](https://developer.crowdin.com/api/v2/#operation/api.projects.screenshots.getMany)
- [Crowdin Personal Access Tokens](https://support.crowdin.com/enterprise/api/#personal-access-tokens) 