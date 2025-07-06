#!/usr/bin/env python3
"""
Advanced EfficientNet Vocabulary Classifier with ImageNet-21k Support

This script provides enhanced vocabulary classification using various EfficientNet models
including ImageNet-21k pretrained models with better class name resolution.
"""

import os
import json
import argparse
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import requests
from PIL import Image
import torch
import numpy as np
from transformers import EfficientNetImageProcessor, EfficientNetForImageClassification
import timm
from timm.data import resolve_model_data_config, create_transform
from difflib import SequenceMatcher
import urllib.request

class ImageNetClassNames:
    """Handle ImageNet class name resolution for different model types."""
    
    def __init__(self):
        self.imagenet_1k_classes = None
        self.imagenet_21k_classes = None
        
    def load_imagenet_1k_classes(self):
        """Load ImageNet-1k class names."""
        if self.imagenet_1k_classes is not None:
            return self.imagenet_1k_classes
            
        # Try to load from multiple sources
        urls = [
            "https://raw.githubusercontent.com/pytorch/hub/master/imagenet_classes.txt",
            "https://gist.githubusercontent.com/yrevar/942d3a0ac09ec9e5eb3a/raw/238f720ff059c1f82f368259d1ca4ffa5dd8f9f5/imagenet1000_clsidx_to_labels.txt"
        ]
        
        for url in urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    lines = response.text.strip().split('\n')
                    if len(lines) >= 1000:
                        self.imagenet_1k_classes = [line.strip() for line in lines]
                        return self.imagenet_1k_classes
            except:
                continue
        
        # Fallback to basic class names
        self.imagenet_1k_classes = [f"class_{i}" for i in range(1000)]
        return self.imagenet_1k_classes
    
    def load_imagenet_21k_classes(self):
        """Load ImageNet-21k class names."""
        if self.imagenet_21k_classes is not None:
            return self.imagenet_21k_classes
            
        # For ImageNet-21k, we'll use a more comprehensive approach
        # This is a simplified version - in practice, you'd want the full 21k class list
        try:
            # Try to load from timm or other sources
            # For now, we'll use a fallback approach
            self.imagenet_21k_classes = [f"class_21k_{i}" for i in range(21841)]
            return self.imagenet_21k_classes
        except:
            self.imagenet_21k_classes = [f"class_21k_{i}" for i in range(21841)]
            return self.imagenet_21k_classes
    
    def get_class_name(self, class_idx: int, model_type: str = "1k") -> str:
        """Get class name for given index and model type."""
        if model_type == "21k":
            classes = self.load_imagenet_21k_classes()
            if 0 <= class_idx < len(classes):
                return classes[class_idx]
        else:
            classes = self.load_imagenet_1k_classes()
            if 0 <= class_idx < len(classes):
                return classes[class_idx]
        
        return f"class_{class_idx}"


class AdvancedVocabularyClassifier:
    """Advanced vocabulary classifier with support for multiple EfficientNet variants."""
    
    RECOMMENDED_MODELS = {
        'efficientnet-b0': 'google/efficientnet-b0',
        'efficientnet-b3': 'google/efficientnet-b3', 
        'efficientnet-b7': 'google/efficientnet-b7',
        'efficientnetv2-l-21k': 'timm/tf_efficientnetv2_l.in21k',
        'efficientnetv2-xl-21k': 'timm/tf_efficientnetv2_xl.in21k',
        'efficientnet-b0-timm': 'tf_efficientnet_b0',
        'efficientnet-b7-timm': 'tf_efficientnet_b7',
    }
    
    def __init__(self, model_name: str = "google/efficientnet-b7", vocab_file: str = "vocab/vocab_list.txt"):
        """Initialize the advanced vocabulary classifier."""
        self.model_name = model_name
        self.vocab_file = vocab_file
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Initialize class name resolver
        self.class_names = ImageNetClassNames()
        
        # Load vocabulary
        self.vocab_list = self._load_vocabulary()
        print(f"Loaded {len(self.vocab_list)} vocabulary terms")
        
        # Initialize model
        self.model = None
        self.processor = None
        self.is_timm_model = False
        self.is_21k_model = False
        self._load_model()
        
    def _load_vocabulary(self) -> List[str]:
        """Load vocabulary from file."""
        try:
            with open(self.vocab_file, 'r', encoding='utf-8') as f:
                vocab = [line.strip() for line in f if line.strip()]
            return vocab
        except FileNotFoundError:
            print(f"Vocabulary file not found: {self.vocab_file}")
            return []
    
    def _load_model(self):
        """Load the EfficientNet model with enhanced support."""
        print(f"Loading model: {self.model_name}")
        
        # Check if it's a 21k model
        self.is_21k_model = '21k' in self.model_name.lower() or 'in21k' in self.model_name.lower()
        
        try:
            # Try Hugging Face transformers first
            if self.model_name.startswith('google/') or self.model_name.startswith('efficientnet'):
                self.processor = EfficientNetImageProcessor.from_pretrained(self.model_name)
                self.model = EfficientNetForImageClassification.from_pretrained(self.model_name)
                self.model.to(self.device)
                self.model.eval()
                print(f"Loaded Hugging Face model: {self.model_name}")
            else:
                raise ValueError("Trying timm model")
                
        except Exception as e:
            print(f"Trying timm model: {self.model_name}")
            
            try:
                # Try timm models
                self.model = timm.create_model(self.model_name, pretrained=True)
                self.model.to(self.device)
                self.model.eval()
                
                # Get model-specific transforms
                data_config = resolve_model_data_config(self.model)
                self.processor = create_transform(**data_config, is_training=False)
                self.is_timm_model = True
                print(f"Loaded timm model: {self.model_name}")
                
            except Exception as e2:
                print(f"Failed to load model: {e2}")
                raise RuntimeError(f"Could not load model {self.model_name}")
    
    def _enhanced_similarity_score(self, text1: str, text2: str) -> float:
        """Enhanced similarity calculation with multiple methods."""
        text1_lower = text1.lower()
        text2_lower = text2.lower()
        
        # Exact match
        if text1_lower == text2_lower:
            return 1.0
        
        # Substring match
        if text1_lower in text2_lower or text2_lower in text1_lower:
            return 0.8
        
        # Word-level match
        words1 = set(text1_lower.split())
        words2 = set(text2_lower.split())
        if words1 & words2:  # Intersection
            return 0.6
        
        # Character-level similarity
        return SequenceMatcher(None, text1_lower, text2_lower).ratio()
    
    def _find_vocab_matches(self, predictions: List[Dict], threshold: float = 0.3) -> List[Dict]:
        """Find vocabulary matches with enhanced matching."""
        matches = []
        
        for pred in predictions:
            class_name = pred['class_name'].lower()
            best_match = None
            best_score = 0
            
            for vocab_term in self.vocab_list:
                score = self._enhanced_similarity_score(class_name, vocab_term)
                
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = vocab_term
            
            if best_match:
                match_type = 'exact' if best_score == 1.0 else 'partial' if best_score >= 0.8 else 'similarity'
                matches.append({
                    'prediction': pred,
                    'vocab_term': best_match,
                    'match_score': best_score,
                    'match_type': match_type
                })
        
        return sorted(matches, key=lambda x: x['match_score'], reverse=True)
    
    def _classify_image(self, image: Image.Image, top_k: int = 20) -> List[Dict]:
        """Classify image with enhanced class name resolution."""
        if self.is_timm_model:
            # timm model processing
            if isinstance(self.processor, torch.nn.Module):
                # Handle transform callable
                input_tensor = self.processor(image).unsqueeze(0).to(self.device)
            else:
                # Handle other processor types
                input_tensor = self.processor(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                
            # Get top predictions
            top_probs, top_indices = torch.topk(probabilities, top_k)
            
            predictions = []
            for i, (prob, idx) in enumerate(zip(top_probs[0], top_indices[0])):
                idx_val = idx.item()
                
                # Get class name based on model type
                if self.is_21k_model:
                    class_name = self.class_names.get_class_name(idx_val, "21k")
                else:
                    class_name = self.class_names.get_class_name(idx_val, "1k")
                
                predictions.append({
                    'class_name': class_name,
                    'confidence': prob.item(),
                    'rank': i + 1,
                    'class_index': idx_val
                })
                
        else:
            # Hugging Face transformers processing
            inputs = self.processor(image, return_tensors="pt").to(self.device)
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.nn.functional.softmax(outputs.logits, dim=1)
            
            # Get top predictions
            top_probs, top_indices = torch.topk(probabilities, top_k)
            
            predictions = []
            for i, (prob, idx) in enumerate(zip(top_probs[0], top_indices[0])):
                idx_val = idx.item()
                class_name = self.model.config.id2label.get(idx_val, f"class_{idx_val}")
                
                predictions.append({
                    'class_name': class_name,
                    'confidence': prob.item(),
                    'rank': i + 1,
                    'class_index': idx_val
                })
        
        return predictions
    
    def _extract_grid_cells(self, image: Image.Image) -> List[Image.Image]:
        """Extract 2x2 grid cells from image."""
        width, height = image.size
        cell_width = width // 2
        cell_height = height // 2
        
        cells = []
        positions = [
            (0, 0, cell_width, cell_height),  # top-left
            (cell_width, 0, width, cell_height),  # top-right
            (0, cell_height, cell_width, height),  # bottom-left
            (cell_width, cell_height, width, height)  # bottom-right
        ]
        
        for pos in positions:
            cell = image.crop(pos)
            cells.append(cell)
        
        return cells
    
    def classify_image(self, image_path: str, analyze_grid: bool = False, top_k: int = 20) -> Dict:
        """Classify image with comprehensive analysis."""
        try:
            # Load image
            if image_path.startswith('http'):
                image = Image.open(requests.get(image_path, stream=True).raw).convert('RGB')
            else:
                image = Image.open(image_path).convert('RGB')
            
            results = {
                'image_path': image_path,
                'image_size': image.size,
                'model_name': self.model_name,
                'model_type': '21k' if self.is_21k_model else '1k',
                'full_image': None,
                'grid_cells': None,
                'vocab_matches': None,
                'best_match': None,
                'expected_vocab': None
            }
            
            # Extract expected vocab term from filename
            filename = Path(image_path).stem
            if filename.startswith('vocab-') and filename[6:].isdigit():
                vocab_index = int(filename[6:]) - 1
                if 0 <= vocab_index < len(self.vocab_list):
                    results['expected_vocab'] = self.vocab_list[vocab_index]
            
            # Classify full image
            predictions = self._classify_image(image, top_k)
            vocab_matches = self._find_vocab_matches(predictions)
            
            results['full_image'] = {
                'predictions': predictions,
                'vocab_matches': vocab_matches
            }
            
            # Grid cell analysis
            if analyze_grid:
                cells = self._extract_grid_cells(image)
                cell_results = []
                
                for i, cell in enumerate(cells):
                    cell_predictions = self._classify_image(cell, top_k)
                    cell_vocab_matches = self._find_vocab_matches(cell_predictions)
                    
                    cell_results.append({
                        'position': ['top-left', 'top-right', 'bottom-left', 'bottom-right'][i],
                        'predictions': cell_predictions,
                        'vocab_matches': cell_vocab_matches
                    })
                
                results['grid_cells'] = cell_results
                
                # Find best overall match across all cells
                all_matches = []
                
                # Add full image matches
                for match in vocab_matches:
                    all_matches.append({
                        'position': 'full-image',
                        'match': match
                    })
                
                # Add cell matches
                for cell_result in cell_results:
                    for match in cell_result['vocab_matches']:
                        all_matches.append({
                            'position': cell_result['position'],
                            'match': match
                        })
                
                if all_matches:
                    best_match = max(all_matches, key=lambda x: x['match']['match_score'])
                    results['best_match'] = best_match
            
            return results
            
        except Exception as e:
            return {
                'image_path': image_path,
                'error': str(e)
            }
    
    def batch_classify(self, image_dir: str, output_file: str = None, analyze_grid: bool = False) -> List[Dict]:
        """Batch classify images with progress tracking."""
        image_dir = Path(image_dir)
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
        
        image_files = []
        for ext in image_extensions:
            image_files.extend(image_dir.glob(f'*{ext}'))
            image_files.extend(image_dir.glob(f'*{ext.upper()}'))
        
        print(f"Found {len(image_files)} images in {image_dir}")
        
        results = []
        for i, image_file in enumerate(sorted(image_files)):
            print(f"Processing {i+1}/{len(image_files)}: {image_file.name}")
            result = self.classify_image(str(image_file), analyze_grid=analyze_grid)
            results.append(result)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"Results saved to {output_file}")
        
        return results
    
    def generate_performance_report(self, results: List[Dict]) -> Dict:
        """Generate comprehensive performance report."""
        report = {
            'model_info': {
                'model_name': self.model_name,
                'model_type': '21k' if self.is_21k_model else '1k',
                'vocab_size': len(self.vocab_list)
            },
            'overall_stats': {
                'total_images': len(results),
                'successful_classifications': 0,
                'failed_classifications': 0,
                'images_with_expected_vocab': 0,
                'exact_matches': 0,
                'partial_matches': 0,
                'similarity_matches': 0,
                'no_matches': 0
            },
            'accuracy_metrics': {
                'overall_accuracy': 0.0,
                'exact_match_rate': 0.0,
                'partial_match_rate': 0.0,
                'any_match_rate': 0.0
            },
            'vocab_performance': {},
            'best_matches': [],
            'worst_matches': []
        }
        
        vocab_stats = {}
        
        for result in results:
            if 'error' in result:
                report['overall_stats']['failed_classifications'] += 1
                continue
            
            report['overall_stats']['successful_classifications'] += 1
            expected_vocab = result.get('expected_vocab')
            
            if expected_vocab:
                report['overall_stats']['images_with_expected_vocab'] += 1
                
                if expected_vocab not in vocab_stats:
                    vocab_stats[expected_vocab] = {
                        'total': 0,
                        'exact_matches': 0,
                        'partial_matches': 0,
                        'similarity_matches': 0,
                        'no_matches': 0,
                        'best_scores': []
                    }
                
                vocab_stats[expected_vocab]['total'] += 1
                
                # Find best match for this expected vocab
                best_score = 0
                best_match_type = 'none'
                
                # Check all matches (full image + grid cells)
                all_matches = []
                
                if result.get('full_image', {}).get('vocab_matches'):
                    all_matches.extend(result['full_image']['vocab_matches'])
                
                if result.get('grid_cells'):
                    for cell in result['grid_cells']:
                        all_matches.extend(cell.get('vocab_matches', []))
                
                for match in all_matches:
                    if match['vocab_term'].lower() == expected_vocab.lower():
                        score = match['match_score']
                        if score > best_score:
                            best_score = score
                            best_match_type = match['match_type']
                
                vocab_stats[expected_vocab]['best_scores'].append(best_score)
                
                if best_score > 0:
                    if best_match_type == 'exact':
                        vocab_stats[expected_vocab]['exact_matches'] += 1
                        report['overall_stats']['exact_matches'] += 1
                    elif best_match_type == 'partial':
                        vocab_stats[expected_vocab]['partial_matches'] += 1
                        report['overall_stats']['partial_matches'] += 1
                    else:
                        vocab_stats[expected_vocab]['similarity_matches'] += 1
                        report['overall_stats']['similarity_matches'] += 1
                else:
                    vocab_stats[expected_vocab]['no_matches'] += 1
                    report['overall_stats']['no_matches'] += 1
        
        # Calculate accuracy metrics
        total_with_expected = report['overall_stats']['images_with_expected_vocab']
        if total_with_expected > 0:
            exact = report['overall_stats']['exact_matches']
            partial = report['overall_stats']['partial_matches']
            similarity = report['overall_stats']['similarity_matches']
            
            report['accuracy_metrics']['exact_match_rate'] = exact / total_with_expected
            report['accuracy_metrics']['partial_match_rate'] = partial / total_with_expected
            report['accuracy_metrics']['any_match_rate'] = (exact + partial + similarity) / total_with_expected
            report['accuracy_metrics']['overall_accuracy'] = (exact + partial) / total_with_expected
        
        # Process vocab performance
        for vocab_term, stats in vocab_stats.items():
            if stats['total'] > 0:
                accuracy = (stats['exact_matches'] + stats['partial_matches']) / stats['total']
                avg_score = sum(stats['best_scores']) / len(stats['best_scores']) if stats['best_scores'] else 0
                
                report['vocab_performance'][vocab_term] = {
                    'total_images': stats['total'],
                    'accuracy': accuracy,
                    'average_score': avg_score,
                    'exact_matches': stats['exact_matches'],
                    'partial_matches': stats['partial_matches'],
                    'similarity_matches': stats['similarity_matches'],
                    'no_matches': stats['no_matches']
                }
        
        # Find best and worst performing vocab terms
        vocab_performance_list = [(term, perf) for term, perf in report['vocab_performance'].items()]
        vocab_performance_list.sort(key=lambda x: x[1]['accuracy'], reverse=True)
        
        report['best_matches'] = vocab_performance_list[:10]
        report['worst_matches'] = vocab_performance_list[-10:]
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Advanced EfficientNet Vocabulary Classifier')
    parser.add_argument('--model', default='google/efficientnet-b7', 
                       help='Model name (HuggingFace or timm)')
    parser.add_argument('--list-models', action='store_true',
                       help='List recommended models')
    parser.add_argument('--vocab', default='vocab/vocab_list.txt',
                       help='Vocabulary file path')
    parser.add_argument('--image', help='Single image to classify')
    parser.add_argument('--batch', help='Directory of images to classify')
    parser.add_argument('--output', help='Output JSON file for results')
    parser.add_argument('--grid', action='store_true',
                       help='Analyze 2x2 grid cells')
    parser.add_argument('--top-k', type=int, default=20,
                       help='Number of top predictions to return')
    parser.add_argument('--report', action='store_true',
                       help='Generate performance report')
    
    args = parser.parse_args()
    
    if args.list_models:
        print("Recommended models:")
        for name, model_id in AdvancedVocabularyClassifier.RECOMMENDED_MODELS.items():
            print(f"  {name}: {model_id}")
        return
    
    # Initialize classifier
    classifier = AdvancedVocabularyClassifier(model_name=args.model, vocab_file=args.vocab)
    
    if args.image:
        # Single image classification
        result = classifier.classify_image(args.image, analyze_grid=args.grid, top_k=args.top_k)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.batch:
        # Batch classification
        results = classifier.batch_classify(args.batch, args.output, analyze_grid=args.grid)
        
        if args.report:
            report = classifier.generate_performance_report(results)
            
            print("\n" + "="*50)
            print("PERFORMANCE REPORT")
            print("="*50)
            print(f"Model: {report['model_info']['model_name']}")
            print(f"Model Type: {report['model_info']['model_type']}")
            print(f"Vocabulary Size: {report['model_info']['vocab_size']}")
            print()
            
            stats = report['overall_stats']
            print(f"Total Images: {stats['total_images']}")
            print(f"Successful Classifications: {stats['successful_classifications']}")
            print(f"Images with Expected Vocab: {stats['images_with_expected_vocab']}")
            print()
            
            metrics = report['accuracy_metrics']
            print(f"Overall Accuracy: {metrics['overall_accuracy']:.2%}")
            print(f"Exact Match Rate: {metrics['exact_match_rate']:.2%}")
            print(f"Any Match Rate: {metrics['any_match_rate']:.2%}")
            print()
            
            print("Top 10 Best Performing Vocab Terms:")
            for i, (term, perf) in enumerate(report['best_matches'][:10]):
                print(f"  {i+1:2d}. {term}: {perf['accuracy']:.2%} ({perf['exact_matches']+perf['partial_matches']}/{perf['total_images']})")
            
            print("\nTop 10 Worst Performing Vocab Terms:")
            for i, (term, perf) in enumerate(report['worst_matches'][:10]):
                print(f"  {i+1:2d}. {term}: {perf['accuracy']:.2%} ({perf['exact_matches']+perf['partial_matches']}/{perf['total_images']})")
            
            # Save detailed report
            if args.output:
                report_file = args.output.replace('.json', '_report.json')
                with open(report_file, 'w', encoding='utf-8') as f:
                    json.dump(report, f, indent=2, ensure_ascii=False)
                print(f"\nDetailed report saved to: {report_file}")
    
    else:
        print("Please specify either --image or --batch")
        parser.print_help()


if __name__ == "__main__":
    main() 