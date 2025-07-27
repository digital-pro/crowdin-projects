#!/usr/bin/env python3
"""
Smart Balanced Vocabulary Analyzer
Detects legitimate instances while preventing over-detection
"""

import torch
import timm
from PIL import Image
import requests
from io import BytesIO
import json
import time
from collections import defaultdict, Counter

class SmartBalancedVocabAnalyzer:
    def __init__(self, model_name="tf_efficientnetv2_l.in21k", vocab_file="vocab/vocab_list.txt"):
        print(f"🚀 Loading {model_name} model...")
        
        # Load model
        self.model = timm.create_model(model_name, pretrained=True)
        self.model.eval()
        
        # Get data transforms
        data_config = timm.data.resolve_model_data_config(self.model)
        self.transforms = timm.data.create_transform(**data_config, is_training=False)
        
        # Load vocabulary terms
        try:
            with open(vocab_file, 'r') as f:
                self.vocab_terms = [line.strip() for line in f.readlines() if line.strip()]
            print(f"📚 Loaded {len(self.vocab_terms)} vocabulary terms")
        except FileNotFoundError:
            print(f"❌ Vocabulary file {vocab_file} not found!")
            self.vocab_terms = []
        
        # Class mapping with smart validation
        self.class_mapping = {}
        self.discovered_classes = defaultdict(list)
        self.validation_stats = defaultdict(dict)
        
        # Track detection frequencies to prevent over-detection
        self.detection_frequency = Counter()
        self.total_cells_analyzed = 0
        
        print(f"✅ Smart balanced analyzer ready!")
    
    def predict_image(self, image):
        """Predict image with EfficientNet-21k"""
        input_tensor = self.transforms(image).unsqueeze(0)
        
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        return probabilities.numpy()
    
    def get_top_predictions(self, probabilities, top_k=20):
        """Get top-k predictions with confidence scores"""
        top_indices = probabilities.argsort()[-top_k:][::-1]
        
        predictions = []
        for i, idx in enumerate(top_indices):
            confidence = float(probabilities[idx])
            predictions.append({
                'rank': i + 1,
                'class_idx': str(idx),
                'class_name': f"class_{idx}",
                'confidence': confidence,
                'confidence_percent': confidence * 100
            })
        
        return predictions
    
    def discover_class_mappings_smart(self, predictions, expected_vocab=None):
        """Smart class mapping discovery with over-detection prevention"""
        if not expected_vocab:
            return
        
        # SMART CRITERIA:
        # 1. Higher confidence for frequently over-detected terms
        # 2. Dynamic thresholds based on detection frequency
        # 3. Expected vocabulary gets priority
        
        # Check if this is a frequently over-detected term
        problematic_terms = ['blender', 'bamboo', 'artichoke', 'cork', 'fork']
        is_problematic = expected_vocab.lower() in problematic_terms
        
        # Dynamic thresholds
        if is_problematic:
            min_confidence = 40.0  # Higher threshold for problematic terms
            min_rank = 2  # Must be in top 2
            min_gap = 15.0  # Larger gap required
        else:
            min_confidence = 25.0  # Standard threshold
            min_rank = 5  # Top 5 is OK
            min_gap = 8.0  # Smaller gap OK
        
        top_predictions = predictions[:min_rank]
        
        for i, pred in enumerate(top_predictions):
            confidence = pred['confidence_percent']
            class_idx = pred['class_idx']
            
            if confidence > min_confidence:
                # Check gap requirement
                if len(predictions) > min_rank:
                    next_confidence = predictions[min_rank]['confidence_percent']
                    confidence_gap = confidence - next_confidence
                    
                    if confidence_gap > min_gap:
                        if class_idx not in self.class_mapping:
                            discovery_info = {
                                'expected_vocab': expected_vocab,
                                'confidence': confidence,
                                'rank': i + 1,
                                'confidence_gap': confidence_gap,
                                'is_problematic': is_problematic
                            }
                            
                            self.discovered_classes[class_idx].append(discovery_info)
                            
                            threshold_type = "HIGH" if is_problematic else "STANDARD"
                            print(f"   🔍 Discovery ({threshold_type}): Class {class_idx} -> '{expected_vocab}' "
                                  f"({confidence:.1f}%, rank {i+1}, gap {confidence_gap:.1f}%)")
    
    def build_class_mapping_smart(self):
        """Build class mapping with smart validation"""
        new_mappings = {}
        
        for class_idx, discoveries in self.discovered_classes.items():
            if len(discoveries) < 2:
                continue
            
            # Quality analysis
            vocab_counts = Counter()
            total_confidence = 0
            rank_1_count = 0
            high_confidence_count = 0
            problematic_count = 0
            
            for discovery in discoveries:
                vocab_term = discovery['expected_vocab']
                vocab_counts[vocab_term] += 1
                total_confidence += discovery['confidence']
                if discovery['rank'] == 1:
                    rank_1_count += 1
                if discovery['confidence'] > 35.0:
                    high_confidence_count += 1
                if discovery.get('is_problematic', False):
                    problematic_count += 1
            
            # Quality metrics
            avg_confidence = total_confidence / len(discoveries)
            most_common_vocab, occurrence_count = vocab_counts.most_common(1)[0]
            consistency_ratio = occurrence_count / len(discoveries)
            rank_1_ratio = rank_1_count / len(discoveries)
            high_confidence_ratio = high_confidence_count / len(discoveries)
            problematic_ratio = problematic_count / len(discoveries)
            
            # Smart validation criteria
            if most_common_vocab.lower() in ['blender', 'bamboo', 'artichoke', 'cork', 'fork']:
                # STRICTER validation for problematic terms
                validation_passed = (
                    avg_confidence > 35.0 and      # Higher confidence
                    consistency_ratio > 0.7 and    # Higher consistency
                    occurrence_count >= 3 and      # More evidence
                    high_confidence_ratio > 0.4    # More high-confidence detections
                )
            else:
                # STANDARD validation for other terms
                validation_passed = (
                    avg_confidence > 25.0 and      # Standard confidence
                    consistency_ratio > 0.5 and    # Standard consistency
                    occurrence_count >= 2          # Standard evidence
                )
            
            if validation_passed:
                new_mappings[class_idx] = most_common_vocab.lower()
                
                # Calculate quality score
                quality_score = avg_confidence * consistency_ratio * (rank_1_ratio + high_confidence_ratio)
                
                self.validation_stats[class_idx] = {
                    'vocab_term': most_common_vocab,
                    'evidence_count': len(discoveries),
                    'avg_confidence': avg_confidence,
                    'consistency_ratio': consistency_ratio,
                    'rank_1_ratio': rank_1_ratio,
                    'high_confidence_ratio': high_confidence_ratio,
                    'quality_score': quality_score,
                    'is_problematic_term': most_common_vocab.lower() in ['blender', 'bamboo', 'artichoke', 'cork', 'fork']
                }
                
                validation_type = "STRICT" if most_common_vocab.lower() in ['blender', 'bamboo', 'artichoke', 'cork', 'fork'] else "STANDARD"
                print(f"   ✅ VALIDATED ({validation_type}): Class {class_idx} -> '{most_common_vocab}' "
                      f"(avg: {avg_confidence:.1f}%, consistency: {consistency_ratio:.1%}, "
                      f"quality: {quality_score:.1f})")
            else:
                print(f"   ❌ REJECTED: Class {class_idx} -> '{most_common_vocab}' "
                      f"(avg: {avg_confidence:.1f}%, consistency: {consistency_ratio:.1%}) "
                      f"- Failed smart validation")
        
        # Update mappings
        old_count = len(self.class_mapping)
        self.class_mapping.update(new_mappings)
        new_count = len(self.class_mapping)
        
        if new_count > old_count:
            print(f"🎯 VALIDATED {new_count - old_count} new mappings! Total: {new_count}")
        
        return new_mappings
    
    def match_vocabulary_terms_smart(self, predictions):
        """Smart vocabulary matching with over-detection prevention"""
        vocab_matches = []
        
        for pred in predictions[:15]:
            class_idx = pred['class_idx']
            
            if class_idx in self.class_mapping:
                vocab_term = self.class_mapping[class_idx]
                quality_score = self.validation_stats.get(class_idx, {}).get('quality_score', 0)
                is_problematic = self.validation_stats.get(class_idx, {}).get('is_problematic_term', False)
                
                # Additional confidence check for problematic terms
                if is_problematic and pred['confidence_percent'] < 35.0:
                    continue  # Skip low-confidence detections of problematic terms
                
                vocab_matches.append({
                    'vocab_term': vocab_term,
                    'prediction': pred,
                    'match_type': 'validated_mapping',
                    'similarity': pred['confidence'],
                    'quality_score': quality_score,
                    'class_idx': class_idx,
                    'is_problematic_term': is_problematic
                })
        
        vocab_matches.sort(key=lambda x: (-x['similarity'], -x['quality_score']))
        return vocab_matches
    
    def analyze_grid_cell_smart(self, image, position, expected_vocab=None):
        """Analyze grid cell with smart validation"""
        try:
            self.total_cells_analyzed += 1
            
            probabilities = self.predict_image(image)
            predictions = self.get_top_predictions(probabilities, top_k=20)
            
            self.discover_class_mappings_smart(predictions, expected_vocab)
            vocab_matches = self.match_vocabulary_terms_smart(predictions)
            
            # Track detection frequency
            for match in vocab_matches:
                self.detection_frequency[match['vocab_term']] += 1
            
            return {
                'position': position,
                'predictions': predictions[:5],
                'vocab_matches': vocab_matches,
                'top_vocab_match': vocab_matches[0] if vocab_matches else None,
                'expected_vocab': expected_vocab
            }
            
        except Exception as e:
            return {
                'position': position,
                'error': str(e),
                'predictions': [],
                'vocab_matches': [],
                'top_vocab_match': None,
                'expected_vocab': expected_vocab
            }
    
    def test_smart_analyzer(self, start_id=4, end_id=20):
        """Test the smart analyzer"""
        print(f"🧠 SMART BALANCED ANALYZER TEST")
        print(f"📊 Processing vocab-{start_id:03d} to vocab-{end_id:03d}")
        print(f"🎯 Goal: Detect legitimate instances while preventing over-detection")
        
        results = []
        start_time = time.time()
        
        # Track metrics
        correct_detections = 0
        total_expected = 0
        images_with_detections = 0
        
        for i in range(start_id, end_id + 1):
            screenshot_id = f"{i:03d}"
            vocab_index = i - 4
            expected_vocab = self.vocab_terms[vocab_index] if vocab_index < len(self.vocab_terms) else None
            
            image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{screenshot_id}.png"
            
            print(f"\n📸 Processing vocab-{screenshot_id}.png (expected: {expected_vocab})")
            
            try:
                # Download and process image
                response = requests.get(image_url, timeout=10)
                image = Image.open(BytesIO(response.content)).convert('RGB')
                
                width, height = image.size
                grid_cells = {
                    'top_left': image.crop((0, 0, width//2, height//2)),
                    'top_right': image.crop((width//2, 0, width, height//2)),
                    'bottom_left': image.crop((0, height//2, width//2, height)),
                    'bottom_right': image.crop((width//2, height//2, width, height))
                }
                
                # Analyze each grid cell
                grid_results = {}
                image_has_correct_detection = False
                image_has_any_detection = False
                
                for position, cell_image in grid_cells.items():
                    cell_result = self.analyze_grid_cell_smart(cell_image, position, expected_vocab)
                    grid_results[position] = cell_result
                    
                    # Check for vocabulary matches
                    if cell_result.get('vocab_matches'):
                        image_has_any_detection = True
                        for match in cell_result['vocab_matches']:
                            vocab_term = match['vocab_term']
                            
                            # Check if correct
                            if expected_vocab and vocab_term.lower() == expected_vocab.lower():
                                image_has_correct_detection = True
                                print(f"      ✅ CORRECT: Found '{vocab_term}' in {position}")
                
                if image_has_correct_detection:
                    correct_detections += 1
                if image_has_any_detection:
                    images_with_detections += 1
                if expected_vocab:
                    total_expected += 1
                
                results.append({
                    'screenshot_id': screenshot_id,
                    'expected_vocab': expected_vocab,
                    'grid_results': grid_results,
                    'has_correct_detection': image_has_correct_detection,
                    'has_any_detection': image_has_any_detection,
                    'success': True
                })
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                results.append({
                    'screenshot_id': screenshot_id,
                    'error': str(e),
                    'success': False
                })
            
            # Build mappings every 3 images
            if i % 3 == 0:
                self.build_class_mapping_smart()
        
        # Final mapping build
        self.build_class_mapping_smart()
        
        # Calculate results
        total_time = time.time() - start_time
        successful_results = [r for r in results if r.get('success')]
        accuracy = (correct_detections / total_expected * 100) if total_expected > 0 else 0
        detection_rate = (images_with_detections / len(successful_results) * 100) if successful_results else 0
        
        print(f"\n📊 SMART ANALYZER RESULTS:")
        print(f"=" * 60)
        print(f"   📸 Images processed: {len(successful_results)}")
        print(f"   🎯 Accuracy: {accuracy:.1f}% ({correct_detections}/{total_expected})")
        print(f"   🔍 Detection rate: {detection_rate:.1f}% ({images_with_detections}/{len(successful_results)})")
        print(f"   🗺️ Validated mappings: {len(self.class_mapping)}")
        print(f"   📊 Total cells analyzed: {self.total_cells_analyzed}")
        
        # Show detection frequency analysis
        print(f"\n🔍 DETECTION FREQUENCY ANALYSIS:")
        print("-" * 60)
        if self.detection_frequency:
            total_detections = sum(self.detection_frequency.values())
            detection_rate_per_cell = (total_detections / self.total_cells_analyzed * 100) if self.total_cells_analyzed > 0 else 0
            
            print(f"   📊 Total detections: {total_detections}")
            print(f"   📊 Detection rate: {detection_rate_per_cell:.1f}% of cells")
            
            # Show top detections
            top_detections = self.detection_frequency.most_common(10)
            for term, count in top_detections:
                percentage = (count / total_detections * 100) if total_detections > 0 else 0
                frequency_per_cell = (count / self.total_cells_analyzed * 100) if self.total_cells_analyzed > 0 else 0
                print(f"   {term}: {count} detections ({percentage:.1f}% of detections, {frequency_per_cell:.1f}% of cells)")
        
        # Check problematic terms
        print(f"\n🚨 PROBLEMATIC TERMS CHECK:")
        print("-" * 60)
        problematic_terms = ['blender', 'bamboo', 'artichoke', 'cork', 'fork']
        
        for term in problematic_terms:
            count = self.detection_frequency.get(term, 0)
            if count > 0:
                frequency_per_cell = (count / self.total_cells_analyzed * 100) if self.total_cells_analyzed > 0 else 0
                if frequency_per_cell > 2.0:  # Flag if appears in >2% of cells
                    print(f"   {term}: {count} detections ({frequency_per_cell:.1f}% of cells) - ⚠️ Still high")
                else:
                    print(f"   {term}: {count} detections ({frequency_per_cell:.1f}% of cells) - ✅ Reasonable")
            else:
                print(f"   {term}: 0 detections - ⚠️ Might be too strict")
        
        return results, self.class_mapping

if __name__ == "__main__":
    print("🧠 SMART BALANCED ENHANCED EFFICIENTNET-21K ANALYZER")
    print("=" * 80)
    
    analyzer = SmartBalancedVocabAnalyzer()
    results, mappings = analyzer.test_smart_analyzer(start_id=4, end_id=20)
    
    print(f"\n🎉 SMART ANALYZER TEST COMPLETE!")
    print(f"This version should:")
    print(f"• ✅ Detect legitimate instances of artichoke, bamboo, etc.")
    print(f"• ❌ Prevent over-detection and false positives")
    print(f"• 🎯 Maintain reasonable detection frequencies")
    print(f"• 🧠 Use dynamic thresholds based on term characteristics") 