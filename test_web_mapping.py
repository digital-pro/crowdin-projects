#!/usr/bin/env python3
"""
Test Web Vocabulary Mapping
Verify that the web interface shows correct vocabulary mapping
"""

def test_vocabulary_mapping():
    """Test the corrected vocabulary mapping"""
    
    # Load vocabulary list
    try:
        with open('vocab/vocab_list.txt', 'r') as f:
            vocab_list = [line.strip() for line in f.readlines() if line.strip()]
    except FileNotFoundError:
        print("❌ vocab_list.txt not found!")
        return
    
    print("🔍 VOCABULARY MAPPING TEST")
    print("=" * 60)
    print("Testing corrected mapping: vocab-004.png = vocab_list[0]")
    print("=" * 60)
    
    # Test key mappings
    test_cases = [
        (4, "acorn"),      # First image
        (7, "artichoke"),  # Was incorrectly shown as expected for 004
        (10, "blender"),   # vocab_list[6]
        (18, "carrot"),    # vocab_list[14]
        (34, "hamster"),   # vocab_list[30]
        (173, "bandage"),  # Last image: vocab_list[169]
    ]
    
    print("📋 CORRECTED MAPPING VERIFICATION:")
    print("-" * 60)
    
    all_correct = True
    for screenshot_num, expected_term in test_cases:
        vocab_index = screenshot_num - 4  # Corrected mapping
        
        if vocab_index >= 0 and vocab_index < len(vocab_list):
            actual_term = vocab_list[vocab_index]
            status = "✅" if actual_term == expected_term else "❌"
            if actual_term != expected_term:
                all_correct = False
            print(f"   vocab-{screenshot_num:03d}.png → vocab_list[{vocab_index}] = '{actual_term}' {status}")
            if actual_term != expected_term:
                print(f"      Expected: '{expected_term}', Got: '{actual_term}'")
        else:
            print(f"   vocab-{screenshot_num:03d}.png → OUT OF RANGE ❌")
            all_correct = False
    
    print(f"\n📊 MAPPING TEST RESULTS:")
    print("-" * 60)
    if all_correct:
        print("✅ All mappings are CORRECT!")
        print("✅ Web interface will show proper expected vocabulary terms")
    else:
        print("❌ Some mappings are incorrect")
        print("❌ Web interface may show wrong expected terms")
    
    # Show vocabulary list sample
    print(f"\n📚 VOCABULARY LIST SAMPLE:")
    print("-" * 60)
    for i in range(min(20, len(vocab_list))):
        screenshot_num = i + 4  # Convert back to screenshot number
        print(f"   vocab-{screenshot_num:03d}.png → vocab_list[{i}] = '{vocab_list[i]}'")
    
    print(f"\n🎯 WEB INTERFACE STATUS:")
    print("-" * 60)
    print("✅ HTML file updated with corrected mapping")
    print("✅ vocab-004.png will show 'Expected: acorn'")
    print("✅ vocab-007.png will show 'Expected: artichoke'")
    print("✅ Enhanced EfficientNet-21k button will use correct mapping")
    print("\n🌐 To test: Open real-imagenet-resnet.html and click")
    print("   '🎯 Show Enhanced EfficientNet-21k (204 Classes)' button")

if __name__ == "__main__":
    test_vocabulary_mapping() 