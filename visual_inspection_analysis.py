#!/usr/bin/env python3
"""
Visual Inspection Analysis
Downloads and analyzes specific vocabulary screenshots to understand content vs. expected terms
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

def analyze_grid_cells(screenshot_id, width, height):
    """Analyze what's in each grid cell"""
    print(f"\n🔍 GRID CELL ANALYSIS for vocab-{screenshot_id:03d}.png ({width}x{height}):")
    
    # Calculate grid positions (2x2 grid)
    cell_width = width // 2
    cell_height = height // 2
    
    positions = {
        'top_left': (0, 0, cell_width, cell_height),
        'top_right': (cell_width, 0, width, cell_height),
        'bottom_left': (0, cell_height, cell_width, height),
        'bottom_right': (cell_width, cell_height, width, height)
    }
    
    for position, (x1, y1, x2, y2) in positions.items():
        print(f"   {position.replace('_', '-')}: pixels ({x1},{y1}) to ({x2},{y2}) - {x2-x1}x{y2-y1}")
    
    return positions

def inspect_vocabulary_screenshots():
    """Inspect key vocabulary screenshots"""
    
    print("🔍 VISUAL INSPECTION ANALYSIS")
    print("=" * 80)
    print("Downloading and analyzing key vocabulary screenshots to understand")
    print("what objects are actually present vs. expected vocabulary terms.")
    print("=" * 80)
    
    # Load vocabulary list
    vocab_list = load_vocab_list()
    if not vocab_list:
        return
    
    # Key test cases to inspect
    test_cases = [
        1,   # acorn
        4,   # artichoke  
        7,   # blender
        15,  # carrot
        31,  # hamster
        50,  # pump
        100, # (vocab_list[99]) 
        150, # (vocab_list[149])
    ]
    
    print(f"📋 VOCABULARY TERMS TO INSPECT:")
    for screenshot_id in test_cases:
        if screenshot_id <= len(vocab_list):
            expected_term = vocab_list[screenshot_id - 1]
            print(f"   vocab-{screenshot_id:03d}.png → Expected: '{expected_term}'")
    
    print(f"\n📥 DOWNLOADING SCREENSHOTS:")
    print("-" * 60)
    
    downloaded_files = []
    
    for screenshot_id in test_cases:
        if screenshot_id <= len(vocab_list):
            expected_term = vocab_list[screenshot_id - 1]
            filename, width, height = download_image(screenshot_id)
            
            if filename:
                downloaded_files.append((screenshot_id, filename, expected_term, width, height))
                
                # Analyze grid cells
                positions = analyze_grid_cells(screenshot_id, width, height)
                
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
                print()
    
    print(f"📊 INSPECTION SUMMARY:")
    print("-" * 60)
    print(f"   📸 Screenshots downloaded: {len(downloaded_files)}")
    print(f"   📁 Files saved for manual inspection:")
    
    for screenshot_id, filename, expected_term, width, height in downloaded_files:
        print(f"      {filename} - Expected: '{expected_term}' ({width}x{height})")
    
    print(f"\n🔍 ANALYSIS INSIGHTS:")
    print("-" * 60)
    print("1. Each screenshot is divided into a 2x2 grid (4 cells)")
    print("2. The AI analyzes each cell independently")
    print("3. Expected vocabulary terms may not be literal objects in the images")
    print("4. Some vocabulary terms might be:")
    print("   - Abstract concepts (e.g., 'dressing', 'mammalogy')")
    print("   - Actions (e.g., 'juggling', 'peeking')")
    print("   - Adjectives (e.g., 'furry', 'rickety')")
    print("   - Complex scenes rather than single objects")
    
    print(f"\n📋 NEXT STEPS:")
    print("1. Manually examine the downloaded images")
    print("2. Compare what you see vs. what the AI detected")
    print("3. Check if vocabulary terms match visual content")
    print("4. Consider if this is a language comprehension task vs. object detection")
    
    print(f"\n🎯 KEY QUESTIONS TO INVESTIGATE:")
    print("- Are the images showing literal objects matching vocabulary terms?")
    print("- Or are they showing scenes/contexts where vocabulary terms apply?")
    print("- Is this testing vocabulary knowledge rather than object recognition?")
    
    return downloaded_files

if __name__ == "__main__":
    inspect_vocabulary_screenshots() 