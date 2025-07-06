#!/usr/bin/env python3
"""
Balanced Enhanced EfficientNet-21k Vocabulary Analyzer
Fine-tuned thresholds: Quality control without being too strict
"""

import torch
import timm
from PIL import Image
import requests
from io import BytesIO
import json
import time
import difflib
from collections import defaultdict, Counter

class BalancedEnhanced21kVocabAnalyzer:
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
        
        # Class mapping with BALANCED validation
        self.class_mapping = {}
        self.discovered_classes = defaultdict(list)
        self.validation_stats = defaultdict(dict)
        
        print(f"✅ Balanced EfficientNet-21k analyzer ready!")
    
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
            confidence = float(probabilities[idx])  # Convert to Python float
            predictions.append({
                'rank': i + 1,
                'class_idx': str(idx),
                'class_name': f"class_{idx}",
                'confidence': confidence,
                'confidence_percent': confidence * 100
            })
        
        return predictions
    
    def discover_class_mappings_balanced(self, predictions, expected_vocab=None):
        """BALANCED class mapping discovery - not too strict, not too loose"""
        if not expected_vocab:
            return
        
        # BALANCED CRITERIA:
        # 1. Top 5 predictions (vs 3 strict, vs 20 loose)
        # 2. >20% confidence (vs 30% strict, vs 5% loose)
        # 3. >5% gap from 6th prediction (vs 10% strict, vs none loose)
        
        top_predictions = predictions[:5]  # Top 5 predictions
        
        for i, pred in enumerate(top_predictions):
            confidence = pred['confidence_percent']
            class_idx = pred['class_idx']
            
            if confidence > 20.0:  # Moderate confidence threshold
                # Check gap from 6th prediction
                if len(predictions) > 5:
                    sixth_confidence = predictions[5]['confidence_percent']
                    confidence_gap = confidence - sixth_confidence
                    
                    if confidence_gap > 5.0:  # Moderate gap requirement
                        if class_idx not in self.class_mapping:
                            discovery_info = {
                                'expected_vocab': expected_vocab,
                                'confidence': confidence,
                                'rank': i + 1,
                                'confidence_gap': confidence_gap
                            }
                            
                            self.discovered_classes[class_idx].append(discovery_info)
                            
                            print(f"   🔍 Discovery: Class {class_idx} -> '{expected_vocab}' "
                                  f"({confidence:.1f}%, rank {i+1}, gap {confidence_gap:.1f}%)")
    
    def build_class_mapping_balanced(self):
        """Build class mapping with balanced validation"""
        new_mappings = {}
        
        for class_idx, discoveries in self.discovered_classes.items():
            if len(discoveries) < 2:  # Still need 2+ evidence points
                continue
            
            # Quality analysis
            vocab_counts = Counter()
            total_confidence = 0
            rank_1_count = 0
            high_confidence_count = 0
            
            for discovery in discoveries:
                vocab_term = discovery['expected_vocab']
                vocab_counts[vocab_term] += 1
                total_confidence += discovery['confidence']
                if discovery['rank'] == 1:
                    rank_1_count += 1
                if discovery['confidence'] > 30.0:
                    high_confidence_count += 1
            
            # Quality metrics
            avg_confidence = total_confidence / len(discoveries)
            most_common_vocab, occurrence_count = vocab_counts.most_common(1)[0]
            consistency_ratio = occurrence_count / len(discoveries)
            rank_1_ratio = rank_1_count / len(discoveries)
            high_confidence_ratio = high_confidence_count / len(discoveries)
            
            # BALANCED validation criteria (more permissive)
            validation_passed = (
                avg_confidence > 25.0 and      # >25% average confidence (vs 40% strict)
                consistency_ratio > 0.5 and    # >50% consistency (vs 60% strict)
                occurrence_count >= 2 and      # 2+ occurrences (same)
                (rank_1_ratio > 0.2 or high_confidence_ratio > 0.3)  # Flexible rank/confidence
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
                    'quality_score': quality_score
                }
                
                print(f"   ✅ VALIDATED: Class {class_idx} -> '{most_common_vocab}' "
                      f"(avg: {avg_confidence:.1f}%, consistency: {consistency_ratio:.1%}, "
                      f"quality: {quality_score:.1f})")
            else:
                print(f"   ❌ REJECTED: Class {class_idx} -> '{most_common_vocab}' "
                      f"(avg: {avg_confidence:.1f}%, consistency: {consistency_ratio:.1%}) "
                      f"- Failed balanced validation")
        
        # Update mappings
        old_count = len(self.class_mapping)
        self.class_mapping.update(new_mappings)
        new_count = len(self.class_mapping)
        
        if new_count > old_count:
            print(f"🎯 VALIDATED {new_count - old_count} new mappings! Total: {new_count}")
        
        return new_mappings
    
    def match_vocabulary_terms_balanced(self, predictions):
        """Vocabulary matching with validated mappings"""
        vocab_matches = []
        
        for pred in predictions[:15]:  # Check top 15 predictions
            class_idx = pred['class_idx']
            
            if class_idx in self.class_mapping:
                vocab_term = self.class_mapping[class_idx]
                quality_score = self.validation_stats.get(class_idx, {}).get('quality_score', 0)
                
                vocab_matches.append({
                    'vocab_term': vocab_term,
                    'prediction': pred,
                    'match_type': 'validated_mapping',
                    'similarity': pred['confidence'],
                    'quality_score': quality_score,
                    'class_idx': class_idx
                })
        
        vocab_matches.sort(key=lambda x: (-x['similarity'], -x['quality_score']))
        return vocab_matches
    
    def analyze_grid_cell_balanced(self, image, position, expected_vocab=None):
        """Analyze grid cell with balanced validation"""
        try:
            probabilities = self.predict_image(image)
            predictions = self.get_top_predictions(probabilities, top_k=20)
            
            self.discover_class_mappings_balanced(predictions, expected_vocab)
            vocab_matches = self.match_vocabulary_terms_balanced(predictions)
            
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
    
    def run_balanced_test(self, start_id=4, end_id=25):
        """Run balanced test with fine-tuned thresholds"""
        print(f"🎯 BALANCED TEST OF ENHANCED ANALYZER")
        print(f"📊 Processing vocab-{start_id:03d} to vocab-{end_id:03d}")
        print(f"⚖️ Goal: Quality control without being too strict")
        
        results = []
        start_time = time.time()
        
        # Track metrics
        vocab_frequency = Counter()
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
                    cell_result = self.analyze_grid_cell_balanced(cell_image, position, expected_vocab)
                    grid_results[position] = cell_result
                    
                    # Check for vocabulary matches
                    if cell_result.get('vocab_matches'):
                        image_has_any_detection = True
                        for match in cell_result['vocab_matches']:
                            vocab_term = match['vocab_term']
                            vocab_frequency[vocab_term] += 1
                            
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
            
            # Build mappings every 4 images
            if i % 4 == 0:
                self.build_class_mapping_balanced()
        
        # Final mapping build
        self.build_class_mapping_balanced()
        
        # Calculate results
        total_time = time.time() - start_time
        successful_results = [r for r in results if r.get('success')]
        accuracy = (correct_detections / total_expected * 100) if total_expected > 0 else 0
        detection_rate = (images_with_detections / len(successful_results) * 100) if successful_results else 0
        
        print(f"\n📊 BALANCED TEST RESULTS:")
        print(f"=" * 60)
        print(f"   📸 Images processed: {len(successful_results)}")
        print(f"   ⏱️ Processing time: {total_time:.1f}s")
        print(f"   🚀 Speed: {len(successful_results)/total_time:.1f} images/second")
        print(f"   🎯 Accuracy: {accuracy:.1f}% ({correct_detections}/{total_expected})")
        print(f"   🔍 Detection rate: {detection_rate:.1f}% ({images_with_detections}/{len(successful_results)})")
        print(f"   🗺️ Validated mappings: {len(self.class_mapping)}")
        
        # Show frequency analysis
        print(f"\n🔍 VOCABULARY DETECTION FREQUENCY:")
        print("-" * 60)
        if vocab_frequency:
            top_detections = vocab_frequency.most_common(15)
            total_detections = sum(vocab_frequency.values())
            
            for term, count in top_detections:
                percentage = (count / total_detections * 100) if total_detections > 0 else 0
                print(f"   {term}: {count} detections ({percentage:.1f}%)")
        else:
            print("   No vocabulary detections found")
        
        # Check for problematic terms
        print(f"\n🚨 PROBLEMATIC TERMS CHECK:")
        print("-" * 60)
        problematic_terms = ['blender', 'bamboo', 'artichoke', 'cork', 'fork']
        total_detections = sum(vocab_frequency.values())
        
        for term in problematic_terms:
            count = vocab_frequency.get(term, 0)
            if count > 0:
                percentage = (count / total_detections * 100) if total_detections > 0 else 0
                if percentage > 5.0:  # Flag if >5% of detections
                    print(f"   {term}: {count} detections ({percentage:.1f}%) - ⚠️ High frequency")
                else:
                    print(f"   {term}: {count} detections ({percentage:.1f}%) - ✅ Controlled")
            else:
                print(f"   {term}: 0 detections - ✅ Eliminated")
        
        # Show quality mappings
        if self.validation_stats:
            print(f"\n🏆 TOP QUALITY MAPPINGS:")
            print("-" * 60)
            sorted_mappings = sorted(
                self.validation_stats.items(),
                key=lambda x: x[1]['quality_score'],
                reverse=True
            )[:10]
            
            for class_idx, stats in sorted_mappings:
                print(f"   Class {class_idx} -> '{stats['vocab_term']}' "
                      f"(quality: {stats['quality_score']:.1f}, "
                      f"evidence: {stats['evidence_count']}, "
                      f"avg conf: {stats['avg_confidence']:.1f}%)")
        
        return results, self.class_mapping

if __name__ == "__main__":
    print("⚖️ BALANCED ENHANCED EFFICIENTNET-21K ANALYZER")
    print("=" * 80)
    
    analyzer = BalancedEnhanced21kVocabAnalyzer()
    results, mappings = analyzer.run_balanced_test(start_id=4, end_id=25)
    
    print(f"\n🎉 BALANCED TEST COMPLETE!")
    print(f"This version should provide:")
    print(f"• Quality control to prevent false positives")
    print(f"• Reasonable detection rate (not too strict)")
    print(f"• Elimination of excessive problematic terms")
    print(f"• Better balance between precision and recall") 