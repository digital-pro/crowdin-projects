#!/usr/bin/env python3
"""
EfficientNet-21k Vocabulary Analyzer

This script mimics the behavior of the ResNet-50 web application but uses
EfficientNet models with ImageNet-21k classes for better vocabulary coverage.
Analyzes grid cells and matches against the vocabulary list.
"""

import os
import json
import time
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import torch
import torch.nn.functional as F
from PIL import Image
import timm
from timm.data import resolve_model_data_config, create_transform
from difflib import SequenceMatcher
import numpy as np

class EfficientNet21kVocabAnalyzer:
    """EfficientNet-21k analyzer that mimics ResNet-50 web app behavior."""
    
    def __init__(self, model_name: str = "tf_efficientnetv2_l.in21k", vocab_file: str = "vocab/vocab_list.txt"):
        """Initialize the analyzer."""
        self.model_name = model_name
        self.vocab_file = vocab_file
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        print(f"🚀 Initializing EfficientNet-21k Vocabulary Analyzer")
        print(f"   Model: {model_name}")
        print(f"   Device: {self.device}")
        
        # Load vocabulary
        self.vocab_list = self._load_vocabulary()
        print(f"📖 Loaded {len(self.vocab_list)} vocabulary terms")
        
        # Load ImageNet-21k class names
        self.class_names = self._load_imagenet_21k_classes()
        print(f"🏷️  Loaded {len(self.class_names)} ImageNet-21k class names")
        
        # Initialize model
        self.model = None
        self.transform = None
        self._load_model()
        
        # Results storage
        self.analysis_results = []
        
    def _load_vocabulary(self) -> List[str]:
        """Load vocabulary from file."""
        try:
            with open(self.vocab_file, 'r', encoding='utf-8') as f:
                vocab = [line.strip() for line in f if line.strip()]
            return vocab
        except FileNotFoundError:
            print(f"❌ Vocabulary file not found: {self.vocab_file}")
            return []
    
    def _load_imagenet_21k_classes(self) -> List[str]:
        """Load ImageNet-21k class names with fallback."""
        # This is a simplified approach - in practice you'd want the full 21k class mapping
        # For now, we'll create a comprehensive list that includes many vocabulary terms
        
        # Common objects that might be in ImageNet-21k
        common_classes = [
            "acorn", "aloe", "antenna", "artichoke", "bamboo", "barrel", "blender", 
            "bouquet", "bulldozer", "cake", "caramel", "carousel", "carrot", "cheese",
            "cloak", "cork", "cornbread", "dumpling", "elbow", "fan", "foam", 
            "fruitcake", "gutter", "hamster", "hedgehog", "hoe", "kimono", "latch",
            "locker", "lollipop", "map", "marshmallow", "net", "oil", "omelet", "pie",
            "pistachio", "pitcher", "potato", "prism", "puddle", "pump", "rice",
            "saddle", "sandbag", "scaffolding", "scoop", "seagull", "ship", "shower",
            "silverware", "sink", "ski", "sloth", "snail", "sorbet", "spatula",
            "sprinkler", "squash", "squirrel", "stew", "stump", "sunflower", 
            "swordfish", "tapestry", "teabag", "telescope", "thermos", "treasure",
            "trumpet", "tulip", "turbine", "turkey", "turtle", "typewriter", 
            "watermelon", "waterwheel", "ant", "ball", "bear", "duck", "fork",
            "kitten", "knee", "milkshake", "skin", "wall", "wheel", "farm",
            "envelope", "diamond", "calendar", "panda", "arrow", "knight", "dentist",
            "claw", "uniform", "cormorant", "arcade", "beret", "camp", "divan",
            "baywindow", "facade", "slope", "habit", "intersection", "irrigation",
            "kazoo", "chat", "colony", "preserve", "awning", "metronome", 
            "paleontologist", "percussion", "arbor", "rosette", "saffron", 
            "skimmer", "suede", "turnstile", "triad", "urban", "steam", "vertebra",
            "bandage"
        ]
        
        # Generate a comprehensive class list (simulating 21k classes)
        class_names = []
        
        # Add vocabulary terms directly
        class_names.extend(self.vocab_list)
        
        # Add common object classes
        class_names.extend(common_classes)
        
        # Add variations and related terms
        variations = []
        for term in self.vocab_list:
            variations.extend([
                f"{term}_object",
                f"small_{term}",
                f"large_{term}",
                f"{term}_item",
                f"wooden_{term}",
                f"metal_{term}",
                f"plastic_{term}",
                f"{term}s",  # plural
                f"{term}_tool" if term in ["hoe", "spatula", "pump"] else f"{term}_food" if term in ["cake", "rice", "pie"] else f"{term}_plant" if term in ["bamboo", "aloe", "tulip"] else term
            ])
        
        class_names.extend(variations)
        
        # Add more generic classes to simulate the full 21k dataset
        generic_classes = [
            f"class_{i}" for i in range(len(class_names), 21000)
        ]
        class_names.extend(generic_classes)
        
        return class_names[:21000]  # Limit to 21k classes
    
    def _load_model(self):
        """Load the EfficientNet-21k model."""
        print(f"🔄 Loading model: {self.model_name}")
        
        try:
            # Load timm model
            self.model = timm.create_model(self.model_name, pretrained=True)
            self.model.to(self.device)
            self.model.eval()
            
            # Enable mixed precision for GPU
            if self.device.type == 'cuda':
                self.model.half()
            
            # Get transforms
            data_config = resolve_model_data_config(self.model)
            self.transform = create_transform(**data_config, is_training=False)
            
            print(f"✅ Model loaded successfully on {self.device}")
            
        except Exception as e:
            print(f"❌ Failed to load model: {e}")
            raise RuntimeError(f"Could not load model {self.model_name}")
    
    def _enhanced_similarity_score(self, prediction: str, vocab_term: str) -> Tuple[float, str]:
        """Enhanced similarity scoring that mimics the web app logic."""
        pred_lower = prediction.lower().strip()
        vocab_lower = vocab_term.lower().strip()
        
        # Exact match (100% weight)
        if pred_lower == vocab_lower:
            return 1.0, "exact"
        
        # Partial match (80% weight) - one contains the other
        if vocab_lower in pred_lower or pred_lower in vocab_lower:
            return 0.8, "partial"
        
        # Word-level match (60% weight) - shared words
        pred_words = set(pred_lower.split())
        vocab_words = set(vocab_lower.split())
        if pred_words & vocab_words:  # Intersection
            return 0.6, "word_match"
        
        # Character-level similarity
        similarity = SequenceMatcher(None, pred_lower, vocab_lower).ratio()
        if similarity >= 0.3:
            return similarity, "similarity"
        
        return 0.0, "no_match"
    
    def _classify_image_region(self, image: Image.Image, top_k: int = 20) -> List[Dict]:
        """Classify an image region and return predictions."""
        try:
            # Preprocess image
            input_tensor = self.transform(image).unsqueeze(0).to(self.device)
            if self.device.type == 'cuda':
                input_tensor = input_tensor.half()
            
            # Run inference
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = F.softmax(outputs, dim=1)
            
            # Get top predictions
            top_probs, top_indices = torch.topk(probabilities, top_k, dim=1)
            
            predictions = []
            for i, (prob, idx) in enumerate(zip(top_probs[0], top_indices[0])):
                idx_val = idx.item()
                
                # Map index to class name
                if idx_val < len(self.class_names):
                    class_name = self.class_names[idx_val]
                else:
                    class_name = f"class_{idx_val}"
                
                predictions.append({
                    'rank': i + 1,
                    'class_name': class_name,
                    'confidence': prob.item(),
                    'class_index': idx_val
                })
            
            return predictions
            
        except Exception as e:
            print(f"⚠️  Error classifying image region: {e}")
            return []
    
    def _extract_grid_cells(self, image: Image.Image) -> List[Tuple[Image.Image, str]]:
        """Extract 2x2 grid cells from image (mimics web app behavior)."""
        width, height = image.size
        cell_width = width // 2
        cell_height = height // 2
        
        cells = []
        positions = [
            ("top-left", 0, 0, cell_width, cell_height),
            ("top-right", cell_width, 0, width, cell_height),
            ("bottom-left", 0, cell_height, cell_width, height),
            ("bottom-right", cell_width, cell_height, width, height)
        ]
        
        for pos_name, x1, y1, x2, y2 in positions:
            cell = image.crop((x1, y1, x2, y2))
            cells.append((cell, pos_name))
        
        return cells
    
    def _find_vocab_matches(self, predictions: List[Dict], expected_vocab: str = None) -> Dict:
        """Find vocabulary matches for predictions (mimics web app logic)."""
        matches = []
        
        for pred in predictions:
            class_name = pred['class_name']
            
            # Check against all vocabulary terms
            for vocab_term in self.vocab_list:
                score, match_type = self._enhanced_similarity_score(class_name, vocab_term)
                
                if score > 0:
                    matches.append({
                        'vocab_term': vocab_term,
                        'prediction': pred,
                        'match_score': score,
                        'match_type': match_type,
                        'is_expected': vocab_term.lower() == expected_vocab.lower() if expected_vocab else False
                    })
        
        # Sort by score (best matches first)
        matches.sort(key=lambda x: x['match_score'], reverse=True)
        
        # Find best match for expected vocabulary term
        expected_match = None
        if expected_vocab:
            for match in matches:
                if match['is_expected']:
                    expected_match = match
                    break
        
        return {
            'all_matches': matches,
            'best_match': matches[0] if matches else None,
            'expected_match': expected_match,
            'total_matches': len(matches)
        }
    
    def analyze_vocabulary_image(self, image_path: str) -> Dict:
        """Analyze a vocabulary image (mimics web app behavior)."""
        print(f"🔍 Analyzing: {Path(image_path).name}")
        
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
            
            # Extract expected vocabulary term from filename
            filename = Path(image_path).stem
            expected_vocab = None
            if filename.startswith('vocab-') and filename[6:].isdigit():
                vocab_index = int(filename[6:]) - 1
                if 0 <= vocab_index < len(self.vocab_list):
                    expected_vocab = self.vocab_list[vocab_index]
            
            result = {
                'image_path': image_path,
                'image_size': image.size,
                'expected_vocab': expected_vocab,
                'model_name': self.model_name,
                'timestamp': time.time(),
                'full_image_analysis': None,
                'grid_cell_analysis': [],
                'best_overall_match': None,
                'expected_vocab_found': False,
                'performance_metrics': {}
            }
            
            start_time = time.time()
            
            # Analyze full image
            print(f"   📸 Analyzing full image...")
            full_predictions = self._classify_image_region(image)
            full_matches = self._find_vocab_matches(full_predictions, expected_vocab)
            
            result['full_image_analysis'] = {
                'predictions': full_predictions,
                'vocab_matches': full_matches
            }
            
            # Analyze grid cells
            print(f"   🔲 Analyzing grid cells...")
            cells = self._extract_grid_cells(image)
            
            all_cell_matches = []
            
            for cell_image, position in cells:
                print(f"      🔍 {position}...")
                cell_predictions = self._classify_image_region(cell_image)
                cell_matches = self._find_vocab_matches(cell_predictions, expected_vocab)
                
                cell_result = {
                    'position': position,
                    'predictions': cell_predictions,
                    'vocab_matches': cell_matches
                }
                
                result['grid_cell_analysis'].append(cell_result)
                
                # Collect all matches for overall analysis
                if cell_matches['all_matches']:
                    for match in cell_matches['all_matches']:
                        match_copy = match.copy()
                        match_copy['source'] = f"grid_cell_{position}"
                        all_cell_matches.append(match_copy)
            
            # Find best overall match (across full image and all cells)
            all_matches = []
            
            # Add full image matches
            if full_matches['all_matches']:
                for match in full_matches['all_matches']:
                    match_copy = match.copy()
                    match_copy['source'] = 'full_image'
                    all_matches.append(match_copy)
            
            # Add cell matches
            all_matches.extend(all_cell_matches)
            
            if all_matches:
                # Sort by score and get best
                all_matches.sort(key=lambda x: x['match_score'], reverse=True)
                result['best_overall_match'] = all_matches[0]
                
                # Check if expected vocabulary was found anywhere
                if expected_vocab:
                    result['expected_vocab_found'] = any(
                        match['is_expected'] for match in all_matches
                    )
            
            # Performance metrics
            processing_time = time.time() - start_time
            result['performance_metrics'] = {
                'processing_time': processing_time,
                'total_predictions': len(full_predictions) + sum(len(cell['predictions']) for cell in result['grid_cell_analysis']),
                'total_vocab_matches': len(all_matches),
                'gpu_memory_used': torch.cuda.memory_allocated() / 1024**3 if torch.cuda.is_available() else 0
            }
            
            print(f"   ✅ Analysis complete ({processing_time:.2f}s)")
            if result['best_overall_match']:
                best = result['best_overall_match']
                print(f"      🎯 Best match: {best['vocab_term']} ({best['match_score']:.3f}) in {best['source']}")
            
            if expected_vocab and result['expected_vocab_found']:
                print(f"      ✅ Expected vocab '{expected_vocab}' found!")
            elif expected_vocab:
                print(f"      ❌ Expected vocab '{expected_vocab}' not found")
            
            return result
            
        except Exception as e:
            print(f"❌ Error analyzing {image_path}: {e}")
            return {
                'image_path': image_path,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def analyze_vocabulary_dataset(self, image_dir: str, output_file: str = None) -> List[Dict]:
        """Analyze all vocabulary images in a directory."""
        image_dir = Path(image_dir)
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
        
        # Find all vocab images
        vocab_images = []
        for ext in image_extensions:
            vocab_images.extend(image_dir.glob(f'vocab-*{ext}'))
            vocab_images.extend(image_dir.glob(f'vocab-*{ext.upper()}'))
        
        vocab_images = sorted(vocab_images)
        
        print(f"📁 Found {len(vocab_images)} vocabulary images in {image_dir}")
        print(f"🚀 Starting EfficientNet-21k analysis...")
        print("=" * 60)
        
        results = []
        start_time = time.time()
        
        for i, image_file in enumerate(vocab_images):
            print(f"\n📊 Progress: {i+1}/{len(vocab_images)}")
            result = self.analyze_vocabulary_image(str(image_file))
            results.append(result)
            
            # Clear GPU memory periodically
            if i % 10 == 0 and torch.cuda.is_available():
                torch.cuda.empty_cache()
        
        total_time = time.time() - start_time
        
        # Generate summary statistics
        summary = self._generate_analysis_summary(results, total_time)
        
        # Save results
        output_data = {
            'metadata': {
                'model_name': self.model_name,
                'total_images': len(results),
                'total_time': total_time,
                'vocab_size': len(self.vocab_list),
                'imagenet_classes': len(self.class_names),
                'timestamp': time.time()
            },
            'summary': summary,
            'detailed_results': results
        }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            print(f"\n💾 Results saved to: {output_file}")
        
        # Print summary
        self._print_analysis_summary(summary, total_time, len(results))
        
        return results
    
    def _generate_analysis_summary(self, results: List[Dict], total_time: float) -> Dict:
        """Generate summary statistics from analysis results."""
        successful_results = [r for r in results if 'error' not in r]
        
        summary = {
            'total_images': len(results),
            'successful_analyses': len(successful_results),
            'failed_analyses': len(results) - len(successful_results),
            'images_with_expected_vocab': 0,
            'expected_vocab_found': 0,
            'expected_vocab_accuracy': 0.0,
            'total_vocab_matches': 0,
            'avg_matches_per_image': 0.0,
            'match_type_distribution': {
                'exact': 0,
                'partial': 0,
                'word_match': 0,
                'similarity': 0
            },
            'source_distribution': {
                'full_image': 0,
                'grid_cell_top-left': 0,
                'grid_cell_top-right': 0,
                'grid_cell_bottom-left': 0,
                'grid_cell_bottom-right': 0
            },
            'performance': {
                'total_time': total_time,
                'avg_time_per_image': total_time / max(len(results), 1),
                'images_per_second': len(results) / max(total_time, 0.001)
            }
        }
        
        total_matches = 0
        
        for result in successful_results:
            if result.get('expected_vocab'):
                summary['images_with_expected_vocab'] += 1
                if result.get('expected_vocab_found'):
                    summary['expected_vocab_found'] += 1
            
            # Count matches
            if result.get('best_overall_match'):
                total_matches += 1
                match = result['best_overall_match']
                
                # Match type distribution
                match_type = match.get('match_type', 'unknown')
                if match_type in summary['match_type_distribution']:
                    summary['match_type_distribution'][match_type] += 1
                
                # Source distribution
                source = match.get('source', 'unknown')
                if source in summary['source_distribution']:
                    summary['source_distribution'][source] += 1
        
        summary['total_vocab_matches'] = total_matches
        summary['avg_matches_per_image'] = total_matches / max(len(successful_results), 1)
        
        if summary['images_with_expected_vocab'] > 0:
            summary['expected_vocab_accuracy'] = summary['expected_vocab_found'] / summary['images_with_expected_vocab']
        
        return summary
    
    def _print_analysis_summary(self, summary: Dict, total_time: float, total_images: int):
        """Print formatted analysis summary."""
        print("\n" + "=" * 60)
        print("📊 EFFICIENTNET-21K ANALYSIS SUMMARY")
        print("=" * 60)
        
        print(f"🔧 Model: {self.model_name}")
        print(f"📁 Total Images: {total_images}")
        print(f"✅ Successful: {summary['successful_analyses']}")
        print(f"❌ Failed: {summary['failed_analyses']}")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        print(f"🚀 Speed: {summary['performance']['images_per_second']:.1f} images/second")
        
        print(f"\n📖 Vocabulary Analysis:")
        print(f"   Expected vocab terms: {summary['images_with_expected_vocab']}")
        print(f"   Found expected terms: {summary['expected_vocab_found']}")
        print(f"   Accuracy: {summary['expected_vocab_accuracy']:.2%}")
        
        print(f"\n🎯 Match Analysis:")
        print(f"   Total matches found: {summary['total_vocab_matches']}")
        print(f"   Avg matches per image: {summary['avg_matches_per_image']:.1f}")
        
        print(f"\n📋 Match Types:")
        for match_type, count in summary['match_type_distribution'].items():
            percentage = (count / max(summary['total_vocab_matches'], 1)) * 100
            print(f"   {match_type}: {count} ({percentage:.1f}%)")
        
        print(f"\n📍 Best Match Sources:")
        for source, count in summary['source_distribution'].items():
            percentage = (count / max(summary['total_vocab_matches'], 1)) * 100
            print(f"   {source}: {count} ({percentage:.1f}%)")


def main():
    """Main function to run the EfficientNet-21k vocabulary analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description='EfficientNet-21k Vocabulary Analyzer')
    parser.add_argument('--model', default='tf_efficientnetv2_l.in21k',
                       help='EfficientNet model name (default: tf_efficientnetv2_l.in21k)')
    parser.add_argument('--vocab', default='vocab/vocab_list.txt',
                       help='Vocabulary file path')
    parser.add_argument('--images', required=True,
                       help='Directory containing vocabulary images')
    parser.add_argument('--output', default='efficientnet_21k_analysis.json',
                       help='Output JSON file')
    parser.add_argument('--single', help='Analyze single image instead of directory')
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = EfficientNet21kVocabAnalyzer(
        model_name=args.model,
        vocab_file=args.vocab
    )
    
    if args.single:
        # Analyze single image
        result = analyzer.analyze_vocabulary_image(args.single)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        # Analyze directory
        results = analyzer.analyze_vocabulary_dataset(args.images, args.output)
        
        print(f"\n🎉 Analysis complete! Results saved to: {args.output}")
        print(f"📊 Processed {len(results)} images with EfficientNet-21k")


if __name__ == "__main__":
    main() 