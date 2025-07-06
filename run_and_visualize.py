#!/usr/bin/env python3
"""
Run and Visualize Smart Balanced Analyzer
Comprehensive analysis with visual results and web interface
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
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from datetime import datetime

class VisualSmartAnalyzer:
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
        
        # Analysis tracking
        self.class_mapping = {}
        self.discovered_classes = defaultdict(list)
        self.validation_stats = defaultdict(dict)
        self.detection_frequency = Counter()
        self.results = []
        self.total_cells_analyzed = 0
        
        print(f"✅ Visual smart analyzer ready!")
    
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
        """Smart class mapping discovery with dynamic thresholds"""
        if not expected_vocab:
            return
        
        # Dynamic thresholds based on term characteristics
        problematic_terms = ['blender', 'bamboo', 'artichoke', 'cork', 'fork']
        is_problematic = expected_vocab.lower() in problematic_terms
        
        if is_problematic:
            min_confidence = 35.0  # Higher threshold for problematic terms
            min_rank = 3
            min_gap = 12.0
        else:
            min_confidence = 25.0  # Standard threshold
            min_rank = 5
            min_gap = 8.0
        
        top_predictions = predictions[:min_rank]
        
        for i, pred in enumerate(top_predictions):
            confidence = pred['confidence_percent']
            class_idx = pred['class_idx']
            
            if confidence > min_confidence:
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
            
            for discovery in discoveries:
                vocab_term = discovery['expected_vocab']
                vocab_counts[vocab_term] += 1
                total_confidence += discovery['confidence']
                if discovery['rank'] == 1:
                    rank_1_count += 1
                if discovery['confidence'] > 40.0:
                    high_confidence_count += 1
            
            # Quality metrics
            avg_confidence = total_confidence / len(discoveries)
            most_common_vocab, occurrence_count = vocab_counts.most_common(1)[0]
            consistency_ratio = occurrence_count / len(discoveries)
            rank_1_ratio = rank_1_count / len(discoveries)
            high_confidence_ratio = high_confidence_count / len(discoveries)
            
            # Smart validation
            if most_common_vocab.lower() in ['blender', 'bamboo', 'artichoke', 'cork', 'fork']:
                validation_passed = (
                    avg_confidence > 40.0 and
                    consistency_ratio > 0.6 and
                    occurrence_count >= 3 and
                    high_confidence_ratio > 0.3
                )
            else:
                validation_passed = (
                    avg_confidence > 30.0 and
                    consistency_ratio > 0.5 and
                    occurrence_count >= 2
                )
            
            if validation_passed:
                new_mappings[class_idx] = most_common_vocab.lower()
                
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
        
        self.class_mapping.update(new_mappings)
        return new_mappings
    
    def match_vocabulary_terms_smart(self, predictions):
        """Smart vocabulary matching with validation"""
        vocab_matches = []
        
        for pred in predictions[:15]:
            class_idx = pred['class_idx']
            
            if class_idx in self.class_mapping:
                vocab_term = self.class_mapping[class_idx]
                quality_score = self.validation_stats.get(class_idx, {}).get('quality_score', 0)
                is_problematic = self.validation_stats.get(class_idx, {}).get('is_problematic_term', False)
                
                # Additional confidence check for problematic terms
                if is_problematic and pred['confidence_percent'] < 35.0:
                    continue
                
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
    
    def analyze_image(self, image_url, screenshot_id, expected_vocab=None):
        """Analyze a single image with full visualization data"""
        try:
            print(f"📸 Processing vocab-{screenshot_id}.png (expected: {expected_vocab})")
            
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
                
                # Discover mappings
                self.discover_class_mappings_smart(predictions, expected_vocab)
                
                # Match vocabulary terms
                vocab_matches = self.match_vocabulary_terms_smart(predictions)
                
                # Track detection frequency
                for match in vocab_matches:
                    self.detection_frequency[match['vocab_term']] += 1
                
                # Check for correct detection
                if vocab_matches:
                    image_has_any_detection = True
                    for match in vocab_matches:
                        if expected_vocab and match['vocab_term'].lower() == expected_vocab.lower():
                            image_has_correct_detection = True
                            print(f"      ✅ CORRECT: Found '{match['vocab_term']}' in {position}")
                
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
                'full_image_size': (width, height),
                'has_correct_detection': image_has_correct_detection,
                'has_any_detection': image_has_any_detection,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {
                'screenshot_id': screenshot_id,
                'error': str(e),
                'success': False
            }
    
    def run_analysis(self, start_id=4, end_id=15):
        """Run comprehensive analysis with visualization"""
        print(f"🎯 RUNNING SMART BALANCED ANALYZER")
        print(f"📊 Processing vocab-{start_id:03d} to vocab-{end_id:03d}")
        print(f"🎨 Generating visualizations and web interface")
        
        start_time = time.time()
        
        for i in range(start_id, end_id + 1):
            screenshot_id = f"{i:03d}"
            vocab_index = i - 4
            expected_vocab = self.vocab_terms[vocab_index] if vocab_index < len(self.vocab_terms) else None
            
            image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{screenshot_id}.png"
            
            result = self.analyze_image(image_url, screenshot_id, expected_vocab)
            self.results.append(result)
            
            # Build mappings periodically
            if i % 3 == 0:
                self.build_class_mapping_smart()
        
        # Final mapping build
        self.build_class_mapping_smart()
        
        # Calculate statistics
        total_time = time.time() - start_time
        successful_results = [r for r in self.results if r.get('success')]
        correct_detections = sum(1 for r in successful_results if r.get('has_correct_detection'))
        images_with_detections = sum(1 for r in successful_results if r.get('has_any_detection'))
        
        print(f"\n📊 ANALYSIS COMPLETE!")
        print(f"   📸 Images processed: {len(successful_results)}")
        print(f"   ⏱️ Processing time: {total_time:.1f}s")
        print(f"   🎯 Accuracy: {correct_detections/len(successful_results)*100:.1f}%")
        print(f"   🔍 Detection rate: {images_with_detections/len(successful_results)*100:.1f}%")
        print(f"   🗺️ Validated mappings: {len(self.class_mapping)}")
        
        return self.generate_visualizations()
    
    def generate_visualizations(self):
        """Generate comprehensive visualizations"""
        print(f"\n🎨 GENERATING VISUALIZATIONS...")
        
        # Create output directory
        output_dir = f"analysis_results_{int(time.time())}"
        os.makedirs(output_dir, exist_ok=True)
        
        # 1. Generate detection frequency chart
        self.create_frequency_chart(output_dir)
        
        # 2. Generate quality mappings chart
        self.create_quality_chart(output_dir)
        
        # 3. Generate grid visualization
        self.create_grid_visualization(output_dir)
        
        # 4. Generate web interface
        self.create_web_interface(output_dir)
        
        # 5. Save detailed results
        self.save_detailed_results(output_dir)
        
        print(f"📁 All visualizations saved to: {output_dir}/")
        print(f"🌐 Open {output_dir}/index.html in your browser to view results")
        
        return output_dir
    
    def create_frequency_chart(self, output_dir):
        """Create detection frequency chart"""
        if not self.detection_frequency:
            return
        
        plt.figure(figsize=(12, 8))
        
        # Get top 15 most frequent detections
        top_detections = self.detection_frequency.most_common(15)
        terms = [term for term, count in top_detections]
        counts = [count for term, count in top_detections]
        
        # Color problematic terms differently
        colors = ['red' if term in ['blender', 'bamboo', 'artichoke', 'cork', 'fork'] else 'blue' for term in terms]
        
        plt.bar(range(len(terms)), counts, color=colors, alpha=0.7)
        plt.xlabel('Vocabulary Terms')
        plt.ylabel('Detection Count')
        plt.title('Vocabulary Detection Frequency\n(Red = Previously Problematic Terms)')
        plt.xticks(range(len(terms)), terms, rotation=45, ha='right')
        plt.tight_layout()
        
        plt.savefig(f"{output_dir}/detection_frequency.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Detection frequency chart saved")
    
    def create_quality_chart(self, output_dir):
        """Create quality mappings chart"""
        if not self.validation_stats:
            return
        
        plt.figure(figsize=(12, 8))
        
        # Get quality scores
        quality_data = []
        for class_idx, stats in self.validation_stats.items():
            quality_data.append({
                'term': stats['vocab_term'],
                'quality_score': stats['quality_score'],
                'evidence_count': stats['evidence_count'],
                'avg_confidence': stats['avg_confidence'],
                'is_problematic': stats.get('is_problematic_term', False)
            })
        
        # Sort by quality score
        quality_data.sort(key=lambda x: x['quality_score'], reverse=True)
        
        terms = [item['term'] for item in quality_data[:15]]
        scores = [item['quality_score'] for item in quality_data[:15]]
        colors = ['red' if item['is_problematic'] else 'green' for item in quality_data[:15]]
        
        plt.bar(range(len(terms)), scores, color=colors, alpha=0.7)
        plt.xlabel('Vocabulary Terms')
        plt.ylabel('Quality Score')
        plt.title('Class Mapping Quality Scores\n(Red = Previously Problematic Terms)')
        plt.xticks(range(len(terms)), terms, rotation=45, ha='right')
        plt.tight_layout()
        
        plt.savefig(f"{output_dir}/quality_scores.png", dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"   📊 Quality scores chart saved")
    
    def create_grid_visualization(self, output_dir):
        """Create grid visualization for key results"""
        successful_results = [r for r in self.results if r.get('success')]
        
        for i, result in enumerate(successful_results[:6]):  # Show first 6 images
            if not result.get('grid_results'):
                continue
            
            fig, axes = plt.subplots(2, 2, figsize=(10, 10))
            fig.suptitle(f"vocab-{result['screenshot_id']}.png (Expected: {result['expected_vocab']})", fontsize=16)
            
            positions = ['top_left', 'top_right', 'bottom_left', 'bottom_right']
            
            for idx, position in enumerate(positions):
                row, col = idx // 2, idx % 2
                ax = axes[row, col]
                
                cell_data = result['grid_results'].get(position, {})
                vocab_matches = cell_data.get('vocab_matches', [])
                
                # Create a placeholder image (we don't have the actual cell images here)
                ax.text(0.5, 0.5, f"{position.replace('_', ' ').title()}", 
                       ha='center', va='center', transform=ax.transAxes, fontsize=12, fontweight='bold')
                
                # Show vocabulary matches
                if vocab_matches:
                    match_text = []
                    for match in vocab_matches[:3]:  # Show top 3 matches
                        confidence = match['prediction']['confidence_percent']
                        term = match['vocab_term']
                        match_text.append(f"{term} ({confidence:.1f}%)")
                    
                    ax.text(0.5, 0.2, '\n'.join(match_text), 
                           ha='center', va='center', transform=ax.transAxes, fontsize=10)
                    
                    # Highlight correct detections
                    if result['expected_vocab'] and any(m['vocab_term'].lower() == result['expected_vocab'].lower() for m in vocab_matches):
                        ax.add_patch(patches.Rectangle((0, 0), 1, 1, linewidth=3, edgecolor='green', facecolor='none', transform=ax.transAxes))
                else:
                    ax.text(0.5, 0.2, "No detections", 
                           ha='center', va='center', transform=ax.transAxes, fontsize=10, style='italic')
                
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.set_xticks([])
                ax.set_yticks([])
            
            plt.tight_layout()
            plt.savefig(f"{output_dir}/grid_viz_{result['screenshot_id']}.png", dpi=300, bbox_inches='tight')
            plt.close()
        
        print(f"   🎨 Grid visualizations saved")
    
    def create_web_interface(self, output_dir):
        """Create interactive web interface"""
        html_content = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Balanced Analyzer Results</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background-color: #f8f9fa; padding: 20px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 2em; font-weight: bold; color: #007bff; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .charts {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(500px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .chart {{ text-align: center; }}
        .chart img {{ max-width: 100%; height: auto; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .results {{ margin-top: 30px; }}
        .result-item {{ margin-bottom: 20px; padding: 15px; background-color: #f8f9fa; border-radius: 8px; }}
        .result-header {{ font-weight: bold; color: #007bff; margin-bottom: 10px; }}
        .grid-results {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 10px; }}
        .grid-cell {{ background-color: white; padding: 10px; border-radius: 5px; border: 1px solid #ddd; }}
        .correct {{ border-color: #28a745; background-color: #d4edda; }}
        .detection {{ border-color: #ffc107; background-color: #fff3cd; }}
        .no-detection {{ border-color: #dc3545; background-color: #f8d7da; }}
        .problematic {{ color: #dc3545; font-weight: bold; }}
        .timestamp {{ text-align: center; color: #666; margin-top: 20px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🎯 Smart Balanced Analyzer Results</h1>
            <p>Enhanced EfficientNet-21k with Dynamic Validation</p>
        </div>
        
        <div class="stats">
            <div class="stat-card">
                <div class="stat-value">{len([r for r in self.results if r.get('success')])}</div>
                <div class="stat-label">Images Processed</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{len(self.class_mapping)}</div>
                <div class="stat-label">Validated Mappings</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(1 for r in self.results if r.get('has_correct_detection'))}</div>
                <div class="stat-label">Correct Detections</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{sum(self.detection_frequency.values())}</div>
                <div class="stat-label">Total Detections</div>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart">
                <h3>Detection Frequency</h3>
                <img src="detection_frequency.png" alt="Detection Frequency Chart">
            </div>
            <div class="chart">
                <h3>Quality Scores</h3>
                <img src="quality_scores.png" alt="Quality Scores Chart">
            </div>
        </div>
        
        <div class="results">
            <h2>📊 Detailed Results</h2>
        """
        
        # Add detailed results
        successful_results = [r for r in self.results if r.get('success')]
        for result in successful_results:
            expected = result.get('expected_vocab', 'Unknown')
            screenshot_id = result.get('screenshot_id', 'Unknown')
            
            html_content += f"""
            <div class="result-item">
                <div class="result-header">vocab-{screenshot_id}.png (Expected: {expected})</div>
                <div class="grid-results">
            """
            
            for position in ['top_left', 'top_right', 'bottom_left', 'bottom_right']:
                cell_data = result.get('grid_results', {}).get(position, {})
                vocab_matches = cell_data.get('vocab_matches', [])
                
                if vocab_matches:
                    # Check if correct detection
                    is_correct = any(m['vocab_term'].lower() == expected.lower() for m in vocab_matches)
                    cell_class = 'correct' if is_correct else 'detection'
                    
                    matches_text = []
                    for match in vocab_matches[:3]:
                        term = match['vocab_term']
                        confidence = match['prediction']['confidence_percent']
                        is_problematic = match.get('is_problematic_term', False)
                        
                        if is_problematic:
                            matches_text.append(f'<span class="problematic">{term}</span> ({confidence:.1f}%)')
                        else:
                            matches_text.append(f'{term} ({confidence:.1f}%)')
                    
                    html_content += f"""
                    <div class="grid-cell {cell_class}">
                        <strong>{position.replace('_', ' ').title()}</strong><br>
                        {' | '.join(matches_text)}
                    </div>
                    """
                else:
                    html_content += f"""
                    <div class="grid-cell no-detection">
                        <strong>{position.replace('_', ' ').title()}</strong><br>
                        No detections
                    </div>
                    """
            
            html_content += """
                </div>
            </div>
            """
        
        html_content += f"""
        </div>
        
        <div class="timestamp">
            Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        </div>
    </div>
</body>
</html>
        """
        
        with open(f"{output_dir}/index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"   🌐 Web interface saved")
    
    def save_detailed_results(self, output_dir):
        """Save detailed JSON results"""
        output_data = {
            'analysis_results': self.results,
            'class_mapping': self.class_mapping,
            'validation_stats': dict(self.validation_stats),
            'detection_frequency': dict(self.detection_frequency),
            'statistics': {
                'total_images': len([r for r in self.results if r.get('success')]),
                'total_cells_analyzed': self.total_cells_analyzed,
                'validated_mappings': len(self.class_mapping),
                'total_detections': sum(self.detection_frequency.values()),
                'correct_detections': sum(1 for r in self.results if r.get('has_correct_detection')),
                'images_with_detections': sum(1 for r in self.results if r.get('has_any_detection'))
            }
        }
        
        with open(f"{output_dir}/detailed_results.json", 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"   💾 Detailed results saved")

if __name__ == "__main__":
    print("🎨 SMART BALANCED ANALYZER WITH VISUALIZATIONS")
    print("=" * 80)
    
    # Check if matplotlib is available
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
    except ImportError:
        print("❌ matplotlib not found. Installing...")
        import subprocess
        subprocess.check_call(["pip", "install", "matplotlib"])
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches
    
    analyzer = VisualSmartAnalyzer()
    output_dir = analyzer.run_analysis(start_id=4, end_id=15)
    
    print(f"\n🎉 ANALYSIS COMPLETE!")
    print(f"📁 Results saved to: {output_dir}/")
    print(f"🌐 Open {output_dir}/index.html in your browser")
    print(f"📊 Charts: detection_frequency.png, quality_scores.png")
    print(f"💾 Data: detailed_results.json") 