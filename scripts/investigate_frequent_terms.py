#!/usr/bin/env python3
"""
Investigate Frequent Terms
Analyze why certain vocabulary terms like bamboo and artichoke appear so frequently
"""

import json
import os
from collections import Counter

def investigate_frequent_terms():
    """Investigate why certain terms appear so frequently"""
    
    print("🔍 INVESTIGATING FREQUENT VOCABULARY TERMS")
    print("=" * 80)
    print("Analyzing why 'bamboo' and 'artichoke' appear so frequently")
    print("=" * 80)
    
    # Find the latest complete results file
    results_files = [f for f in os.listdir('.') if f.startswith('complete_170_vocab_analysis_') and f.endswith('.json')]
    if not results_files:
        print("❌ No complete results file found!")
        return
    
    latest_file = max(results_files, key=lambda x: os.path.getmtime(x))
    print(f"📁 Reading results from: {latest_file}")
    
    try:
        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        results = data.get('analysis_results', [])
        class_mapping = data.get('class_mapping', {})
        
        print(f"\n📊 ANALYSIS OVERVIEW:")
        print(f"   📸 Total screenshots: {len(results)}")
        print(f"   🔍 Class mappings: {len(class_mapping)}")
        
        # Count all vocabulary term occurrences
        vocab_term_counts = Counter()
        class_index_counts = Counter()
        position_term_counts = {}
        
        # Track which class indices map to frequent terms
        bamboo_classes = []
        artichoke_classes = []
        
        for class_idx, vocab_term in class_mapping.items():
            if vocab_term.lower() == 'bamboo':
                bamboo_classes.append(class_idx)
            elif vocab_term.lower() == 'artichoke':
                artichoke_classes.append(class_idx)
        
        print(f"\n🔍 CLASS MAPPING ANALYSIS:")
        print(f"   🎋 'bamboo' mapped to {len(bamboo_classes)} class indices: {bamboo_classes[:10]}...")
        print(f"   🥬 'artichoke' mapped to {len(artichoke_classes)} class indices: {artichoke_classes[:10]}...")
        
        # Analyze all results
        total_vocab_matches = 0
        for result in results:
            if result.get('success') and result.get('grid_results'):
                for position, cell_data in result['grid_results'].items():
                    if cell_data.get('vocab_matches'):
                        for match in cell_data['vocab_matches']:
                            vocab_term = match.get('vocab_term')
                            if vocab_term:
                                vocab_term_counts[vocab_term] += 1
                                total_vocab_matches += 1
                                
                                # Track position-specific counts
                                if position not in position_term_counts:
                                    position_term_counts[position] = Counter()
                                position_term_counts[position][vocab_term] += 1
                                
                                # Track class indices
                                if 'class_idx' in match:
                                    class_index_counts[match['class_idx']] += 1
        
        # Show most frequent terms
        print(f"\n🏆 TOP 15 MOST FREQUENT VOCABULARY TERMS:")
        print("-" * 60)
        top_terms = vocab_term_counts.most_common(15)
        for i, (term, count) in enumerate(top_terms):
            percentage = (count / total_vocab_matches * 100) if total_vocab_matches > 0 else 0
            print(f"   {i+1:2d}. {term}: {count} occurrences ({percentage:.1f}%)")
        
        # Analyze the suspicious frequent terms
        suspicious_terms = ['bamboo', 'artichoke', 'blender']
        
        print(f"\n🚨 SUSPICIOUS FREQUENT TERMS ANALYSIS:")
        print("-" * 60)
        
        for term in suspicious_terms:
            if term in vocab_term_counts:
                count = vocab_term_counts[term]
                percentage = (count / total_vocab_matches * 100) if total_vocab_matches > 0 else 0
                
                print(f"\n📋 '{term.upper()}' ANALYSIS:")
                print(f"   Total occurrences: {count} ({percentage:.1f}% of all matches)")
                
                # Find which class indices are mapped to this term
                mapped_classes = [idx for idx, vocab in class_mapping.items() if vocab.lower() == term.lower()]
                print(f"   Mapped to {len(mapped_classes)} class indices: {mapped_classes[:15]}...")
                
                # Show position distribution
                print(f"   Position distribution:")
                for position in ['top_left', 'top_right', 'bottom_left', 'bottom_right']:
                    pos_count = position_term_counts.get(position, {}).get(term, 0)
                    print(f"      {position.replace('_', '-')}: {pos_count} occurrences")
                
                # Find examples where this term appears
                print(f"   Example screenshots with '{term}':")
                example_count = 0
                for result in results:
                    if example_count >= 5:  # Show max 5 examples
                        break
                    if result.get('success') and result.get('grid_results'):
                        found_in_image = False
                        positions_found = []
                        for position, cell_data in result['grid_results'].items():
                            if cell_data.get('vocab_matches'):
                                for match in cell_data['vocab_matches']:
                                    if match.get('vocab_term', '').lower() == term.lower():
                                        positions_found.append(position)
                                        found_in_image = True
                                        break
                        
                        if found_in_image:
                            screenshot_id = result.get('screenshot_id', 'unknown')
                            print(f"      vocab-{screenshot_id}.png: {', '.join(positions_found)}")
                            example_count += 1
        
        # Analyze class mapping quality
        print(f"\n🔍 CLASS MAPPING QUALITY ANALYSIS:")
        print("-" * 60)
        
        # Count how many class indices map to each vocabulary term
        vocab_to_class_count = Counter()
        for vocab_term in class_mapping.values():
            vocab_to_class_count[vocab_term] += 1
        
        print(f"   Vocabulary terms with most class mappings:")
        for term, class_count in vocab_to_class_count.most_common(10):
            print(f"      '{term}': {class_count} class indices")
        
        # Check for potential over-mapping
        print(f"\n⚠️  POTENTIAL ISSUES:")
        print("-" * 60)
        
        over_mapped_threshold = 20  # If a term maps to >20 classes, it might be over-mapped
        over_mapped_terms = [(term, count) for term, count in vocab_to_class_count.items() if count > over_mapped_threshold]
        
        if over_mapped_terms:
            print(f"   🚨 Terms mapped to too many class indices (>{over_mapped_threshold}):")
            for term, count in over_mapped_terms:
                print(f"      '{term}': {count} class indices (possibly over-mapped)")
        else:
            print(f"   ✅ No terms appear to be over-mapped")
        
        # Check for low-confidence mappings
        print(f"\n💡 RECOMMENDATIONS:")
        print("-" * 60)
        print("1. Review class mapping discovery algorithm")
        print("2. Increase confidence thresholds for class mapping")
        print("3. Implement class mapping validation")
        print("4. Consider filtering out mappings with too many class indices")
        print("5. Manually verify frequent terms like 'bamboo' and 'artichoke'")
        
        print(f"\n🎯 NEXT STEPS:")
        print("1. Examine the downloaded inspection images manually")
        print("2. Check if images actually contain bamboo/artichoke")
        print("3. If not, the class mapping discovery needs refinement")
        print("4. Consider implementing stricter mapping validation")
        
        return {
            'vocab_term_counts': vocab_term_counts,
            'class_mapping': class_mapping,
            'over_mapped_terms': over_mapped_terms,
            'suspicious_terms': {term: vocab_term_counts.get(term, 0) for term in suspicious_terms}
        }
        
    except Exception as e:
        print(f"❌ Error analyzing results: {str(e)}")
        return None

if __name__ == "__main__":
    investigate_frequent_terms() 