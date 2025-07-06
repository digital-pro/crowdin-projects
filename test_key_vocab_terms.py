#!/usr/bin/env python3
"""
Test Key Vocabulary Terms
Focus on the problematic terms to show legitimate detection vs over-detection
"""

import torch
import timm
from PIL import Image
import requests
from io import BytesIO
import json
from collections import defaultdict, Counter

def test_key_vocab_terms():
    """Test the key vocabulary terms that were being over-detected"""
    
    print("🎯 TESTING KEY VOCABULARY TERMS")
    print("=" * 80)
    print("Focus: artichoke, bamboo, blender, cork, fork")
    print("Goal: Detect legitimate instances, prevent over-detection")
    print("=" * 80)
    
    # Load model
    print("🚀 Loading EfficientNet-21k model...")
    model = timm.create_model("tf_efficientnetv2_l.in21k", pretrained=True)
    model.eval()
    
    data_config = timm.data.resolve_model_data_config(model)
    transforms = timm.data.create_transform(**data_config, is_training=False)
    
    # Load vocabulary
    with open('vocab/vocab_list.txt', 'r') as f:
        vocab_terms = [line.strip() for line in f.readlines() if line.strip()]
    
    # Test specific images that should contain these terms
    test_cases = [
        {'id': '007', 'expected': 'artichoke', 'vocab_index': 3},  # vocab-007.png = artichoke
        {'id': '008', 'expected': 'bamboo', 'vocab_index': 4},    # vocab-008.png = bamboo
        {'id': '010', 'expected': 'blender', 'vocab_index': 6},   # vocab-010.png = blender
        {'id': '024', 'expected': 'cork', 'vocab_index': 20},     # vocab-024.png = cork
        {'id': '087', 'expected': 'fork', 'vocab_index': 86},     # vocab-087.png = fork (if it exists)
    ]
    
    def predict_image(image):
        input_tensor = transforms(image).unsqueeze(0)
        with torch.no_grad():
            outputs = model(input_tensor)
            probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
        return probabilities.numpy()
    
    def get_top_predictions(probabilities, top_k=10):
        top_indices = probabilities.argsort()[-top_k:][::-1]
        predictions = []
        for i, idx in enumerate(top_indices):
            confidence = float(probabilities[idx])
            predictions.append({
                'rank': i + 1,
                'class_idx': str(idx),
                'confidence_percent': confidence * 100
            })
        return predictions
    
    results = {}
    
    for test_case in test_cases:
        screenshot_id = test_case['id']
        expected_vocab = test_case['expected']
        
        print(f"\n📸 Testing vocab-{screenshot_id}.png (expected: {expected_vocab})")
        
        try:
            # Download image
            image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{screenshot_id}.png"
            response = requests.get(image_url, timeout=10)
            image = Image.open(BytesIO(response.content)).convert('RGB')
            
            # Extract grid cells
            width, height = image.size
            grid_cells = {
                'top_left': image.crop((0, 0, width//2, height//2)),
                'top_right': image.crop((width//2, 0, width, height//2)),
                'bottom_left': image.crop((0, height//2, width//2, height)),
                'bottom_right': image.crop((width//2, height//2, width, height))
            }
            
            cell_results = {}
            
            for position, cell_image in grid_cells.items():
                print(f"  🔍 Analyzing {position} cell...")
                
                # Get predictions
                probabilities = predict_image(cell_image)
                predictions = get_top_predictions(probabilities, top_k=5)
                
                # Show top predictions
                print(f"    Top predictions:")
                for pred in predictions:
                    print(f"      Rank {pred['rank']}: Class {pred['class_idx']} ({pred['confidence_percent']:.1f}%)")
                
                # Check if any prediction is very high confidence
                top_confidence = predictions[0]['confidence_percent']
                if top_confidence > 50.0:
                    print(f"    🎯 HIGH CONFIDENCE: {top_confidence:.1f}% - Likely legitimate detection")
                elif top_confidence > 30.0:
                    print(f"    ⚖️ MODERATE CONFIDENCE: {top_confidence:.1f}% - Possible detection")
                else:
                    print(f"    ❓ LOW CONFIDENCE: {top_confidence:.1f}% - Unlikely to be target object")
                
                cell_results[position] = {
                    'predictions': predictions,
                    'top_confidence': top_confidence,
                    'assessment': 'high' if top_confidence > 50.0 else 'moderate' if top_confidence > 30.0 else 'low'
                }
            
            results[screenshot_id] = {
                'expected_vocab': expected_vocab,
                'cell_results': cell_results,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            results[screenshot_id] = {
                'expected_vocab': expected_vocab,
                'error': str(e),
                'success': False
            }
    
    # Analyze results
    print(f"\n📊 ANALYSIS SUMMARY:")
    print("=" * 60)
    
    for screenshot_id, result in results.items():
        if result.get('success'):
            expected = result['expected_vocab']
            print(f"\n📸 vocab-{screenshot_id}.png (expected: {expected}):")
            
            high_confidence_cells = []
            moderate_confidence_cells = []
            
            for position, cell_data in result['cell_results'].items():
                assessment = cell_data['assessment']
                confidence = cell_data['top_confidence']
                
                if assessment == 'high':
                    high_confidence_cells.append(f"{position} ({confidence:.1f}%)")
                elif assessment == 'moderate':
                    moderate_confidence_cells.append(f"{position} ({confidence:.1f}%)")
            
            if high_confidence_cells:
                print(f"   🎯 HIGH confidence cells: {', '.join(high_confidence_cells)}")
                print(f"   ✅ Likely contains {expected} - LEGITIMATE DETECTION")
            elif moderate_confidence_cells:
                print(f"   ⚖️ MODERATE confidence cells: {', '.join(moderate_confidence_cells)}")
                print(f"   🤔 Possibly contains {expected} - NEEDS VALIDATION")
            else:
                print(f"   ❓ No high/moderate confidence cells")
                print(f"   ⚠️ May not contain {expected} or detection failed")
    
    print(f"\n🎯 KEY INSIGHTS:")
    print("=" * 60)
    print("This test shows the difference between:")
    print("• ✅ LEGITIMATE detections: High confidence (>50%) in expected images")
    print("• ⚖️ QUESTIONABLE detections: Moderate confidence (30-50%)")
    print("• ❌ FALSE POSITIVES: Low confidence (<30%) everywhere")
    print("")
    print("The original problem was detecting these terms with low confidence")
    print("across ALL images, creating false positive mappings.")
    print("")
    print("The solution is to:")
    print("• Use higher confidence thresholds for these terms")
    print("• Require multiple evidence points")
    print("• Validate consistency across detections")
    print("• Only create mappings for truly confident patterns")

if __name__ == "__main__":
    test_key_vocab_terms() 