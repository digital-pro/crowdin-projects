#!/usr/bin/env python3
"""
Example usage of the EfficientNet Vocabulary Classifiers
"""

import os
from python_efficientnet_classifier import VocabularyClassifier
from advanced_efficientnet_classifier import AdvancedVocabularyClassifier

def basic_example():
    """Basic usage example with standard EfficientNet-B7."""
    print("=== Basic EfficientNet-B7 Example ===")
    
    # Initialize classifier
    classifier = VocabularyClassifier(
        model_name="google/efficientnet-b7",
        vocab_file="vocab/vocab_list.txt"
    )
    
    # Classify a single image (replace with your image path)
    image_path = "path/to/your/image.jpg"  # Update this path
    
    if os.path.exists(image_path):
        result = classifier.classify_image(image_path, analyze_grid=True)
        
        print(f"Image: {result['image_path']}")
        print(f"Expected vocab: {result.get('expected_vocab', 'N/A')}")
        
        # Show top predictions
        print("\nTop predictions:")
        for pred in result['full_image']['predictions'][:5]:
            print(f"  {pred['rank']}. {pred['class_name']}: {pred['confidence']:.3f}")
        
        # Show vocabulary matches
        print("\nVocabulary matches:")
        for match in result['full_image']['vocab_matches'][:3]:
            print(f"  {match['vocab_term']}: {match['match_score']:.3f} ({match['match_type']})")
        
        # Show best grid cell match
        if result.get('best_match'):
            best = result['best_match']
            print(f"\nBest match: {best['match']['vocab_term']} in {best['position']}")
            print(f"  Score: {best['match']['match_score']:.3f}")
    else:
        print(f"Image not found: {image_path}")

def advanced_example():
    """Advanced usage example with EfficientNet-21k."""
    print("\n=== Advanced EfficientNet-21k Example ===")
    
    # Initialize advanced classifier with ImageNet-21k model
    classifier = AdvancedVocabularyClassifier(
        model_name="timm/tf_efficientnetv2_l.in21k",
        vocab_file="vocab/vocab_list.txt"
    )
    
    # Example with a sample image
    image_path = "path/to/your/image.jpg"  # Update this path
    
    if os.path.exists(image_path):
        result = classifier.classify_image(image_path, analyze_grid=True, top_k=10)
        
        print(f"Model: {result['model_name']} ({result['model_type']})")
        print(f"Image: {result['image_path']}")
        print(f"Expected vocab: {result.get('expected_vocab', 'N/A')}")
        
        # Show vocabulary matches with enhanced scoring
        print("\nVocabulary matches:")
        for match in result['full_image']['vocab_matches'][:5]:
            print(f"  {match['vocab_term']}: {match['match_score']:.3f} ({match['match_type']})")
    else:
        print(f"Image not found: {image_path}")

def batch_example():
    """Example of batch processing."""
    print("\n=== Batch Processing Example ===")
    
    # Initialize classifier
    classifier = AdvancedVocabularyClassifier(
        model_name="google/efficientnet-b3",  # Faster model for batch processing
        vocab_file="vocab/vocab_list.txt"
    )
    
    # Process a directory of images
    image_dir = "path/to/your/image/directory"  # Update this path
    
    if os.path.exists(image_dir):
        results = classifier.batch_classify(
            image_dir=image_dir,
            output_file="batch_results.json",
            analyze_grid=True
        )
        
        # Generate performance report
        report = classifier.generate_performance_report(results)
        
        print(f"\nProcessed {len(results)} images")
        print(f"Overall accuracy: {report['accuracy_metrics']['overall_accuracy']:.2%}")
        print(f"Exact match rate: {report['accuracy_metrics']['exact_match_rate']:.2%}")
        
        # Show top performing vocab terms
        print("\nTop 5 best performing vocab terms:")
        for i, (term, perf) in enumerate(report['best_matches'][:5]):
            print(f"  {i+1}. {term}: {perf['accuracy']:.2%}")
    else:
        print(f"Directory not found: {image_dir}")

def model_comparison():
    """Compare different models."""
    print("\n=== Model Comparison Example ===")
    
    models_to_test = [
        "google/efficientnet-b0",
        "google/efficientnet-b3", 
        "google/efficientnet-b7",
        # "timm/tf_efficientnetv2_l.in21k",  # Uncomment if you want to test 21k model
    ]
    
    image_path = "path/to/your/test/image.jpg"  # Update this path
    
    if not os.path.exists(image_path):
        print(f"Test image not found: {image_path}")
        return
    
    results = {}
    
    for model_name in models_to_test:
        print(f"\nTesting {model_name}...")
        
        try:
            classifier = VocabularyClassifier(
                model_name=model_name,
                vocab_file="vocab/vocab_list.txt"
            )
            
            result = classifier.classify_image(image_path, analyze_grid=False, top_k=5)
            
            # Extract top vocab matches
            vocab_matches = result.get('full_image', {}).get('vocab_matches', [])
            top_match = vocab_matches[0] if vocab_matches else None
            
            results[model_name] = {
                'top_match': top_match,
                'num_matches': len(vocab_matches)
            }
            
            if top_match:
                print(f"  Best match: {top_match['vocab_term']} ({top_match['match_score']:.3f})")
            else:
                print("  No vocabulary matches found")
                
        except Exception as e:
            print(f"  Error: {e}")
            results[model_name] = {'error': str(e)}
    
    # Summary
    print("\n=== Comparison Summary ===")
    for model_name, result in results.items():
        if 'error' in result:
            print(f"{model_name}: Failed ({result['error']})")
        elif result['top_match']:
            print(f"{model_name}: {result['top_match']['vocab_term']} ({result['top_match']['match_score']:.3f})")
        else:
            print(f"{model_name}: No matches")

if __name__ == "__main__":
    print("EfficientNet Vocabulary Classifier Examples")
    print("=" * 50)
    
    # Note: Update the image paths before running
    print("Note: Please update the image paths in this script before running!")
    print()
    
    # Run examples
    basic_example()
    advanced_example()
    batch_example()
    model_comparison()
    
    print("\n" + "=" * 50)
    print("Examples completed!")
    print("\nTo run the classifiers from command line:")
    print("python python_efficientnet_classifier.py --image path/to/image.jpg --grid")
    print("python advanced_efficientnet_classifier.py --batch path/to/images/ --output results.json --report") 