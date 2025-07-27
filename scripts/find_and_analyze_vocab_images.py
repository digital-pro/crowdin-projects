#!/usr/bin/env python3
"""
Find and analyze vocabulary images using full EfficientNet-21k classes
"""

import requests
from PIL import Image
from io import BytesIO
import torch
import timm
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
import json
import os
import time
from collections import defaultdict

class FullEfficientNet21kAnalyzer:
    def __init__(self, model_name="tf_efficientnetv2_l.in21k", vocab_file="vocab/vocab_list.txt"):
        """Initialize analyzer with full 21k class space"""
        
        print(f"🔄 Loading EfficientNet-21k model: {model_name}")
        
        # Load model
        self.model = timm.create_model(model_name, pretrained=True)
        self.model.eval()
        
        if torch.cuda.is_available():
            self.model = self.model.cuda()
            print("✅ Using GPU acceleration")
        else:
            print("⚠️ Using CPU")
        
        # Load transforms
        config = resolve_data_config({}, model=self.model)
        self.transform = create_transform(**config)
        
        # Try to get class names from the model
        self.class_names = self.extract_class_names()
        
        # Load vocabulary list
        self.vocab_terms = []
        if os.path.exists(vocab_file):
            with open(vocab_file, 'r') as f:
                self.vocab_terms = [line.strip() for line in f if line.strip()]
        
        print(f"📝 Loaded {len(self.vocab_terms)} vocabulary terms")
    
    def extract_class_names(self):
        """Try to extract class names from the model or use indices"""
        print("🔍 Extracting class names...")
        
        # Try various ways to get class names
        class_names = None
        
        # Method 1: Check if model has class names
        if hasattr(self.model, 'class_names'):
            class_names = self.model.class_names
            print(f"✅ Found class names from model.class_names ({len(class_names)} classes)")
        
        # Method 2: Check default config
        elif hasattr(self.model, 'default_cfg') and 'label_names' in self.model.default_cfg:
            class_names = self.model.default_cfg['label_names']
            print(f"✅ Found class names from default_cfg ({len(class_names)} classes)")
        
        # Method 3: Try to load from timm
        else:
            try:
                from timm.data import ImageNetInfo
                info = ImageNetInfo.from_model(self.model)
                class_names = info.class_names
                print(f"✅ Found class names from ImageNetInfo ({len(class_names)} classes)")
            except:
                pass
        
        # Method 4: Try to download ImageNet-21k class names
        if class_names is None:
            class_names = self.download_imagenet21k_classes()
        
        # Fallback: Generate generic names
        if class_names is None:
            print("⚠️ No class names found, generating generic names for 21k classes")
            class_names = [f"class_{i:05d}" for i in range(21000)]
        
        print(f"📊 Using {len(class_names)} class names")
        return class_names
    
    def download_imagenet21k_classes(self):
        """Try to download ImageNet-21k class names"""
        print("📥 Attempting to download ImageNet-21k class names...")
        
        urls = [
            "https://raw.githubusercontent.com/Alibaba-MIIL/ImageNet21K/main/dataset_preprocessing/imagenet21k_classes.txt",
            "https://raw.githubusercontent.com/rwightman/pytorch-image-models/master/timm/data/imagenet21k_classes.json",
            "https://storage.googleapis.com/bit_models/imagenet21k_classes.txt"
        ]
        
        for url in urls:
            try:
                print(f"  Trying {url}")
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    content = response.text.strip()
                    if url.endswith('.json'):
                        class_names = json.loads(content)
                    else:
                        class_names = [line.strip() for line in content.split('\n') if line.strip()]
                    
                    if len(class_names) > 10000:  # Reasonable check for 21k classes
                        print(f"✅ Downloaded {len(class_names)} class names from {url}")
                        return class_names
            except Exception as e:
                print(f"  Failed: {e}")
                continue
        
        print("❌ Could not download ImageNet-21k class names")
        return None
    
    def predict_image(self, image):
        """Get predictions for an image"""
        # Preprocess image
        input_tensor = self.transform(image).unsqueeze(0)
        
        if torch.cuda.is_available():
            input_tensor = input_tensor.cuda()
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        return probabilities.cpu()
    
    def get_top_predictions(self, probabilities, top_k=20):
        """Get top k predictions with class names"""
        top_probs, top_indices = torch.topk(probabilities, top_k)
        
        predictions = []
        for i, (prob, idx) in enumerate(zip(top_probs, top_indices)):
            class_idx = int(idx)
            confidence = float(prob)
            
            # Get class name
            if class_idx < len(self.class_names):
                class_name = self.class_names[class_idx]
            else:
                class_name = f"class_{class_idx:05d}"
            
            predictions.append({
                'rank': i + 1,
                'class_idx': class_idx,
                'class_name': class_name,
                'confidence': confidence,
                'confidence_percent': confidence * 100
            })
        
        return predictions
    
    def match_vocabulary_terms(self, predictions):
        """Match predictions against vocabulary terms using fuzzy matching"""
        vocab_matches = []
        
        for pred in predictions:
            class_name = pred['class_name'].lower()
            
            # Skip generic class names
            if class_name.startswith('class_'):
                continue
            
            # Find vocabulary matches
            for i, vocab_term in enumerate(self.vocab_terms):
                vocab_lower = vocab_term.lower()
                
                # Exact match
                if vocab_lower == class_name:
                    vocab_matches.append({
                        'vocab_rank': i + 1,
                        'vocab_term': vocab_term,
                        'prediction': pred,
                        'match_type': 'exact',
                        'similarity': 1.0
                    })
                    continue
                
                # Partial match
                if vocab_lower in class_name or class_name in vocab_lower:
                    similarity = max(
                        len(vocab_lower) / len(class_name) if class_name else 0,
                        len(class_name) / len(vocab_lower) if vocab_lower else 0
                    )
                    vocab_matches.append({
                        'vocab_rank': i + 1,
                        'vocab_term': vocab_term,
                        'prediction': pred,
                        'match_type': 'partial',
                        'similarity': similarity
                    })
                    continue
                
                # Word-level match
                vocab_words = set(vocab_lower.split())
                class_words = set(class_name.split())
                common_words = vocab_words & class_words
                if common_words:
                    similarity = len(common_words) / len(vocab_words | class_words)
                    vocab_matches.append({
                        'vocab_rank': i + 1,
                        'vocab_term': vocab_term,
                        'prediction': pred,
                        'match_type': 'word_match',
                        'similarity': similarity
                    })
                
                # Character-level similarity for close matches
                import difflib
                similarity = difflib.SequenceMatcher(None, vocab_lower, class_name).ratio()
                if similarity > 0.7:  # High similarity threshold
                    vocab_matches.append({
                        'vocab_rank': i + 1,
                        'vocab_term': vocab_term,
                        'prediction': pred,
                        'match_type': 'character_similarity',
                        'similarity': similarity
                    })
        
        # Sort by similarity and rank
        vocab_matches.sort(key=lambda x: (-x['similarity'], x['vocab_rank']))
        
        return vocab_matches
    
    def analyze_grid_cell(self, image, position):
        """Analyze a single grid cell"""
        try:
            # Get predictions
            probabilities = self.predict_image(image)
            predictions = self.get_top_predictions(probabilities, top_k=50)  # More predictions for better matching
            
            # Match vocabulary terms
            vocab_matches = self.match_vocabulary_terms(predictions)
            
            return {
                'position': position,
                'predictions': predictions,
                'vocab_matches': vocab_matches,
                'top_vocab_match': vocab_matches[0] if vocab_matches else None
            }
            
        except Exception as e:
            print(f"❌ Error analyzing grid cell {position}: {str(e)}")
            return {
                'position': position,
                'error': str(e),
                'predictions': [],
                'vocab_matches': [],
                'top_vocab_match': None
            }
    
    def analyze_vocab_screenshot(self, image_url, screenshot_id):
        """Analyze a vocabulary screenshot with 2x2 grid"""
        try:
            print(f"📥 Downloading {image_url}")
            
            # Download image
            response = requests.get(image_url, timeout=10)
            image = Image.open(BytesIO(response.content)).convert('RGB')
            
            # Get image dimensions
            width, height = image.size
            
            # Extract 2x2 grid cells
            grid_cells = {
                'top_left': image.crop((0, 0, width//2, height//2)),
                'top_right': image.crop((width//2, 0, width, height//2)),
                'bottom_left': image.crop((0, height//2, width//2, height)),
                'bottom_right': image.crop((width//2, height//2, width, height))
            }
            
            # Analyze each grid cell
            results = {}
            for position, cell_image in grid_cells.items():
                print(f"  🔍 Analyzing {position} cell...")
                results[position] = self.analyze_grid_cell(cell_image, position)
            
            return {
                'screenshot_id': screenshot_id,
                'image_url': image_url,
                'grid_results': results,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {image_url}: {str(e)}")
            return {
                'screenshot_id': screenshot_id,
                'image_url': image_url,
                'error': str(e),
                'success': False
            }

def test_vocab_004():
    """Test on vocab-004.png to see if we can find the acorn"""
    print("🧪 Testing full EfficientNet-21k on vocab-004.png")
    
    analyzer = FullEfficientNet21kAnalyzer()
    
    # Test vocab-004.png
    image_url = "https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-004.png"
    
    result = analyzer.analyze_vocab_screenshot(image_url, "004")
    
    if result['success']:
        print(f"\n📊 Results for vocab-004.png:")
        
        for position, cell_result in result['grid_results'].items():
            print(f"\n🔲 {position.upper()}:")
            
            if cell_result.get('error'):
                print(f"  ❌ Error: {cell_result['error']}")
                continue
            
            # Show top predictions
            print(f"  📈 Top 5 predictions:")
            for pred in cell_result['predictions'][:5]:
                print(f"    {pred['rank']}. {pred['class_name']} ({pred['confidence_percent']:.1f}%)")
            
            # Show vocabulary matches
            if cell_result['vocab_matches']:
                print(f"  📝 Top vocabulary matches:")
                for match in cell_result['vocab_matches'][:3]:
                    print(f"    {match['vocab_term']} (rank {match['vocab_rank']}) - {match['match_type']} ({match['similarity']:.2f})")
            else:
                print(f"  📝 No vocabulary matches found")
    
    # Check if acorn was found
    acorn_found = False
    for position, cell_result in result['grid_results'].items():
        if cell_result.get('predictions'):
            for pred in cell_result['predictions']:
                if 'acorn' in pred['class_name'].lower():
                    print(f"\n🎯 ACORN FOUND in {position}! {pred['class_name']} (rank {pred['rank']}, {pred['confidence_percent']:.1f}%)")
                    acorn_found = True
    
    if not acorn_found:
        print(f"\n❌ Acorn not found in any grid cell")

if __name__ == "__main__":
    test_vocab_004() 