#!/usr/bin/env python3
"""
Extract ImageNet-21k class names from timm model
"""

import timm
import torch
import json

def extract_imagenet21k_classes():
    """Extract class names from EfficientNet-21k model"""
    
    print("🔄 Loading EfficientNet-21k model...")
    model = timm.create_model('tf_efficientnetv2_l.in21k', pretrained=True)
    
    # Try to get class names from model
    if hasattr(model, 'class_names'):
        class_names = model.class_names
        print(f"✅ Found {len(class_names)} class names from model.class_names")
    elif hasattr(model, 'imagenet_classes'):
        class_names = model.imagenet_classes
        print(f"✅ Found {len(class_names)} class names from model.imagenet_classes")
    else:
        # Try to get from timm data
        try:
            from timm.data import ImageNetInfo
            info = ImageNetInfo.from_model(model)
            class_names = info.class_names
            print(f"✅ Found {len(class_names)} class names from ImageNetInfo")
        except:
            # Try to get from model's config
            if hasattr(model, 'default_cfg') and 'label_names' in model.default_cfg:
                class_names = model.default_cfg['label_names']
                print(f"✅ Found {len(class_names)} class names from default_cfg")
            else:
                print("❌ Could not find class names, generating generic names")
                class_names = [f"class_{i}" for i in range(21000)]
    
    # Save as JSON
    with open('imagenet21k_classes.json', 'w') as f:
        json.dump(class_names, f, indent=2)
    
    print(f"💾 Saved {len(class_names)} class names to imagenet21k_classes.json")
    
    # Check for acorn-related classes
    acorn_classes = [i for i, cls in enumerate(class_names) if 'acorn' in cls.lower()]
    print(f"\n🔍 Found {len(acorn_classes)} acorn-related classes:")
    for i in acorn_classes:
        print(f"  {i}: {class_names[i]}")
    
    # Check for nut/seed/oak related classes
    nut_classes = [i for i, cls in enumerate(class_names) if any(word in cls.lower() for word in ['nut', 'seed', 'oak'])]
    print(f"\n🌰 Found {len(nut_classes)} nut/seed/oak-related classes (showing first 20):")
    for i in nut_classes[:20]:
        print(f"  {i}: {class_names[i]}")
    
    return class_names

if __name__ == "__main__":
    extract_imagenet21k_classes() 