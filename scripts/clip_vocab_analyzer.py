#!/usr/bin/env python3
"""
CLIP-based Vocabulary Image Analyzer
Uses OpenAI's CLIP model for better text-image alignment
"""

import os
import json
import time
import requests
from PIL import Image
from io import BytesIO
import torch
import clip
import numpy as np
from typing import List, Dict, Tuple, Optional

class CLIPVocabAnalyzer:
    """CLIP-based vocabulary image analyzer with better text-image understanding"""
    
    def __init__(self, model_name="ViT-B/32", vocab_file="vocab/vocab_list.txt"):
        """Initialize CLIP analyzer"""
        print(f"🚀 Initializing CLIP Vocabulary Analyzer")
        print(f"📦 Model: {model_name}")
        
        # Check if CUDA is available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"🔧 Device: {self.device}")
        
        # Load CLIP model
        print(f"⏳ Loading CLIP model...")
        self.model, self.preprocess = clip.load(model_name, device=self.device)
        print(f"✅ CLIP model loaded successfully")
        
        # Load vocabulary list
        self.vocab_terms = self.load_vocabulary_list(vocab_file)
        print(f"📚 Loaded {len(self.vocab_terms)} vocabulary terms")
        
        # Precompute text embeddings for all vocabulary terms
        self.text_embeddings = self.precompute_text_embeddings()
        print(f"🧠 Precomputed text embeddings for {len(self.text_embeddings)} terms")
        
    def load_vocabulary_list(self, vocab_file: str) -> List[str]:
        """Load vocabulary list from file"""
        vocab_terms = [
            'acorn', 'aloe', 'antenna', 'artichoke', 'bamboo', 'barrel', 'blender', 'blower',
            'bouquet', 'buffet', 'bulldozer', 'cake', 'caramel', 'carousel', 'carrot', 'cassette',
            'cheese', 'cloak', 'clothespin', 'coaster', 'cork', 'cornbread', 'corset', 'dumpling',
            'elbow', 'fan', 'foam', 'footbath', 'fruitcake', 'gutter', 'hamster', 'hedgehog',
            'hoe', 'hopscotch', 'kimono', 'latch', 'locker', 'lollipop', 'map', 'marshmallow',
            'net', 'oil', 'omelet', 'pie', 'pistachio', 'pitcher', 'potato', 'prism', 'puddle',
            'pump', 'rice', 'saddle', 'sandbag', 'scaffolding', 'scoop', 'seagull', 'ship',
            'shower', 'silverware', 'sink', 'ski', 'sloth', 'snail', 'sorbet', 'spatula',
            'sprinkler', 'squash', 'squirrel', 'stew', 'rubber band', 'stump', 'sunflower',
            'swordfish', 'tapestry', 'teabag', 'telescope', 'thermos', 'treasure', 'trumpet',
            'tulip', 'turbine', 'turkey', 'turtle', 'typewriter', 'watermelon', 'waterwheel',
            'ant', 'ball', 'bear', 'duck', 'fork', 'kitten', 'knee', 'milkshake', 'skin', 'wall',
            'wheel', 'farm', 'juggling', 'dressing', 'roof', 'peeking', 'ruler', 'tunnel',
            'envelope', 'diamond', 'calendar', 'panda', 'arrow', 'picking', 'dripping', 'knight',
            'delivering', 'dentist', 'claw', 'uniform', 'furry', 'cormorant', 'fetch', 'arcade',
            'artifact', 'aversion', 'beret', 'applaud', 'timid', 'camp', 'tumble', 'concentric',
            'confectionery', 'couturier', 'degression', 'divan', 'wetland', 'baywindow', 'aesthete',
            'ecstatic', 'rickety', 'gourmet', 'gesticulate', 'facade', 'slope', 'habit',
            'intersection', 'irrigation', 'kazoo', 'chat', 'colony', 'preserve', 'awning',
            'mammalogy', 'metronome', 'paleontologist', 'percussion', 'posterior', 'precarious',
            'arbor', 'resuscitation', 'rosette', 'saffron', 'mischievous', 'skimmer', 'sedentary',
            'suede', 'turnstile', 'triad', 'dredging', 'urban', 'steam', 'vertebra', 'bandage'
        ]
        
        try:
            if os.path.exists(vocab_file):
                with open(vocab_file, 'r', encoding='utf-8') as f:
                    file_vocab = [line.strip() for line in f if line.strip()]
                if file_vocab:
                    return file_vocab
        except Exception as e:
            print(f"⚠️ Could not load {vocab_file}: {e}")
        
        return vocab_terms
    
    def precompute_text_embeddings(self) -> Dict[str, torch.Tensor]:
        """Precompute CLIP text embeddings for all vocabulary terms"""
        text_embeddings = {}
        
        # Create text prompts for better context
        text_prompts = []
        vocab_to_prompt = {}
        
        for vocab_term in self.vocab_terms:
            # Try multiple prompt formats for better matching
            prompts = [
                f"a photo of {vocab_term}",
                f"a picture of {vocab_term}",
                f"an image of {vocab_term}",
                f"{vocab_term}",
                f"a {vocab_term}",
                f"the {vocab_term}"
            ]
            
            for prompt in prompts:
                text_prompts.append(prompt)
                vocab_to_prompt[prompt] = vocab_term
        
        # Tokenize all prompts
        text_tokens = clip.tokenize(text_prompts).to(self.device)
        
        # Get embeddings in batches
        batch_size = 100
        all_embeddings = []
        
        with torch.no_grad():
            for i in range(0, len(text_tokens), batch_size):
                batch_tokens = text_tokens[i:i+batch_size]
                batch_embeddings = self.model.encode_text(batch_tokens)
                batch_embeddings = batch_embeddings / batch_embeddings.norm(dim=-1, keepdim=True)
                all_embeddings.append(batch_embeddings)
        
        # Combine all embeddings
        all_embeddings = torch.cat(all_embeddings, dim=0)
        
        # Group embeddings by vocabulary term
        for i, prompt in enumerate(text_prompts):
            vocab_term = vocab_to_prompt[prompt]
            if vocab_term not in text_embeddings:
                text_embeddings[vocab_term] = []
            text_embeddings[vocab_term].append(all_embeddings[i])
        
        # Average embeddings for each vocabulary term
        for vocab_term in text_embeddings:
            text_embeddings[vocab_term] = torch.stack(text_embeddings[vocab_term]).mean(dim=0)
        
        return text_embeddings
    
    def analyze_image_with_clip(self, image: Image.Image, top_k: int = 10) -> List[Dict]:
        """Analyze image using CLIP and return top vocabulary matches"""
        try:
            # Preprocess image
            image_tensor = self.preprocess(image).unsqueeze(0).to(self.device)
            
            # Get image embedding
            with torch.no_grad():
                image_embedding = self.model.encode_image(image_tensor)
                image_embedding = image_embedding / image_embedding.norm(dim=-1, keepdim=True)
            
            # Calculate similarities with all vocabulary terms
            similarities = {}
            for vocab_term, text_embedding in self.text_embeddings.items():
                similarity = torch.cosine_similarity(image_embedding, text_embedding.unsqueeze(0))
                similarities[vocab_term] = similarity.item()
            
            # Sort by similarity and return top matches
            sorted_matches = sorted(similarities.items(), key=lambda x: x[1], reverse=True)
            
            results = []
            for i, (vocab_term, similarity) in enumerate(sorted_matches[:top_k]):
                results.append({
                    'rank': i + 1,
                    'vocab_term': vocab_term,
                    'similarity': similarity,
                    'confidence': (similarity + 1) / 2 * 100  # Convert to 0-100 scale
                })
            
            return results
            
        except Exception as e:
            print(f"❌ Error analyzing image with CLIP: {str(e)}")
            return []
    
    def analyze_grid_cell(self, image: Image.Image, position: str, expected_vocab: Optional[str] = None) -> Dict:
        """Analyze a single grid cell with CLIP"""
        try:
            # Get CLIP predictions
            predictions = self.analyze_image_with_clip(image, top_k=20)
            
            # Find expected vocabulary term in predictions
            expected_match = None
            expected_rank = None
            
            if expected_vocab:
                for pred in predictions:
                    if pred['vocab_term'].lower() == expected_vocab.lower():
                        expected_match = pred
                        expected_rank = pred['rank']
                        break
            
            return {
                'position': position,
                'predictions': predictions,
                'top_match': predictions[0] if predictions else None,
                'expected_vocab': expected_vocab,
                'expected_match': expected_match,
                'expected_rank': expected_rank,
                'expected_found': expected_match is not None
            }
            
        except Exception as e:
            print(f"❌ Error analyzing grid cell {position}: {str(e)}")
            return {
                'position': position,
                'error': str(e),
                'predictions': [],
                'top_match': None,
                'expected_vocab': expected_vocab,
                'expected_match': None,
                'expected_rank': None,
                'expected_found': False
            }
    
    def analyze_vocab_screenshot(self, image_url: str, screenshot_id: str, expected_vocab: Optional[str] = None) -> Dict:
        """Analyze a vocabulary screenshot using CLIP"""
        try:
            print(f"📥 Downloading {image_url}")
            
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
            results = {}
            for position, cell_image in grid_cells.items():
                print(f"  🔍 Analyzing {position} cell with CLIP...")
                results[position] = self.analyze_grid_cell(cell_image, position, expected_vocab)
            
            # Determine best match across all cells
            best_match = None
            best_confidence = 0
            
            for position, cell_result in results.items():
                if cell_result.get('expected_match'):
                    confidence = cell_result['expected_match']['confidence']
                    if confidence > best_confidence:
                        best_confidence = confidence
                        best_match = position
            
            return {
                'screenshot_id': screenshot_id,
                'image_url': image_url,
                'expected_vocab': expected_vocab,
                'grid_results': results,
                'best_match_position': best_match,
                'best_match_confidence': best_confidence,
                'expected_found': best_match is not None,
                'success': True
            }
            
        except Exception as e:
            print(f"❌ Error analyzing {image_url}: {str(e)}")
            return {
                'screenshot_id': screenshot_id,
                'image_url': image_url,
                'expected_vocab': expected_vocab,
                'error': str(e),
                'success': False
            }
    
    def analyze_vocabulary_dataset(self, start_id: int = 4, end_id: int = 20) -> List[Dict]:
        """Analyze vocabulary dataset using CLIP"""
        print(f"🚀 Analyzing vocabulary dataset with CLIP")
        print(f"📊 Processing vocab-{start_id:03d} to vocab-{end_id:03d}")
        
        results = []
        start_time = time.time()
        
        for i in range(start_id, end_id + 1):
            screenshot_id = f"{i:03d}"
            image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/e9c3216adb900a8c32b18d0ef356c83d7dc77234/golden-runs/vocab/vocab-{screenshot_id}.png"
            
            # Get expected vocabulary term
            expected_vocab = self.vocab_terms[i-4] if i-4 < len(self.vocab_terms) else None
            
            print(f"\n📸 Processing vocab-{screenshot_id}.png (expected: {expected_vocab})")
            
            result = self.analyze_vocab_screenshot(image_url, screenshot_id, expected_vocab)
            results.append(result)
            
            if result.get('success'):
                found_status = "✅ FOUND" if result.get('expected_found') else "❌ NOT FOUND"
                if result.get('expected_found'):
                    print(f"   {found_status} in {result['best_match_position']} ({result['best_match_confidence']:.1f}%)")
                else:
                    print(f"   {found_status}")
        
        # Calculate statistics
        total_time = time.time() - start_time
        successful_results = [r for r in results if r.get('success')]
        found_results = [r for r in successful_results if r.get('expected_found')]
        
        print(f"\n📊 CLIP Analysis Complete!")
        print(f"   Total images processed: {len(successful_results)}")
        print(f"   Expected terms found: {len(found_results)}")
        print(f"   Success rate: {len(found_results)/len(successful_results)*100:.1f}%")
        print(f"   Processing time: {total_time:.2f}s")
        print(f"   Average time per image: {total_time/len(successful_results):.3f}s")
        
        # Save results
        output_data = {
            'metadata': {
                'model': 'CLIP',
                'created_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_images': len(successful_results),
                'found_count': len(found_results),
                'success_rate': len(found_results)/len(successful_results)*100,
                'processing_time': total_time
            },
            'vocabulary_list': self.vocab_terms,
            'results': results
        }
        
        output_file = f"clip_vocab_analysis_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"💾 Results saved to: {output_file}")
        
        return results

def main():
    """Main function to run CLIP analysis"""
    print("🚀 CLIP Vocabulary Analysis")
    print("=" * 60)
    
    # Check if CLIP is installed
    try:
        import clip
        print("✅ CLIP is available")
    except ImportError:
        print("❌ CLIP not installed. Please install with: pip install git+https://github.com/openai/CLIP.git")
        return
    
    analyzer = CLIPVocabAnalyzer()
    
    # Analyze first 20 images
    print("\n🔍 Analyzing first 20 vocabulary images with CLIP...")
    results = analyzer.analyze_vocabulary_dataset(start_id=4, end_id=23)
    
    # Test specific problematic cases
    print(f"\n🧪 Testing vocab-004 (acorn) with CLIP...")
    test_result = analyzer.analyze_vocab_screenshot(
        "https://raw.githubusercontent.com/levante-framework/core-tasks/e9c3216adb900a8c32b18d0ef356c83d7dc77234/golden-runs/vocab/vocab-004.png",
        "004",
        "acorn"
    )
    
    if test_result['success']:
        print(f"   Expected vocab: {test_result['expected_vocab']}")
        print(f"   Found: {test_result['expected_found']}")
        if test_result['expected_found']:
            print(f"   Best match: {test_result['best_match_position']} ({test_result['best_match_confidence']:.1f}%)")
        
        print(f"\n   Grid cell analysis:")
        for position, cell_result in test_result['grid_results'].items():
            if cell_result.get('top_match'):
                top = cell_result['top_match']
                print(f"     {position}: {top['vocab_term']} ({top['confidence']:.1f}%)")

if __name__ == "__main__":
    main() 