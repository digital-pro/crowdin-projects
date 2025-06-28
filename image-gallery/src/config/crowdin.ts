// Crowdin API Configuration
export interface CrowdinConfig {
  apiToken: string;
  projectId: string;
  baseUrl: string;
}

// Default configuration - update these values with your actual Crowdin credentials
export const crowdinConfig: CrowdinConfig = {
  apiToken: '', // Add your Crowdin API token here
  projectId: 'levantetranslations', // LEVANTE translations project
  baseUrl: 'https://api.crowdin.com/api/v2'
};

// Crowdin API endpoints
export const crowdinEndpoints = {
  screenshots: (projectId: string) => `${crowdinConfig.baseUrl}/projects/${projectId}/screenshots`,
  screenshot: (projectId: string, screenshotId: string) => `${crowdinConfig.baseUrl}/projects/${projectId}/screenshots/${screenshotId}`,
  screenshotTags: (projectId: string, screenshotId: string) => `${crowdinConfig.baseUrl}/projects/${projectId}/screenshots/${screenshotId}/tags`,
  screenshotStrings: (projectId: string, screenshotId: string) => `${crowdinConfig.baseUrl}/projects/${projectId}/screenshots/${screenshotId}/strings`
};

// Helper function to check if Crowdin is configured
export const isCrowdinConfigured = (): boolean => {
  return !!crowdinConfig.apiToken;
}; 