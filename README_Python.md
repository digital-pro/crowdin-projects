# EfficientNet Vocabulary Classifier - Python Implementation

This Python implementation provides powerful vocabulary classification using EfficientNet models from Hugging Face Transformers and timm libraries. It supports both standard ImageNet-1k and ImageNet-21k models with grid cell analysis capabilities.

## Features

- **Multiple Model Support**: EfficientNet-B0 through B7, EfficientNetV2, and ImageNet-21k models
- **Grid Cell Analysis**: Analyze 2x2 grid cells in images for precise object detection
- **Vocabulary Matching**: Advanced matching algorithms with similarity scoring
- **Batch Processing**: Process entire directories of images
- **Performance Reporting**: Comprehensive accuracy analysis and reporting
- **Flexible Input**: Support for local images and URLs

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. The scripts will automatically download models from Hugging Face on first use.

## Quick Start

### Basic Usage

```python
from python_efficientnet_classifier import VocabularyClassifier

# Initialize classifier
classifier = VocabularyClassifier(
    model_name="google/efficientnet-b7",
    vocab_file="vocab/vocab_list.txt"
)

# Classify a single image
result = classifier.classify_image("path/to/image.jpg", analyze_grid=True)
print(f"Best match: {result['best_match']['match']['vocab_term']}")
```

### Advanced Usage

```python
from advanced_efficientnet_classifier import AdvancedVocabularyClassifier

# Use ImageNet-21k model for better accuracy
classifier = AdvancedVocabularyClassifier(
    model_name="timm/tf_efficientnetv2_l.in21k",
    vocab_file="vocab/vocab_list.txt"
)

# Batch process images with performance report
results = classifier.batch_classify("images/", "results.json", analyze_grid=True)
report = classifier.generate_performance_report(results)
```

## Command Line Usage

### Basic Classifier

```bash
# Single image classification
python scripts/python_efficientnet_classifier.py --image vocab-004.png --grid

# Batch processing
python scripts/python_efficientnet_classifier.py --batch images/ --output results.json --analyze-performance
```

### Advanced Classifier

```bash
# List available models
python scripts/advanced_efficientnet_classifier.py --list-models

# Use ImageNet-21k model
python scripts/advanced_efficientnet_classifier.py --model timm/tf_efficientnetv2_l.in21k --batch images/ --output results.json --report --grid

# Compare different models
python scripts/advanced_efficientnet_classifier.py --model google/efficientnet-b3 --image test.jpg --top-k 20
```

## Recommended Models

| Model Name | Model ID | Description |
|------------|----------|-------------|
| efficientnet-b0 | google/efficientnet-b0 | Fastest, good for testing |
| efficientnet-b3 | google/efficientnet-b3 | Balanced speed/accuracy |
| efficientnet-b7 | google/efficientnet-b7 | High accuracy, slower |
| efficientnetv2-l-21k | timm/tf_efficientnetv2_l.in21k | Best accuracy, 21k classes |
| efficientnetv2-xl-21k | timm/tf_efficientnetv2_xl.in21k | Highest accuracy, largest |

## Model Performance Comparison

Based on the ImageNet-21k models vs ImageNet-1k models:

- **ImageNet-21k models**: Better vocabulary coverage, more classes, higher accuracy for specific objects
- **ImageNet-1k models**: Faster inference, smaller memory footprint, good for general classification

## Grid Cell Analysis

The grid cell analysis feature divides each image into a 2x2 grid and classifies each quadrant separately:

```python
# Enable grid analysis
result = classifier.classify_image("image.jpg", analyze_grid=True)

# Access grid cell results
for cell in result['grid_cells']:
    print(f"Position: {cell['position']}")
    print(f"Best match: {cell['vocab_matches'][0]['vocab_term']}")
```

Grid positions:
- `top-left`: Upper left quadrant
- `top-right`: Upper right quadrant  
- `bottom-left`: Lower left quadrant
- `bottom-right`: Lower right quadrant

## Vocabulary Matching

The system uses a sophisticated matching algorithm:

1. **Exact Match** (Score: 1.0): Perfect string match
2. **Partial Match** (Score: 0.8): One string contains the other
3. **Word Match** (Score: 0.6): Shared words between strings
4. **Similarity Match** (Score: 0.3-0.6): Character-level similarity

## Performance Reporting

The advanced classifier provides comprehensive performance analysis:

```python
report = classifier.generate_performance_report(results)

# Access metrics
print(f"Overall accuracy: {report['accuracy_metrics']['overall_accuracy']:.2%}")
print(f"Exact match rate: {report['accuracy_metrics']['exact_match_rate']:.2%}")

# Per-vocabulary performance
for vocab_term, perf in report['vocab_performance'].items():
    print(f"{vocab_term}: {perf['accuracy']:.2%}")
```

## Output Format

### Single Image Result

```json
{
  "image_path": "vocab-004.png",
  "model_name": "google/efficientnet-b7",
  "expected_vocab": "acorn",
  "full_image": {
    "predictions": [
      {
        "class_name": "acorn",
        "confidence": 0.85,
        "rank": 1
      }
    ],
    "vocab_matches": [
      {
        "vocab_term": "acorn",
        "match_score": 1.0,
        "match_type": "exact"
      }
    ]
  },
  "grid_cells": [...],
  "best_match": {
    "position": "top-left",
    "match": {
      "vocab_term": "acorn",
      "match_score": 1.0
    }
  }
}
```

### Performance Report

```json
{
  "model_info": {
    "model_name": "google/efficientnet-b7",
    "vocab_size": 170
  },
  "accuracy_metrics": {
    "overall_accuracy": 0.75,
    "exact_match_rate": 0.60,
    "any_match_rate": 0.85
  },
  "vocab_performance": {
    "acorn": {
      "accuracy": 0.90,
      "total_images": 10,
      "exact_matches": 8
    }
  }
}
```

## Memory and Performance

### GPU Support
- Automatically detects and uses CUDA if available
- Fallback to CPU processing
- Memory usage scales with model size

### Model Sizes
- EfficientNet-B0: ~5MB
- EfficientNet-B7: ~66MB  
- EfficientNetV2-L-21k: ~145MB
- EfficientNetV2-XL-21k: ~208MB

### Processing Speed
- B0: ~50 images/second (GPU)
- B7: ~10 images/second (GPU)
- V2-L-21k: ~5 images/second (GPU)

## Troubleshooting

### Common Issues

1. **Model Download Fails**
   ```bash
   # Clear cache and retry
   rm -rf ~/.cache/huggingface/
   python -c "from transformers import EfficientNetForImageClassification; EfficientNetForImageClassification.from_pretrained('google/efficientnet-b7')"
   ```

2. **Out of Memory**
   ```python
   # Use smaller model or reduce batch size
   classifier = VocabularyClassifier(model_name="google/efficientnet-b0")
   ```

3. **No Vocabulary Matches**
   ```python
   # Lower the similarity threshold
   matches = classifier._find_vocab_matches(predictions, threshold=0.2)
   ```

### Error Messages

- `"Could not load model"`: Check internet connection and model name
- `"Vocabulary file not found"`: Verify vocab file path
- `"CUDA out of memory"`: Use CPU or smaller model

## Integration with Web Application

The Python classifiers can be integrated with your existing web application:

```python
# Create API endpoint
from flask import Flask, request, jsonify

app = Flask(__name__)
classifier = VocabularyClassifier()

@app.route('/classify', methods=['POST'])
def classify_image():
    image_path = request.json['image_path']
    result = classifier.classify_image(image_path, analyze_grid=True)
    return jsonify(result)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this code in your research, please cite:

```bibtex
@software{efficientnet_vocab_classifier,
  title={EfficientNet Vocabulary Classifier},
  author={Your Name},
  year={2024},
  url={https://github.com/your-repo/crowdin-projects}
}
``` 