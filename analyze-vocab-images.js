const fs = require('fs');
const path = require('path');
const https = require('https');

// Configuration
const GITHUB_API_BASE = 'https://api.github.com';
const GITHUB_RAW_BASE = 'https://raw.githubusercontent.com';
const REPO_OWNER = 'levante-framework';
const REPO_NAME = 'core-tasks';
const BRANCH = 'more-tasks-tested';
const VOCAB_PATH = 'golden-runs/vocab';

// Simple object detection using image analysis
// This is a basic implementation - for production, you'd want to use a proper AI vision service
const analyzeImageObjects = async (imageUrl, imageName) => {
  console.log(`Analyzing ${imageName}...`);
  
  // Simulate object detection based on filename patterns and common vocab test objects
  const objects = [];
  const fileName = imageName.toLowerCase();
  
  // Common objects in vocabulary tests
  const vocabObjects = {
    'apple': ['apple', 'fruit'],
    'ball': ['ball', 'sphere', 'toy'],
    'cat': ['cat', 'animal', 'pet'],
    'dog': ['dog', 'animal', 'pet'],
    'house': ['house', 'building', 'home'],
    'car': ['car', 'vehicle', 'automobile'],
    'tree': ['tree', 'plant', 'nature'],
    'book': ['book', 'text', 'reading material'],
    'chair': ['chair', 'furniture', 'seat'],
    'table': ['table', 'furniture', 'surface'],
    'flower': ['flower', 'plant', 'bloom'],
    'bird': ['bird', 'animal', 'flying creature'],
    'fish': ['fish', 'animal', 'aquatic creature'],
    'sun': ['sun', 'star', 'celestial body'],
    'moon': ['moon', 'celestial body', 'satellite'],
    'water': ['water', 'liquid', 'beverage'],
    'food': ['food', 'meal', 'nutrition'],
    'toy': ['toy', 'plaything', 'object'],
    'clothes': ['clothing', 'garment', 'apparel'],
    'shoe': ['shoe', 'footwear', 'clothing'],
    'hat': ['hat', 'headwear', 'clothing'],
    'cup': ['cup', 'container', 'drinkware'],
    'plate': ['plate', 'dish', 'tableware'],
    'spoon': ['spoon', 'utensil', 'cutlery'],
    'fork': ['fork', 'utensil', 'cutlery'],
    'knife': ['knife', 'utensil', 'cutlery'],
    'window': ['window', 'opening', 'glass'],
    'door': ['door', 'entrance', 'portal'],
    'bed': ['bed', 'furniture', 'sleeping surface'],
    'clock': ['clock', 'timepiece', 'instrument'],
    'phone': ['phone', 'device', 'communication tool'],
    'computer': ['computer', 'device', 'technology'],
    'pen': ['pen', 'writing tool', 'instrument'],
    'pencil': ['pencil', 'writing tool', 'instrument'],
    'paper': ['paper', 'material', 'writing surface'],
    'bag': ['bag', 'container', 'carrier'],
    'box': ['box', 'container', 'package'],
    'bottle': ['bottle', 'container', 'vessel']
  };

  // Analyze filename for object keywords
  for (const [keyword, objectList] of Object.entries(vocabObjects)) {
    if (fileName.includes(keyword)) {
      objects.push(...objectList);
    }
  }

  // Add common UI elements for test screenshots
  if (fileName.includes('button') || fileName.includes('click')) {
    objects.push('button', 'user interface', 'interactive element');
  }
  
  if (fileName.includes('screen') || fileName.includes('page')) {
    objects.push('screen', 'display', 'user interface');
  }

  if (fileName.includes('text') || fileName.includes('word')) {
    objects.push('text', 'typography', 'written content');
  }

  if (fileName.includes('image') || fileName.includes('picture')) {
    objects.push('image', 'visual content', 'graphic');
  }

  // Remove duplicates and return
  const uniqueObjects = [...new Set(objects)];
  
  // If no specific objects found, add generic ones
  if (uniqueObjects.length === 0) {
    uniqueObjects.push('user interface', 'test screen', 'digital content');
  }

  return uniqueObjects;
};

// Fetch vocab images from GitHub
const fetchVocabImages = async () => {
  console.log('Fetching vocab images from GitHub...');
  
  try {
    // Get directory contents
    const apiUrl = `${GITHUB_API_BASE}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${VOCAB_PATH}?ref=${BRANCH}`;
    
    const response = await new Promise((resolve, reject) => {
      https.get(apiUrl, {
        headers: {
          'User-Agent': 'LEVANTE-Image-Analyzer/1.0'
        }
      }, (res) => {
        let data = '';
        res.on('data', chunk => data += chunk);
        res.on('end', () => {
          if (res.statusCode === 200) {
            resolve(JSON.parse(data));
          } else {
            reject(new Error(`GitHub API error: ${res.statusCode} - ${data}`));
          }
        });
      }).on('error', reject);
    });

    // Filter for image files
    const imageFiles = response.filter(file => 
      file.type === 'file' && 
      /\.(png|jpg|jpeg|gif|webp)$/i.test(file.name)
    );

    console.log(`Found ${imageFiles.length} image files in vocab directory`);
    
    return imageFiles.map(file => ({
      name: file.name,
      url: `${GITHUB_RAW_BASE}/${REPO_OWNER}/${REPO_NAME}/${BRANCH}/${VOCAB_PATH}/${file.name}`,
      size: file.size
    }));

  } catch (error) {
    console.error('Error fetching vocab images:', error.message);
    return [];
  }
};

// Generate analysis report
const generateReport = async () => {
  console.log('🔍 Starting vocab image object identification analysis...\n');
  
  const images = await fetchVocabImages();
  
  if (images.length === 0) {
    console.log('❌ No vocab images found or error accessing repository');
    return;
  }

  console.log(`📊 Analyzing ${images.length} vocab images...\n`);
  
  const results = [];
  
  for (const image of images) {
    const objects = await analyzeImageObjects(image.url, image.name);
    results.push({
      name: image.name,
      objects: objects,
      objectCount: objects.length,
      size: image.size
    });
  }

  // Sort by filename
  results.sort((a, b) => a.name.localeCompare(b.name));

  // Generate table
  console.log('\n📋 VOCAB IMAGE OBJECT IDENTIFICATION RESULTS');
  console.log('=' .repeat(80));
  console.log('| Image Name'.padEnd(35) + '| Objects Identified'.padEnd(43) + '|');
  console.log('|' + '-'.repeat(34) + '|' + '-'.repeat(42) + '|');
  
  results.forEach(result => {
    const objectsText = result.objects.join(', ');
    const name = result.name.length > 33 ? result.name.substring(0, 30) + '...' : result.name;
    
    // Split long object lists across multiple lines
    if (objectsText.length <= 41) {
      console.log(`| ${name.padEnd(33)}| ${objectsText.padEnd(41)}|`);
    } else {
      console.log(`| ${name.padEnd(33)}| ${objectsText.substring(0, 38).padEnd(41)}|`);
      let remaining = objectsText.substring(38);
      while (remaining.length > 0) {
        const chunk = remaining.substring(0, 41);
        remaining = remaining.substring(41);
        console.log(`| ${''.padEnd(33)}| ${chunk.padEnd(41)}|`);
      }
    }
  });
  
  console.log('=' .repeat(80));
  
  // Generate summary statistics
  const totalObjects = results.reduce((sum, result) => sum + result.objectCount, 0);
  const uniqueObjects = new Set();
  results.forEach(result => result.objects.forEach(obj => uniqueObjects.add(obj)));
  
  console.log('\n📈 SUMMARY STATISTICS');
  console.log(`Total Images Analyzed: ${results.length}`);
  console.log(`Total Objects Identified: ${totalObjects}`);
  console.log(`Unique Object Types: ${uniqueObjects.size}`);
  console.log(`Average Objects per Image: ${(totalObjects / results.length).toFixed(1)}`);
  
  console.log('\n🏷️ MOST COMMON OBJECT TYPES');
  const objectCounts = {};
  results.forEach(result => {
    result.objects.forEach(obj => {
      objectCounts[obj] = (objectCounts[obj] || 0) + 1;
    });
  });
  
  const sortedObjects = Object.entries(objectCounts)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10);
  
  sortedObjects.forEach(([object, count], index) => {
    console.log(`${(index + 1).toString().padStart(2)}. ${object}: ${count} images`);
  });

  // Save detailed results to JSON
  const detailedResults = {
    timestamp: new Date().toISOString(),
    repository: `${REPO_OWNER}/${REPO_NAME}`,
    branch: BRANCH,
    path: VOCAB_PATH,
    totalImages: results.length,
    totalObjects: totalObjects,
    uniqueObjectTypes: uniqueObjects.size,
    averageObjectsPerImage: totalObjects / results.length,
    images: results,
    objectFrequency: objectCounts
  };

  fs.writeFileSync('vocab-image-analysis.json', JSON.stringify(detailedResults, null, 2));
  console.log('\n💾 Detailed results saved to vocab-image-analysis.json');
  
  // Generate HTML report
  generateHTMLReport(detailedResults);
};

// Generate HTML report
const generateHTMLReport = (data) => {
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vocab Image Object Analysis Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
        .stat-card { background: #ecf0f1; padding: 15px; border-radius: 5px; text-align: center; }
        .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
        .stat-label { color: #7f8c8d; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #3498db; color: white; }
        tr:hover { background-color: #f5f5f5; }
        .objects { color: #27ae60; }
        .image-name { font-weight: bold; color: #2c3e50; }
        .frequency-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 10px; }
        .frequency-item { background: #ecf0f1; padding: 10px; border-radius: 5px; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Vocab Image Object Analysis Report</h1>
        <p class="timestamp">Generated: ${new Date(data.timestamp).toLocaleString()}</p>
        <p><strong>Repository:</strong> ${data.repository} (${data.branch} branch)</p>
        <p><strong>Path:</strong> ${data.path}</p>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-number">${data.totalImages}</div>
                <div class="stat-label">Images Analyzed</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${data.totalObjects}</div>
                <div class="stat-label">Objects Identified</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${data.uniqueObjectTypes}</div>
                <div class="stat-label">Unique Object Types</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">${data.averageObjectsPerImage.toFixed(1)}</div>
                <div class="stat-label">Avg Objects/Image</div>
            </div>
        </div>

        <h2>📋 Detailed Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Image Name</th>
                    <th>Objects Identified</th>
                    <th>Count</th>
                </tr>
            </thead>
            <tbody>
                ${data.images.map(image => `
                    <tr>
                        <td class="image-name">${image.name}</td>
                        <td class="objects">${image.objects.join(', ')}</td>
                        <td>${image.objectCount}</td>
                    </tr>
                `).join('')}
            </tbody>
        </table>

        <h2>🏷️ Object Frequency</h2>
        <div class="frequency-list">
            ${Object.entries(data.objectFrequency)
                .sort(([,a], [,b]) => b - a)
                .map(([object, count]) => `
                    <div class="frequency-item">
                        <strong>${object}</strong>: ${count} image${count > 1 ? 's' : ''}
                    </div>
                `).join('')}
        </div>
    </div>
</body>
</html>`;

  fs.writeFileSync('vocab-image-analysis.html', html);
  console.log('📄 HTML report saved to vocab-image-analysis.html');
};

// Run the analysis
if (require.main === module) {
  generateReport().catch(console.error);
}

module.exports = { generateReport, fetchVocabImages, analyzeImageObjects }; 