export interface GitHubFile {
  name: string;
  path: string;
  sha: string;
  size: number;
  url: string;
  html_url: string;
  git_url: string;
  download_url: string;
  type: 'file' | 'dir';
  content?: string;
  encoding?: string;
}

export interface GitHubScreenshot {
  filename: string;
  path: string;
  size: number;
  publicPath: string;
  githubUrl: string;
  relativePath: string;
  lastModified?: string;
  width?: number;
  height?: number;
  format?: string;
}

class GitHubService {
  private baseUrl = 'https://api.github.com';
  private repoOwner = 'levante-framework';
  private repoName = 'core-tasks';
  private branch = '14337ff781dda568b50f09be5f636259bc917245';
  private screenshotsPath = 'task-launcher/cypress/screenshots';

  private async makeRequest(endpoint: string): Promise<any> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      headers: {
        'Accept': 'application/vnd.github.v3+json',
        'User-Agent': 'LEVANTE-Image-Gallery'
      }
    });

    if (!response.ok) {
      throw new Error(`GitHub API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getRepositoryContents(path: string): Promise<GitHubFile[]> {
    const endpoint = `/repos/${this.repoOwner}/${this.repoName}/contents/${path}?ref=${this.branch}`;
    const response = await this.makeRequest(endpoint);
    
    // Handle single file response
    if (!Array.isArray(response)) {
      return [response];
    }
    
    return response;
  }

  async getAllScreenshots(): Promise<GitHubScreenshot[]> {
    const screenshots: GitHubScreenshot[] = [];
    
    try {
      await this.recursiveScanDirectory(this.screenshotsPath, screenshots);
    } catch (error) {
      console.error('Error scanning GitHub repository:', error);
    }

    return screenshots;
  }

  private async recursiveScanDirectory(dirPath: string, screenshots: GitHubScreenshot[]): Promise<void> {
    try {
      const contents = await this.getRepositoryContents(dirPath);
      
      for (const item of contents) {
        if (item.type === 'file') {
          // Check if it's an image file
          if (this.isImageFile(item.name)) {
            const screenshot: GitHubScreenshot = {
              filename: item.name,
              path: item.path,
              size: item.size,
              publicPath: item.download_url,
              githubUrl: item.html_url,
              relativePath: item.path.replace(`${this.screenshotsPath}/`, ''),
              lastModified: new Date().toISOString() // GitHub API doesn't provide modification date in contents endpoint
            };
            screenshots.push(screenshot);
          }
        } else if (item.type === 'dir') {
          // Recursively scan subdirectories
          await this.recursiveScanDirectory(item.path, screenshots);
        }
      }
    } catch (error) {
      console.warn(`Error scanning directory ${dirPath}:`, error);
    }
  }

  private isImageFile(filename: string): boolean {
    const imageExtensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.webp', '.svg'];
    const lowerFilename = filename.toLowerCase();
    return imageExtensions.some(ext => lowerFilename.endsWith(ext));
  }

  // Helper method to get file metadata (for future use)
  async getFileMetadata(path: string): Promise<GitHubFile> {
    const endpoint = `/repos/${this.repoOwner}/${this.repoName}/contents/${path}?ref=${this.branch}`;
    return this.makeRequest(endpoint);
  }
}

export const githubService = new GitHubService(); 