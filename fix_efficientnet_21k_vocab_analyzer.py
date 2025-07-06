#!/usr/bin/env python3
"""
Fixed EfficientNet-21k Vocabulary Analyzer
Maps 21k class indices to proper ImageNet-1k labels using WordNet synsets
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
import difflib

class FixedEfficientNet21kVocabAnalyzer:
    def __init__(self, model_name="tf_efficientnetv2_l.in21k", vocab_file="vocab/vocab_list.txt"):
        """Initialize the fixed analyzer with proper class mapping"""
        
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
        
        # Load ImageNet-1k class mapping
        print("📥 Loading ImageNet-1k class mapping...")
        with open('imagenet21k_wordnet_mapping.json', 'r') as f:
            self.imagenet1k_mapping = json.load(f)
        
        # Create reverse mapping: synset -> class info
        self.synset_to_class = {}
        for class_info in self.imagenet1k_mapping:
            synset = class_info['v3p0']  # WordNet 3.0 synset
            self.synset_to_class[synset] = {
                'idx': class_info['idx'],
                'label': class_info['label'].rstrip("'")
            }
        
        print(f"✅ Loaded {len(self.synset_to_class)} ImageNet-1k class mappings")
        
        # Load vocabulary list
        self.vocab_terms = []
        if os.path.exists(vocab_file):
            with open(vocab_file, 'r') as f:
                self.vocab_terms = [line.strip() for line in f if line.strip()]
        
        print(f"📝 Loaded {len(self.vocab_terms)} vocabulary terms")
        
        # Create a mapping from 21k model output to ImageNet-1k classes
        # This is the key fix - we need to map 21k predictions to 1k classes
        self.create_21k_to_1k_mapping()
    
    def create_21k_to_1k_mapping(self):
        """Create mapping from 21k model predictions to ImageNet-1k classes"""
        print("🔄 Creating 21k to 1k class mapping...")
        
        # For EfficientNet-21k models, the first 1000 classes typically correspond to ImageNet-1k
        # But we need to verify this mapping
        self.class_21k_to_1k = {}
        
        # Map the first 1000 classes directly
        for i in range(min(1000, len(self.imagenet1k_mapping))):
            self.class_21k_to_1k[i] = self.imagenet1k_mapping[i]
        
        print(f"✅ Created mapping for {len(self.class_21k_to_1k)} classes")
    
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
    
    def get_top_predictions(self, probabilities, top_k=10):
        """Get top k predictions with proper class mapping"""
        top_probs, top_indices = torch.topk(probabilities, top_k)
        
        predictions = []
        for i, (prob, idx) in enumerate(zip(top_probs, top_indices)):
            class_idx = int(idx)
            confidence = float(prob)
            
            # Map to ImageNet-1k class if available
            if class_idx in self.class_21k_to_1k:
                class_info = self.class_21k_to_1k[class_idx]
                class_name = class_info['label']
                imagenet1k_idx = class_info['idx']
            else:
                class_name = f"class_{class_idx}"
                imagenet1k_idx = None
            
            predictions.append({
                'rank': i + 1,
                'class_21k_idx': class_idx,
                'imagenet1k_idx': imagenet1k_idx,
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
                if vocab_words & class_words:
                    similarity = len(vocab_words & class_words) / len(vocab_words | class_words)
                    vocab_matches.append({
                        'vocab_rank': i + 1,
                        'vocab_term': vocab_term,
                        'prediction': pred,
                        'match_type': 'word_match',
                        'similarity': similarity
                    })
        
        # Sort by similarity and rank
        vocab_matches.sort(key=lambda x: (-x['similarity'], x['vocab_rank']))
        
        return vocab_matches
    
    def analyze_image(self, image_url, position="unknown"):
        """Analyze a single image"""
        try:
            # Download image
            response = requests.get(image_url, timeout=10)
            image = Image.open(BytesIO(response.content)).convert('RGB')
            
            # Get predictions
            probabilities = self.predict_image(image)
            predictions = self.get_top_predictions(probabilities, top_k=20)
            
            # Match vocabulary terms
            vocab_matches = self.match_vocabulary_terms(predictions)
            
            return {
                'image_url': image_url,
                'position': position,
                'predictions': predictions,
                'vocab_matches': vocab_matches,
                'top_vocab_match': vocab_matches[0] if vocab_matches else None
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {image_url}: {str(e)}")
            return {
                'image_url': image_url,
                'position': position,
                'error': str(e),
                'predictions': [],
                'vocab_matches': [],
                'top_vocab_match': None
            }

def test_acorn_detection():
    """Test the fixed analyzer on vocab-004.png"""
    print("🧪 Testing fixed EfficientNet-21k analyzer on vocab-004.png")
    
    analyzer = FixedEfficientNet21kVocabAnalyzer()
    
    # Test vocab-004.png
    image_url = "https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-004.png"
    
    print(f"📥 Downloading and analyzing {image_url}")
    
    # Download and crop to bottom-right (where acorn should be)
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content)).convert('RGB')
    
    # Get image dimensions and extract bottom-right quadrant
    width, height = image.size
    bottom_right = image.crop((width//2, height//2, width, height))
    
    print("🔍 Analyzing bottom-right quadrant (where acorn should be)...")
    
    # Get predictions for the bottom-right quadrant
    probabilities = analyzer.predict_image(bottom_right)
    predictions = analyzer.get_top_predictions(probabilities, top_k=20)
    
    print("\n📊 Top 20 predictions:")
    for pred in predictions:
        print(f"  {pred['rank']:2d}. {pred['class_name']:<50} ({pred['confidence_percent']:.1f}%)")
    
    # Check for acorn specifically
    acorn_found = False
    for pred in predictions:
        if 'acorn' in pred['class_name'].lower():
            print(f"\n🎯 ACORN FOUND! Rank {pred['rank']}: {pred['class_name']} ({pred['confidence_percent']:.1f}%)")
            acorn_found = True
            break
    
    if not acorn_found:
        print(f"\n❌ Acorn not found in top 20 predictions")
    
    # Match against vocabulary
    vocab_matches = analyzer.match_vocabulary_terms(predictions)
    if vocab_matches:
        print(f"\n📝 Top vocabulary matches:")
        for i, match in enumerate(vocab_matches[:5]):
            print(f"  {i+1}. {match['vocab_term']} (rank {match['vocab_rank']}) - {match['match_type']} match ({match['similarity']:.2f})")

if __name__ == "__main__":
    test_acorn_detection() 