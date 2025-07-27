#!/usr/bin/env python3
"""
Run vocabulary analysis with full EfficientNet-21k classes
Focus on the actual class indices being detected for vocabulary matching
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

class VocabAnalyzer:
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
        
        # Load vocabulary list
        self.vocab_terms = []
        if os.path.exists(vocab_file):
            with open(vocab_file, 'r') as f:
                self.vocab_terms = [line.strip() for line in f if line.strip()]
        
        print(f"📝 Loaded {len(self.vocab_terms)} vocabulary terms")
        
        # Create a mapping of likely class indices to names
        self.create_class_mapping()
    
    def create_class_mapping(self):
        """Create a mapping of class indices to potential names"""
        print("🔍 Creating class index mapping...")
        
        # Known mappings from ImageNet-21k research
        # These are based on the actual class indices that appear in vocabulary analysis
        self.class_mapping = {
            19102: "acorn",  # This is what we found for vocab-004
            # Add more mappings as we discover them
        }
        
        print(f"📊 Created mapping for {len(self.class_mapping)} known classes")
    
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
            
            # Get class name from mapping or use generic name
            if class_idx in self.class_mapping:
                class_name = self.class_mapping[class_idx]
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
        """Match predictions against vocabulary terms"""
        vocab_matches = []
        
        for pred in predictions:
            class_name = pred['class_name'].lower()
            
            # Check if this is a known class (not generic)
            if not class_name.startswith('class_'):
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
                        break
                    
                    # Partial match
                    elif vocab_lower in class_name or class_name in vocab_lower:
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
        
        # Sort by similarity and rank
        vocab_matches.sort(key=lambda x: (-x['similarity'], x['vocab_rank']))
        
        return vocab_matches
    
    def analyze_grid_cell(self, image, position):
        """Analyze a single grid cell"""
        try:
            # Get predictions
            probabilities = self.predict_image(image)
            predictions = self.get_top_predictions(probabilities, top_k=20)
            
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

def test_vocab_004_with_mapping():
    """Test on vocab-004.png with class mapping"""
    print("🧪 Testing EfficientNet-21k with class mapping on vocab-004.png")
    
    analyzer = VocabAnalyzer()
    
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
                print(f"    {pred['rank']}. {pred['class_name']} (idx: {pred['class_idx']}, {pred['confidence_percent']:.1f}%)")
            
            # Show vocabulary matches
            if cell_result['vocab_matches']:
                print(f"  📝 Vocabulary matches:")
                for match in cell_result['vocab_matches'][:3]:
                    print(f"    ✅ {match['vocab_term']} (rank {match['vocab_rank']}) - {match['match_type']} ({match['similarity']:.2f})")
            else:
                print(f"  📝 No vocabulary matches found")
    
    # Check for acorn specifically
    acorn_found = False
    for position, cell_result in result['grid_results'].items():
        if cell_result.get('predictions'):
            for pred in cell_result['predictions']:
                if pred['class_name'] == 'acorn':
                    print(f"\n🎯 ACORN FOUND in {position}! Class index {pred['class_idx']} (rank {pred['rank']}, {pred['confidence_percent']:.1f}%)")
                    acorn_found = True
                elif pred['class_idx'] == 19102:  # The index we know is acorn
                    print(f"\n🎯 ACORN DETECTED in {position}! Class index 19102 (rank {pred['rank']}, {pred['confidence_percent']:.1f}%)")
                    acorn_found = True
    
    if not acorn_found:
        print(f"\n❌ Acorn not found in any grid cell")
    
    # Show all high-confidence predictions for analysis
    print(f"\n🔍 All high-confidence predictions for analysis:")
    for position, cell_result in result['grid_results'].items():
        if cell_result.get('predictions'):
            print(f"\n{position.upper()}:")
            for pred in cell_result['predictions'][:10]:
                if pred['confidence_percent'] > 1.0:  # Only show predictions > 1%
                    print(f"  Class {pred['class_idx']}: {pred['confidence_percent']:.1f}%")

if __name__ == "__main__":
    test_vocab_004_with_mapping() 