export interface TaskReference {
  filename: string;
  taskFile: string;
  matchCount: number;
  matchType: string;
}

export interface ImageData {
  filename: string;
  taskName: string;
  coreTaskName?: string;
  relativePath: string;
  publicPath: string;
  githubUrl: string;
  size: number;
  lastModified: string;
  width: number | null;
  height: number | null;
  format: string | null;
  hasTaskImplementation: boolean;
  isReferencedInTask: boolean;
  taskReferences?: TaskReference[];
  itemNumber: number | null;
  variant: string | null;
  condition: string | null;
  itemDescription: string | null;
}

export interface ResolutionBucket {
  width: number;
  count: number;
  tasks: string[];
}

export interface ResolutionAnalysis {
  totalWithDimensions: number;
  resolutionBuckets: ResolutionBucket[];
  commonWidths: { width: number; count: number }[];
}

export interface TaskAssetMapping {
  totalAssets: number;
  referencedAssets: number;
  references: TaskReference[];
}

export interface TaskConfiguration {
  hasTimeline: boolean;
  hasConfig: boolean;
  path: string;
}

export interface ImageMetadata {
  totalImages: number;
  tasks: string[];
  coreTasks: string[];
  images: ImageData[];
  resolutionAnalysis?: ResolutionAnalysis;
  taskAssetMappings: Record<string, TaskAssetMapping>;
  taskConfigurations: Record<string, TaskConfiguration>;
  generatedAt: string;
}

export interface FilterOptions {
  task: string;
  searchTerm: string;
  implementationStatus: string;
}

export interface SortOptions {
  field: 'filename' | 'taskName' | 'size' | 'lastModified';
  direction: 'asc' | 'desc';
} 