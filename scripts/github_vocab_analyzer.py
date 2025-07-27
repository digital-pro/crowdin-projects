#!/usr/bin/env python3
"""
GitHub Vocabulary Analyzer with Full EfficientNet-21k Class Mapping
Systematically builds class index mappings by analyzing vocabulary images
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
from collections import defaultdict, Counter
import difflib

class Enhanced21kVocabAnalyzer:
    def __init__(self, model_name="tf_efficientnetv2_l.in21k", vocab_file="vocab/vocab_list.txt"):
        """Initialize analyzer with comprehensive 21k class mapping"""
        
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
        
        # Initialize class mapping with known mappings
        self.class_mapping = {
            19102: "acorn",  # Confirmed from vocab-004
        }
        
        # Track discovered class indices for building mapping
        self.discovered_classes = defaultdict(list)  # class_idx -> [vocab_terms_that_might_match]
        
        print(f"📊 Starting with {len(self.class_mapping)} known class mappings")
    
    def predict_image(self, image):
        """Get predictions for an image"""
        input_tensor = self.transform(image).unsqueeze(0)
        
        if torch.cuda.is_available():
            input_tensor = input_tensor.cuda()
        
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        return probabilities.cpu()
    
    def get_top_predictions(self, probabilities, top_k=50):
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
    
    def discover_class_mappings(self, predictions, expected_vocab=None):
        """Discover potential class mappings based on predictions and expected vocabulary"""
        if not expected_vocab:
            return
        
        expected_lower = expected_vocab.lower()
        
        # Look for high-confidence predictions that might match the expected vocab
        for pred in predictions[:20]:  # Top 20 predictions
            if pred['confidence_percent'] > 5.0:  # High confidence threshold
                class_idx = pred['class_idx']
                
                # Skip if we already know this class
                if class_idx in self.class_mapping:
                    continue
                
                # Add to discovered classes for potential mapping
                if expected_vocab not in self.discovered_classes[class_idx]:
                    self.discovered_classes[class_idx].append(expected_vocab)
    
    def build_class_mapping_from_discoveries(self):
        """Build class mapping from discovered patterns"""
        new_mappings = {}
        
        for class_idx, potential_terms in self.discovered_classes.items():
            if len(potential_terms) >= 2:  # Multiple evidence points
                # Use the most common term
                term_counts = Counter(potential_terms)
                most_common_term = term_counts.most_common(1)[0][0]
                new_mappings[class_idx] = most_common_term.lower()
        
        # Add high-confidence single mappings
        for class_idx, potential_terms in self.discovered_classes.items():
            if len(potential_terms) == 1 and class_idx not in new_mappings:
                term = potential_terms[0].lower()
                # Only add if the term appears in our vocabulary
                if any(term == vocab.lower() for vocab in self.vocab_terms):
                    new_mappings[class_idx] = term
        
        # Update class mapping
        old_count = len(self.class_mapping)
        self.class_mapping.update(new_mappings)
        new_count = len(self.class_mapping)
        
        if new_count > old_count:
            print(f"🔍 Discovered {new_count - old_count} new class mappings!")
            for class_idx, class_name in new_mappings.items():
                print(f"   Class {class_idx} -> {class_name}")
    
    def match_vocabulary_terms(self, predictions):
        """Enhanced vocabulary matching with discovered mappings"""
        vocab_matches = []
        
        for pred in predictions:
            class_name = pred['class_name'].lower()
            
            # Skip generic class names for vocab matching
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
                
                # Character-level similarity
                similarity = difflib.SequenceMatcher(None, vocab_lower, class_name).ratio()
                if similarity > 0.7:
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
    
    def analyze_grid_cell(self, image, position, expected_vocab=None):
        """Analyze a single grid cell with class discovery"""
        try:
            # Get predictions
            probabilities = self.predict_image(image)
            predictions = self.get_top_predictions(probabilities, top_k=50)
            
            # Discover potential class mappings
            self.discover_class_mappings(predictions, expected_vocab)
            
            # Match vocabulary terms
            vocab_matches = self.match_vocabulary_terms(predictions)
            
            return {
                'position': position,
                'predictions': predictions,
                'vocab_matches': vocab_matches,
                'top_vocab_match': vocab_matches[0] if vocab_matches else None,
                'expected_vocab': expected_vocab
            }
            
        except Exception as e:
            print(f"❌ Error analyzing grid cell {position}: {str(e)}")
            return {
                'position': position,
                'error': str(e),
                'predictions': [],
                'vocab_matches': [],
                'top_vocab_match': None,
                'expected_vocab': expected_vocab
            }
    
    def analyze_vocab_screenshot(self, image_url, screenshot_id, expected_vocab=None):
        """Analyze a vocabulary screenshot with enhanced class discovery"""
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
                results[position] = self.analyze_grid_cell(cell_image, position, expected_vocab)
            
            return {
                'screenshot_id': screenshot_id,
                'image_url': image_url,
                'grid_results': results,
                'expected_vocab': expected_vocab,
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
    
    def analyze_vocabulary_dataset(self, start_id=4, end_id=20):
        """Analyze vocabulary dataset with class mapping discovery"""
        print(f"🚀 Analyzing vocabulary dataset with EfficientNet-21k class discovery")
        print(f"📊 Processing vocab-{start_id:03d} to vocab-{end_id:03d}")
        
        results = []
        start_time = time.time()
        
        for i in range(start_id, end_id + 1):
            screenshot_id = f"{i:03d}"
            image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{screenshot_id}.png"
            
            # Get expected vocabulary term (assuming vocab-001 = acorn, vocab-002 = aloe, etc.)
            expected_vocab = self.vocab_terms[i-1] if i-1 < len(self.vocab_terms) else None
            
            print(f"\n📸 Processing vocab-{screenshot_id}.png (expected: {expected_vocab})")
            
            result = self.analyze_vocab_screenshot(image_url, screenshot_id, expected_vocab)
            results.append(result)
            
            # Build class mapping periodically
            if i % 5 == 0:
                self.build_class_mapping_from_discoveries()
        
        # Final class mapping build
        self.build_class_mapping_from_discoveries()
        
        # Calculate statistics
        total_time = time.time() - start_time
        successful_results = [r for r in results if r.get('success')]
        
        print(f"\n📊 Analysis Complete!")
        print(f"   Total images processed: {len(successful_results)}")
        print(f"   Processing time: {total_time:.2f}s")
        print(f"   Average time per image: {total_time/len(successful_results):.3f}s")
        print(f"   Images per second: {len(successful_results)/total_time:.1f}")
        print(f"   Class mappings discovered: {len(self.class_mapping)}")
        
        # Save results with class mapping
        output_data = {
            'analysis_results': results,
            'class_mapping': self.class_mapping,
            'discovered_classes': dict(self.discovered_classes),
            'statistics': {
                'total_images': len(successful_results),
                'processing_time': total_time,
                'images_per_second': len(successful_results)/total_time,
                'class_mappings_found': len(self.class_mapping)
            }
        }
        
        output_file = f"enhanced_21k_vocab_analysis_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_file}")
        
        return results, self.class_mapping

def main():
    """Main function to run enhanced analysis"""
    print("🚀 Enhanced EfficientNet-21k Vocabulary Analysis")
    print("=" * 60)
    
    analyzer = Enhanced21kVocabAnalyzer()
    
    # Analyze a subset first to build mappings
    print("\n🔍 Phase 1: Building class mappings from first 20 images...")
    results, class_mapping = analyzer.analyze_vocabulary_dataset(start_id=4, end_id=23)
    
    print(f"\n📊 Class Mapping Summary:")
    print(f"   Total mappings discovered: {len(class_mapping)}")
    for class_idx, class_name in sorted(class_mapping.items()):
        print(f"   Class {class_idx} -> {class_name}")
    
    # Test the improved system on vocab-004
    print(f"\n🧪 Testing improved system on vocab-004...")
    test_result = analyzer.analyze_vocab_screenshot(
        "https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-004.png",
        "004",
        "acorn"
    )
    
    if test_result['success']:
        for position, cell_result in test_result['grid_results'].items():
            if cell_result.get('vocab_matches'):
                print(f"   {position}: Found {len(cell_result['vocab_matches'])} vocabulary matches")
                for match in cell_result['vocab_matches'][:2]:
                    print(f"     ✅ {match['vocab_term']} ({match['match_type']}, {match['similarity']:.2f})")

if __name__ == "__main__":
    main() 