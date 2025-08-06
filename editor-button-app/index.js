const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const fetch = require('node-fetch');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;

// Crowdin API configuration
const CROWDIN_API_BASE = 'https://api.crowdin.com/api/v2';
const CROWDIN_ENTERPRISE_API_BASE = 'https://api.crowdin.com/api/v2'; // Can be customized for enterprise

// Deployment health tracking
let deploymentHealth = {
  startTime: new Date(),
  requestCount: 0,
  errors: 0,
  lastHealthCheck: new Date()
};

// Function to extract string information from request
function extractStringInfo(requestBody) {
  const stringInfo = {
    stringId: null,
    stringKey: null,
    identifier: null,
    sourceString: null,
    targetString: null,
    context: null,
    maxLength: null,
    isPlural: null,
    pluralForm: null,
    projectId: null,
    fileId: null,
    languageId: null
  };
  
  // Extract from crowdinContext
  if (requestBody.crowdinContext) {
    const ctx = requestBody.crowdinContext;
    stringInfo.stringId = ctx.stringId || ctx.string_id || null;
    stringInfo.stringKey = ctx.stringKey || ctx.string_key || ctx.key || ctx.identifier || null;
    stringInfo.identifier = ctx.identifier || ctx.key || ctx.stringKey || null;
    stringInfo.sourceString = ctx.sourceString || ctx.source_string || ctx.source || null;
    stringInfo.targetString = ctx.targetString || ctx.target_string || ctx.target || null;
    stringInfo.context = ctx.context || ctx.string_context || null;
    stringInfo.maxLength = ctx.maxLength || ctx.max_length || null;
    stringInfo.isPlural = ctx.isPlural || ctx.is_plural || null;
    stringInfo.pluralForm = ctx.pluralForm || ctx.plural_form || null;
    stringInfo.projectId = ctx.projectId || ctx.project_id || null;
    stringInfo.fileId = ctx.fileId || ctx.file_id || null;
    stringInfo.languageId = ctx.languageId || ctx.language_id || null;
  }
  
  // Extract from URL parameters in windowLocation
  if (requestBody.windowLocation && requestBody.windowLocation.search) {
    const urlParams = new URLSearchParams(requestBody.windowLocation.search);
    
    // Try various parameter names that Crowdin might use
    const possibleStringKeyParams = [
      'stringKey', 'string_key', 'key', 'identifier', 'string_identifier',
      'sourceKey', 'source_key', 'translationKey', 'translation_key'
    ];
    
    const possibleStringIdParams = [
      'stringId', 'string_id', 'id', 'translation_id'
    ];
    
    // Extract string key/identifier
    for (const param of possibleStringKeyParams) {
      const value = urlParams.get(param);
      if (value && !stringInfo.stringKey) {
        stringInfo.stringKey = value;
        stringInfo.identifier = value;
        break;
      }
    }
    
    // Extract string ID
    for (const param of possibleStringIdParams) {
      const value = urlParams.get(param);
      if (value && !stringInfo.stringId) {
        stringInfo.stringId = value;
        break;
      }
    }
    
    // Extract project context
    stringInfo.projectId = stringInfo.projectId || urlParams.get('projectId') || urlParams.get('project_id');
    stringInfo.fileId = stringInfo.fileId || urlParams.get('fileId') || urlParams.get('file_id');
    stringInfo.languageId = stringInfo.languageId || urlParams.get('languageId') || urlParams.get('language_id');
    
    // Extract other string-related parameters
    stringInfo.sourceString = stringInfo.sourceString || urlParams.get('sourceString') || urlParams.get('source');
    stringInfo.targetString = stringInfo.targetString || urlParams.get('targetString') || urlParams.get('target');
    stringInfo.context = stringInfo.context || urlParams.get('context') || urlParams.get('string_context');
    
    // Try to decode JWT token if present
    const jwtToken = urlParams.get('jwtToken');
    if (jwtToken) {
      try {
        // Decode JWT payload (without verification for debugging)
        const payload = JSON.parse(Buffer.from(jwtToken.split('.')[1], 'base64').toString());
        console.log('JWT Payload:', JSON.stringify(payload, null, 2));
        
        // Extract context from JWT if available
        if (payload.context) {
          Object.assign(stringInfo, payload.context);
        }
        if (payload.stringId) stringInfo.stringId = payload.stringId;
        if (payload.stringKey) stringInfo.stringKey = payload.stringKey;
        if (payload.projectId) stringInfo.projectId = payload.projectId;
        if (payload.fileId) stringInfo.fileId = payload.fileId;
        if (payload.languageId) stringInfo.languageId = payload.languageId;
      } catch (e) {
        console.log('Failed to decode JWT token:', e.message);
      }
    }
  }
  
  // Extract from URL hash if present
  if (requestBody.windowLocation && requestBody.windowLocation.hash) {
    const hash = requestBody.windowLocation.hash.substring(1); // Remove #
    const hashParams = new URLSearchParams(hash);
    
    // Check hash parameters for string info
    stringInfo.stringKey = stringInfo.stringKey || hashParams.get('stringKey') || hashParams.get('key');
    stringInfo.stringId = stringInfo.stringId || hashParams.get('stringId') || hashParams.get('id');
    stringInfo.projectId = stringInfo.projectId || hashParams.get('projectId');
    stringInfo.fileId = stringInfo.fileId || hashParams.get('fileId');
  }
  
  // Extract from referrer URL if available
  if (requestBody.referrer) {
    try {
      const referrerUrl = new URL(requestBody.referrer);
      const referrerParams = new URLSearchParams(referrerUrl.search);
      
      stringInfo.stringKey = stringInfo.stringKey || referrerParams.get('stringKey') || referrerParams.get('key');
      stringInfo.stringId = stringInfo.stringId || referrerParams.get('stringId') || referrerParams.get('id');
      stringInfo.projectId = stringInfo.projectId || referrerParams.get('projectId');
      stringInfo.fileId = stringInfo.fileId || referrerParams.get('fileId');
    } catch (e) {
      // Invalid referrer URL, ignore
    }
  }
  
  return stringInfo;
}

// Function to make authenticated Crowdin API calls
async function makeCrowdinAPICall(endpoint, token, method = 'GET', body = null) {
  const url = `${CROWDIN_API_BASE}${endpoint}`;
  
  const options = {
    method,
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
      'User-Agent': 'Crowdin-String-Extractor-App/1.0'
    }
  };
  
  if (body && method !== 'GET') {
    options.body = JSON.stringify(body);
  }
  
  console.log(`🌐 Making Crowdin API call: ${method} ${url}`);
  
  try {
    const response = await fetch(url, options);
    const data = await response.json();
    
    if (!response.ok) {
      console.error('❌ Crowdin API error:', data);
      throw new Error(`Crowdin API error: ${response.status} - ${data.error?.message || 'Unknown error'}`);
    }
    
    console.log('✅ Crowdin API response received');
    return data;
  } catch (error) {
    console.error('❌ Failed to call Crowdin API:', error.message);
    throw error;
  }
}

// Function to fetch string details from Crowdin API
async function fetchStringFromAPI(token, projectId, stringId, stringKey, fileId, strategy = 'specific', limit = 10) {
  console.log('🔍 Fetching string details from Crowdin API...');
  console.log(`Project ID: ${projectId}, Strategy: ${strategy}, String ID: ${stringId}, String Key: ${stringKey}, File ID: ${fileId}`);
  
  if (!token) {
    throw new Error('No authentication token provided');
  }
  
  if (!projectId) {
    throw new Error('No project ID provided');
  }
  
  try {
    let stringData = null;
    let stringsData = null;
    let debugInfo = {
      attempts: [],
      projectInfo: null,
      errors: []
    };
    
    // First, try to get project info to validate access and project type
    try {
      console.log(`📊 Fetching project info for validation...`);
      const projectResponse = await makeCrowdinAPICall(`/projects/${projectId}`, token);
      debugInfo.projectInfo = {
        id: projectResponse.data.id,
        name: projectResponse.data.name,
        type: projectResponse.data.type,
        sourceLanguageId: projectResponse.data.sourceLanguageId,
        targetLanguageIds: projectResponse.data.targetLanguageIds
      };
      console.log(`✅ Project found: ${projectResponse.data.name} (Type: ${projectResponse.data.type})`);
    } catch (error) {
      console.log(`❌ Failed to fetch project info: ${error.message}`);
      debugInfo.errors.push(`Project access error: ${error.message}`);
      
      // If project info fails, the project ID might be wrong or permissions insufficient
      return {
        success: false,
        error: `Cannot access project "${projectId}". Please check: 1) Project ID is correct, 2) API token has project access permissions, 3) Project exists and is accessible.`,
        debugInfo: debugInfo
      };
    }
    
    // Strategy 1: Get recent strings for user selection
    if (strategy === 'recent_strings') {
      const attempts = [
        { endpoint: `/projects/${projectId}/strings?limit=${limit}&orderBy=createdAt desc`, name: 'Recent strings (desc)' },
        { endpoint: `/projects/${projectId}/strings?limit=${limit}&orderBy=createdAt asc`, name: 'Recent strings (asc)' },
        { endpoint: `/projects/${projectId}/strings?limit=${limit}`, name: 'All strings (default)' },
        { endpoint: `/projects/${projectId}/strings`, name: 'All strings (no limit)' }
      ];
      
      for (const attempt of attempts) {
        try {
          console.log(`📊 Trying: ${attempt.name}`);
          debugInfo.attempts.push({ endpoint: attempt.endpoint, status: 'trying' });
          
          const response = await makeCrowdinAPICall(attempt.endpoint, token);
          
          if (response.data && response.data.length > 0) {
            stringsData = response.data;
            console.log(`✅ Found ${stringsData.length} strings using: ${attempt.name}`);
            debugInfo.attempts[debugInfo.attempts.length - 1].status = 'success';
            debugInfo.attempts[debugInfo.attempts.length - 1].count = stringsData.length;
            
            return {
              success: true,
              strings: stringsData,
              method: 'recent_strings',
              debugInfo: debugInfo
            };
          } else {
            console.log(`⚠️ No strings returned from: ${attempt.name}`);
            debugInfo.attempts[debugInfo.attempts.length - 1].status = 'empty';
          }
        } catch (error) {
          console.log(`❌ Failed ${attempt.name}: ${error.message}`);
          debugInfo.attempts[debugInfo.attempts.length - 1].status = 'error';
          debugInfo.attempts[debugInfo.attempts.length - 1].error = error.message;
          debugInfo.errors.push(`${attempt.name}: ${error.message}`);
        }
      }
      
      // If no strings found, try to get files and then strings from files
      try {
        console.log(`📁 Trying to get files first...`);
        const filesResponse = await makeCrowdinAPICall(`/projects/${projectId}/files`, token);
        
        if (filesResponse.data && filesResponse.data.length > 0) {
          console.log(`✅ Found ${filesResponse.data.length} files`);
          debugInfo.filesFound = filesResponse.data.length;
          
          // Try to get strings from the first file
          const firstFile = filesResponse.data[0];
          try {
            console.log(`📄 Getting strings from file: ${firstFile.name} (ID: ${firstFile.id})`);
            const fileStringsResponse = await makeCrowdinAPICall(`/projects/${projectId}/strings?fileId=${firstFile.id}&limit=${limit}`, token);
            
            if (fileStringsResponse.data && fileStringsResponse.data.length > 0) {
              stringsData = fileStringsResponse.data;
              console.log(`✅ Found ${stringsData.length} strings from file: ${firstFile.name}`);
              
              return {
                success: true,
                strings: stringsData,
                method: 'file_strings',
                debugInfo: debugInfo
              };
            }
          } catch (error) {
            console.log(`❌ Failed to get strings from file: ${error.message}`);
            debugInfo.errors.push(`File strings error: ${error.message}`);
          }
        } else {
          console.log(`⚠️ No files found in project`);
          debugInfo.filesFound = 0;
        }
      } catch (error) {
        console.log(`❌ Failed to get files: ${error.message}`);
        debugInfo.errors.push(`Files error: ${error.message}`);
      }
    }
    
    // Strategy 2: Get string by ID if available
    if (stringId && strategy !== 'recent_strings') {
      try {
        console.log(`🎯 Attempting to fetch string by ID: ${stringId}`);
        const response = await makeCrowdinAPICall(`/projects/${projectId}/strings/${stringId}`, token);
        stringData = response.data;
        console.log('✅ String found by ID');
        debugInfo.attempts.push({ method: 'byId', status: 'success' });
      } catch (error) {
        console.log('❌ Failed to fetch string by ID:', error.message);
        debugInfo.attempts.push({ method: 'byId', status: 'error', error: error.message });
      }
    }
    
    // Strategy 3: Search strings by identifier/key if ID method failed
    if (!stringData && (stringKey || stringId) && strategy !== 'recent_strings') {
      try {
        console.log(`🔍 Searching strings by identifier: ${stringKey || stringId}`);
        const searchParams = new URLSearchParams({
          limit: '20'
        });
        
        if (stringKey) {
          searchParams.append('filter', stringKey);
        } else if (stringId) {
          searchParams.append('filter', stringId);
        }
        
        if (fileId) {
          searchParams.append('fileId', fileId);
        }
        
        const response = await makeCrowdinAPICall(`/projects/${projectId}/strings?${searchParams}`, token);
        
        if (response.data && response.data.length > 0) {
          // Find exact match or return all matches for user selection
          const exactMatch = response.data.find(s => 
            s.identifier === stringKey || 
            s.text === stringKey ||
            s.id.toString() === stringId
          );
          
          if (exactMatch) {
            stringData = exactMatch;
            console.log('✅ Exact string match found');
            debugInfo.attempts.push({ method: 'search', status: 'exact_match' });
          } else if (response.data.length === 1) {
            stringData = response.data[0];
            console.log('✅ Single string found by search');
            debugInfo.attempts.push({ method: 'search', status: 'single_match' });
          } else {
            // Multiple matches - return for user selection
            stringsData = response.data;
            console.log(`✅ Found ${stringsData.length} matching strings`);
            debugInfo.attempts.push({ method: 'search', status: 'multiple_matches', count: stringsData.length });
            
            return {
              success: true,
              strings: stringsData,
              method: 'search_results',
              debugInfo: debugInfo
            };
          }
        }
      } catch (error) {
        console.log('❌ Failed to search strings:', error.message);
        debugInfo.attempts.push({ method: 'search', status: 'error', error: error.message });
      }
    }
    
    // Strategy 4: Get all strings from file if file ID is available
    if (!stringData && !stringsData && fileId && strategy !== 'recent_strings') {
      try {
        console.log(`📁 Fetching strings from file: ${fileId}`);
        const response = await makeCrowdinAPICall(`/projects/${projectId}/strings?fileId=${fileId}&limit=50`, token);
        
        if (response.data && response.data.length > 0) {
          // If we have a string key/identifier, try to find it
          if (stringKey) {
            const match = response.data.find(s => 
              s.identifier === stringKey || 
              s.text === stringKey
            );
            if (match) {
              stringData = match;
              console.log('✅ String found in file');
              debugInfo.attempts.push({ method: 'file_search', status: 'found' });
            } else {
              // Return all strings from file for user selection
              stringsData = response.data;
              console.log(`✅ Found ${stringsData.length} strings in file`);
              debugInfo.attempts.push({ method: 'file_search', status: 'multiple', count: stringsData.length });
              
              return {
                success: true,
                strings: stringsData,
                method: 'file_strings',
                debugInfo: debugInfo
              };
            }
          } else {
            // Return all strings from file for user selection
            stringsData = response.data;
            console.log(`✅ Found ${stringsData.length} strings in file`);
            debugInfo.attempts.push({ method: 'file_all', status: 'success', count: stringsData.length });
            
            return {
              success: true,
              strings: stringsData,
              method: 'file_strings',
              debugInfo: debugInfo
            };
          }
        }
      } catch (error) {
        console.log('❌ Failed to fetch strings from file:', error.message);
        debugInfo.attempts.push({ method: 'file_search', status: 'error', error: error.message });
      }
    }
    
    if (stringData) {
      console.log('🎉 String data retrieved successfully:', {
        id: stringData.id,
        identifier: stringData.identifier,
        text: stringData.text?.substring(0, 100) + (stringData.text?.length > 100 ? '...' : ''),
        fileId: stringData.fileId
      });
      
      return {
        success: true,
        data: stringData,
        method: stringId ? 'byId' : stringKey ? 'bySearch' : fileId ? 'fromFile' : 'fallback',
        debugInfo: debugInfo
      };
    } else if (stringsData) {
      return {
        success: true,
        strings: stringsData,
        method: strategy || 'multiple_results',
        debugInfo: debugInfo
      };
    } else {
      console.log('❌ No string data found after all attempts');
      
      // Provide helpful error message based on what we found
      let errorMessage = 'No strings found in the project.';
      
      if (debugInfo.projectInfo) {
        errorMessage += ` Project "${debugInfo.projectInfo.name}" exists but appears to have no strings.`;
        
        if (debugInfo.filesFound === 0) {
          errorMessage += ' No files found in project - this might be a string-based project or files may not be uploaded yet.';
        } else if (debugInfo.filesFound > 0) {
          errorMessage += ` Found ${debugInfo.filesFound} files but no strings in them.`;
        }
      }
      
      return {
        success: false,
        error: errorMessage,
        searchedFor: { projectId, stringId, stringKey, fileId, strategy },
        debugInfo: debugInfo
      };
    }
    
  } catch (error) {
    console.error('❌ Error fetching string from API:', error.message);
    return {
      success: false,
      error: error.message,
      searchedFor: { projectId, stringId, stringKey, fileId, strategy },
      debugInfo: debugInfo
    };
  }
}

// Function to get project information
async function getProjectInfo(token, projectId) {
  try {
    console.log(`📊 Fetching project info for: ${projectId}`);
    const response = await makeCrowdinAPICall(`/projects/${projectId}`, token);
    return {
      success: true,
      data: response.data
    };
  } catch (error) {
    console.error('❌ Error fetching project info:', error.message);
    return {
      success: false,
      error: error.message
    };
  }
}

// Function to extract authentication token from request
function extractAuthToken(req) {
  // Try multiple sources for the token
  const token = req.headers.authorization?.replace('Bearer ', '') ||
                req.query.token ||
                req.query.jwtToken ||
                req.body.token ||
                req.body.jwtToken;
  
  // If it's a JWT token, try to extract the actual API token from it
  if (token && token.includes('.')) {
    try {
      const payload = JSON.parse(Buffer.from(token.split('.')[1], 'base64').toString());
      return payload.token || payload.apiToken || payload.access_token || token;
    } catch (e) {
      return token;
    }
  }
  
  return token;
}

// Middleware
app.use(cors({
  origin: '*',
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
  credentials: false
}));
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Request tracking middleware
app.use((req, res, next) => {
  deploymentHealth.requestCount++;
  deploymentHealth.lastHealthCheck = new Date();
  
  // Log all requests for debugging
  console.log(`${new Date().toISOString()} - ${req.method} ${req.path} - ${req.get('User-Agent') || 'Unknown'}`);
  
  next();
});

// Serve the manifest file dynamically
app.get('/manifest.json', (req, res) => {
  try {
    const manifestPath = path.join(__dirname, 'manifest.json');
    
    if (!fs.existsSync(manifestPath)) {
      console.error('Manifest file not found at:', manifestPath);
      deploymentHealth.errors++;
      return res.status(404).json({ error: 'Manifest not found' });
    }
    
    const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
    
    // Ensure URLs are absolute for production
    if (process.env.VERCEL) {
      const baseUrl = 'https://editor-button-app.vercel.app';
      if (manifest.modules && manifest.modules[0] && manifest.modules[0].url) {
        manifest.modules[0].url = `${baseUrl}/editor-button`;
      }
    }
    
    res.setHeader('Content-Type', 'application/json');
    res.setHeader('Cache-Control', 'public, max-age=300, s-maxage=300');
    res.json(manifest);
  } catch (error) {
    console.error('Error serving manifest:', error);
    deploymentHealth.errors++;
    res.status(500).json({ error: 'Failed to load manifest' });
  }
});

// New Crowdin API endpoint for string extraction
app.post('/api/crowdin/extract-string', async (req, res) => {
  console.log('\n=== CROWDIN API STRING EXTRACTION ===');
  console.log('Timestamp:', new Date().toISOString());
  console.log('Request body:', JSON.stringify(req.body, null, 2));
  
  try {
    const token = extractAuthToken(req);
    const { projectId, stringId, stringKey, fileId, languageId, strategy, limit } = req.body;
    
    if (!token) {
      return res.status(401).json({
        success: false,
        error: 'No authentication token provided',
        message: 'Please provide a valid Crowdin API token'
      });
    }
    
    if (!projectId) {
      return res.status(400).json({
        success: false,
        error: 'No project ID provided',
        message: 'Project ID is required to fetch string data'
      });
    }
    
    // Fetch string data from Crowdin API
    const stringResult = await fetchStringFromAPI(token, projectId, stringId, stringKey, fileId, strategy, limit);
    
    // Also get project info for context
    const projectResult = await getProjectInfo(token, projectId);
    
    const response = {
      success: stringResult.success,
      timestamp: new Date().toISOString(),
      string: stringResult.success ? stringResult.data : null,
      strings: stringResult.success ? stringResult.strings : null,
      project: projectResult.success ? projectResult.data : null,
      extractionMethod: stringResult.method || 'api',
      debugInfo: stringResult.debugInfo || null,
      searchParameters: {
        projectId,
        stringId,
        stringKey,
        fileId,
        languageId,
        strategy,
        limit
      }
    };
    
    if (!stringResult.success) {
      response.error = stringResult.error;
      response.searchedFor = stringResult.searchedFor;
    }
    
    console.log('API Response:', JSON.stringify(response, null, 2));
    console.log('=====================================\n');
    
    res.json(response);
    
  } catch (error) {
    console.error('❌ API endpoint error:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Enhanced endpoint for testing API connectivity
app.post('/api/crowdin/test-connection', async (req, res) => {
  console.log('\n=== CROWDIN API CONNECTION TEST ===');
  
  try {
    const token = extractAuthToken(req);
    
    if (!token) {
      return res.status(401).json({
        success: false,
        error: 'No authentication token provided'
      });
    }
    
    // Test API connectivity by fetching user profile
    const response = await makeCrowdinAPICall('/user', token);
    
    res.json({
      success: true,
      message: 'Crowdin API connection successful',
      user: response.data,
      timestamp: new Date().toISOString()
    });
    
  } catch (error) {
    console.error('❌ API connection test failed:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// New endpoint for discovering user's projects
app.post('/api/crowdin/discover-projects', async (req, res) => {
  console.log('\n=== CROWDIN PROJECT DISCOVERY ===');
  
  try {
    const token = extractAuthToken(req);
    
    if (!token) {
      return res.status(401).json({
        success: false,
        error: 'No authentication token provided'
      });
    }
    
    console.log('🔍 Fetching user projects...');
    
    // Get user's projects
    const response = await makeCrowdinAPICall('/projects?limit=100', token);
    
    if (response.data && response.data.length > 0) {
      const projects = response.data.map(project => ({
        id: project.id,
        name: project.name,
        type: project.type,
        sourceLanguageId: project.sourceLanguageId,
        targetLanguageIds: project.targetLanguageIds,
        createdAt: project.createdAt
      }));
      
      console.log(`✅ Found ${projects.length} accessible projects`);
      
      res.json({
        success: true,
        projects: projects,
        count: projects.length,
        timestamp: new Date().toISOString()
      });
    } else {
      console.log('⚠️ No projects found for this user');
      res.json({
        success: false,
        error: 'No projects found. This API token may not have access to any projects.',
        projects: [],
        timestamp: new Date().toISOString()
      });
    }
    
  } catch (error) {
    console.error('❌ Project discovery failed:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Fetch string details from Crowdin API to get identifier when missing
app.get('/api/crowdin/projects/:projectId/strings/:stringId', async (req, res) => {
  console.log('\n=== CROWDIN STRING DETAILS FETCH ===');
  
  try {
    const { projectId, stringId } = req.params;
    const token = extractAuthToken(req);
    
    if (!token) {
      return res.status(401).json({
        success: false,
        error: 'No authentication token provided'
      });
    }
    
    if (!projectId || !stringId) {
      return res.status(400).json({
        success: false,
        error: 'Project ID and String ID are required'
      });
    }
    
    console.log(`🔍 Fetching string ${stringId} from project ${projectId}`);
    
    // Fetch string details from Crowdin API
    const stringData = await makeCrowdinAPICall(`/projects/${projectId}/strings/${stringId}`, token);
    
    if (stringData && stringData.data) {
      console.log('✅ Successfully fetched string details:', {
        id: stringData.data.id,
        identifier: stringData.data.identifier,
        text: stringData.data.text?.substring(0, 50) + '...'
      });
      
      res.json({
        success: true,
        string: stringData.data,
        identifier: stringData.data.identifier,
        timestamp: new Date().toISOString()
      });
    } else {
      res.status(404).json({
        success: false,
        error: 'String not found',
        timestamp: new Date().toISOString()
      });
    }
    
  } catch (error) {
    console.error('❌ Error fetching string details:', error.message);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: new Date().toISOString()
    });
  }
});

// Main editor button route (legacy)
app.get('/editor-button', (req, res) => {
  try {
    const htmlPath = path.join(__dirname, 'public', 'audio-previewer.html');
    
    if (!fs.existsSync(htmlPath)) {
      console.error('Audio previewer HTML not found at:', htmlPath);
      deploymentHealth.errors++;
      return res.status(404).send('Audio previewer not found');
    }
    
    res.setHeader('Content-Type', 'text/html');
    res.setHeader('Cache-Control', 'public, max-age=300, s-maxage=300');
    res.sendFile(htmlPath);
  } catch (error) {
    console.error('Error serving audio previewer:', error);
    deploymentHealth.errors++;
    res.status(500).send('Failed to load audio previewer');
  }
});

// New translations panel route
app.get('/translations-panel', (req, res) => {
  console.log('📝 Translations panel requested');
  console.log('Query params:', req.query);
  console.log('Headers:', req.headers);
  
  // Check for empty authentication parameters
  if (req.query.client_id === '' || req.query.clientId === '' || req.query.jwtToken === '') {
    console.log('⚠️ Empty authentication parameters detected');
    console.log('client_id:', req.query.client_id);
    console.log('clientId:', req.query.clientId);
    console.log('jwtToken:', req.query.jwtToken);
  }
  
  // Check origin
  if (req.query.origin) {
    console.log('🌐 Origin:', req.query.origin);
  }
  
  res.sendFile(path.join(__dirname, 'public', 'translations-panel.html'));
});

// String key extractor route (legacy) - REDIRECT TO AUDIO PREVIEWER
app.get('/string-key-extractor', (req, res) => {
  console.log('🔑 Legacy string key extractor requested - redirecting to audio previewer');
  console.log('Query params:', req.query);
  
  // Preserve query parameters in redirect
  const queryString = Object.keys(req.query).length > 0 ? '?' + new URLSearchParams(req.query).toString() : '';
  res.redirect(`/audio-previewer${queryString}`);
});

// Audio previewer route
app.get('/audio-previewer', (req, res) => {
  console.log('🎵 Audio previewer requested');
  console.log('Query params:', req.query);
  console.log('Headers:', req.headers);
  
  // Log all parameters for debugging
  Object.keys(req.query).forEach(key => {
    console.log(`  ${key}: ${req.query[key]}`);
  });
  
  res.sendFile(path.join(__dirname, 'public', 'audio-previewer.html'));
});

// Test page route
app.get('/test', (req, res) => {
  console.log('🧪 Test page requested');
  console.log('Query params:', req.query);
  console.log('Headers:', req.headers);
  res.sendFile(path.join(__dirname, 'public', 'test.html'));
});

// API endpoint for button actions
app.post('/api/button-action', async (req, res) => {
  const timestamp = new Date().toISOString();
  
  // Enhanced logging
  console.log('\n=== BUTTON ACTION RECEIVED ===');
  console.log('Timestamp:', timestamp);
  console.log('Action Type:', req.body.action || 'UNKNOWN');
  console.log('Request Headers:', JSON.stringify(req.headers, null, 2));
  console.log('Crowdin Context:', req.body.crowdinContext || 'NO CONTEXT');
  console.log('User Agent:', req.body.userAgent || 'NO USER AGENT');
  console.log('Referrer:', req.body.referrer || 'NO REFERRER');
  console.log('Full Request Body:', JSON.stringify(req.body, null, 2));
  console.log('Request IP:', req.ip || req.connection.remoteAddress);
  
  // Extract string information from various sources
  const extractedStringInfo = extractStringInfo(req.body);
  console.log('Extracted String Info:', JSON.stringify(extractedStringInfo, null, 2));
  console.log('================================\n');
  
  // Here you can add your custom logic based on the Crowdin context
  const { action, crowdinContext } = req.body;
  
  let processingLog = [];
  let actionResults = [];
  
  // Example: Different actions based on context
  if (crowdinContext && Object.keys(crowdinContext).length > 0) {
    processingLog.push('✅ Context data received');
    
    // EXAMPLE ACTIONS YOU CAN IMPLEMENT:
    
    // 1. Project-specific logic
    if (crowdinContext.projectId) {
      processingLog.push(`📁 Project: ${crowdinContext.projectId}`);
      
      // Example: Different behavior for different projects
      if (crowdinContext.projectId === '123456') {
        actionResults.push('🎯 Special handling for project 123456');
      }
    }
    
    // 2. String-specific actions
    if (crowdinContext.stringId) {
      processingLog.push(`📝 String: ${crowdinContext.stringId}`);
      
      // Example: Log string for analysis, send to external API, etc.
      actionResults.push(`📊 String ${crowdinContext.stringId} logged for analysis`);
      
      // Add string key information if available
      if (extractedStringInfo.stringKey) {
        actionResults.push(`🔑 String Key: ${extractedStringInfo.stringKey}`);
      }
      if (extractedStringInfo.identifier) {
        actionResults.push(`🏷️ String Identifier: ${extractedStringInfo.identifier}`);
      }
    }
    
    // 3. File-specific actions
    if (crowdinContext.fileId) {
      processingLog.push(`📄 File: ${crowdinContext.fileId}`);
      
      // Example: Track file progress, send notifications, etc.
      actionResults.push(`📈 File ${crowdinContext.fileId} progress tracked`);
    }
    
    // 4. Language-specific actions
    if (crowdinContext.languageId) {
      processingLog.push(`🌐 Language: ${crowdinContext.languageId}`);
      
      // Example: Language-specific quality checks
      if (crowdinContext.languageId === 'es') {
        actionResults.push('🔍 Spanish quality check initiated');
      }
    }
    
    // 5. User-specific actions
    if (crowdinContext.userId) {
      actionResults.push(`👤 User ${crowdinContext.userId} action recorded`);
    }
    
    // 6. Mode-specific actions
    if (crowdinContext.mode) {
      actionResults.push(`⚙️ ${crowdinContext.mode} mode detected`);
    }
    
    // 7. API-based string fetching
    if (action === 'fetch-via-api' && crowdinContext.projectId) {
      try {
        const stringDetails = await fetchStringFromAPI(token, crowdinContext.projectId, crowdinContext.stringId, crowdinContext.stringKey, crowdinContext.fileId);
        if (stringDetails) {
          actionResults.push(`🔍 API fetch successful: Found ${stringDetails.length} strings`);
          // Update extracted string info with API data
          if (stringDetails.length > 0) {
            const firstString = stringDetails[0];
            extractedStringInfo.stringKey = firstString.identifier || extractedStringInfo.stringKey;
            extractedStringInfo.sourceString = firstString.text || extractedStringInfo.sourceString;
            extractedStringInfo.context = firstString.context || extractedStringInfo.context;
            extractedStringInfo.maxLength = firstString.maxLength || extractedStringInfo.maxLength;
            actionResults.push(`🔑 Found string key: ${firstString.identifier}`);
          }
        }
      } catch (error) {
        actionResults.push(`❌ API fetch failed: ${error.message}`);
      }
    }
    
    // 8. Translations panel specific actions
    if (req.body.moduleType === 'editor-translations-panel') {
      actionResults.push(`📝 Translations panel module detected`);
      
      if (action === 'get-current-string') {
        actionResults.push(`🎯 Attempting to get current string context`);
        // In a real implementation, this would use the translations panel API
        if (extractedStringInfo.stringId || extractedStringInfo.stringKey) {
          actionResults.push(`✅ String context available`);
        } else {
          actionResults.push(`⚠️ No string context detected - may need API authentication`);
        }
      }
      
      if (action === 'analyze-translations-context') {
        actionResults.push(`🔍 Analyzing translations panel context`);
        actionResults.push(`📊 Module type: editor-translations-panel`);
        actionResults.push(`🔗 Better string access than right-panel`);
      }
      
      if (action === 'fetch-string-details') {
        actionResults.push(`📊 Fetching detailed string information`);
        // This would make actual API calls in a real implementation
        actionResults.push(`💡 Use JWT token for authenticated API access`);
      }
      
      if (action === 'test-api-access') {
        actionResults.push(`🌐 Testing API access capabilities`);
        const jwtToken = urlParams.get('jwtToken');
        if (jwtToken) {
          actionResults.push(`🔑 JWT token available for API authentication`);
        } else {
          actionResults.push(`❌ No JWT token found - limited API access`);
        }
      }
    }
    
    // 9. String key extraction specific actions
    if (action === 'extract-string-key') {
      actionResults.push(`🔑 String key extraction request received`);
      actionResults.push(`📊 Module type: ${req.body.moduleType}`);
      
      if (req.body.extractedStringKey) {
        actionResults.push(`✅ String key extracted: ${req.body.extractedStringKey}`);
        actionResults.push(`🔍 Extraction method: ${req.body.extractionMethod}`);
        
        // Store the extracted string key for analysis
        extractedStringInfo.stringKey = req.body.extractedStringKey;
        extractedStringInfo.extractionMethod = req.body.extractionMethod;
      } else {
        actionResults.push(`❌ No string key found in extraction attempt`);
      }
      
      // Log all available context
      if (req.body.allContext) {
        actionResults.push(`📋 Available context keys: ${Object.keys(req.body.allContext).join(', ')}`);
        
        // Check for potential string identifiers in context
        const potentialKeys = ['stringKey', 'identifier', 'key', 'stringId'];
        potentialKeys.forEach(keyName => {
          if (req.body.allContext[keyName]) {
            actionResults.push(`🔍 Found ${keyName}: ${req.body.allContext[keyName]}`);
          }
        });
      }
      
      // Provide recommendations based on module type
      if (req.body.moduleType === 'editor-right-panel') {
        actionResults.push(`💡 Right panel has better string context access`);
        actionResults.push(`🎯 Try selecting different strings to test extraction`);
      }
    }
    
    // EXAMPLE INTEGRATIONS YOU COULD ADD:
    // - Send data to external APIs (Slack, Discord, webhooks)
    // - Store in database for analytics
    // - Trigger automated workflows
    // - Generate reports
    // - Send notifications to project managers
    // - Quality assurance checks
    // - Custom validation rules
    
  } else {
    processingLog.push('❌ No context data received');
  }
  
  console.log('Processing Log:', processingLog.join(' | '));
  console.log('Action Results:', actionResults.join(' | '));
  
  res.json({
    success: true,
    message: `${action || 'unknown'} action completed successfully!`,
    timestamp: timestamp,
    processedContext: crowdinContext || null,
    processingLog: processingLog,
    actionResults: actionResults,
    extractedStringInfo: extractedStringInfo,
    debugInfo: {
      hasContext: !!(crowdinContext && Object.keys(crowdinContext).length > 0),
      contextKeys: crowdinContext ? Object.keys(crowdinContext) : [],
      requestSize: JSON.stringify(req.body).length,
      hasStringKey: !!(extractedStringInfo.stringKey || extractedStringInfo.identifier),
      hasStringId: !!extractedStringInfo.stringId
    },
    // Example: What you could return to the frontend
    suggestions: [
      '💡 You could integrate with Slack to notify team members',
      '📊 You could store this data for project analytics',
      '🔄 You could trigger automated workflows',
      '✅ You could implement custom quality checks',
      '📧 You could send email notifications to project managers'
    ],
    // Important information about string keys
    stringKeyInfo: {
      moduleType: req.body.moduleType || 'editor-right-panel',
      issue: req.body.moduleType === 'editor-translations-panel' ? 
        'Translations panel should have better string context access' :
        'String keys are typically not passed in URL parameters for editor-right-panel apps',
      solutions: [
        '1. Use Crowdin API with JWT token to fetch string details',
        '2. Implement OAuth authentication to access project data',
        '3. Use webhooks to capture string events',
        '4. ✅ Now using editor-translations-panel for better context',
        '5. Use postMessage API to communicate with parent Crowdin window'
      ],
      currentLimitations: req.body.moduleType === 'editor-translations-panel' ?
        'Translations panel may have better string access but still requires API calls' :
        'Editor right panel apps have limited access to current string context',
      recommendation: req.body.moduleType === 'editor-translations-panel' ?
        'Use JWT token for authenticated API calls to get full string details' :
        'For string-specific operations, consider using Crowdin API or webhooks'
    }
  });
});

// Enhanced logging for string key extraction
app.post('/extract-context', (req, res) => {
    const timestamp = new Date().toISOString();
    const { action, context } = req.body;
    
    console.log('\n=== STRING KEY EXTRACTION ATTEMPT ===');
    console.log(`Timestamp: ${timestamp}`);
    console.log(`Action: ${action}`);
    console.log(`URL: ${context.url}`);
    console.log(`Referrer: ${context.referrer}`);
    console.log(`Frame Depth: ${context.frameDepth}`);
    console.log(`Parent Origin: ${context.parentOrigin}`);
    console.log(`URL Parameters:`, JSON.stringify(context.urlParams, null, 2));
    console.log(`Hash Parameters: ${context.hashParams}`);
    console.log(`Available APIs:`, JSON.stringify(context.availableAPIs, null, 2));
    console.log(`Crowdin Context:`, JSON.stringify(context.crowdinContext, null, 2));
    
    if (context.postMessages && context.postMessages.length > 0) {
        console.log(`PostMessage Data:`, JSON.stringify(context.postMessages, null, 2));
    }
    
    console.log('=====================================\n');
    
    res.json({ 
        success: true, 
        message: 'Context logged successfully',
        timestamp: timestamp,
        limitations: {
            moduleType: 'editor-right-panel',
            stringContextAccess: 'limited',
            reason: 'Crowdin security architecture prevents direct string context access',
            alternatives: [
                'Use Crowdin API with authentication',
                'Copy String URL from editor menu',
                'Browser developer tools inspection',
                'Export project data',
                'Webhook integration',
                'Custom server-side integration'
            ]
        }
    });
});

// Root route - redirect to audio previewer
app.get('/', (req, res) => {
  res.redirect('/audio-previewer');
});

// Audio metadata endpoint (to bypass CORS)
app.post('/api/get-audio-metadata', async (req, res) => {
  const { audioUrl } = req.body;
  
  if (!audioUrl) {
    return res.status(400).json({ error: 'audioUrl is required' });
  }
  
  console.log('📊 Server: Getting metadata for audio URL:', audioUrl);
  
  try {
    const response = await fetch(audioUrl, {
      method: 'HEAD',
      headers: {
        'User-Agent': 'Crowdin-Audio-Previewer/1.0'
      }
    });
    
    if (response.ok) {
      const metadata = {
        lastModified: response.headers.get('Last-Modified'),
        date: response.headers.get('Date'),
        contentLength: response.headers.get('Content-Length'),
        contentType: response.headers.get('Content-Type'),
        etag: response.headers.get('ETag'),
        cacheControl: response.headers.get('Cache-Control'),
        server: response.headers.get('Server'),
        expires: response.headers.get('Expires'),
        age: response.headers.get('Age'),
        url: audioUrl,
        status: response.status,
        statusText: response.statusText,
        method: 'server-proxy'
      };
      
      // Parse date information with priority for actual file dates
      let dateToUse = null;
      let dateSource = null;
      
      // Priority 1: Last-Modified header (actual file modification date)
      if (metadata.lastModified) {
        dateToUse = metadata.lastModified;
        dateSource = 'Last-Modified header';
      } 
      // Priority 2: ETag timestamps (sometimes contains file date)
      else if (metadata.etag) {
        console.log('📊 Server: Analyzing ETag for timestamp:', metadata.etag);
        const etagMatch = metadata.etag.match(/(\d{10,13})/);
        if (etagMatch) {
          const timestamp = parseInt(etagMatch[1]);
          console.log('📊 Server: Found potential timestamp in ETag:', timestamp);
          
          // Validate timestamp is reasonable (between 2000 and 2030)
          const minTimestamp = new Date('2000-01-01').getTime() / 1000; // Year 2000 in seconds
          const maxTimestamp = new Date('2030-01-01').getTime() / 1000; // Year 2030 in seconds
          
          let parsedDate = null;
          
          // Try as seconds first
          if (timestamp >= minTimestamp && timestamp <= maxTimestamp) {
            parsedDate = new Date(timestamp * 1000);
            console.log('📊 Server: Parsed as seconds:', parsedDate);
          }
          // Try as milliseconds
          else if (timestamp >= minTimestamp * 1000 && timestamp <= maxTimestamp * 1000) {
            parsedDate = new Date(timestamp);
            console.log('📊 Server: Parsed as milliseconds:', parsedDate);
          }
          
          // Validate the parsed date is reasonable
          if (parsedDate && !isNaN(parsedDate.getTime()) && 
              parsedDate.getFullYear() >= 2000 && parsedDate.getFullYear() <= 2030) {
            dateToUse = parsedDate.toUTCString();
            dateSource = 'ETag timestamp';
            console.log('📊 Server: Valid ETag timestamp found:', dateToUse);
          } else {
            console.log('📊 Server: ETag timestamp invalid or unreasonable:', parsedDate);
          }
        } else {
          console.log('📊 Server: No timestamp pattern found in ETag');
        }
      }
      // Priority 3: Try to extract date from URL path
      else {
        const urlDateMatch = audioUrl.match(/(\d{4})[\/\-_](\d{1,2})[\/\-_](\d{1,2})/);
        if (urlDateMatch) {
          const [, year, month, day] = urlDateMatch;
          const urlDate = new Date(year, month - 1, day);
          if (!isNaN(urlDate.getTime()) && urlDate.getFullYear() > 2000) {
            dateToUse = urlDate.toUTCString();
            dateSource = 'URL path date pattern';
          }
        }
      }
      
      // Last resort: Date header (just server response time - not file date)
      if (!dateToUse && metadata.date) {
        dateToUse = metadata.date;
        dateSource = 'Date header (server response time)';
      }
      
      // Parse the date
      if (dateToUse) {
        const parsedDate = new Date(dateToUse);
        if (!isNaN(parsedDate.getTime())) {
          metadata.lastModifiedParsed = parsedDate;
          metadata.lastModifiedFormatted = parsedDate.toLocaleString();
          metadata.daysAgo = Math.floor((Date.now() - parsedDate.getTime()) / (1000 * 60 * 60 * 24));
          metadata.dateSource = dateSource;
          
          // Warn if we're using server response time instead of file date
          if (dateSource === 'Date header (server response time)') {
            console.log('⚠️ Server: Using server response time, not actual file modification date');
            metadata.isServerResponseTime = true;
          }
        }
      } else {
        metadata.noDateInfo = true;
        console.log('📊 Server: No date information available for:', audioUrl);
      }
      
      // Format file size
      if (metadata.contentLength) {
        const bytes = parseInt(metadata.contentLength);
        if (bytes < 1024) {
          metadata.fileSizeFormatted = bytes + ' bytes';
        } else if (bytes < 1024 * 1024) {
          metadata.fileSizeFormatted = (bytes / 1024).toFixed(1) + ' KB';
        } else {
          metadata.fileSizeFormatted = (bytes / (1024 * 1024)).toFixed(1) + ' MB';
        }
      }
      
      console.log('📊 Server: Successfully got metadata:', metadata);
      
      res.json({
        success: true,
        metadata: metadata
      });
    } else {
      console.log('📊 Server: Failed to get metadata for URL:', audioUrl);
      console.log('📊 Server: Response status:', response.status, response.statusText);
      res.status(response.status).json({
        error: 'Failed to get metadata',
        status: response.status,
        statusText: response.statusText,
        url: audioUrl
      });
    }
  } catch (error) {
    console.error('📊 Server: Error getting metadata for URL:', audioUrl);
    console.error('📊 Server: Error details:', error);
    res.status(500).json({
      error: 'Server error getting metadata',
      message: error.message,
      url: audioUrl
    });
  }
});

// Enhanced health check endpoint
app.get('/health', (req, res) => {
  const uptime = Date.now() - deploymentHealth.startTime.getTime();
  const healthStatus = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: Math.floor(uptime / 1000),
    deployment: {
      startTime: deploymentHealth.startTime.toISOString(),
      requestCount: deploymentHealth.requestCount,
      errorCount: deploymentHealth.errors,
      lastActivity: deploymentHealth.lastHealthCheck.toISOString()
    },
    environment: {
      nodeVersion: process.version,
      platform: process.platform,
      vercel: !!process.env.VERCEL
    }
  };
  
  res.json(healthStatus);
});

// Audio Generation API Endpoints

// PlayHT Proxy for TTS generation
app.post('/api/playht-proxy', async (req, res) => {
  try {
    const { text, voice, voice_engine, output_format, sample_rate } = req.body;
    const apiKey = req.headers.authorization;
    const userId = req.headers['x-user-id'];

    if (!apiKey || !userId) {
      return res.status(400).json({ error: 'Missing PlayHT credentials' });
    }

    const response = await fetch('https://api.play.ht/api/v2/tts/stream', {
      method: 'POST',
      headers: {
        'Authorization': apiKey,
        'X-USER-ID': userId,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        text,
        voice,
        voice_engine: voice_engine || 'Play3.0-mini',
        output_format: output_format || 'mp3',
        sample_rate: sample_rate || 22050
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      return res.status(response.status).json({ 
        error: 'PlayHT API error', 
        details: errorText 
      });
    }

    // Stream the audio response back to the client
    response.body.pipe(res);
    
  } catch (error) {
    console.error('PlayHT proxy error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// PlayHT Voices Proxy
app.post('/api/playht-voices-proxy', async (req, res) => {
  try {
    const { languageCode } = req.body;
    const apiKey = req.headers.authorization;
    const userId = req.headers['x-user-id'];

    console.log('🎤 PlayHT Voices Proxy - Request received:', {
      languageCode,
      hasApiKey: !!apiKey,
      hasUserId: !!userId,
      apiKeyStart: apiKey ? apiKey.substring(0, 10) + '...' : 'missing',
      userIdStart: userId ? userId.substring(0, 10) + '...' : 'missing'
    });

    if (!apiKey || !userId) {
      console.error('❌ PlayHT Voices Proxy - Missing credentials');
      return res.status(400).json({ error: 'Missing PlayHT credentials' });
    }

    console.log('📡 PlayHT Voices Proxy - Making API call to:', 'https://api.play.ht/api/v2/voices');
    
    const response = await fetch('https://api.play.ht/api/v2/voices', {
      headers: {
        'Authorization': apiKey,
        'X-USER-ID': userId
      }
    });

    console.log('📡 PlayHT Voices Proxy - API response status:', response.status);

    if (!response.ok) {
      const errorText = await response.text();
      console.error('❌ PlayHT Voices Proxy - API error:', {
        status: response.status,
        statusText: response.statusText,
        errorText
      });
      return res.status(response.status).json({ 
        error: 'PlayHT API error', 
        details: errorText 
      });
    }

    const data = await response.json();
    console.log('📦 PlayHT Voices Proxy - Raw API response:', {
      dataStructure: Object.keys(data),
      voicesCount: data.voices ? data.voices.length : 0,
      rawData: data
    });
    
    // Log first few voices if any exist
    if (data.voices && data.voices.length > 0) {
      console.log('🎵 PlayHT Voices Proxy - Sample voices:', data.voices.slice(0, 3));
    } else {
      console.warn('⚠️ PlayHT Voices Proxy - No voices in response!');
      console.warn('🔍 This could mean:');
      console.warn('  1. Account has no configured voices');
      console.warn('  2. Different API endpoint needed');
      console.warn('  3. Credentials access different account than expected');
    }
    
    // Filter voices by language if specified
    let voices = data.voices || [];
    const originalCount = voices.length;
    
    if (languageCode) {
      voices = voices.filter(voice => {
        const voiceLang = voice.language || voice.language_code || '';
        return voiceLang.toLowerCase().includes(languageCode.toLowerCase());
      });
      console.log(`🔍 PlayHT Voices Proxy - Language filtering: ${originalCount} → ${voices.length} (for "${languageCode}")`);
    }

    console.log(`✅ PlayHT Voices Proxy - Returning ${voices.length} voices`);
    res.json({ voices });
    
  } catch (error) {
    console.error('PlayHT voices proxy error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// ElevenLabs Voices Proxy (to fetch available voices)
app.get('/api/elevenlabs-voices-proxy', async (req, res) => {
  try {
    const apiKey = req.headers['xi-api-key'];

    if (!apiKey) {
      return res.status(400).json({ error: 'Missing ElevenLabs API key' });
    }

    const response = await fetch('https://api.elevenlabs.io/v1/voices?show_legacy=false', {
      method: 'GET',
      headers: {
        'xi-api-key': apiKey,
        'Content-Type': 'application/json'
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      return res.status(response.status).json({ 
        error: 'ElevenLabs Voices API error', 
        details: errorText 
      });
    }

    const voicesData = await response.json();
    res.json(voicesData);
    
  } catch (error) {
    console.error('ElevenLabs voices proxy error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// ElevenLabs Proxy (if needed for CORS issues)
app.post('/api/elevenlabs-proxy/:voiceId', async (req, res) => {
  try {
    const { voiceId } = req.params;
    const { text, model_id, voice_settings } = req.body;
    const apiKey = req.headers['xi-api-key'];

    if (!apiKey) {
      return res.status(400).json({ error: 'Missing ElevenLabs API key' });
    }

    const response = await fetch(`https://api.elevenlabs.io/v1/text-to-speech/${voiceId}`, {
      method: 'POST',
      headers: {
        'xi-api-key': apiKey,
        'Content-Type': 'application/json',
        'Accept': 'audio/mpeg'
      },
      body: JSON.stringify({
        text,
        model_id: model_id || 'eleven_multilingual_v2',
        voice_settings: voice_settings || {
          stability: 0.65,
          similarity_boost: 0.5,
          style: 0.0,
          use_speaker_boost: true
        }
      })
    });

    if (!response.ok) {
      const errorText = await response.text();
      return res.status(response.status).json({ 
        error: 'ElevenLabs API error', 
        details: errorText 
      });
    }

    // Stream the audio response back to the client
    response.body.pipe(res);
    
  } catch (error) {
    console.error('ElevenLabs proxy error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

// Error handling middleware
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  deploymentHealth.errors++;
  res.status(500).json({ 
    error: 'Internal server error',
    timestamp: new Date().toISOString()
  });
});

// 404 handler with helpful information
app.use((req, res) => {
  console.log(`404 - Path not found: ${req.path}`);
  deploymentHealth.errors++;
  res.status(404).json({ 
    error: 'Not found',
    path: req.path,
    timestamp: new Date().toISOString(),
    availableEndpoints: [
      '/health',
      '/manifest.json',
      '/editor-button',
      '/audio-previewer',
      '/translations-panel',
      '/api/get-audio-metadata',
      '/api/button-action',
      '/api/playht-proxy',
      '/api/playht-voices-proxy',
      '/api/elevenlabs-proxy/:voiceId'
    ]
  });
});

// Start server
app.listen(PORT, () => {
  console.log(`Crowdin Editor Button App running on port ${PORT}`);
  console.log(`Manifest available at: http://localhost:${PORT}/manifest.json`);
  console.log(`Editor button at: http://localhost:${PORT}/editor-button`);
  console.log(`Health check at: http://localhost:${PORT}/health`);
  
  if (process.env.VERCEL) {
    console.log('🚀 Running on Vercel');
    console.log('🌐 Production URL: https://editor-button-app.vercel.app');
  }
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  process.exit(0);
});

module.exports = app; 