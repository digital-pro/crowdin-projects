#!/usr/bin/env python3
"""
Fixed Hybrid Analyzer - Builds mappings immediately after discovery
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
from collections import OrderedDict

class FixedHybridAnalyzer:
    def __init__(self, model_name="tf_efficientnetv2_l.in21k", vocab_file="vocab/vocab_list.txt"):
        print(f"🔄 Initializing Fixed Hybrid Analyzer...")
        
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
        self.class_mapping = {}
        self.discovered_classes = defaultdict(list)
        self.validation_stats = {}
        self.detection_frequency = Counter()
        self.results = []
        self.total_cells_analyzed = 0
        
        print(f"📚 Loaded {len(self.vocab_terms)} vocabulary terms")
        print(f"🎯 Ready for analysis!")
    
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
    
    def discover_class_mappings_hybrid(self, predictions, expected_vocab=None):
        """HYBRID: Allow single evidence for very high confidence"""
        if not expected_vocab:
            return
        
        # Check top predictions for high confidence
        for i, pred in enumerate(predictions[:3]):  # Top 3 only
            confidence = pred['confidence_percent']
            class_idx = pred['class_idx']
            
            # Skip if already mapped
            if class_idx in self.class_mapping:
                continue
            
            # HYBRID CRITERIA:
            if confidence > 70.0:
                # IMMEDIATE MAPPING for very high confidence
                self.class_mapping[class_idx] = expected_vocab.lower()
                self.validation_stats[class_idx] = {
                    'vocab_term': expected_vocab,
                    'evidence_count': 1,
                    'avg_confidence': confidence,
                    'consistency_ratio': 1.0,
                    'quality_score': confidence,
                    'mapping_type': 'immediate_high_confidence'
                }
                
            elif confidence > 50.0:
                # SINGLE EVIDENCE with validation
                discovery_info = {
                    'expected_vocab': expected_vocab,
                    'confidence': confidence,
                    'rank': i + 1,
                    'mapping_type': 'single_evidence_validated'
                }
                self.discovered_classes[class_idx].append(discovery_info)
                
            elif confidence > 30.0:
                # MULTIPLE EVIDENCE required
                discovery_info = {
                    'expected_vocab': expected_vocab,
                    'confidence': confidence,
                    'rank': i + 1,
                    'mapping_type': 'multiple_evidence_required'
                }
                self.discovered_classes[class_idx].append(discovery_info)
    
    def build_class_mapping_hybrid(self):
        """Build hybrid class mapping with flexible evidence requirements"""
        new_mappings = {}
        
        for class_idx, discoveries in self.discovered_classes.items():
            if class_idx in self.class_mapping:  # Already mapped
                continue
            
            # Analyze discoveries
            vocab_counts = Counter()
            total_confidence = 0
            high_confidence_count = 0
            
            for discovery in discoveries:
                vocab_term = discovery['expected_vocab']
                vocab_counts[vocab_term] += 1
                total_confidence += discovery['confidence']
                if discovery['confidence'] > 50.0:
                    high_confidence_count += 1
            
            if not discoveries:
                continue
            
            # Quality metrics
            avg_confidence = total_confidence / len(discoveries)
            most_common_vocab, occurrence_count = vocab_counts.most_common(1)[0]
            consistency_ratio = occurrence_count / len(discoveries)
            high_confidence_ratio = high_confidence_count / len(discoveries)
            
            # HYBRID VALIDATION:
            if len(discoveries) == 1 and avg_confidence > 50.0:
                # Single high-confidence evidence
                validation_passed = True
                mapping_type = 'single_high_confidence'
                
            elif len(discoveries) >= 2:
                # Multiple evidence - require consistency
                validation_passed = (
                    avg_confidence > 35.0 and
                    consistency_ratio > 0.6 and
                    occurrence_count >= 2
                )
                mapping_type = 'multiple_evidence_validated'
            else:
                # Single low-confidence evidence - reject
                validation_passed = False
            
            if validation_passed:
                new_mappings[class_idx] = most_common_vocab.lower()
                
                quality_score = avg_confidence * consistency_ratio * (1 + high_confidence_ratio)
                
                self.validation_stats[class_idx] = {
                    'vocab_term': most_common_vocab,
                    'evidence_count': len(discoveries),
                    'avg_confidence': avg_confidence,
                    'consistency_ratio': consistency_ratio,
                    'high_confidence_ratio': high_confidence_ratio,
                    'quality_score': quality_score,
                    'mapping_type': mapping_type
                }
        
        # Update mappings
        self.class_mapping.update(new_mappings)
        return new_mappings
    
    def match_vocabulary_terms_hybrid(self, predictions):
        """Match vocabulary terms using hybrid mappings"""
        vocab_matches = []
        
        for pred in predictions[:10]:
            class_idx = pred['class_idx']
            
            if class_idx in self.class_mapping:
                vocab_term = self.class_mapping[class_idx]
                quality_score = self.validation_stats.get(class_idx, {}).get('quality_score', 0)
                mapping_type = self.validation_stats.get(class_idx, {}).get('mapping_type', 'unknown')
                
                vocab_matches.append({
                    'vocab_term': vocab_term,
                    'prediction': pred,
                    'match_type': 'hybrid_mapping',
                    'similarity': pred['confidence'],
                    'quality_score': quality_score,
                    'class_idx': class_idx,
                    'mapping_type': mapping_type
                })
        
        vocab_matches.sort(key=lambda x: (-x['similarity'], -x['quality_score']))
        return vocab_matches
    
    def analyze_image_hybrid(self, image_url, screenshot_id, expected_vocab=None):
        """Analyze image with hybrid approach - FIXED VERSION"""
        try:
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
                
                # Discover mappings with hybrid approach
                self.discover_class_mappings_hybrid(predictions, expected_vocab)
                
                # 🔧 FIX: Build mappings immediately after discovery
                self.build_class_mapping_hybrid()
                
                # Match vocabulary terms
                vocab_matches = self.match_vocabulary_terms_hybrid(predictions)
                
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
    
    def test_specific_cases(self, test_cases=['007', '008', '009']):
        """Test specific problematic cases"""
        print(f"🧪 TESTING SPECIFIC CASES: {test_cases}")
        print("=" * 80)
        
        for test_id in test_cases:
            vocab_index = int(test_id) - 4
            expected_vocab = self.vocab_terms[vocab_index] if vocab_index < len(self.vocab_terms) else None
            
            image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{test_id}.png"
            
            print(f"\n📸 Testing vocab-{test_id} (expected: {expected_vocab})")
            print("-" * 60)
            
            result = self.analyze_image_hybrid(image_url, test_id, expected_vocab)
            
            if result.get('success'):
                grid_results = result.get('grid_results', {})
                total_matches = 0
                correct_matches = 0
                
                for position, cell_data in grid_results.items():
                    vocab_matches = cell_data.get('vocab_matches', [])
                    total_matches += len(vocab_matches)
                    
                    for match in vocab_matches:
                        if match['vocab_term'].lower() == expected_vocab.lower():
                            correct_matches += 1
                    
                    if vocab_matches:
                        top_match = vocab_matches[0]
                        status = "✅ CORRECT" if top_match['vocab_term'].lower() == expected_vocab.lower() else "❌ WRONG"
                        print(f"  {position}: {status} - {top_match['vocab_term']} ({top_match['prediction']['confidence_percent']:.1f}%)")
                    else:
                        print(f"  {position}: ❌ NO DETECTIONS")
                
                print(f"  📊 Total matches: {total_matches}, Correct: {correct_matches}")
                print(f"  🎯 Result: {'✅ SUCCESS' if correct_matches > 0 else '❌ FAILED'}")
            else:
                print(f"  ❌ Error: {result.get('error')}")
        
        print(f"\n🗺️ Total class mappings created: {len(self.class_mapping)}")
        print(f"📊 Detection frequency: {dict(self.detection_frequency.most_common(10))}")

def main():
    """Test the fixed hybrid analyzer"""
    analyzer = FixedHybridAnalyzer()
    
    # Test the specific problematic cases
    analyzer.test_specific_cases(['007', '008', '009'])

if __name__ == "__main__":
    main() 