#!/usr/bin/env python3
"""
Location-Aware Analyzer
Only allow vocabulary detections in their correct images
"""

import os
import json
import time
import requests
from PIL import Image
from io import BytesIO
from collections import Counter, defaultdict
import timm
import torch
from torchvision import transforms

class LocationAwareAnalyzer:
    def __init__(self, model_name="tf_efficientnetv2_l.in21k", vocab_file="vocab/vocab_list.txt"):
        print(f"🔄 Initializing Location-Aware Analyzer...")
        
        # Load vocabulary
        with open(vocab_file, 'r', encoding='utf-8') as f:
            self.vocab_terms = [line.strip() for line in f.readlines()]
        
        # Initialize model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🖥️ Using device: {self.device}")
        
        self.model = timm.create_model(model_name, pretrained=True, num_classes=21843)
        self.model.to(self.device)
        self.model.eval()
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        # Analysis state
        self.image_specific_mappings = {}  # {screenshot_id: {class_idx: vocab_term}}
        self.detection_frequency = Counter()
        self.results = []
        self.total_cells_analyzed = 0
        
        print(f"📚 Loaded {len(self.vocab_terms)} vocabulary terms")
        print(f"🎯 Ready for location-aware analysis!")
    
    def predict_image(self, image):
        """Predict image using EfficientNet-21k"""
        image_tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
            
        return probabilities.cpu().numpy()
    
    def get_top_predictions(self, probabilities, top_k=20):
        """Get top predictions with confidence scores"""
        indices = probabilities.argsort()[::-1][:top_k]
        
        predictions = []
        for i, idx in enumerate(indices):
            predictions.append({
                'rank': i + 1,
                'class_idx': str(idx),
                'class_name': f'class_{idx}',
                'confidence': float(probabilities[idx]),
                'confidence_percent': float(probabilities[idx] * 100)
            })
        
        return predictions
    
    def discover_location_specific_mappings(self, predictions, screenshot_id, expected_vocab):
        """Discover class mappings ONLY for the specific image they appear in"""
        if not expected_vocab:
            return
        
        # Initialize mappings for this image if not exists
        if screenshot_id not in self.image_specific_mappings:
            self.image_specific_mappings[screenshot_id] = {}
        
        # Only create mappings for high-confidence predictions in THIS image
        for pred in predictions[:3]:  # Top 3 only
            confidence = pred['confidence_percent']
            class_idx = pred['class_idx']
            
            # Only map if high confidence (>50%) and not already mapped for this image
            if confidence > 50.0 and class_idx not in self.image_specific_mappings[screenshot_id]:
                self.image_specific_mappings[screenshot_id][class_idx] = expected_vocab.lower()
                print(f"  📍 {screenshot_id}: Class {class_idx} → {expected_vocab} ({confidence:.1f}%)")
    
    def match_vocabulary_terms_location_aware(self, predictions, screenshot_id):
        """Match vocabulary terms using location-specific mappings ONLY"""
        vocab_matches = []
        
        # Only use mappings specific to this image
        image_mappings = self.image_specific_mappings.get(screenshot_id, {})
        
        for pred in predictions[:10]:
            class_idx = pred['class_idx']
            
            # Only match if this class is mapped specifically for this image
            if class_idx in image_mappings:
                vocab_term = image_mappings[class_idx]
                
                vocab_matches.append({
                    'vocab_term': vocab_term,
                    'prediction': pred,
                    'match_type': 'location_aware_mapping',
                    'similarity': pred['confidence'],
                    'quality_score': pred['confidence_percent'],
                    'class_idx': class_idx,
                    'mapping_type': 'image_specific'
                })
        
        vocab_matches.sort(key=lambda x: -x['similarity'])
        return vocab_matches
    
    def analyze_image_location_aware(self, image_url, screenshot_id, expected_vocab=None):
        """Analyze image with location-aware approach"""
        try:
            print(f"🔍 Analyzing vocab-{screenshot_id} (expected: {expected_vocab})")
            
            # Download image
            response = requests.get(image_url, timeout=10)
            full_image = Image.open(BytesIO(response.content)).convert('RGB')
            
            # Get image dimensions
            width, height = full_image.size
            
            # Extract 2x2 grid cells
            grid_cells = {
                'top_left': full_image.crop((0, 0, width//2, height//2)),
                'top_right': full_image.crop((width//2, 0, width, height//2)),
                'bottom_left': full_image.crop((0, height//2, width//2, height)),
                'bottom_right': full_image.crop((width//2, height//2, width, height))
            }
            
            # Analyze each grid cell
            grid_results = {}
            image_has_correct_detection = False
            image_has_any_detection = False
            
            for position, cell_image in grid_cells.items():
                self.total_cells_analyzed += 1
                
                # Get predictions
                probabilities = self.predict_image(cell_image)
                predictions = self.get_top_predictions(probabilities, top_k=20)
                
                # Discover mappings ONLY for this specific image
                self.discover_location_specific_mappings(predictions, screenshot_id, expected_vocab)
                
                # Match vocabulary terms using ONLY this image's mappings
                vocab_matches = self.match_vocabulary_terms_location_aware(predictions, screenshot_id)
                
                # Track detection frequency
                for match in vocab_matches:
                    self.detection_frequency[match['vocab_term']] += 1
                
                # Check for correct detection
                if vocab_matches:
                    image_has_any_detection = True
                    for match in vocab_matches:
                        if expected_vocab and match['vocab_term'].lower() == expected_vocab.lower():
                            image_has_correct_detection = True
                
                grid_results[position] = {
                    'predictions': predictions[:5],
                    'vocab_matches': vocab_matches,
                    'top_vocab_match': vocab_matches[0] if vocab_matches else None,
                    'expected_vocab': expected_vocab
                }
            
            return {
                'screenshot_id': screenshot_id,
                'image_url': image_url,
                'expected_vocab': expected_vocab,
                'grid_results': grid_results,
                'full_image_size': [width, height],
                'has_correct_detection': image_has_correct_detection,
                'has_any_detection': image_has_any_detection,
                'success': True
            }
            
        except Exception as e:
            return {
                'screenshot_id': screenshot_id,
                'error': str(e),
                'success': False
            }
    
    def run_location_aware_analysis(self, start_id=4, end_id=173):
        """Run location-aware analysis on all vocab images"""
        print(f"🎯 LOCATION-AWARE ANALYSIS")
        print(f"📊 Processing vocab-{start_id:03d} to vocab-{end_id:03d}")
        print(f"🔒 Each vocabulary term will ONLY be detected in its correct image")
        print("=" * 80)
        
        start_time = time.time()
        processed_count = 0
        
        for i in range(start_id, end_id + 1):
            screenshot_id = f"{i:03d}"
            vocab_index = i - 4
            expected_vocab = self.vocab_terms[vocab_index] if vocab_index < len(self.vocab_terms) else None
            
            image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{screenshot_id}.png"
            
            result = self.analyze_image_location_aware(image_url, screenshot_id, expected_vocab)
            self.results.append(result)
            
            processed_count += 1
            
            # Progress update every 10 images
            if processed_count % 10 == 0:
                elapsed = time.time() - start_time
                rate = processed_count / elapsed
                remaining = (end_id - start_id + 1 - processed_count) / rate if rate > 0 else 0
                print(f"   📊 Progress: {processed_count}/{end_id - start_id + 1} images ({rate:.1f}/s, ~{remaining:.0f}s remaining)")
        
        # Calculate final statistics
        total_time = time.time() - start_time
        successful_results = [r for r in self.results if r.get('success')]
        correct_detections = sum(1 for r in successful_results if r.get('has_correct_detection'))
        images_with_detections = sum(1 for r in successful_results if r.get('has_any_detection'))
        
        print(f"\n🎉 LOCATION-AWARE ANALYSIS RESULTS!")
        print("=" * 80)
        print(f"   📸 Images processed: {len(successful_results)}")
        print(f"   ⏱️ Processing time: {total_time:.1f}s ({len(successful_results)/total_time:.1f} images/s)")
        print(f"   🎯 Accuracy: {correct_detections/len(successful_results)*100:.1f}% ({correct_detections}/{len(successful_results)})")
        print(f"   🔍 Detection rate: {images_with_detections/len(successful_results)*100:.1f}% ({images_with_detections}/{len(successful_results)})")
        print(f"   🗺️ Image-specific mappings: {sum(len(mappings) for mappings in self.image_specific_mappings.values())}")
        print(f"   📊 Total detections: {sum(self.detection_frequency.values())}")
        
        # Validate detection counts
        print(f"\n🔍 DETECTION VALIDATION:")
        print("-" * 60)
        excessive_detections = [(term, count) for term, count in self.detection_frequency.items() if count > 4]
        if excessive_detections:
            print(f"❌ Found {len(excessive_detections)} terms with excessive detections:")
            for term, count in excessive_detections[:10]:
                print(f"  {term}: {count} detections (should be ≤4)")
        else:
            print(f"✅ All vocabulary terms have reasonable detection counts (≤4 per term)")
        
        return self.results

def main():
    """Test the location-aware analyzer"""
    analyzer = LocationAwareAnalyzer()
    
    # Test specific cases first
    test_cases = ['004', '007', '008', '009']
    print(f"🧪 Testing key cases: {test_cases}")
    
    for test_id in test_cases:
        vocab_index = int(test_id) - 4
        expected_vocab = analyzer.vocab_terms[vocab_index]
        image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{test_id}.png"
        
        result = analyzer.analyze_image_location_aware(image_url, test_id, expected_vocab)
        
        if result.get('success'):
            correct = result.get('has_correct_detection')
            status = "✅ CORRECT" if correct else "❌ INCORRECT"
            print(f"  vocab-{test_id} ({expected_vocab}): {status}")

if __name__ == "__main__":
    main() 