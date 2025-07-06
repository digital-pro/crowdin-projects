#!/usr/bin/env python3
"""
EfficientNet Vocabulary Classifier using Hugging Face Transformers

This script uses EfficientNet models to classify images against a vocabulary list,
with support for grid cell analysis similar to the web application.
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

class VocabularyClassifier:
    def __init__(self, model_name: str = "google/efficientnet-b7", vocab_file: str = "vocab/vocab_list.txt"):
        """
        Initialize the vocabulary classifier.
        
        Args:
            model_name: Hugging Face model name or timm model name
            vocab_file: Path to vocabulary list file
        """
        self.model_name = model_name
        self.vocab_file = vocab_file
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        # Load vocabulary
        self.vocab_list = self._load_vocabulary()
        print(f"Loaded {len(self.vocab_list)} vocabulary terms")
        
        # Initialize model
        self.model = None
        self.processor = None
        self.is_timm_model = False
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
        """Load the EfficientNet model."""
        print(f"Loading model: {self.model_name}")
        
        try:
            # Try Hugging Face transformers first
            if "efficientnet" in self.model_name.lower():
                self.processor = EfficientNetImageProcessor.from_pretrained(self.model_name)
                self.model = EfficientNetForImageClassification.from_pretrained(self.model_name)
                self.model.to(self.device)
                self.model.eval()
                print(f"Loaded Hugging Face model: {self.model_name}")
            else:
                raise ValueError("Not a standard HF EfficientNet model")
                
        except Exception as e:
            print(f"Failed to load HF model: {e}")
            print("Trying timm model...")
            
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
                print(f"Failed to load timm model: {e2}")
                raise RuntimeError(f"Could not load model {self.model_name}")
    
    def _similarity_score(self, text1: str, text2: str) -> float:
        """Calculate similarity between two strings."""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _find_vocab_matches(self, predictions: List[Dict], threshold: float = 0.3) -> List[Dict]:
        """Find vocabulary matches in predictions."""
        matches = []
        
        for pred in predictions:
            class_name = pred['class_name'].lower()
            best_match = None
            best_score = 0
            
            for vocab_term in self.vocab_list:
                vocab_lower = vocab_term.lower()
                
                # Exact match
                if vocab_lower == class_name:
                    score = 1.0
                # Partial match (vocab term in class name or vice versa)
                elif vocab_lower in class_name or class_name in vocab_lower:
                    score = 0.8
                # Word-level match
                elif any(word in class_name.split() for word in vocab_lower.split()) or \
                     any(word in vocab_lower.split() for word in class_name.split()):
                    score = 0.6
                # Similarity match
                else:
                    score = self._similarity_score(class_name, vocab_lower)
                
                if score > best_score and score >= threshold:
                    best_score = score
                    best_match = vocab_term
            
            if best_match:
                matches.append({
                    'prediction': pred,
                    'vocab_term': best_match,
                    'match_score': best_score,
                    'match_type': 'exact' if best_score == 1.0 else 'partial' if best_score >= 0.8 else 'similarity'
                })
        
        return matches
    
    def _classify_image(self, image: Image.Image, top_k: int = 10) -> List[Dict]:
        """Classify a single image."""
        if self.is_timm_model:
            # timm model processing
            input_tensor = self.processor(image).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = torch.nn.functional.softmax(outputs, dim=1)
                
            # Get top predictions
            top_probs, top_indices = torch.topk(probabilities, top_k)
            
            # For timm models, we need to get class names from ImageNet
            predictions = []
            for i, (prob, idx) in enumerate(zip(top_probs[0], top_indices[0])):
                predictions.append({
                    'class_name': f"imagenet_class_{idx.item()}",  # timm doesn't include class names by default
                    'confidence': prob.item(),
                    'rank': i + 1
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
                class_name = self.model.config.id2label.get(idx.item(), f"class_{idx.item()}")
                predictions.append({
                    'class_name': class_name,
                    'confidence': prob.item(),
                    'rank': i + 1
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
    
    def classify_image(self, image_path: str, analyze_grid: bool = False, top_k: int = 10) -> Dict:
        """
        Classify an image and optionally analyze grid cells.
        
        Args:
            image_path: Path to image file
            analyze_grid: Whether to analyze 2x2 grid cells
            top_k: Number of top predictions to return
            
        Returns:
            Dictionary with classification results
        """
        try:
            # Load image
            if image_path.startswith('http'):
                image = Image.open(requests.get(image_path, stream=True).raw).convert('RGB')
            else:
                image = Image.open(image_path).convert('RGB')
            
            results = {
                'image_path': image_path,
                'image_size': image.size,
                'full_image': None,
                'grid_cells': None,
                'vocab_matches': None,
                'best_match': None
            }
            
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
                
                # Find best overall match
                all_matches = []
                for cell_result in cell_results:
                    for match in cell_result['vocab_matches']:
                        all_matches.append({
                            'position': cell_result['position'],
                            'match': match
                        })
                
                if all_matches:
                    best_match = max(all_matches, key=lambda x: x['match']['match_score'])
                    results['best_match'] = best_match
            
            # Extract expected vocab term from filename if applicable
            filename = Path(image_path).stem
            if filename.startswith('vocab-') and filename[6:].isdigit():
                vocab_index = int(filename[6:]) - 1  # Convert to 0-based index
                if 0 <= vocab_index < len(self.vocab_list):
                    results['expected_vocab'] = self.vocab_list[vocab_index]
            
            return results
            
        except Exception as e:
            return {
                'image_path': image_path,
                'error': str(e)
            }
    
    def batch_classify(self, image_dir: str, output_file: str = None, analyze_grid: bool = False) -> List[Dict]:
        """
        Classify all images in a directory.
        
        Args:
            image_dir: Directory containing images
            output_file: Optional output JSON file
            analyze_grid: Whether to analyze grid cells
            
        Returns:
            List of classification results
        """
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
    
    def analyze_vocab_performance(self, results: List[Dict]) -> Dict:
        """Analyze vocabulary classification performance."""
        stats = {
            'total_images': len(results),
            'images_with_expected_vocab': 0,
            'correct_matches': 0,
            'partial_matches': 0,
            'no_matches': 0,
            'accuracy': 0.0,
            'vocab_term_performance': {}
        }
        
        for result in results:
            if 'error' in result:
                continue
                
            expected_vocab = result.get('expected_vocab')
            if expected_vocab:
                stats['images_with_expected_vocab'] += 1
                
                # Check if expected vocab was found
                found_match = False
                best_score = 0
                
                # Check full image matches
                if result.get('full_image', {}).get('vocab_matches'):
                    for match in result['full_image']['vocab_matches']:
                        if match['vocab_term'].lower() == expected_vocab.lower():
                            found_match = True
                            best_score = max(best_score, match['match_score'])
                
                # Check grid cell matches
                if result.get('grid_cells'):
                    for cell in result['grid_cells']:
                        for match in cell.get('vocab_matches', []):
                            if match['vocab_term'].lower() == expected_vocab.lower():
                                found_match = True
                                best_score = max(best_score, match['match_score'])
                
                # Update stats
                if found_match:
                    if best_score == 1.0:
                        stats['correct_matches'] += 1
                    else:
                        stats['partial_matches'] += 1
                else:
                    stats['no_matches'] += 1
                
                # Track per-vocab performance
                if expected_vocab not in stats['vocab_term_performance']:
                    stats['vocab_term_performance'][expected_vocab] = {
                        'total': 0,
                        'found': 0,
                        'accuracy': 0.0
                    }
                
                stats['vocab_term_performance'][expected_vocab]['total'] += 1
                if found_match:
                    stats['vocab_term_performance'][expected_vocab]['found'] += 1
        
        # Calculate accuracy
        if stats['images_with_expected_vocab'] > 0:
            stats['accuracy'] = (stats['correct_matches'] + stats['partial_matches']) / stats['images_with_expected_vocab']
        
        # Calculate per-vocab accuracy
        for vocab_term, perf in stats['vocab_term_performance'].items():
            if perf['total'] > 0:
                perf['accuracy'] = perf['found'] / perf['total']
        
        return stats


def main():
    parser = argparse.ArgumentParser(description='EfficientNet Vocabulary Classifier')
    parser.add_argument('--model', default='google/efficientnet-b7', 
                       help='Model name (HuggingFace or timm)')
    parser.add_argument('--vocab', default='vocab/vocab_list.txt',
                       help='Vocabulary file path')
    parser.add_argument('--image', help='Single image to classify')
    parser.add_argument('--batch', help='Directory of images to classify')
    parser.add_argument('--output', help='Output JSON file for results')
    parser.add_argument('--grid', action='store_true',
                       help='Analyze 2x2 grid cells')
    parser.add_argument('--top-k', type=int, default=10,
                       help='Number of top predictions to return')
    parser.add_argument('--analyze-performance', action='store_true',
                       help='Analyze vocabulary classification performance')
    
    args = parser.parse_args()
    
    # Initialize classifier
    classifier = VocabularyClassifier(model_name=args.model, vocab_file=args.vocab)
    
    if args.image:
        # Single image classification
        result = classifier.classify_image(args.image, analyze_grid=args.grid, top_k=args.top_k)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.batch:
        # Batch classification
        results = classifier.batch_classify(args.batch, args.output, analyze_grid=args.grid)
        
        if args.analyze_performance:
            stats = classifier.analyze_vocab_performance(results)
            print("\nVocabulary Performance Analysis:")
            print(f"Total images: {stats['total_images']}")
            print(f"Images with expected vocab: {stats['images_with_expected_vocab']}")
            print(f"Correct matches: {stats['correct_matches']}")
            print(f"Partial matches: {stats['partial_matches']}")
            print(f"No matches: {stats['no_matches']}")
            print(f"Overall accuracy: {stats['accuracy']:.2%}")
            
            # Show worst performing vocab terms
            worst_performers = sorted(
                [(term, perf) for term, perf in stats['vocab_term_performance'].items() if perf['total'] > 0],
                key=lambda x: x[1]['accuracy']
            )[:10]
            
            print("\nWorst performing vocabulary terms:")
            for term, perf in worst_performers:
                print(f"  {term}: {perf['accuracy']:.2%} ({perf['found']}/{perf['total']})")
    
    else:
        print("Please specify either --image or --batch")
        parser.print_help()


if __name__ == "__main__":
    main() 