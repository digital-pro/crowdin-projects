const fs = require('fs');
const https = require('https');

// Configuration
const GITHUB_API_BASE = 'https://api.github.com';
const GITHUB_RAW_BASE = 'https://raw.githubusercontent.com';
const REPO_OWNER = 'levante-framework';
const REPO_NAME = 'core-tasks';
const BRANCH = 'more-tasks-tested';
const VOCAB_PATH = 'golden-runs/vocab';

// ImageNet-style classification categories (top 1000 classes)
const IMAGENET_CLASSES = {
  // Animals
  'tabby_cat': ['cat', 'kitten', 'feline', 'tabby'],
  'golden_retriever': ['dog', 'puppy', 'retriever', 'canine'],
  'robin': ['bird', 'robin', 'songbird'],
  'goldfish': ['fish', 'goldfish', 'aquarium_fish'],
  'horse': ['horse', 'stallion', 'mare'],
  'cow': ['cow', 'cattle', 'bovine'],
  'pig': ['pig', 'swine', 'hog'],
  'sheep': ['sheep', 'lamb', 'wool'],
  'chicken': ['chicken', 'hen', 'rooster'],
  'duck': ['duck', 'waterfowl', 'mallard'],
  'rabbit': ['rabbit', 'bunny', 'hare'],
  'mouse': ['mouse', 'rodent'],
  'elephant': ['elephant', 'pachyderm'],
  'lion': ['lion', 'big_cat'],
  'tiger': ['tiger', 'big_cat'],
  'bear': ['bear', 'ursine'],
  'monkey': ['monkey', 'primate'],
  'zebra': ['zebra', 'striped_horse'],
  'giraffe': ['giraffe', 'tall_mammal'],
  'frog': ['frog', 'amphibian'],
  'snake': ['snake', 'serpent', 'reptile'],
  'turtle': ['turtle', 'tortoise', 'reptile'],
  'butterfly': ['butterfly', 'insect', 'lepidoptera'],
  'bee': ['bee', 'insect', 'honeybee'],
  'spider': ['spider', 'arachnid'],
  'ant': ['ant', 'insect'],

  // Food
  'granny_smith': ['apple', 'green_apple', 'fruit'],
  'banana': ['banana', 'fruit', 'yellow_fruit'],
  'orange': ['orange', 'citrus', 'fruit'],
  'strawberry': ['strawberry', 'berry', 'fruit'],
  'lemon': ['lemon', 'citrus', 'yellow_fruit'],
  'pineapple': ['pineapple', 'tropical_fruit'],
  'corn': ['corn', 'maize', 'vegetable'],
  'carrot': ['carrot', 'vegetable', 'root_vegetable'],
  'broccoli': ['broccoli', 'vegetable', 'green_vegetable'],
  'mushroom': ['mushroom', 'fungi'],
  'pizza': ['pizza', 'food', 'italian_food'],
  'hamburger': ['hamburger', 'burger', 'fast_food'],
  'hot_dog': ['hot_dog', 'sausage', 'fast_food'],
  'ice_cream': ['ice_cream', 'dessert', 'frozen_dessert'],
  'chocolate_sauce': ['chocolate', 'sauce', 'dessert'],
  'pretzel': ['pretzel', 'snack', 'baked_good'],
  'bagel': ['bagel', 'bread', 'breakfast'],
  'croissant': ['croissant', 'pastry', 'french_bread'],
  'french_loaf': ['bread', 'loaf', 'baguette'],
  'meat_loaf': ['meatloaf', 'meat', 'dinner'],

  // Vehicles
  'sports_car': ['car', 'automobile', 'vehicle'],
  'convertible': ['convertible', 'car', 'vehicle'],
  'taxi': ['taxi', 'cab', 'vehicle'],
  'school_bus': ['bus', 'school_bus', 'vehicle'],
  'fire_engine': ['fire_truck', 'emergency_vehicle'],
  'garbage_truck': ['garbage_truck', 'truck', 'vehicle'],
  'pickup': ['pickup_truck', 'truck', 'vehicle'],
  'tow_truck': ['tow_truck', 'truck', 'vehicle'],
  'recreational_vehicle': ['rv', 'motor_home', 'vehicle'],
  'limousine': ['limousine', 'limo', 'luxury_car'],
  'jeep': ['jeep', 'suv', 'off_road_vehicle'],
  'minivan': ['minivan', 'van', 'family_vehicle'],
  'ambulance': ['ambulance', 'emergency_vehicle'],
  'police_van': ['police_car', 'police_vehicle'],
  'motorcycle': ['motorcycle', 'bike', 'motorbike'],
  'bicycle': ['bicycle', 'bike', 'two_wheeler'],
  'tricycle': ['tricycle', 'three_wheeler'],
  'unicycle': ['unicycle', 'one_wheeler'],
  'go_kart': ['go_kart', 'racing_vehicle'],
  'snowmobile': ['snowmobile', 'winter_vehicle'],

  // Household items
  'dining_table': ['table', 'furniture', 'dining_table'],
  'chair': ['chair', 'seat', 'furniture'],
  'couch': ['sofa', 'couch', 'furniture'],
  'bed': ['bed', 'furniture', 'sleeping'],
  'wardrobe': ['wardrobe', 'closet', 'furniture'],
  'bookshelf': ['bookshelf', 'shelf', 'furniture'],
  'desk': ['desk', 'table', 'workspace'],
  'coffee_table': ['coffee_table', 'table', 'furniture'],
  'rocking_chair': ['rocking_chair', 'chair', 'furniture'],
  'folding_chair': ['folding_chair', 'chair', 'portable'],
  'throne': ['throne', 'royal_chair', 'ornate_seat'],
  'barber_chair': ['barber_chair', 'chair', 'salon'],
  'electric_chair': ['electric_chair', 'execution_device'],
  'toilet_seat': ['toilet_seat', 'bathroom', 'seat'],
  'high_chair': ['high_chair', 'baby_chair', 'furniture'],

  // Tools and objects
  'hammer': ['hammer', 'tool', 'construction'],
  'screwdriver': ['screwdriver', 'tool', 'repair'],
  'wrench': ['wrench', 'tool', 'mechanical'],
  'saw': ['saw', 'tool', 'cutting'],
  'scissors': ['scissors', 'cutting_tool', 'office'],
  'knife': ['knife', 'cutting_tool', 'kitchen'],
  'spoon': ['spoon', 'utensil', 'cutlery'],
  'fork': ['fork', 'utensil', 'cutlery'],
  'plate': ['plate', 'dish', 'tableware'],
  'bowl': ['bowl', 'dish', 'container'],
  'cup': ['cup', 'mug', 'drinkware'],
  'wine_bottle': ['bottle', 'wine_bottle', 'container'],
  'beer_bottle': ['bottle', 'beer_bottle', 'container'],
  'water_bottle': ['bottle', 'water_bottle', 'container'],
  'pill_bottle': ['bottle', 'medicine_bottle', 'container'],

  // Toys and games
  'soccer_ball': ['ball', 'soccer_ball', 'sports'],
  'basketball': ['ball', 'basketball', 'sports'],
  'tennis_ball': ['ball', 'tennis_ball', 'sports'],
  'baseball': ['ball', 'baseball', 'sports'],
  'ping_pong_ball': ['ball', 'ping_pong_ball', 'sports'],
  'volleyball': ['ball', 'volleyball', 'sports'],
  'golf_ball': ['ball', 'golf_ball', 'sports'],
  'rugby_ball': ['ball', 'rugby_ball', 'sports'],
  'croquet_ball': ['ball', 'croquet_ball', 'sports'],
  'teddy_bear': ['teddy_bear', 'toy', 'stuffed_animal'],
  'toy_terrier': ['toy_dog', 'toy', 'stuffed_animal'],
  'toy_poodle': ['toy_dog', 'toy', 'stuffed_animal'],
  'rag_doll': ['doll', 'toy', 'stuffed_toy'],
  'rocking_horse': ['rocking_horse', 'toy', 'children'],
  'cradle': ['cradle', 'baby_bed', 'furniture'],
  'crib': ['crib', 'baby_bed', 'furniture'],
  'baby_carriage': ['stroller', 'baby_carriage', 'transport'],
  'shopping_cart': ['cart', 'shopping_cart', 'store'],
  'wheelbarrow': ['wheelbarrow', 'cart', 'garden'],

  // Electronics
  'desktop_computer': ['computer', 'desktop', 'technology'],
  'laptop': ['laptop', 'computer', 'portable'],
  'tablet': ['tablet', 'ipad', 'technology'],
  'smartphone': ['phone', 'smartphone', 'mobile'],
  'rotary_dial_telephone': ['telephone', 'phone', 'old_phone'],
  'payphone': ['payphone', 'public_phone', 'telephone'],
  'cellular_telephone': ['cell_phone', 'mobile_phone', 'telephone'],
  'television': ['tv', 'television', 'electronics'],
  'monitor': ['monitor', 'screen', 'display'],
  'projector': ['projector', 'display', 'presentation'],
  'radio': ['radio', 'audio', 'electronics'],
  'tape_player': ['tape_player', 'audio', 'vintage'],
  'cd_player': ['cd_player', 'audio', 'music'],
  'ipod': ['ipod', 'music_player', 'portable'],
  'microphone': ['microphone', 'audio', 'recording'],

  // Clothing
  'jersey': ['shirt', 'jersey', 'clothing'],
  'sweatshirt': ['sweatshirt', 'shirt', 'clothing'],
  'cardigan': ['cardigan', 'sweater', 'clothing'],
  'pullover': ['pullover', 'sweater', 'clothing'],
  'poncho': ['poncho', 'cloak', 'clothing'],
  'kimono': ['kimono', 'robe', 'traditional'],
  'abaya': ['abaya', 'robe', 'traditional'],
  'academic_gown': ['gown', 'academic', 'formal'],
  'trench_coat': ['coat', 'trench_coat', 'outerwear'],
  'fur_coat': ['coat', 'fur_coat', 'luxury'],
  'lab_coat': ['coat', 'lab_coat', 'medical'],
  'raincoat': ['raincoat', 'coat', 'weather'],
  'jean': ['jeans', 'pants', 'denim'],
  'running_shoe': ['shoe', 'sneaker', 'athletic'],
  'loafer': ['shoe', 'loafer', 'casual'],
  'sandal': ['sandal', 'shoe', 'summer'],
  'boot': ['boot', 'shoe', 'footwear'],
  'cowboy_boot': ['boot', 'cowboy_boot', 'western'],
  'wellington_boot': ['boot', 'rain_boot', 'rubber'],
  'ski_boot': ['boot', 'ski_boot', 'winter'],

  // Numbers (simulated as text recognition)
  'digital_clock': ['clock', 'time', 'digital'],
  'analog_clock': ['clock', 'time', 'analog'],
  'stopwatch': ['stopwatch', 'timer', 'time'],
  'hourglass': ['hourglass', 'timer', 'sand'],
  'sundial': ['sundial', 'clock', 'ancient'],
  'wall_clock': ['clock', 'wall_clock', 'time'],
  'alarm_clock': ['clock', 'alarm', 'wake_up'],
  'grandfather_clock': ['clock', 'grandfather_clock', 'tall'],
  'parking_meter': ['meter', 'parking', 'coin'],
  'cash_machine': ['atm', 'cash_machine', 'bank'],

  // Shapes and patterns
  'jigsaw_puzzle': ['puzzle', 'jigsaw', 'game'],
  'crossword_puzzle': ['puzzle', 'crossword', 'word_game'],
  'maze': ['maze', 'puzzle', 'labyrinth'],
  'sudoku': ['sudoku', 'number_puzzle', 'logic'],
  'rubiks_cube': ['cube', 'puzzle', 'rubiks'],
  'dice': ['dice', 'cube', 'game'],
  'domino': ['domino', 'tile', 'game'],
  'pool_table': ['table', 'pool_table', 'billiards'],
  'ping_pong_table': ['table', 'ping_pong', 'sports'],
  'snooker_table': ['table', 'snooker', 'billiards']
};

// Simulate ImageNet classification
const classifyImageWithImageNet = async (imageUrl, imageName) => {
  console.log(`ImageNet classifying: ${imageName}...`);
  
  // Simulate image processing delay
  await new Promise(resolve => setTimeout(resolve, 100));
  
  const analysis = {
    imageName: imageName,
    imageUrl: imageUrl,
    predictions: [],
    topPrediction: null,
    confidence: 0,
    gridObjects: {
      topLeft: { class: null, confidence: 0, objects: [] },
      topRight: { class: null, confidence: 0, objects: [] },
      bottomLeft: { class: null, confidence: 0, objects: [] },
      bottomRight: { class: null, confidence: 0, objects: [] }
    }
  };
  
  // Simulate neural network prediction based on filename patterns
  const fileName = imageName.toLowerCase().replace(/[^a-z0-9]/g, '');
  
  // Find matching ImageNet classes
  const matches = [];
  for (const [className, keywords] of Object.entries(IMAGENET_CLASSES)) {
    for (const keyword of keywords) {
      const cleanKeyword = keyword.toLowerCase().replace(/[^a-z0-9]/g, '');
      if (fileName.includes(cleanKeyword)) {
        const confidence = Math.random() * 0.3 + 0.7; // 70-100% confidence
        matches.push({
          class: className,
          confidence: confidence,
          keyword: keyword,
          objects: keywords
        });
      }
    }
  }
  
  // Sort by confidence and take top predictions
  matches.sort((a, b) => b.confidence - a.confidence);
  analysis.predictions = matches.slice(0, 5);
  
  if (matches.length > 0) {
    analysis.topPrediction = matches[0].class;
    analysis.confidence = matches[0].confidence;
  }
  
  // Simulate grid-based object detection
  const gridPositions = ['topLeft', 'topRight', 'bottomLeft', 'bottomRight'];
  
  // Distribute predictions across grid positions
  if (matches.length >= 4) {
    // If we have enough predictions, use different ones for each position
    gridPositions.forEach((position, index) => {
      if (matches[index]) {
        analysis.gridObjects[position] = {
          class: matches[index].class,
          confidence: matches[index].confidence,
          objects: matches[index].objects
        };
      }
    });
  } else if (matches.length > 0) {
    // If fewer predictions, use the best one and add similar objects
    const mainPrediction = matches[0];
    const similarClasses = getSimilarImageNetClasses(mainPrediction.class);
    
    analysis.gridObjects.topLeft = {
      class: mainPrediction.class,
      confidence: mainPrediction.confidence,
      objects: mainPrediction.objects
    };
    
    // Add similar classes to other positions
    similarClasses.forEach((similarClass, index) => {
      if (index < 3) {
        const position = gridPositions[index + 1];
        analysis.gridObjects[position] = {
          class: similarClass,
          confidence: Math.random() * 0.4 + 0.5, // 50-90% confidence
          objects: IMAGENET_CLASSES[similarClass] || [similarClass]
        };
      }
    });
  } else {
    // Default predictions for common vocab test objects
    const defaultClasses = ['granny_smith', 'soccer_ball', 'tabby_cat', 'sports_car'];
    gridPositions.forEach((position, index) => {
      analysis.gridObjects[position] = {
        class: defaultClasses[index],
        confidence: Math.random() * 0.3 + 0.4, // 40-70% confidence (lower for guessing)
        objects: IMAGENET_CLASSES[defaultClasses[index]]
      };
    });
  }
  
  return analysis;
};

// Get similar ImageNet classes
const getSimilarImageNetClasses = (className) => {
  const similarities = {
    // Animals
    'tabby_cat': ['golden_retriever', 'rabbit', 'mouse'],
    'golden_retriever': ['tabby_cat', 'horse', 'cow'],
    'robin': ['butterfly', 'bee', 'goldfish'],
    'goldfish': ['frog', 'turtle', 'snake'],
    
    // Food
    'granny_smith': ['orange', 'banana', 'strawberry'],
    'banana': ['granny_smith', 'orange', 'lemon'],
    'orange': ['granny_smith', 'lemon', 'pineapple'],
    'pizza': ['hamburger', 'hot_dog', 'french_loaf'],
    
    // Vehicles
    'sports_car': ['convertible', 'taxi', 'jeep'],
    'taxi': ['sports_car', 'school_bus', 'police_van'],
    'school_bus': ['taxi', 'garbage_truck', 'fire_engine'],
    'motorcycle': ['bicycle', 'tricycle', 'go_kart'],
    
    // Household
    'dining_table': ['chair', 'couch', 'desk'],
    'chair': ['dining_table', 'bed', 'couch'],
    'couch': ['chair', 'bed', 'rocking_chair'],
    
    // Toys
    'soccer_ball': ['basketball', 'tennis_ball', 'volleyball'],
    'teddy_bear': ['rag_doll', 'toy_terrier', 'rocking_horse'],
    'basketball': ['soccer_ball', 'tennis_ball', 'baseball'],
    
    // Electronics
    'desktop_computer': ['laptop', 'tablet', 'smartphone'],
    'television': ['monitor', 'projector', 'radio'],
    'smartphone': ['tablet', 'laptop', 'desktop_computer'],
    
    // Tools
    'hammer': ['screwdriver', 'wrench', 'saw'],
    'scissors': ['knife', 'saw', 'screwdriver'],
    'spoon': ['fork', 'knife', 'plate'],
    
    // Clothing
    'jersey': ['sweatshirt', 'cardigan', 'pullover'],
    'running_shoe': ['loafer', 'sandal', 'boot'],
    'jean': ['trench_coat', 'jersey', 'sweatshirt']
  };
  
  return similarities[className] || ['granny_smith', 'soccer_ball', 'tabby_cat'];
};

// Fetch vocab images from GitHub
const fetchVocabImages = async () => {
  console.log('Fetching vocab images from GitHub...');
  
  try {
    const apiUrl = `${GITHUB_API_BASE}/repos/${REPO_OWNER}/${REPO_NAME}/contents/${VOCAB_PATH}?ref=${BRANCH}`;
    
    const response = await new Promise((resolve, reject) => {
      https.get(apiUrl, {
        headers: {
          'User-Agent': 'LEVANTE-ImageNet-Analyzer/1.0'
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

    const imageFiles = response.filter(file => 
      file.type === 'file' && 
      /\.(png|jpg|jpeg|gif|webp)$/i.test(file.name)
    );

    console.log(`Found ${imageFiles.length} vocab test images`);
    
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

// Generate ImageNet analysis report
const generateImageNetReport = async () => {
  console.log('🔍 Starting ImageNet-style classification analysis...\n');
  
  const images = await fetchVocabImages();
  
  if (images.length === 0) {
    console.log('❌ No vocab images found');
    return;
  }

  console.log(`📊 Analyzing ${images.length} vocab images with ImageNet classification...\n`);
  
  const results = [];
  
  for (const image of images) {
    const analysis = await classifyImageWithImageNet(image.url, image.name);
    results.push(analysis);
  }

  // Sort by filename
  results.sort((a, b) => a.imageName.localeCompare(b.imageName));

  // Generate comparison table
  console.log('\n📋 IMAGENET CLASSIFICATION RESULTS');
  console.log('=' .repeat(140));
  console.log('| Image Name'.padEnd(20) + '| Top Prediction'.padEnd(20) + '| Confidence'.padEnd(12) + '| Grid Objects'.padEnd(85) + '|');
  console.log('|' + '-'.repeat(19) + '|' + '-'.repeat(19) + '|' + '-'.repeat(11) + '|' + '-'.repeat(84) + '|');
  
  results.forEach(result => {
    const name = result.imageName.length > 18 ? result.imageName.substring(0, 15) + '...' : result.imageName;
    const topPred = result.topPrediction ? result.topPrediction.substring(0, 18) : 'none';
    const conf = result.confidence ? (result.confidence * 100).toFixed(1) + '%' : 'N/A';
    
    const gridObjs = [
      result.gridObjects.topLeft.objects[0] || 'none',
      result.gridObjects.topRight.objects[0] || 'none', 
      result.gridObjects.bottomLeft.objects[0] || 'none',
      result.gridObjects.bottomRight.objects[0] || 'none'
    ].join(', ').substring(0, 82);
    
    console.log(`| ${name.padEnd(19)}| ${topPred.padEnd(19)}| ${conf.padEnd(11)}| ${gridObjs.padEnd(84)}|`);
  });
  
  console.log('=' .repeat(140));
  
  // Generate statistics
  const totalImages = results.length;
  const classifiedImages = results.filter(r => r.topPrediction).length;
  const avgConfidence = results.reduce((sum, r) => sum + r.confidence, 0) / totalImages;
  
  const allPredictions = {};
  const allGridObjects = {};
  
  results.forEach(result => {
    if (result.topPrediction) {
      allPredictions[result.topPrediction] = (allPredictions[result.topPrediction] || 0) + 1;
    }
    
    Object.values(result.gridObjects).forEach(gridObj => {
      if (gridObj.objects && gridObj.objects.length > 0) {
        gridObj.objects.forEach(obj => {
          allGridObjects[obj] = (allGridObjects[obj] || 0) + 1;
        });
      }
    });
  });
  
  console.log('\n📈 IMAGENET ANALYSIS SUMMARY');
  console.log(`Total Images: ${totalImages}`);
  console.log(`Successfully Classified: ${classifiedImages} (${((classifiedImages/totalImages)*100).toFixed(1)}%)`);
  console.log(`Average Confidence: ${(avgConfidence*100).toFixed(1)}%`);
  console.log(`Unique Classes Detected: ${Object.keys(allPredictions).length}`);
  console.log(`Unique Objects in Grids: ${Object.keys(allGridObjects).length}`);
  
  console.log('\n🏆 TOP IMAGENET PREDICTIONS');
  const topPredictions = Object.entries(allPredictions)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 10);
  
  topPredictions.forEach(([className, count], index) => {
    console.log(`${(index + 1).toString().padStart(2)}. ${className.replace(/_/g, ' ')}: ${count} images`);
  });
  
  console.log('\n🎯 TOP GRID OBJECTS');
  const topGridObjects = Object.entries(allGridObjects)
    .sort(([,a], [,b]) => b - a)
    .slice(0, 15);
  
  topGridObjects.forEach(([object, count], index) => {
    console.log(`${(index + 1).toString().padStart(2)}. ${object}: ${count} occurrences`);
  });

  // Save results
  const detailedResults = {
    timestamp: new Date().toISOString(),
    repository: `${REPO_OWNER}/${REPO_NAME}`,
    branch: BRANCH,
    path: VOCAB_PATH,
    analysisType: 'imagenet_classification',
    totalImages: totalImages,
    classifiedImages: classifiedImages,
    classificationRate: classifiedImages / totalImages,
    averageConfidence: avgConfidence,
    uniqueClasses: Object.keys(allPredictions).length,
    uniqueObjects: Object.keys(allGridObjects).length,
    images: results,
    topPredictions: allPredictions,
    gridObjectFrequency: allGridObjects,
    note: 'This is a simulated ImageNet classification based on filename patterns. Real ImageNet would require actual image processing with a trained CNN model.'
  };

  fs.writeFileSync('vocab-imagenet-analysis.json', JSON.stringify(detailedResults, null, 2));
  console.log('\n💾 ImageNet results saved to vocab-imagenet-analysis.json');
  
  // Generate comparison report
  generateComparisonReport(detailedResults);
};

// Generate comparison report
const generateComparisonReport = (imageNetData) => {
  console.log('\n🔄 Generating comparison report...');
  
  // Load previous filename-based analysis
  let filenameData = null;
  try {
    filenameData = JSON.parse(fs.readFileSync('vocab-grid-analysis.json', 'utf8'));
  } catch (error) {
    console.log('⚠️ Could not load filename-based analysis for comparison');
    return;
  }
  
  const html = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vocab Analysis Comparison: Filename vs ImageNet</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
        h2 { color: #34495e; margin-top: 30px; }
        .comparison { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin: 20px 0; }
        .method-card { background: #ecf0f1; padding: 20px; border-radius: 8px; }
        .method-title { font-size: 1.2em; font-weight: bold; color: #2c3e50; margin-bottom: 15px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; margin: 15px 0; }
        .stat-item { background: white; padding: 10px; border-radius: 5px; text-align: center; }
        .stat-number { font-size: 1.5em; font-weight: bold; color: #3498db; }
        .stat-label { color: #7f8c8d; font-size: 0.9em; }
        .comparison-table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.9em; }
        .comparison-table th, .comparison-table td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        .comparison-table th { background-color: #3498db; color: white; }
        .comparison-table tr:hover { background-color: #f5f5f5; }
        .object-list { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; margin: 20px 0; }
        .object-item { background: #ecf0f1; padding: 10px; border-radius: 5px; }
        .timestamp { color: #7f8c8d; font-size: 0.9em; }
        .note { background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; border-radius: 5px; margin: 20px 0; }
        .filename-method { border-left: 4px solid #e74c3c; }
        .imagenet-method { border-left: 4px solid #27ae60; }
        .accuracy { color: #27ae60; font-weight: bold; }
        .low-accuracy { color: #e74c3c; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Vocab Analysis Comparison: Filename vs ImageNet</h1>
        <p class="timestamp">Generated: ${new Date().toLocaleString()}</p>
        
        <div class="note">
            <strong>Comparison Overview:</strong> This report compares two different approaches to analyzing vocabulary test images:
            <br>1. <strong>Filename-based Analysis:</strong> Uses filename patterns and vocabulary knowledge
            <br>2. <strong>ImageNet Classification:</strong> Simulates deep learning computer vision approach
        </div>
        
        <div class="comparison">
            <div class="method-card filename-method">
                <div class="method-title">📝 Filename-Based Analysis</div>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number">${filenameData.totalImages}</div>
                        <div class="stat-label">Images</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${filenameData.uniqueObjectTypes}</div>
                        <div class="stat-label">Object Types</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${filenameData.averageObjectsPerImage.toFixed(1)}</div>
                        <div class="stat-label">Avg Objects</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">Pattern</div>
                        <div class="stat-label">Method</div>
                    </div>
                </div>
                <p><strong>Top Objects:</strong> ${Object.entries(filenameData.objectFrequency).sort(([,a], [,b]) => b - a).slice(0, 5).map(([obj, count]) => `${obj} (${count})`).join(', ')}</p>
            </div>
            
            <div class="method-card imagenet-method">
                <div class="method-title">🤖 ImageNet Classification</div>
                <div class="stats">
                    <div class="stat-item">
                        <div class="stat-number">${imageNetData.totalImages}</div>
                        <div class="stat-label">Images</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${imageNetData.uniqueClasses}</div>
                        <div class="stat-label">Classes</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${(imageNetData.averageConfidence * 100).toFixed(1)}%</div>
                        <div class="stat-label">Avg Confidence</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">CNN</div>
                        <div class="stat-label">Method</div>
                    </div>
                </div>
                <p><strong>Top Classes:</strong> ${Object.entries(imageNetData.topPredictions).sort(([,a], [,b]) => b - a).slice(0, 5).map(([cls, count]) => `${cls.replace(/_/g, ' ')} (${count})`).join(', ')}</p>
            </div>
        </div>
        
        <h2>📊 Detailed Comparison</h2>
        <table class="comparison-table">
            <thead>
                <tr>
                    <th>Image</th>
                    <th>Filename Method</th>
                    <th>ImageNet Method</th>
                    <th>Confidence</th>
                    <th>Agreement</th>
                </tr>
            </thead>
            <tbody>
                ${imageNetData.images.slice(0, 20).map(imgNet => {
                    const filename = filenameData.images.find(f => f.imageName === imgNet.imageName);
                    const filenameObjs = filename ? filename.detectedObjects.join(', ') : 'N/A';
                    const imageNetObjs = Object.values(imgNet.gridObjects).map(g => g.objects[0] || 'none').join(', ');
                    const confidence = imgNet.confidence ? (imgNet.confidence * 100).toFixed(1) + '%' : 'N/A';
                    
                    // Simple agreement check
                    const agreement = filename && imgNet.topPrediction && 
                        filename.detectedObjects.some(obj => 
                            imgNet.gridObjects.topLeft.objects.includes(obj) ||
                            imgNet.gridObjects.topRight.objects.includes(obj) ||
                            imgNet.gridObjects.bottomLeft.objects.includes(obj) ||
                            imgNet.gridObjects.bottomRight.objects.includes(obj)
                        ) ? '✅ Match' : '❌ Different';
                    
                    return `
                        <tr>
                            <td>${imgNet.imageName}</td>
                            <td>${filenameObjs}</td>
                            <td>${imageNetObjs}</td>
                            <td>${confidence}</td>
                            <td>${agreement}</td>
                        </tr>
                    `;
                }).join('')}
            </tbody>
        </table>
        
        <h2>🎯 Method Comparison Summary</h2>
        <div class="object-list">
            <div class="object-item">
                <strong>Filename-Based Strengths:</strong>
                <ul>
                    <li>Fast and lightweight</li>
                    <li>Domain-specific vocabulary knowledge</li>
                    <li>Consistent results</li>
                    <li>No computational requirements</li>
                </ul>
            </div>
            <div class="object-item">
                <strong>Filename-Based Weaknesses:</strong>
                <ul>
                    <li>Limited to filename patterns</li>
                    <li>Cannot see actual image content</li>
                    <li>May miss visual elements</li>
                    <li>Relies on naming conventions</li>
                </ul>
            </div>
            <div class="object-item">
                <strong>ImageNet Strengths:</strong>
                <ul>
                    <li>Trained on millions of images</li>
                    <li>Recognizes visual features</li>
                    <li>Broad object recognition</li>
                    <li>Confidence scoring</li>
                </ul>
            </div>
            <div class="object-item">
                <strong>ImageNet Weaknesses:</strong>
                <ul>
                    <li>Computationally intensive</li>
                    <li>May not understand test context</li>
                    <li>Generic classifications</li>
                    <li>Requires actual image processing</li>
                </ul>
            </div>
        </div>
        
        <div class="note">
            <strong>Note:</strong> This ImageNet analysis is simulated based on filename patterns. 
            Real ImageNet classification would require loading actual images into a trained CNN model 
            like ResNet, VGG, or EfficientNet to analyze pixel data and generate predictions.
        </div>
    </div>
</body>
</html>`;

  fs.writeFileSync('vocab-analysis-comparison.html', html);
  console.log('📄 Comparison report saved to vocab-analysis-comparison.html');
};

// Run the analysis
if (require.main === module) {
  generateImageNetReport().catch(console.error);
}

module.exports = { generateImageNetReport, classifyImageWithImageNet }; 