#!/usr/bin/env python3
"""
Comprehensive EfficientNet-21k Vocabulary Analysis
Analyzes more vocabulary images to build comprehensive class mappings
"""

from github_vocab_analyzer import Enhanced21kVocabAnalyzer
import json
import time

def main():
    """Run comprehensive analysis with more images"""
    print("🚀 Comprehensive EfficientNet-21k Vocabulary Analysis")
    print("=" * 70)
    
    analyzer = Enhanced21kVocabAnalyzer()
    
    # Phase 1: Build initial mappings (images 4-30)
    print("\n🔍 Phase 1: Building class mappings from images 4-30...")
    results_phase1, mappings_phase1 = analyzer.analyze_vocabulary_dataset(start_id=4, end_id=30)
    
    print(f"\n📊 Phase 1 Results:")
    print(f"   Images analyzed: {len(results_phase1)}")
    print(f"   Class mappings discovered: {len(mappings_phase1)}")
    
    # Phase 2: Expand mappings (images 31-60)
    print("\n🔍 Phase 2: Expanding class mappings from images 31-60...")
    results_phase2, mappings_phase2 = analyzer.analyze_vocabulary_dataset(start_id=31, end_id=60)
    
    print(f"\n📊 Phase 2 Results:")
    print(f"   Images analyzed: {len(results_phase2)}")
    print(f"   Total class mappings discovered: {len(mappings_phase2)}")
    
    # Phase 3: Final expansion (images 61-90)
    print("\n🔍 Phase 3: Final expansion from images 61-90...")
    results_phase3, mappings_phase3 = analyzer.analyze_vocabulary_dataset(start_id=61, end_id=90)
    
    print(f"\n📊 Phase 3 Results:")
    print(f"   Images analyzed: {len(results_phase3)}")
    print(f"   Total class mappings discovered: {len(mappings_phase3)}")
    
    # Combine all results
    all_results = results_phase1 + results_phase2 + results_phase3
    final_mappings = mappings_phase3  # This includes all accumulated mappings
    
    print(f"\n🎯 Final Comprehensive Results:")
    print(f"   Total images analyzed: {len(all_results)}")
    print(f"   Total class mappings discovered: {len(final_mappings)}")
    
    # Test on vocab-004 with comprehensive mappings
    print(f"\n🧪 Testing comprehensive system on vocab-004...")
    test_result = analyzer.analyze_vocab_screenshot(
        "https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-004.png",
        "004",
        "acorn"
    )
    
    if test_result['success']:
        print("✅ vocab-004 test results with comprehensive mappings:")
        for position, cell_result in test_result['grid_results'].items():
            if cell_result.get('vocab_matches'):
                print(f"   {position}: Found {len(cell_result['vocab_matches'])} vocabulary matches")
                for match in cell_result['vocab_matches'][:3]:
                    print(f"     • {match['vocab_term']} ({match['match_type']}, {match['similarity']:.2f})")
    
    # Save comprehensive results
    comprehensive_data = {
        'analysis_results': all_results,
        'class_mapping': final_mappings,
        'discovered_classes': dict(analyzer.discovered_classes),
        'statistics': {
            'total_images': len(all_results),
            'total_processing_time': sum(r.get('processing_time', 0) for r in all_results if 'processing_time' in r),
            'class_mappings_found': len(final_mappings),
            'phases': {
                'phase1': {'images': len(results_phase1), 'mappings': len(mappings_phase1)},
                'phase2': {'images': len(results_phase2), 'mappings': len(mappings_phase2)},
                'phase3': {'images': len(results_phase3), 'mappings': len(mappings_phase3)}
            }
        }
    }
    
    output_file = f"comprehensive_21k_vocab_analysis_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Comprehensive results saved to: {output_file}")
    
    # Show top vocabulary terms found
    vocab_counts = {}
    for vocab_term, class_indices in final_mappings.items():
        if isinstance(class_indices, list):
            vocab_counts[vocab_term] = len(class_indices)
        else:
            vocab_counts[vocab_term] = 1
    
    print(f"\n📚 Top Vocabulary Terms by Class Mapping Count:")
    sorted_vocab = sorted(vocab_counts.items(), key=lambda x: x[1], reverse=True)
    for i, (term, count) in enumerate(sorted_vocab[:20]):
        print(f"   {i+1:2d}. {term}: {count} class mappings")
    
    return comprehensive_data

if __name__ == "__main__":
    main() 