const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

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
    pluralForm: null
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
  }
  
  // Extract from referrer URL if available
  if (requestBody.referrer) {
    try {
      const referrerUrl = new URL(requestBody.referrer);
      const referrerParams = new URLSearchParams(referrerUrl.search);
      
      stringInfo.stringKey = stringInfo.stringKey || referrerParams.get('stringKey') || referrerParams.get('key');
      stringInfo.stringId = stringInfo.stringId || referrerParams.get('stringId') || referrerParams.get('id');
    } catch (e) {
      // Invalid referrer URL, ignore
    }
  }
  
  return stringInfo;
}

// Function to fetch string details from Crowdin API
async function fetchStringFromAPI(crowdinContext, extractedStringInfo) {
  // This is a simplified example - in a real implementation, you would:
  // 1. Use the JWT token to authenticate with Crowdin API
  // 2. Make API calls to get string details
  // 3. Handle different project types (file-based vs string-based)
  
  console.log('🌐 Attempting to fetch string details via API...');
  console.log('Context:', crowdinContext);
  console.log('Extracted info:', extractedStringInfo);
  
  // For now, return mock data to demonstrate the concept
  // In a real implementation, you would make actual API calls here
  const mockStringData = [
    {
      id: extractedStringInfo.stringId || 123,
      identifier: 'welcome.message',
      text: 'Welcome to our application',
      context: 'Homepage greeting message',
      maxLength: 50,
      fileId: crowdinContext.fileId || 456,
      projectId: crowdinContext.projectId || 789
    }
  ];
  
  // Simulate API delay
  await new Promise(resolve => setTimeout(resolve, 500));
  
  return mockStringData;
}

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: true }));

// Serve static files
app.use(express.static(path.join(__dirname, 'public')));

// Serve the manifest file
app.get('/manifest.json', (req, res) => {
  res.sendFile(path.join(__dirname, 'manifest.json'));
});

// Main editor button route
app.get('/editor-button', (req, res) => {
  res.sendFile(path.join(__dirname, 'public', 'editor-button.html'));
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
        const stringDetails = await fetchStringFromAPI(crowdinContext, extractedStringInfo);
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
      issue: 'String keys are typically not passed in URL parameters for editor-right-panel apps',
      solutions: [
        '1. Use Crowdin API with JWT token to fetch string details',
        '2. Implement OAuth authentication to access project data',
        '3. Use webhooks to capture string events',
        '4. Consider using different module types (e.g., editor-translations-panel)',
        '5. Use postMessage API to communicate with parent Crowdin window'
      ],
      currentLimitations: 'Editor right panel apps have limited access to current string context',
      recommendation: 'For string-specific operations, consider using Crowdin API or webhooks'
    }
  });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Start server
app.listen(PORT, () => {
  console.log(`Crowdin Editor Button App running on port ${PORT}`);
  console.log(`Manifest available at: http://localhost:${PORT}/manifest.json`);
  console.log(`Editor button at: http://localhost:${PORT}/editor-button`);
});

module.exports = app; 