#!/usr/bin/env python3
"""
GPU-Optimized EfficientNet Vocabulary Classifier

This script is optimized for GPU acceleration with memory management,
batch processing, and performance monitoring.
"""

import os
import json
import argparse
import time
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import requests
from PIL import Image
import torch
import torch.nn.functional as F
import numpy as np
from transformers import EfficientNetImageProcessor, EfficientNetForImageClassification
import timm
from timm.data import resolve_model_data_config, create_transform
from difflib import SequenceMatcher
import gc

class GPUOptimizedVocabularyClassifier:
    """GPU-optimized vocabulary classifier with memory management."""
    
    def __init__(self, model_name: str = "google/efficientnet-b3", vocab_file: str = "vocab/vocab_list.txt"):
        """Initialize the GPU-optimized classifier."""
        self.model_name = model_name
        self.vocab_file = vocab_file
        
        # GPU setup
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        if torch.cuda.is_available():
            print(f"🚀 Using GPU: {torch.cuda.get_device_name(0)}")
            print(f"   GPU Memory: {torch.cuda.get_device_properties(0).total_memory // 1024**3} GB")
            # Enable memory optimization
            torch.backends.cudnn.benchmark = True
            torch.backends.cudnn.enabled = True
        else:
            print("⚠️  GPU not available, using CPU")
        
        # Load vocabulary
        self.vocab_list = self._load_vocabulary()
        print(f"📖 Loaded {len(self.vocab_list)} vocabulary terms")
        
        # Initialize model
        self.model = None
        self.processor = None
        self.is_timm_model = False
        self._load_model()
        
        # Performance tracking
        self.stats = {
            'total_images': 0,
            'total_time': 0.0,
            'gpu_memory_used': 0.0,
            'batch_times': []
        }
    
    def _load_vocabulary(self) -> List[str]:
        """Load vocabulary from file."""
        try:
            with open(self.vocab_file, 'r', encoding='utf-8') as f:
                vocab = [line.strip() for line in f if line.strip()]
            return vocab
        except FileNotFoundError:
            print(f"❌ Vocabulary file not found: {self.vocab_file}")
            return []
    
    def _load_model(self):
        """Load model with GPU optimization."""
        print(f"🔄 Loading model: {self.model_name}")
        
        try:
            # Try HuggingFace transformers first
            if self.model_name.startswith('google/') or 'efficientnet' in self.model_name.lower():
                self.processor = EfficientNetImageProcessor.from_pretrained(self.model_name)
                self.model = EfficientNetForImageClassification.from_pretrained(self.model_name)
                self.model.to(self.device)
                self.model.eval()
                
                # Enable mixed precision for faster inference
                if self.device.type == 'cuda':
                    self.model.half()  # Use FP16 for faster inference
                
                print(f"✅ HuggingFace model loaded on {self.device}")
                
            else:
                raise ValueError("Trying timm model")
                
        except Exception as e:
            print(f"🔄 Trying timm model: {self.model_name}")
            
            try:
                self.model = timm.create_model(self.model_name, pretrained=True)
                self.model.to(self.device)
                self.model.eval()
                
                # Enable mixed precision
                if self.device.type == 'cuda':
                    self.model.half()
                
                # Get transforms
                data_config = resolve_model_data_config(self.model)
                self.processor = create_transform(**data_config, is_training=False)
                self.is_timm_model = True
                
                print(f"✅ timm model loaded on {self.device}")
                
            except Exception as e2:
                print(f"❌ Failed to load model: {e2}")
                raise RuntimeError(f"Could not load model {self.model_name}")
    
    def _clear_gpu_memory(self):
        """Clear GPU memory to prevent OOM errors."""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
    
    def _get_gpu_memory_usage(self) -> float:
        """Get current GPU memory usage in GB."""
        if torch.cuda.is_available():
            return torch.cuda.memory_allocated() / 1024**3
        return 0.0
    
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
                # Partial match
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
        
        return sorted(matches, key=lambda x: x['match_score'], reverse=True)
    
    def _classify_image_batch(self, images: List[Image.Image], top_k: int = 10) -> List[List[Dict]]:
        """Classify multiple images in a batch for GPU efficiency."""
        if not images:
            return []
        
        start_time = time.time()
        
        try:
            if self.is_timm_model:
                # Process images for timm
                inputs = []
                for image in images:
                    if isinstance(self.processor, torch.nn.Module):
                        tensor = self.processor(image)
                    else:
                        tensor = self.processor(image)
                    inputs.append(tensor)
                
                # Stack into batch
                batch_tensor = torch.stack(inputs).to(self.device)
                if self.device.type == 'cuda':
                    batch_tensor = batch_tensor.half()
                
                # Run inference
                with torch.no_grad():
                    outputs = self.model(batch_tensor)
                    probabilities = F.softmax(outputs, dim=1)
                
                # Get top predictions for each image
                top_probs, top_indices = torch.topk(probabilities, top_k, dim=1)
                
                results = []
                for i in range(len(images)):
                    predictions = []
                    for j, (prob, idx) in enumerate(zip(top_probs[i], top_indices[i])):
                        predictions.append({
                            'class_name': f"class_{idx.item()}",
                            'confidence': prob.item(),
                            'rank': j + 1,
                            'class_index': idx.item()
                        })
                    results.append(predictions)
                
            else:
                # Process images for HuggingFace
                inputs = self.processor(images, return_tensors="pt").to(self.device)
                if self.device.type == 'cuda':
                    inputs = {k: v.half() if v.dtype == torch.float32 else v for k, v in inputs.items()}
                
                # Run inference
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    probabilities = F.softmax(outputs.logits, dim=1)
                
                # Get top predictions for each image
                top_probs, top_indices = torch.topk(probabilities, top_k, dim=1)
                
                results = []
                for i in range(len(images)):
                    predictions = []
                    for j, (prob, idx) in enumerate(zip(top_probs[i], top_indices[i])):
                        class_name = self.model.config.id2label.get(idx.item(), f"class_{idx.item()}")
                        predictions.append({
                            'class_name': class_name,
                            'confidence': prob.item(),
                            'rank': j + 1,
                            'class_index': idx.item()
                        })
                    results.append(predictions)
            
            # Track performance
            batch_time = time.time() - start_time
            self.stats['batch_times'].append(batch_time)
            self.stats['total_images'] += len(images)
            self.stats['total_time'] += batch_time
            self.stats['gpu_memory_used'] = max(self.stats['gpu_memory_used'], self._get_gpu_memory_usage())
            
            return results
            
        except RuntimeError as e:
            if "out of memory" in str(e):
                print(f"⚠️  GPU out of memory, clearing cache and retrying with smaller batch...")
                self._clear_gpu_memory()
                # Retry with smaller batch
                if len(images) > 1:
                    mid = len(images) // 2
                    results1 = self._classify_image_batch(images[:mid], top_k)
                    results2 = self._classify_image_batch(images[mid:], top_k)
                    return results1 + results2
                else:
                    raise e
            else:
                raise e
    
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
        """Classify a single image with GPU optimization."""
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
                'device': str(self.device),
                'full_image': None,
                'grid_cells': None,
                'best_match': None,
                'expected_vocab': None,
                'processing_time': 0.0,
                'gpu_memory_used': 0.0
            }
            
            start_time = time.time()
            
            # Extract expected vocab term from filename
            filename = Path(image_path).stem
            if filename.startswith('vocab-') and filename[6:].isdigit():
                vocab_index = int(filename[6:]) - 1
                if 0 <= vocab_index < len(self.vocab_list):
                    results['expected_vocab'] = self.vocab_list[vocab_index]
            
            # Classify full image
            predictions_batch = self._classify_image_batch([image], top_k)
            predictions = predictions_batch[0] if predictions_batch else []
            vocab_matches = self._find_vocab_matches(predictions)
            
            results['full_image'] = {
                'predictions': predictions,
                'vocab_matches': vocab_matches
            }
            
            # Grid cell analysis
            if analyze_grid:
                cells = self._extract_grid_cells(image)
                cell_predictions_batch = self._classify_image_batch(cells, top_k)
                
                cell_results = []
                for i, cell_predictions in enumerate(cell_predictions_batch):
                    cell_vocab_matches = self._find_vocab_matches(cell_predictions)
                    
                    cell_results.append({
                        'position': ['top-left', 'top-right', 'bottom-left', 'bottom-right'][i],
                        'predictions': cell_predictions,
                        'vocab_matches': cell_vocab_matches
                    })
                
                results['grid_cells'] = cell_results
                
                # Find best overall match
                all_matches = []
                for match in vocab_matches:
                    all_matches.append({
                        'position': 'full-image',
                        'match': match
                    })
                
                for cell_result in cell_results:
                    for match in cell_result['vocab_matches']:
                        all_matches.append({
                            'position': cell_result['position'],
                            'match': match
                        })
                
                if all_matches:
                    best_match = max(all_matches, key=lambda x: x['match']['match_score'])
                    results['best_match'] = best_match
            
            # Performance metrics
            results['processing_time'] = time.time() - start_time
            results['gpu_memory_used'] = self._get_gpu_memory_usage()
            
            return results
            
        except Exception as e:
            return {
                'image_path': image_path,
                'error': str(e)
            }
    
    def batch_classify(self, image_dir: str, output_file: str = None, analyze_grid: bool = False, 
                      batch_size: int = 8) -> List[Dict]:
        """Batch classify images with GPU optimization."""
        image_dir = Path(image_dir)
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff'}
        
        image_files = []
        for ext in image_extensions:
            image_files.extend(image_dir.glob(f'*{ext}'))
            image_files.extend(image_dir.glob(f'*{ext.upper()}'))
        
        print(f"📁 Found {len(image_files)} images in {image_dir}")
        print(f"🔧 Using batch size: {batch_size}")
        
        results = []
        
        # Process in batches for GPU efficiency
        for i in range(0, len(image_files), batch_size):
            batch_files = image_files[i:i + batch_size]
            print(f"🔄 Processing batch {i//batch_size + 1}/{(len(image_files) + batch_size - 1)//batch_size}")
            
            # Load batch of images
            batch_images = []
            batch_paths = []
            
            for image_file in batch_files:
                try:
                    image = Image.open(image_file).convert('RGB')
                    batch_images.append(image)
                    batch_paths.append(str(image_file))
                except Exception as e:
                    print(f"⚠️  Error loading {image_file}: {e}")
                    results.append({
                        'image_path': str(image_file),
                        'error': str(e)
                    })
            
            if batch_images:
                # Classify batch
                batch_start = time.time()
                batch_predictions = self._classify_image_batch(batch_images, top_k=10)
                batch_time = time.time() - batch_start
                
                # Process results
                for j, (image_path, predictions) in enumerate(zip(batch_paths, batch_predictions)):
                    vocab_matches = self._find_vocab_matches(predictions)
                    
                    result = {
                        'image_path': image_path,
                        'image_size': batch_images[j].size,
                        'model_name': self.model_name,
                        'device': str(self.device),
                        'full_image': {
                            'predictions': predictions,
                            'vocab_matches': vocab_matches
                        },
                        'processing_time': batch_time / len(batch_images),
                        'gpu_memory_used': self._get_gpu_memory_usage()
                    }
                    
                    # Extract expected vocab
                    filename = Path(image_path).stem
                    if filename.startswith('vocab-') and filename[6:].isdigit():
                        vocab_index = int(filename[6:]) - 1
                        if 0 <= vocab_index < len(self.vocab_list):
                            result['expected_vocab'] = self.vocab_list[vocab_index]
                    
                    # Grid analysis (if requested)
                    if analyze_grid:
                        cells = self._extract_grid_cells(batch_images[j])
                        cell_predictions_batch = self._classify_image_batch(cells, top_k=10)
                        
                        cell_results = []
                        for k, cell_predictions in enumerate(cell_predictions_batch):
                            cell_vocab_matches = self._find_vocab_matches(cell_predictions)
                            cell_results.append({
                                'position': ['top-left', 'top-right', 'bottom-left', 'bottom-right'][k],
                                'predictions': cell_predictions,
                                'vocab_matches': cell_vocab_matches
                            })
                        
                        result['grid_cells'] = cell_results
                        
                        # Find best match
                        all_matches = []
                        for match in vocab_matches:
                            all_matches.append({'position': 'full-image', 'match': match})
                        for cell_result in cell_results:
                            for match in cell_result['vocab_matches']:
                                all_matches.append({'position': cell_result['position'], 'match': match})
                        
                        if all_matches:
                            best_match = max(all_matches, key=lambda x: x['match']['match_score'])
                            result['best_match'] = best_match
                    
                    results.append(result)
                
                # Clear GPU memory periodically
                if i % (batch_size * 4) == 0:
                    self._clear_gpu_memory()
        
        # Save results
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"💾 Results saved to {output_file}")
        
        return results
    
    def get_performance_stats(self) -> Dict:
        """Get performance statistics."""
        avg_time = self.stats['total_time'] / max(self.stats['total_images'], 1)
        images_per_second = self.stats['total_images'] / max(self.stats['total_time'], 0.001)
        
        return {
            'total_images': self.stats['total_images'],
            'total_time': self.stats['total_time'],
            'avg_time_per_image': avg_time,
            'images_per_second': images_per_second,
            'max_gpu_memory_used': self.stats['gpu_memory_used'],
            'device': str(self.device),
            'model_name': self.model_name
        }


def main():
    parser = argparse.ArgumentParser(description='GPU-Optimized EfficientNet Vocabulary Classifier')
    parser.add_argument('--model', default='google/efficientnet-b3', 
                       help='Model name (optimized for GPU)')
    parser.add_argument('--vocab', default='vocab/vocab_list.txt',
                       help='Vocabulary file path')
    parser.add_argument('--image', help='Single image to classify')
    parser.add_argument('--batch', help='Directory of images to classify')
    parser.add_argument('--output', help='Output JSON file for results')
    parser.add_argument('--grid', action='store_true',
                       help='Analyze 2x2 grid cells')
    parser.add_argument('--batch-size', type=int, default=8,
                       help='Batch size for GPU processing')
    parser.add_argument('--top-k', type=int, default=10,
                       help='Number of top predictions to return')
    parser.add_argument('--stats', action='store_true',
                       help='Show performance statistics')
    
    args = parser.parse_args()
    
    # Initialize GPU-optimized classifier
    classifier = GPUOptimizedVocabularyClassifier(
        model_name=args.model, 
        vocab_file=args.vocab
    )
    
    if args.image:
        # Single image classification
        result = classifier.classify_image(args.image, analyze_grid=args.grid, top_k=args.top_k)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
    elif args.batch:
        # Batch classification
        results = classifier.batch_classify(
            args.batch, 
            args.output, 
            analyze_grid=args.grid, 
            batch_size=args.batch_size
        )
        
        print(f"\n📊 Processed {len(results)} images")
        
    else:
        print("Please specify either --image or --batch")
        parser.print_help()
    
    # Show performance stats
    if args.stats or args.batch:
        stats = classifier.get_performance_stats()
        print("\n🚀 Performance Statistics:")
        print(f"   Device: {stats['device']}")
        print(f"   Model: {stats['model_name']}")
        print(f"   Total images: {stats['total_images']}")
        print(f"   Total time: {stats['total_time']:.2f}s")
        print(f"   Avg time per image: {stats['avg_time_per_image']:.3f}s")
        print(f"   Images per second: {stats['images_per_second']:.1f}")
        print(f"   Max GPU memory used: {stats['max_gpu_memory_used']:.1f} GB")


if __name__ == "__main__":
    main() 