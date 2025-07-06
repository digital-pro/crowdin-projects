# Troubleshooting Guide - EfficientNet Classifiers

## ✅ Good News: Your Setup is Working!

Based on the test results, your PyTorch installation and all dependencies are working correctly:

- ✅ PyTorch 2.7.1 (CPU version)
- ✅ Transformers 4.53.1
- ✅ timm 1.0.16
- ✅ All other dependencies installed
- ✅ Model downloading and inference working

## Common Issues and Solutions

### 1. "Import Error" or "Module Not Found"

**Problem**: Missing dependencies
**Solution**: 
```bash
pip install -r requirements.txt
```

### 2. "Model Loading Hangs" or "Slow First Run"

**Problem**: Models download on first use (20-200MB each)
**Solution**: 
- Be patient during first run (models are being downloaded)
- Check internet connection
- Use smaller models for testing (e.g., `efficientnet-b0`)

### 3. "CUDA Out of Memory"

**Problem**: GPU memory insufficient
**Solution**: 
- Your system uses CPU (which is fine)
- For GPU users: Use smaller models or reduce batch size

### 4. "No Vocabulary Matches Found"

**Problem**: Threshold too high or model mismatch
**Solution**: 
```python
# Lower similarity threshold
matches = classifier._find_vocab_matches(predictions, threshold=0.2)

# Use ImageNet-21k models for better vocabulary coverage
classifier = AdvancedVocabularyClassifier(
    model_name="timm/tf_efficientnetv2_l.in21k"
)
```

### 5. "Vocabulary File Not Found"

**Problem**: Missing vocab file
**Solution**: 
- Ensure `vocab/vocab_list.txt` exists
- Check file path in script arguments

### 6. "Slow Performance"

**Problem**: Large models on CPU
**Solutions**: 
- Use smaller models (B0 instead of B7)
- Process images in smaller batches
- Consider GPU setup for better performance

## Performance Optimization

### Model Selection by Speed

| Model | Speed (CPU) | Accuracy | Use Case |
|-------|-------------|----------|----------|
| efficientnet-b0 | ⚡⚡⚡ | ⭐⭐ | Testing, fast inference |
| efficientnet-b3 | ⚡⚡ | ⭐⭐⭐ | Balanced performance |
| efficientnet-b7 | ⚡ | ⭐⭐⭐⭐ | High accuracy |
| efficientnetv2-l-21k | ⚡ | ⭐⭐⭐⭐⭐ | Best vocabulary coverage |

### Recommended Settings

```python
# For testing and development
classifier = VocabularyClassifier(
    model_name="google/efficientnet-b0"
)

# For production with good accuracy
classifier = VocabularyClassifier(
    model_name="google/efficientnet-b3"
)

# For best vocabulary coverage
classifier = AdvancedVocabularyClassifier(
    model_name="timm/tf_efficientnetv2_l.in21k"
)
```

## Quick Test Commands

```bash
# Test basic functionality
python advanced_efficientnet_classifier.py --list-models

# Test with a single image (replace path)
python python_efficientnet_classifier.py --image path/to/image.jpg --grid

# Test batch processing
python advanced_efficientnet_classifier.py --batch images/ --output results.json --report
```

## System Requirements

### Minimum Requirements
- Python 3.8+
- 4GB RAM
- 2GB free disk space
- Internet connection (for model downloads)

### Recommended Requirements
- Python 3.9+
- 8GB RAM
- 5GB free disk space
- GPU with 4GB+ VRAM (optional)

## Error Messages and Solutions

### `"Could not load model"`
- Check internet connection
- Verify model name spelling
- Clear cache: `rm -rf ~/.cache/huggingface/`

### `"RuntimeError: CUDA out of memory"`
- Use CPU version: Models work on CPU
- Reduce batch size
- Use smaller model

### `"ConnectionError" or "HTTPError"`
- Check internet connection
- Try again later (server issues)
- Use cached models if available

### `"Permission denied"`
- Check file permissions
- Run as administrator if needed
- Check antivirus software

## Advanced Troubleshooting

### Clear All Caches
```bash
# Windows
rmdir /s "%USERPROFILE%\.cache\huggingface"

# Linux/Mac
rm -rf ~/.cache/huggingface/
```

### Reinstall Dependencies
```bash
pip uninstall torch torchvision transformers timm
pip install -r requirements.txt
```

### Check GPU Setup (Optional)
```python
import torch
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA device count: {torch.cuda.device_count()}")
if torch.cuda.is_available():
    print(f"CUDA device: {torch.cuda.get_device_name(0)}")
```

## Getting Help

1. **Check this troubleshooting guide first**
2. **Run the test suite** to identify specific issues
3. **Check error messages** for specific solutions
4. **Try smaller models** if performance is an issue
5. **Check internet connection** for model downloads

## Contact Information

If you encounter issues not covered here:
1. Check the error message carefully
2. Try the suggested solutions
3. Test with smaller models first
4. Verify your Python environment

Your current setup is working correctly, so any issues are likely configuration-related rather than installation problems. 