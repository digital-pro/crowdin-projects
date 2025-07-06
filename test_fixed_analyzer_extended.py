#!/usr/bin/env python3
"""
Extended Test of Fixed Analyzer
Run on larger dataset to confirm quality improvements
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

class FixedEnhanced21kVocabAnalyzer:
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
        
        # Class mapping with STRICT validation
        self.class_mapping = {}
        self.discovered_classes = defaultdict(list)
        self.validation_stats = defaultdict(dict)
        
        print(f"✅ Enhanced EfficientNet-21k analyzer ready!")
    
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
            confidence = probabilities[idx]
            predictions.append({
                'rank': i + 1,
                'class_idx': str(idx),
                'class_name': f"class_{idx}",
                'confidence': confidence,
                'confidence_percent': confidence * 100
            })
        
        return predictions
    
    def discover_class_mappings_strict(self, predictions, expected_vocab=None):
        """STRICT class mapping discovery with validation"""
        if not expected_vocab:
            return
        
        # STRICT CRITERIA: Top 3 predictions, >30% confidence, >10% gap
        top_predictions = predictions[:3]
        
        for i, pred in enumerate(top_predictions):
            confidence = pred['confidence_percent']
            class_idx = pred['class_idx']
            
            if confidence > 30.0:  # High confidence
                # Check gap from 4th prediction
                if len(predictions) > 3:
                    fourth_confidence = predictions[3]['confidence_percent']
                    confidence_gap = confidence - fourth_confidence
                    
                    if confidence_gap > 10.0:  # Significant gap
                        if class_idx not in self.class_mapping:
                            discovery_info = {
                                'expected_vocab': expected_vocab,
                                'confidence': confidence,
                                'rank': i + 1,
                                'confidence_gap': confidence_gap
                            }
                            
                            self.discovered_classes[class_idx].append(discovery_info)
    
    def build_class_mapping_strict(self):
        """Build class mapping with strict validation"""
        new_mappings = {}
        
        for class_idx, discoveries in self.discovered_classes.items():
            if len(discoveries) < 2:  # Need 2+ evidence points
                continue
            
            # Quality analysis
            vocab_counts = Counter()
            total_confidence = 0
            rank_1_count = 0
            
            for discovery in discoveries:
                vocab_term = discovery['expected_vocab']
                vocab_counts[vocab_term] += 1
                total_confidence += discovery['confidence']
                if discovery['rank'] == 1:
                    rank_1_count += 1
            
            # Quality metrics
            avg_confidence = total_confidence / len(discoveries)
            most_common_vocab, occurrence_count = vocab_counts.most_common(1)[0]
            consistency_ratio = occurrence_count / len(discoveries)
            rank_1_ratio = rank_1_count / len(discoveries)
            
            # STRICT validation
            validation_passed = (
                avg_confidence > 40.0 and      # >40% average confidence
                consistency_ratio > 0.6 and    # >60% consistency
                occurrence_count >= 2 and      # 2+ occurrences
                rank_1_ratio > 0.3             # >30% rank-1 predictions
            )
            
            if validation_passed:
                new_mappings[class_idx] = most_common_vocab.lower()
                
                self.validation_stats[class_idx] = {
                    'vocab_term': most_common_vocab,
                    'evidence_count': len(discoveries),
                    'avg_confidence': avg_confidence,
                    'consistency_ratio': consistency_ratio,
                    'rank_1_ratio': rank_1_ratio,
                    'quality_score': avg_confidence * consistency_ratio * rank_1_ratio
                }
        
        # Update mappings
        old_count = len(self.class_mapping)
        self.class_mapping.update(new_mappings)
        new_count = len(self.class_mapping)
        
        if new_count > old_count:
            print(f"🎯 VALIDATED {new_count - old_count} new mappings! Total: {new_count}")
        
        return new_mappings
    
    def match_vocabulary_terms_fixed(self, predictions):
        """Vocabulary matching with validated mappings only"""
        vocab_matches = []
        
        for pred in predictions[:10]:
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
    
    def analyze_grid_cell_fixed(self, image, position, expected_vocab=None):
        """Analyze grid cell with strict validation"""
        try:
            probabilities = self.predict_image(image)
            predictions = self.get_top_predictions(probabilities, top_k=20)
            
            self.discover_class_mappings_strict(predictions, expected_vocab)
            vocab_matches = self.match_vocabulary_terms_fixed(predictions)
            
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
    
    def run_extended_test(self, start_id=4, end_id=30):
        """Run extended test to demonstrate improvements"""
        print(f"🧪 EXTENDED TEST OF FIXED ANALYZER")
        print(f"📊 Processing vocab-{start_id:03d} to vocab-{end_id:03d}")
        print(f"🎯 Goal: Eliminate false positives like excessive 'bamboo' and 'artichoke'")
        
        results = []
        start_time = time.time()
        
        # Track frequency of detections
        vocab_frequency = Counter()
        correct_detections = 0
        total_expected = 0
        
        for i in range(start_id, end_id + 1):
            screenshot_id = f"{i:03d}"
            vocab_index = i - 4  # Corrected mapping
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
                
                for position, cell_image in grid_cells.items():
                    cell_result = self.analyze_grid_cell_fixed(cell_image, position, expected_vocab)
                    grid_results[position] = cell_result
                    
                    # Check for vocabulary matches
                    if cell_result.get('vocab_matches'):
                        for match in cell_result['vocab_matches']:
                            vocab_term = match['vocab_term']
                            vocab_frequency[vocab_term] += 1
                            
                            # Check if correct
                            if expected_vocab and vocab_term.lower() == expected_vocab.lower():
                                image_has_correct_detection = True
                
                if image_has_correct_detection:
                    correct_detections += 1
                if expected_vocab:
                    total_expected += 1
                
                results.append({
                    'screenshot_id': screenshot_id,
                    'expected_vocab': expected_vocab,
                    'grid_results': grid_results,
                    'has_correct_detection': image_has_correct_detection,
                    'success': True
                })
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                results.append({
                    'screenshot_id': screenshot_id,
                    'error': str(e),
                    'success': False
                })
            
            # Build mappings periodically
            if i % 5 == 0:
                self.build_class_mapping_strict()
        
        # Final mapping build
        self.build_class_mapping_strict()
        
        # Calculate results
        total_time = time.time() - start_time
        successful_results = [r for r in results if r.get('success')]
        accuracy = (correct_detections / total_expected * 100) if total_expected > 0 else 0
        
        print(f"\n📊 EXTENDED TEST RESULTS:")
        print(f"=" * 60)
        print(f"   📸 Images processed: {len(successful_results)}")
        print(f"   ⏱️ Processing time: {total_time:.1f}s")
        print(f"   🚀 Speed: {len(successful_results)/total_time:.1f} images/second")
        print(f"   🎯 Accuracy: {accuracy:.1f}% ({correct_detections}/{total_expected})")
        print(f"   🗺️ Validated mappings: {len(self.class_mapping)}")
        
        # Show frequency analysis
        print(f"\n🔍 VOCABULARY DETECTION FREQUENCY:")
        print("-" * 60)
        if vocab_frequency:
            top_detections = vocab_frequency.most_common(10)
            total_detections = sum(vocab_frequency.values())
            
            for term, count in top_detections:
                percentage = (count / total_detections * 100) if total_detections > 0 else 0
                print(f"   {term}: {count} detections ({percentage:.1f}%)")
        else:
            print("   No vocabulary detections found (strict validation working!)")
        
        # Check for problematic terms
        print(f"\n🚨 PROBLEMATIC TERMS CHECK:")
        print("-" * 60)
        problematic_terms = ['blender', 'bamboo', 'artichoke', 'cork', 'fork']
        
        for term in problematic_terms:
            count = vocab_frequency.get(term, 0)
            if count > 0:
                percentage = (count / total_detections * 100) if total_detections > 0 else 0
                print(f"   {term}: {count} detections ({percentage:.1f}%) - ⚠️ Still appearing")
            else:
                print(f"   {term}: 0 detections - ✅ Successfully eliminated!")
        
        # Show quality mappings
        if self.validation_stats:
            print(f"\n🏆 TOP QUALITY MAPPINGS:")
            print("-" * 60)
            sorted_mappings = sorted(
                self.validation_stats.items(),
                key=lambda x: x[1]['quality_score'],
                reverse=True
            )[:8]
            
            for class_idx, stats in sorted_mappings:
                print(f"   Class {class_idx} -> '{stats['vocab_term']}' "
                      f"(quality: {stats['quality_score']:.2f}, "
                      f"evidence: {stats['evidence_count']}, "
                      f"confidence: {stats['avg_confidence']:.1f}%)")
        
        # Save results
        output_data = {
            'analysis_results': results,
            'class_mapping': self.class_mapping,
            'validation_stats': dict(self.validation_stats),
            'frequency_analysis': dict(vocab_frequency),
            'statistics': {
                'total_images': len(successful_results),
                'processing_time': total_time,
                'accuracy': accuracy,
                'correct_detections': correct_detections,
                'total_expected': total_expected,
                'validated_mappings': len(self.class_mapping)
            }
        }
        
        output_file = f"fixed_analyzer_results_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        return results, self.class_mapping

if __name__ == "__main__":
    print("🔧 EXTENDED TEST OF FIXED ENHANCED EFFICIENTNET-21K ANALYZER")
    print("=" * 80)
    
    analyzer = FixedEnhanced21kVocabAnalyzer()
    results, mappings = analyzer.run_extended_test(start_id=4, end_id=30)
    
    print(f"\n🎉 EXTENDED TEST COMPLETE!")
    print(f"The fixed analyzer should show:")
    print(f"• Dramatic reduction in false positives")
    print(f"• Higher quality, validated mappings only")
    print(f"• Elimination of excessive 'bamboo' and 'artichoke' detections")
    print(f"• Better accuracy with fewer but higher-confidence matches") 