import { crowdinConfig, crowdinEndpoints, isCrowdinConfigured } from '../config/crowdin';

export interface CrowdinScreenshot {
  id: number;
  projectId: number;
  name: string;
  url: string;
  tags: string[];
  strings: number[];
  createdAt: string;
  updatedAt: string;
}

export interface CrowdinScreenshotResponse {
  data: CrowdinScreenshot[];
  pagination: {
    limit: number;
    offset: number;
    hasMore: boolean;
  };
}

class CrowdinService {
  private async makeRequest(endpoint: string): Promise<any> {
    if (!isCrowdinConfigured()) {
      throw new Error('Crowdin API is not configured. Please add your API token to the configuration.');
    }

    const response = await fetch(endpoint, {
      headers: {
        'Authorization': `Bearer ${crowdinConfig.apiToken}`,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      throw new Error(`Crowdin API error: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async getScreenshots(limit: number = 50, offset: number = 0): Promise<CrowdinScreenshotResponse> {
    const endpoint = `${crowdinEndpoints.screenshots(crowdinConfig.projectId)}?limit=${limit}&offset=${offset}`;
    return this.makeRequest(endpoint);
  }

  async getScreenshot(screenshotId: string): Promise<CrowdinScreenshot> {
    const endpoint = crowdinEndpoints.screenshot(crowdinConfig.projectId, screenshotId);
    const response = await this.makeRequest(endpoint);
    return response.data;
  }

  async getScreenshotTags(screenshotId: string): Promise<any[]> {
    const endpoint = crowdinEndpoints.screenshotTags(crowdinConfig.projectId, screenshotId);
    const response = await this.makeRequest(endpoint);
    return response.data;
  }

  async getScreenshotStrings(screenshotId: string): Promise<any[]> {
    const endpoint = crowdinEndpoints.screenshotStrings(crowdinConfig.projectId, screenshotId);
    const response = await this.makeRequest(endpoint);
    return response.data;
  }

  // Helper method to get all screenshots (handles pagination)
  async getAllScreenshots(): Promise<CrowdinScreenshot[]> {
    const allScreenshots: CrowdinScreenshot[] = [];
    let offset = 0;
    const limit = 50;
    let hasMore = true;

    while (hasMore) {
      const response = await this.getScreenshots(limit, offset);
      allScreenshots.push(...response.data);
      hasMore = response.pagination.hasMore;
      offset += limit;
    }

    return allScreenshots;
  }
}

export const crowdinService = new CrowdinService(); 