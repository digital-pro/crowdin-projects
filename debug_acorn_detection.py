#!/usr/bin/env python3
"""
Debug script to test acorn detection in vocab-004.png
"""

import requests
from PIL import Image
from io import BytesIO
import torch
import timm
from timm.data import resolve_data_config
from timm.data.transforms_factory import create_transform
import json

def test_acorn_detection():
    """Test what EfficientNet-21k detects for vocab-004.png"""
    
    print("🔄 Loading EfficientNet-21k model directly...")
    
    # Load model
    model = timm.create_model('tf_efficientnetv2_l.in21k', pretrained=True)
    model.eval()
    
    if torch.cuda.is_available():
        model = model.cuda()
        print("✅ Using GPU")
    
    # Load transforms
    config = resolve_data_config({}, model=model)
    transform = create_transform(**config)
    
    # Load ImageNet-21k class names
    try:
        with open('imagenet21k_classes.json', 'r') as f:
            class_names = json.load(f)
    except:
        print("❌ Could not load imagenet21k_classes.json, using indices")
        class_names = [f"class_{i}" for i in range(21000)]
    
    # Download vocab-004.png
    image_url = "https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-004.png"
    print(f"📥 Downloading {image_url}")
    
    response = requests.get(image_url)
    image = Image.open(BytesIO(response.content))
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Save full image for analysis
    image.save("debug_vocab_004_full.png")
    print("💾 Saved full image as debug_vocab_004_full.png")
    
    # Extract bottom-right cell (where acorn should be)
    width, height = image.size
    half_width = width // 2
    half_height = height // 2
    
    bottom_right = image.crop((half_width, half_height, width, height))
    bottom_right.save("debug_vocab_004_bottom_right.png")
    print("💾 Saved bottom-right cell as debug_vocab_004_bottom_right.png")
    
    # Analyze bottom-right cell directly
    print("\n🔍 Analyzing bottom-right cell (where acorn should be)...")
    
    input_tensor = transform(bottom_right).unsqueeze(0)
    if torch.cuda.is_available():
        input_tensor = input_tensor.cuda()
    
    with torch.no_grad():
        outputs = model(input_tensor)
        probabilities = torch.nn.functional.softmax(outputs[0], dim=0)
    
    # Get top 20 predictions
    top_probs, top_indices = torch.topk(probabilities, 20)
    
    print("\n📊 TOP 20 PREDICTIONS FOR BOTTOM-RIGHT CELL:")
    acorn_found = False
    for i, (prob, idx) in enumerate(zip(top_probs, top_indices)):
        class_name = class_names[idx.item()] if idx.item() < len(class_names) else f"class_{idx.item()}"
        print(f"  {i+1:2d}. {class_name} ({prob.item():.6f})")
        
        if 'acorn' in class_name.lower():
            print(f"      ⭐ FOUND ACORN!")
            acorn_found = True
    
    if not acorn_found:
        print("\n❌ No 'acorn' found in top 20 predictions")
    
    # Check if acorn is anywhere in the class names
    print(f"\n🔍 Checking if 'acorn' is in ImageNet-21k classes...")
    acorn_classes = [cls for cls in class_names if 'acorn' in cls.lower()]
    print(f"Found {len(acorn_classes)} acorn-related classes:")
    for cls in acorn_classes:
        print(f"  - {cls}")
    
    # Check for nut-related classes
    nut_classes = [cls for cls in class_names if any(word in cls.lower() for word in ['nut', 'seed', 'oak'])][:10]
    print(f"\nFound {len(nut_classes)} nut/seed/oak-related classes (showing first 10):")
    for cls in nut_classes:
        print(f"  - {cls}")

if __name__ == "__main__":
    test_acorn_detection() 