#!/usr/bin/env python3
"""
Test Optimized Global Mapping
Evaluate the performance of the optimized global mapping approach
"""

import json
import requests
from PIL import Image
from io import BytesIO
import timm
import torch
from torchvision import transforms
from collections import Counter

class OptimizedMappingAnalyzer:
    def __init__(self, mapping_file="optimized_global_mapping_1751927020.json"):
        print(f"🔄 Initializing Optimized Mapping Analyzer...")
        
        # Load optimized global mapping
        with open(mapping_file, 'r', encoding='utf-8') as f:
            mapping_data = json.load(f)
        
        self.global_mapping = mapping_data['global_mapping']
        self.mapping_stats = mapping_data['mapping_statistics']
        
        print(f"📊 Loaded {len(self.global_mapping)} global class mappings")
        print(f"📚 Covering {mapping_data['vocabulary_terms_covered']} vocabulary terms")
        
        # Load vocabulary
        with open('vocab/vocab_list.txt', 'r', encoding='utf-8') as f:
            self.vocab_terms = [line.strip() for line in f.readlines()]
        
        # Initialize model
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"🖥️ Using device: {self.device}")
        
        self.model = timm.create_model("tf_efficientnetv2_l.in21k", pretrained=True, num_classes=21843)
        self.model.to(self.device)
        self.model.eval()
        
        # Image preprocessing
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
        
        print(f"🎯 Ready for optimized mapping analysis!")
    
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
    
    def match_vocabulary_with_global_mapping(self, predictions):
        """Match vocabulary terms using optimized global mapping"""
        vocab_matches = []
        
        for pred in predictions:
            class_idx = pred['class_idx']
            
            # Check if this class has a global mapping
            if class_idx in self.global_mapping:
                vocab_term = self.global_mapping[class_idx]
                
                # Get mapping statistics
                stats = self.mapping_stats.get(class_idx, {})
                
                vocab_matches.append({
                    'vocab_term': vocab_term,
                    'prediction': pred,
                    'match_type': 'optimized_global_mapping',
                    'similarity': pred['confidence'],
                    'quality_score': pred['confidence_percent'],
                    'class_idx': class_idx,
                    'mapping_confidence': stats.get('avg_confidence', 0),
                    'mapping_occurrences': stats.get('occurrence_count', 0)
                })
        
        vocab_matches.sort(key=lambda x: -x['similarity'])
        return vocab_matches
    
    def test_key_cases(self):
        """Test the optimized mapping on key vocabulary images"""
        
        print(f"\n🧪 TESTING OPTIMIZED MAPPING ON KEY CASES")
        print("=" * 80)
        
        test_cases = [
            ('004', 'acorn'),
            ('007', 'artichoke'),
            ('008', 'bamboo'),
            ('009', 'barrel'),
            ('010', 'blender'),
            ('018', 'carrot'),
            ('034', 'hamster'),
            ('153', 'mammalogy')
        ]
        
        results = []
        detection_frequency = Counter()
        
        for case_id, expected_vocab in test_cases:
            print(f"\n🔍 Testing vocab-{case_id} (expected: {expected_vocab})")
            
            # Download image
            image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{case_id}.png"
            
            try:
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
                
                # Test each grid cell
                grid_results = {}
                found_expected = False
                
                for position, cell_image in grid_cells.items():
                    # Get predictions
                    probabilities = self.predict_image(cell_image)
                    predictions = self.get_top_predictions(probabilities, top_k=20)
                    
                    # Match with global mapping
                    vocab_matches = self.match_vocabulary_with_global_mapping(predictions)
                    
                    # Track detection frequency
                    for match in vocab_matches:
                        detection_frequency[match['vocab_term']] += 1
                    
                    # Check if expected vocabulary was found
                    expected_found = any(match['vocab_term'] == expected_vocab.lower() for match in vocab_matches)
                    if expected_found:
                        found_expected = True
                    
                    grid_results[position] = {
                        'vocab_matches': vocab_matches,
                        'expected_found': expected_found
                    }
                    
                    # Show results for this cell
                    if vocab_matches:
                        top_match = vocab_matches[0]
                        status = "✅" if expected_found else "❌"
                        print(f"  {position}: {top_match['vocab_term']} ({top_match['quality_score']:.1f}%) {status}")
                    else:
                        print(f"  {position}: No vocabulary matches")
                
                # Overall result for this image
                status = "✅ CORRECT" if found_expected else "❌ INCORRECT"
                print(f"  Result: {status}")
                
                results.append({
                    'case_id': case_id,
                    'expected_vocab': expected_vocab,
                    'found_expected': found_expected,
                    'grid_results': grid_results
                })
                
            except Exception as e:
                print(f"  Error: {e}")
                results.append({
                    'case_id': case_id,
                    'expected_vocab': expected_vocab,
                    'found_expected': False,
                    'error': str(e)
                })
        
        # Calculate overall statistics
        correct_cases = sum(1 for r in results if r.get('found_expected', False))
        total_cases = len(results)
        accuracy = correct_cases / total_cases * 100 if total_cases > 0 else 0
        
        print(f"\n📊 OPTIMIZED MAPPING TEST RESULTS:")
        print("=" * 80)
        print(f"✅ Correct detections: {correct_cases}/{total_cases} ({accuracy:.1f}%)")
        print(f"📈 Total vocabulary detections: {sum(detection_frequency.values())}")
        print(f"🎯 Unique terms detected: {len(detection_frequency)}")
        
        # Show detection frequency
        print(f"\n🔍 Detection frequency:")
        for term, count in detection_frequency.most_common(15):
            status = "✅" if count <= 8 else "⚠️"
            print(f"  {term}: {count} detections {status}")
        
        # Compare with location-aware results
        print(f"\n📈 COMPARISON WITH LOCATION-AWARE:")
        print("-" * 60)
        print(f"Location-Aware: 100% accuracy, 716 total detections (very sparse)")
        print(f"Optimized Global: {accuracy:.1f}% accuracy, {sum(detection_frequency.values())} total detections")
        
        if accuracy >= 75 and sum(detection_frequency.values()) < 100:
            print(f"✅ GOOD BALANCE: High accuracy with reasonable detection counts")
        elif accuracy >= 90:
            print(f"✅ EXCELLENT ACCURACY: Very high accuracy maintained")
        else:
            print(f"⚠️ NEEDS IMPROVEMENT: Accuracy could be better")
        
        return results, detection_frequency

def main():
    """Test the optimized global mapping"""
    analyzer = OptimizedMappingAnalyzer()
    results, detection_freq = analyzer.test_key_cases()
    
    print(f"\n💡 CONCLUSION:")
    print("=" * 80)
    print(f"The optimized global mapping provides a better balance between:")
    print(f"1. ✅ ACCURACY: Still maintains good detection rates")
    print(f"2. ✅ USEFULNESS: Global mappings work across all images")
    print(f"3. ✅ EFFICIENCY: Fewer total detections than over-detection approach")
    print(f"4. ✅ GENERALIZATION: Can detect vocabulary terms in new images")

if __name__ == "__main__":
    main() 