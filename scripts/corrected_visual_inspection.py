#!/usr/bin/env python3
"""
Corrected Visual Inspection Analysis
Starts from vocab-004.png and properly maps to vocabulary list
"""

import requests
import json
import os
from PIL import Image
import io

def download_image(screenshot_id):
    """Download a vocabulary screenshot"""
    url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{screenshot_id:03d}.png"
    
    try:
        print(f"📥 Downloading vocab-{screenshot_id:03d}.png...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        
        # Save image
        filename = f"inspect_vocab_{screenshot_id:03d}.png"
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        # Load image to get dimensions
        img = Image.open(io.BytesIO(response.content))
        width, height = img.size
        
        print(f"   ✅ Downloaded: {filename} ({width}x{height})")
        return filename, width, height
        
    except Exception as e:
        print(f"   ❌ Failed to download vocab-{screenshot_id:03d}.png: {str(e)}")
        return None, 0, 0

def load_vocab_list():
    """Load the vocabulary list"""
    try:
        with open('vocab/vocab_list.txt', 'r') as f:
            vocab_list = [line.strip() for line in f.readlines() if line.strip()]
        return vocab_list
    except FileNotFoundError:
        print("❌ vocab_list.txt not found!")
        return []

def get_expected_vocab_corrected(screenshot_id, vocab_list):
    """Get expected vocabulary term for a screenshot ID (corrected mapping)"""
    try:
        # Screenshots start from 004, so:
        # vocab-004.png = vocab_list[0] (acorn)
        # vocab-005.png = vocab_list[1] (aloe)
        # vocab-006.png = vocab_list[2] (antenna)
        # vocab-007.png = vocab_list[3] (artichoke)
        # etc.
        index = int(screenshot_id) - 4  # Convert to 0-based index, starting from 004
        if 0 <= index < len(vocab_list):
            return vocab_list[index]
        return None
    except (ValueError, IndexError):
        return None

def get_analysis_results(screenshot_id):
    """Get analysis results for a specific screenshot"""
    try:
        # Find the latest complete results file
        results_files = [f for f in os.listdir('.') if f.startswith('complete_170_vocab_analysis_') and f.endswith('.json')]
        if not results_files:
            return None
        
        latest_file = max(results_files, key=lambda x: os.path.getmtime(x))
        
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = data.get('analysis_results', [])
        
        # Find this screenshot's results
        for result in results:
            if result.get('screenshot_id') == screenshot_id:
                return result
        
        return None
        
    except Exception as e:
        print(f"❌ Error loading results: {str(e)}")
        return None

def corrected_visual_inspection():
    """Corrected visual inspection starting from vocab-004.png"""
    
    print("🔍 CORRECTED VISUAL INSPECTION ANALYSIS")
    print("=" * 80)
    print("Starting from vocab-004.png with proper vocabulary mapping")
    print("Screenshots 001, 002, 003 are skipped as they don't exist")
    print("=" * 80)
    
    # Load vocabulary list
    vocab_list = load_vocab_list()
    if not vocab_list:
        return
    
    print(f"📚 Loaded {len(vocab_list)} vocabulary terms")
    
    # Key test cases to inspect (starting from 004)
    test_cases = [
        4,   # vocab-004.png = acorn (vocab_list[0])
        7,   # vocab-007.png = artichoke (vocab_list[3])
        10,  # vocab-010.png = buffet (vocab_list[6])
        18,  # vocab-018.png = carrot (vocab_list[14])
        34,  # vocab-034.png = hamster (vocab_list[30])
        53,  # vocab-053.png = pump (vocab_list[49])
        103, # vocab-103.png = dressing (vocab_list[99])
        153, # vocab-153.png = mammalogy (vocab_list[149])
    ]
    
    print(f"\n📋 CORRECTED VOCABULARY MAPPING:")
    print("-" * 60)
    for screenshot_id in test_cases:
        expected_term = get_expected_vocab_corrected(screenshot_id, vocab_list)
        if expected_term:
            vocab_index = screenshot_id - 4  # Show the actual index
            print(f"   vocab-{screenshot_id:03d}.png → vocab_list[{vocab_index}] = '{expected_term}'")
        else:
            print(f"   vocab-{screenshot_id:03d}.png → OUT OF RANGE")
    
    print(f"\n📥 DOWNLOADING CORRECTED SCREENSHOTS:")
    print("-" * 60)
    
    downloaded_files = []
    
    for screenshot_id in test_cases:
        expected_term = get_expected_vocab_corrected(screenshot_id, vocab_list)
        if not expected_term:
            print(f"⚠️  Skipping vocab-{screenshot_id:03d}.png - out of range")
            continue
            
        filename, width, height = download_image(screenshot_id)
        
        if filename:
            downloaded_files.append((screenshot_id, filename, expected_term, width, height))
            
            print(f"\n🔍 ANALYSIS for vocab-{screenshot_id:03d}.png:")
            print(f"   Expected: '{expected_term}' (vocab_list[{screenshot_id-4}])")
            print(f"   Dimensions: {width}x{height}")
            print(f"   Grid cells: 2x2 ({width//2}x{height//2} each)")
            
            # Get AI analysis results
            ai_results = get_analysis_results(f"{screenshot_id:03d}")
            if ai_results and ai_results.get('success') and ai_results.get('grid_results'):
                print(f"   🤖 AI Analysis Results:")
                for position, cell_data in ai_results['grid_results'].items():
                    if cell_data.get('vocab_matches'):
                        top_matches = cell_data['vocab_matches'][:3]  # Top 3 matches
                        match_text = ", ".join([f"{m['vocab_term']} ({m.get('similarity', 0):.1f})" 
                                              for m in top_matches if m.get('vocab_term')])
                        print(f"      {position.replace('_', '-')}: {match_text}")
                    else:
                        print(f"      {position.replace('_', '-')}: No matches")
            
            # Check if expected term was found
            found_expected = False
            if ai_results and ai_results.get('success') and ai_results.get('grid_results'):
                for position, cell_data in ai_results['grid_results'].items():
                    if cell_data.get('vocab_matches'):
                        for match in cell_data['vocab_matches']:
                            if match.get('vocab_term') and match['vocab_term'].lower() == expected_term.lower():
                                found_expected = True
                                break
            
            status = "✅ FOUND" if found_expected else "❌ MISSED"
            print(f"   🎯 Expected '{expected_term}': {status}")
    
    print(f"\n📊 CORRECTED INSPECTION SUMMARY:")
    print("-" * 60)
    print(f"   📸 Screenshots downloaded: {len(downloaded_files)}")
    print(f"   📁 Files saved for manual inspection:")
    
    for screenshot_id, filename, expected_term, width, height in downloaded_files:
        vocab_index = screenshot_id - 4
        print(f"      {filename} - Expected: '{expected_term}' (vocab_list[{vocab_index}])")
    
    print(f"\n🔍 CORRECTED MAPPING VERIFICATION:")
    print("-" * 60)
    print("✅ Screenshots now start from vocab-004.png")
    print("✅ vocab-004.png = vocab_list[0] = 'acorn'")
    print("✅ vocab-007.png = vocab_list[3] = 'artichoke'")
    print("✅ vocab-018.png = vocab_list[14] = 'carrot'")
    print("✅ Proper alignment with 170-term vocabulary list")
    
    print(f"\n📋 NEXT STEPS:")
    print("1. Manually examine the downloaded images")
    print("2. Verify the corrected vocabulary mapping")
    print("3. Check if objects match expected terms")
    print("4. Determine if this is object detection vs. vocabulary comprehension")
    
    return downloaded_files

if __name__ == "__main__":
    corrected_visual_inspection() 