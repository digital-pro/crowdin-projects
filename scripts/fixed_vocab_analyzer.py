#!/usr/bin/env python3
"""
Fixed Enhanced EfficientNet-21k Vocabulary Analyzer
Corrects the over-mapping issues with proper confidence thresholds and validation
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
        self.validation_stats = defaultdict(dict)  # Track mapping quality
        
        print(f"✅ Enhanced EfficientNet-21k analyzer ready!")
    
    def predict_image(self, image):
        """Predict image with EfficientNet-21k"""
        # Preprocess image
        input_tensor = self.transforms(image).unsqueeze(0)
        
        # Get predictions
        with torch.no_grad():
            outputs = self.model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        
        return probabilities.numpy()
    
    def get_top_predictions(self, probabilities, top_k=50):
        """Get top-k predictions with confidence scores"""
        top_indices = probabilities.argsort()[-top_k:][::-1]
        
        predictions = []
        for i, idx in enumerate(top_indices):
            confidence = probabilities[idx]
            predictions.append({
                'rank': i + 1,
                'class_idx': str(idx),
                'class_name': f"class_{idx}",  # Generic name since we don't have ImageNet-21k labels
                'confidence': confidence,
                'confidence_percent': confidence * 100
            })
        
        return predictions
    
    def discover_class_mappings_strict(self, predictions, expected_vocab=None):
        """FIXED: Strict class mapping discovery with proper validation"""
        if not expected_vocab:
            return
        
        expected_lower = expected_vocab.lower()
        
        # MUCH STRICTER CRITERIA:
        # 1. Must be in TOP 3 predictions (not top 20!)
        # 2. Must have >30% confidence (not 5%!)
        # 3. Must be significantly higher than other predictions
        
        top_predictions = predictions[:3]  # Only top 3
        
        for i, pred in enumerate(top_predictions):
            confidence = pred['confidence_percent']
            class_idx = pred['class_idx']
            
            # STRICT confidence threshold
            if confidence > 30.0:  # Must be >30% confident
                
                # Additional validation: must be significantly higher than 4th prediction
                if len(predictions) > 3:
                    fourth_confidence = predictions[3]['confidence_percent']
                    confidence_gap = confidence - fourth_confidence
                    
                    # Must have at least 10% gap from 4th prediction
                    if confidence_gap > 10.0:
                        
                        # Skip if we already have a STRONG mapping for this class
                        if class_idx in self.class_mapping:
                            continue
                        
                        # Track discovery with validation metadata
                        discovery_info = {
                            'expected_vocab': expected_vocab,
                            'confidence': confidence,
                            'rank': i + 1,
                            'confidence_gap': confidence_gap
                        }
                        
                        self.discovered_classes[class_idx].append(discovery_info)
                        
                        print(f"   🔍 Potential mapping: Class {class_idx} -> '{expected_vocab}' "
                              f"({confidence:.1f}% confidence, rank {i+1})")
    
    def build_class_mapping_strict(self):
        """FIXED: Build class mapping with strict validation"""
        new_mappings = {}
        
        for class_idx, discoveries in self.discovered_classes.items():
            if len(discoveries) < 2:  # Need at least 2 evidence points
                continue
            
            # Analyze discovery quality
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
            
            # STRICT validation criteria
            validation_passed = (
                avg_confidence > 40.0 and      # Average confidence >40%
                consistency_ratio > 0.6 and    # >60% consistency
                occurrence_count >= 2 and      # At least 2 occurrences
                rank_1_ratio > 0.3             # >30% rank-1 predictions
            )
            
            if validation_passed:
                new_mappings[class_idx] = most_common_vocab.lower()
                
                # Store validation stats
                self.validation_stats[class_idx] = {
                    'vocab_term': most_common_vocab,
                    'evidence_count': len(discoveries),
                    'avg_confidence': avg_confidence,
                    'consistency_ratio': consistency_ratio,
                    'rank_1_ratio': rank_1_ratio,
                    'quality_score': avg_confidence * consistency_ratio * rank_1_ratio
                }
                
                print(f"   ✅ VALIDATED mapping: Class {class_idx} -> '{most_common_vocab}' "
                      f"(avg: {avg_confidence:.1f}%, consistency: {consistency_ratio:.1%}, "
                      f"rank-1: {rank_1_ratio:.1%})")
            else:
                print(f"   ❌ REJECTED mapping: Class {class_idx} -> '{most_common_vocab}' "
                      f"(avg: {avg_confidence:.1f}%, consistency: {consistency_ratio:.1%}, "
                      f"rank-1: {rank_1_ratio:.1%}) - Failed validation")
        
        # Update class mapping
        old_count = len(self.class_mapping)
        self.class_mapping.update(new_mappings)
        new_count = len(self.class_mapping)
        
        if new_count > old_count:
            print(f"🎯 VALIDATED {new_count - old_count} new class mappings!")
            print(f"   Total validated mappings: {new_count}")
        
        return new_mappings
    
    def match_vocabulary_terms_fixed(self, predictions):
        """FIXED: Vocabulary matching with validated mappings only"""
        vocab_matches = []
        
        # ONLY use validated class mappings
        for pred in predictions[:10]:  # Only check top 10
            class_idx = pred['class_idx']
            
            # Check if we have a VALIDATED mapping for this class
            if class_idx in self.class_mapping:
                vocab_term = self.class_mapping[class_idx]
                
                # Get validation quality score
                quality_score = self.validation_stats.get(class_idx, {}).get('quality_score', 0)
                
                vocab_matches.append({
                    'vocab_term': vocab_term,
                    'prediction': pred,
                    'match_type': 'validated_mapping',
                    'similarity': pred['confidence'],
                    'quality_score': quality_score,
                    'class_idx': class_idx
                })
        
        # Sort by confidence and quality
        vocab_matches.sort(key=lambda x: (-x['similarity'], -x['quality_score']))
        
        return vocab_matches
    
    def analyze_grid_cell_fixed(self, image, position, expected_vocab=None):
        """FIXED: Analyze grid cell with strict validation"""
        try:
            # Get predictions
            probabilities = self.predict_image(image)
            predictions = self.get_top_predictions(probabilities, top_k=20)
            
            # Strict class mapping discovery
            self.discover_class_mappings_strict(predictions, expected_vocab)
            
            # Fixed vocabulary matching
            vocab_matches = self.match_vocabulary_terms_fixed(predictions)
            
            return {
                'position': position,
                'predictions': predictions[:5],  # Only store top 5
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
    
    def test_fixed_analyzer(self, start_id=4, end_id=10):
        """Test the fixed analyzer on a small set"""
        print(f"🧪 TESTING FIXED ANALYZER")
        print(f"📊 Processing vocab-{start_id:03d} to vocab-{end_id:03d}")
        
        results = []
        
        for i in range(start_id, end_id + 1):
            screenshot_id = f"{i:03d}"
            
            # Corrected mapping: vocab-004.png = vocab_list[0]
            vocab_index = i - 4
            expected_vocab = self.vocab_terms[vocab_index] if vocab_index < len(self.vocab_terms) else None
            
            image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{screenshot_id}.png"
            
            print(f"\n📸 Processing vocab-{screenshot_id}.png (expected: {expected_vocab})")
            
            try:
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
                grid_results = {}
                for position, cell_image in grid_cells.items():
                    print(f"  🔍 Analyzing {position} cell...")
                    grid_results[position] = self.analyze_grid_cell_fixed(cell_image, position, expected_vocab)
                
                results.append({
                    'screenshot_id': screenshot_id,
                    'image_url': image_url,
                    'grid_results': grid_results,
                    'expected_vocab': expected_vocab,
                    'success': True
                })
                
            except Exception as e:
                print(f"❌ Error processing {screenshot_id}: {str(e)}")
                results.append({
                    'screenshot_id': screenshot_id,
                    'error': str(e),
                    'success': False
                })
            
            # Build mappings every 3 images
            if i % 3 == 0:
                self.build_class_mapping_strict()
        
        # Final mapping build
        final_mappings = self.build_class_mapping_strict()
        
        print(f"\n📊 FIXED ANALYZER TEST RESULTS:")
        print(f"   Images processed: {len([r for r in results if r.get('success')])}")
        print(f"   VALIDATED class mappings: {len(self.class_mapping)}")
        print(f"   Quality-controlled vocabulary detection")
        
        # Show quality metrics
        if self.validation_stats:
            print(f"\n🏆 TOP QUALITY MAPPINGS:")
            sorted_mappings = sorted(
                self.validation_stats.items(), 
                key=lambda x: x[1]['quality_score'], 
                reverse=True
            )[:10]
            
            for class_idx, stats in sorted_mappings:
                print(f"   Class {class_idx} -> '{stats['vocab_term']}' "
                      f"(quality: {stats['quality_score']:.2f}, "
                      f"evidence: {stats['evidence_count']})")
        
        return results, self.class_mapping

if __name__ == "__main__":
    print("🔧 TESTING FIXED ENHANCED EFFICIENTNET-21K ANALYZER")
    print("=" * 80)
    
    analyzer = FixedEnhanced21kVocabAnalyzer()
    results, mappings = analyzer.test_fixed_analyzer(start_id=4, end_id=10)
    
    print(f"\n🎉 Fixed analyzer test complete!")
    print(f"   This should eliminate false positive mappings like excessive 'bamboo' and 'artichoke'")
    print(f"   Only high-confidence, validated mappings are retained") 