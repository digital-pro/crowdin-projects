#!/usr/bin/env python3
"""
Full Hybrid Analysis with Visualization
Run hybrid analyzer on all vocab images and create interactive visualization
"""

import torch
import timm
from PIL import Image
import requests
from io import BytesIO
import json
import time
import os
from collections import defaultdict, Counter
import html

class FullHybridAnalyzer:
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
        
        # Hybrid mapping system
        self.class_mapping = {}
        self.discovered_classes = defaultdict(list)
        self.validation_stats = defaultdict(dict)
        self.detection_frequency = Counter()
        self.results = []
        self.total_cells_analyzed = 0
        
        print(f"✅ Full hybrid analyzer ready!")
    
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
        """Analyze image with hybrid approach"""
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
    
    def run_full_analysis(self, start_id=4, end_id=173):
        """Run full hybrid analysis on all vocab images"""
        print(f"🔄 FULL HYBRID ANALYSIS")
        print(f"📊 Processing vocab-{start_id:03d} to vocab-{end_id:03d}")
        print(f"🎯 Expected images: {end_id - start_id + 1}")
        
        start_time = time.time()
        processed_count = 0
        
        for i in range(start_id, end_id + 1):
            screenshot_id = f"{i:03d}"
            vocab_index = i - 4
            expected_vocab = self.vocab_terms[vocab_index] if vocab_index < len(self.vocab_terms) else None
            
            image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{screenshot_id}.png"
            
            result = self.analyze_image_hybrid(image_url, screenshot_id, expected_vocab)
            self.results.append(result)
            
            processed_count += 1
            
            # Progress update every 10 images
            if processed_count % 10 == 0:
                elapsed = time.time() - start_time
                rate = processed_count / elapsed
                remaining = (end_id - start_id + 1 - processed_count) / rate if rate > 0 else 0
                print(f"   📊 Progress: {processed_count}/{end_id - start_id + 1} images ({rate:.1f}/s, ~{remaining:.0f}s remaining)")
            
            # Build mappings every 20 images
            if processed_count % 20 == 0:
                self.build_class_mapping_hybrid()
        
        # Final mapping build
        self.build_class_mapping_hybrid()
        
        # Calculate statistics
        total_time = time.time() - start_time
        successful_results = [r for r in self.results if r.get('success')]
        correct_detections = sum(1 for r in successful_results if r.get('has_correct_detection'))
        images_with_detections = sum(1 for r in successful_results if r.get('has_any_detection'))
        
        print(f"\n📊 FULL HYBRID ANALYSIS COMPLETE!")
        print(f"=" * 60)
        print(f"   📸 Images processed: {len(successful_results)}")
        print(f"   ⏱️ Processing time: {total_time:.1f}s ({len(successful_results)/total_time:.1f} images/s)")
        print(f"   🎯 Accuracy: {correct_detections/len(successful_results)*100:.1f}% ({correct_detections}/{len(successful_results)})")
        print(f"   🔍 Detection rate: {images_with_detections/len(successful_results)*100:.1f}% ({images_with_detections}/{len(successful_results)})")
        print(f"   🗺️ Class mappings: {len(self.class_mapping)}")
        print(f"   📊 Total detections: {sum(self.detection_frequency.values())}")
        
        return self.results
    
    def generate_visualization(self, output_dir="full_hybrid_results"):
        """Generate interactive visualization of results"""
        print(f"🎨 Generating visualization in {output_dir}/")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save detailed results
        with open(f"{output_dir}/detailed_results.json", 'w', encoding='utf-8') as f:
            json.dump({
                'analysis_results': self.results,
                'class_mappings': self.class_mapping,
                'validation_stats': dict(self.validation_stats),
                'detection_frequency': dict(self.detection_frequency),
                'total_cells_analyzed': self.total_cells_analyzed
            }, f, indent=2)
        
        # Generate HTML visualization
        html_content = self.generate_html_visualization()
        
        with open(f"{output_dir}/index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Visualization saved to {output_dir}/index.html")
        print(f"📊 Detailed results saved to {output_dir}/detailed_results.json")
        
        return output_dir
    
    def generate_html_visualization(self):
        """Generate HTML visualization"""
        successful_results = [r for r in self.results if r.get('success')]
        correct_detections = sum(1 for r in successful_results if r.get('has_correct_detection'))
        images_with_detections = sum(1 for r in successful_results if r.get('has_any_detection'))
        
        # Top detections
        top_detections = self.detection_frequency.most_common(20)
        
        # Mapping types
        mapping_types = Counter()
        for stats in self.validation_stats.values():
            mapping_types[stats.get('mapping_type', 'unknown')] += 1
        
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Full Hybrid Vocabulary Analysis Results</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
            border-left: 4px solid #007bff;
        }}
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #007bff;
        }}
        .stat-label {{
            color: #666;
            margin-top: 5px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }}
        .image-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .image-card {{
            border: 1px solid #ddd;
            border-radius: 8px;
            overflow: hidden;
            background: white;
        }}
        .image-card.correct {{
            border-color: #28a745;
            box-shadow: 0 0 10px rgba(40, 167, 69, 0.3);
        }}
        .image-card.detected {{
            border-color: #17a2b8;
            box-shadow: 0 0 10px rgba(23, 162, 184, 0.3);
        }}
        .image-header {{
            padding: 15px;
            background: #f8f9fa;
            border-bottom: 1px solid #ddd;
        }}
        .image-header.correct {{
            background: #d4edda;
            color: #155724;
        }}
        .image-header.detected {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        .image-title {{
            font-weight: bold;
            font-size: 1.1em;
        }}
        .expected-vocab {{
            font-size: 0.9em;
            color: #666;
            margin-top: 5px;
        }}
        .grid-results {{
            padding: 15px;
        }}
        .grid-cell {{
            margin-bottom: 15px;
            padding: 10px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        .grid-cell.has-match {{
            background: #e7f3ff;
            border-left: 4px solid #007bff;
        }}
        .grid-cell.correct-match {{
            background: #e8f5e8;
            border-left: 4px solid #28a745;
        }}
        .cell-title {{
            font-weight: bold;
            color: #333;
        }}
        .vocab-match {{
            margin-top: 8px;
            padding: 8px;
            background: white;
            border-radius: 4px;
            border: 1px solid #ddd;
        }}
        .vocab-match.correct {{
            background: #f0fff0;
            border-color: #28a745;
        }}
        .match-term {{
            font-weight: bold;
            color: #007bff;
        }}
        .match-term.correct {{
            color: #28a745;
        }}
        .match-confidence {{
            font-size: 0.9em;
            color: #666;
        }}
        .detection-list {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .detection-item {{
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #007bff;
        }}
        .detection-term {{
            font-weight: bold;
            color: #333;
        }}
        .detection-count {{
            color: #666;
            font-size: 0.9em;
        }}
        .mapping-stats {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
        }}
        .mapping-type {{
            padding: 15px;
            background: #f8f9fa;
            border-radius: 8px;
            border-left: 4px solid #6c757d;
        }}
        .no-detections {{
            color: #666;
            font-style: italic;
            text-align: center;
            padding: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Full Hybrid Vocabulary Analysis Results</h1>
            <p>EfficientNet-21k with Single-Evidence High-Confidence Mapping</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len(successful_results)}</div>
                <div class="stat-label">Images Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{correct_detections/len(successful_results)*100:.1f}%</div>
                <div class="stat-label">Accuracy</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{images_with_detections/len(successful_results)*100:.1f}%</div>
                <div class="stat-label">Detection Rate</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(self.class_mapping)}</div>
                <div class="stat-label">Class Mappings</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(self.detection_frequency.values())}</div>
                <div class="stat-label">Total Detections</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔍 Top Vocabulary Detections</h2>
            <div class="detection-list">
"""
        
        for term, count in top_detections:
            html_content += f"""
                <div class="detection-item">
                    <div class="detection-term">{html.escape(term)}</div>
                    <div class="detection-count">{count} detections</div>
                </div>
"""
        
        html_content += f"""
            </div>
        </div>
        
        <div class="section">
            <h2>🗺️ Mapping Types</h2>
            <div class="mapping-stats">
"""
        
        for mapping_type, count in mapping_types.items():
            html_content += f"""
                <div class="mapping-type">
                    <div class="detection-term">{html.escape(mapping_type.replace('_', ' ').title())}</div>
                    <div class="detection-count">{count} mappings</div>
                </div>
"""
        
        html_content += f"""
            </div>
        </div>
        
        <div class="section">
            <h2>📸 Analysis Results</h2>
            <div class="image-grid">
"""
        
        for result in successful_results:
            screenshot_id = result['screenshot_id']
            expected_vocab = result.get('expected_vocab', 'unknown')
            has_correct = result.get('has_correct_detection', False)
            has_any = result.get('has_any_detection', False)
            
            card_class = 'correct' if has_correct else ('detected' if has_any else '')
            header_class = 'correct' if has_correct else ('detected' if has_any else '')
            
            html_content += f"""
                <div class="image-card {card_class}">
                    <div class="image-header {header_class}">
                        <div class="image-title">vocab-{screenshot_id}.png</div>
                        <div class="expected-vocab">Expected: {html.escape(expected_vocab)}</div>
                    </div>
                    <div class="grid-results">
"""
            
            grid_results = result.get('grid_results', {})
            if not any(cell.get('vocab_matches') for cell in grid_results.values()):
                html_content += '<div class="no-detections">No vocabulary detections</div>'
            else:
                for position, cell_data in grid_results.items():
                    vocab_matches = cell_data.get('vocab_matches', [])
                    
                    if vocab_matches:
                        has_correct_match = any(match['vocab_term'].lower() == expected_vocab.lower() for match in vocab_matches)
                        cell_class = 'correct-match' if has_correct_match else 'has-match'
                        
                        html_content += f"""
                            <div class="grid-cell {cell_class}">
                                <div class="cell-title">{position.replace('_', ' ').title()}</div>
"""
                        
                        for match in vocab_matches[:2]:  # Show top 2 matches
                            is_correct = match['vocab_term'].lower() == expected_vocab.lower()
                            match_class = 'correct' if is_correct else ''
                            term_class = 'correct' if is_correct else ''
                            
                            html_content += f"""
                                <div class="vocab-match {match_class}">
                                    <span class="match-term {term_class}">{html.escape(match['vocab_term'])}</span>
                                    <span class="match-confidence">({match['prediction']['confidence_percent']:.1f}%)</span>
                                </div>
"""
                        
                        html_content += '</div>'
            
            html_content += """
                    </div>
                </div>
"""
        
        html_content += """
            </div>
        </div>
    </div>
</body>
</html>
"""
        
        return html_content

if __name__ == "__main__":
    print("🔄 FULL HYBRID VOCABULARY ANALYZER")
    print("=" * 80)
    print("Processing all vocab images with hybrid single-evidence mapping")
    
    analyzer = FullHybridAnalyzer()
    
    # Run full analysis
    results = analyzer.run_full_analysis(start_id=4, end_id=173)
    
    # Generate visualization
    output_dir = analyzer.generate_visualization()
    
    print(f"\n🎉 ANALYSIS COMPLETE!")
    print(f"📊 Open {output_dir}/index.html to view results")
    print(f"📁 Detailed data in {output_dir}/detailed_results.json") 