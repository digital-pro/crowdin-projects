#!/usr/bin/env python3
"""
Comprehensive Analysis of All 170 Vocabulary Screenshots
Analyzes all 680 images (170 screenshots × 4 grid cells) to evaluate vocabulary term identification performance
"""

from github_vocab_analyzer import Enhanced21kVocabAnalyzer
import json
import time
from collections import defaultdict, Counter
import os

def analyze_all_vocabulary_screenshots():
    """Analyze all 170 vocabulary screenshots with enhanced EfficientNet-21k"""
    
    print("🚀 COMPREHENSIVE VOCABULARY ANALYSIS")
    print("=" * 80)
    print("📊 Target: 170 screenshots × 4 grid cells = 680 total images")
    print("🎯 Goal: Evaluate vocabulary term identification performance")
    print("=" * 80)
    
    # Initialize enhanced analyzer
    analyzer = Enhanced21kVocabAnalyzer()
    
    # Phase 1: Build class mappings from first 50 images (vocab-004 to vocab-053)
    print("\n🔍 PHASE 1: Building class mappings from first 50 images...")
    print("   Processing vocab-004 to vocab-053 to discover class mappings...")
    
    phase1_results, initial_mappings = analyzer.analyze_vocabulary_dataset(start_id=4, end_id=53)
    
    print(f"✅ Phase 1 Complete:")
    print(f"   📸 Images analyzed: {len(phase1_results)}")
    print(f"   🔍 Class mappings discovered: {len(initial_mappings)}")
    print(f"   📚 Vocabulary terms mapped: {len(set(initial_mappings.values()))}")
    
    # Phase 2: Expand mappings with next 50 images (vocab-054 to vocab-103)
    print(f"\n🔍 PHASE 2: Expanding class mappings with next 50 images...")
    print("   Processing vocab-054 to vocab-103 to expand mappings...")
    
    phase2_results, expanded_mappings = analyzer.analyze_vocabulary_dataset(start_id=54, end_id=103)
    
    print(f"✅ Phase 2 Complete:")
    print(f"   📸 Images analyzed: {len(phase2_results)}")
    print(f"   🔍 Total class mappings: {len(expanded_mappings)}")
    print(f"   📚 Vocabulary terms mapped: {len(set(expanded_mappings.values()))}")
    
    # Phase 3: Final expansion with remaining images (vocab-104 to vocab-173)
    print(f"\n🔍 PHASE 3: Final analysis of remaining images...")
    print("   Processing vocab-104 to vocab-173 to complete analysis...")
    
    phase3_results, final_mappings = analyzer.analyze_vocabulary_dataset(start_id=104, end_id=173)
    
    print(f"✅ Phase 3 Complete:")
    print(f"   📸 Images analyzed: {len(phase3_results)}")
    print(f"   🔍 Total class mappings: {len(final_mappings)}")
    print(f"   📚 Vocabulary terms mapped: {len(set(final_mappings.values()))}")
    
    # Combine all results
    all_results = phase1_results + phase2_results + phase3_results
    total_images = len(all_results)
    total_grid_cells = total_images * 4
    
    print(f"\n🎉 ANALYSIS COMPLETE!")
    print(f"=" * 80)
    print(f"📊 FINAL STATISTICS:")
    print(f"   📸 Total screenshots analyzed: {total_images}")
    print(f"   🔲 Total grid cells processed: {total_grid_cells}")
    print(f"   🔍 Total class mappings discovered: {len(final_mappings)}")
    print(f"   📚 Vocabulary terms successfully mapped: {len(set(final_mappings.values()))}")
    print(f"=" * 80)
    
    # Analyze vocabulary identification performance
    print(f"\n📈 VOCABULARY IDENTIFICATION PERFORMANCE:")
    print("-" * 60)
    
    # Count vocabulary matches and accuracy
    vocab_stats = analyze_vocabulary_performance(all_results, analyzer.vocab_terms)
    
    # Print performance metrics
    print(f"✅ ACCURACY METRICS:")
    print(f"   🎯 Images with vocabulary matches: {vocab_stats['images_with_matches']}/{total_images} ({vocab_stats['match_rate']:.1f}%)")
    print(f"   🔍 Total vocabulary matches found: {vocab_stats['total_matches']}")
    print(f"   📊 Average matches per image: {vocab_stats['avg_matches_per_image']:.2f}")
    print(f"   🏆 Correct vocabulary identifications: {vocab_stats['correct_identifications']}")
    print(f"   ✅ Accuracy rate: {vocab_stats['accuracy_rate']:.1f}%")
    
    # Show top performing vocabulary terms
    print(f"\n🏆 TOP PERFORMING VOCABULARY TERMS:")
    for i, (term, count) in enumerate(vocab_stats['top_terms'][:15]):
        print(f"   {i+1:2d}. {term}: {count} identifications")
    
    # Show grid position analysis
    print(f"\n📍 GRID POSITION ANALYSIS:")
    for position, stats in vocab_stats['grid_positions'].items():
        print(f"   {position}: {stats['matches']} matches ({stats['rate']:.1f}%)")
    
    # Show match type distribution
    print(f"\n🔍 MATCH TYPE DISTRIBUTION:")
    for match_type, count in vocab_stats['match_types'].items():
        print(f"   {match_type}: {count} matches ({count/vocab_stats['total_matches']*100:.1f}%)")
    
    # Test specific challenging cases
    print(f"\n🧪 TESTING SPECIFIC CASES:")
    test_cases = [
        ("004", "acorn"),
        ("010", "buffet"),
        ("015", "carrot"),
        ("020", "coaster"),
        ("050", "map"),
        ("100", "turkey"),
        ("150", "bandage")
    ]
    
    for screenshot_id, expected_term in test_cases:
        test_result = test_specific_image(analyzer, screenshot_id, expected_term)
        if test_result:
            print(f"   vocab-{screenshot_id} (expected: {expected_term}): {test_result}")
    
    # Save comprehensive results
    comprehensive_data = {
        'metadata': {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_screenshots': total_images,
            'total_grid_cells': total_grid_cells,
            'class_mappings_discovered': len(final_mappings),
            'vocabulary_terms_mapped': len(set(final_mappings.values())),
            'analysis_phases': 3
        },
        'performance_metrics': vocab_stats,
        'class_mapping': final_mappings,
        'discovered_classes': dict(analyzer.discovered_classes),
        'analysis_results': all_results,
        'statistics': {
            'total_images': total_images,
            'total_grid_cells': total_grid_cells,
            'processing_time': sum(r.get('processing_time', 0) for r in all_results if 'processing_time' in r),
            'images_per_second': analyzer.statistics.get('images_per_second', 0) if hasattr(analyzer, 'statistics') else 0,
            'class_mappings_found': len(final_mappings)
        }
    }
    
    # Save results
    output_file = f"complete_170_vocab_analysis_{int(time.time())}.json"
    with open(output_file, 'w') as f:
        json.dump(comprehensive_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 RESULTS SAVED:")
    print(f"   📁 File: {output_file}")
    print(f"   📊 Size: {os.path.getsize(output_file) / 1024 / 1024:.1f} MB")
    
    # Generate summary report
    generate_summary_report(comprehensive_data)
    
    return comprehensive_data

def analyze_vocabulary_performance(results, vocab_terms):
    """Analyze vocabulary identification performance across all results"""
    
    images_with_matches = 0
    total_matches = 0
    correct_identifications = 0
    vocab_term_counts = Counter()
    match_types = Counter()
    grid_positions = defaultdict(lambda: {'matches': 0, 'total': 0})
    
    for result in results:
        if not result.get('success'):
            continue
            
        image_has_match = False
        expected_vocab = result.get('expected_vocab')
        if expected_vocab:
            expected_vocab = expected_vocab.lower()
        else:
            expected_vocab = ''
        
        for position, cell_data in result.get('grid_results', {}).items():
            grid_positions[position]['total'] += 1
            
            if cell_data.get('vocab_matches'):
                vocab_matches = cell_data['vocab_matches']
                total_matches += len(vocab_matches)
                
                if not image_has_match:
                    images_with_matches += 1
                    image_has_match = True
                
                grid_positions[position]['matches'] += 1
                
                # Count vocabulary terms and match types
                for match in vocab_matches:
                    vocab_term_counts[match['vocab_term']] += 1
                    match_types[match['match_type']] += 1
                    
                    # Check if this is a correct identification
                    if expected_vocab and match.get('vocab_term') and match['vocab_term'].lower() == expected_vocab:
                        correct_identifications += 1
    
    # Calculate rates
    total_images = len([r for r in results if r.get('success')])
    match_rate = (images_with_matches / total_images * 100) if total_images > 0 else 0
    accuracy_rate = (correct_identifications / total_matches * 100) if total_matches > 0 else 0
    avg_matches_per_image = total_matches / total_images if total_images > 0 else 0
    
    # Calculate grid position rates
    for position in grid_positions:
        total = grid_positions[position]['total']
        matches = grid_positions[position]['matches']
        grid_positions[position]['rate'] = (matches / total * 100) if total > 0 else 0
    
    return {
        'images_with_matches': images_with_matches,
        'total_matches': total_matches,
        'correct_identifications': correct_identifications,
        'match_rate': match_rate,
        'accuracy_rate': accuracy_rate,
        'avg_matches_per_image': avg_matches_per_image,
        'top_terms': vocab_term_counts.most_common(20),
        'match_types': dict(match_types),
        'grid_positions': dict(grid_positions)
    }

def test_specific_image(analyzer, screenshot_id, expected_term):
    """Test vocabulary identification on a specific image"""
    try:
        image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{screenshot_id}.png"
        result = analyzer.analyze_vocab_screenshot(image_url, screenshot_id, expected_term)
        
        if result['success']:
            found_terms = []
            for position, cell_data in result['grid_results'].items():
                if cell_data.get('vocab_matches'):
                    for match in cell_data['vocab_matches'][:1]:  # Top match only
                        if match.get('vocab_term') and match['vocab_term'].lower() == expected_term.lower():
                            found_terms.append(f"✅ {match['vocab_term']} in {position}")
                        elif match.get('vocab_term'):
                            found_terms.append(f"❌ {match['vocab_term']} in {position}")
                        else:
                            found_terms.append(f"❓ No term in {position}")
            
            return f"Found: {', '.join(found_terms[:2])}" if found_terms else "No matches"
        else:
            return "Analysis failed"
    except Exception as e:
        return f"Error: {str(e)}"

def generate_summary_report(data):
    """Generate a human-readable summary report"""
    
    report_file = f"vocabulary_analysis_report_{int(time.time())}.txt"
    
    with open(report_file, 'w') as f:
        f.write("🚀 ENHANCED EFFICIENTNET-21K VOCABULARY ANALYSIS REPORT\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"📊 ANALYSIS OVERVIEW:\n")
        f.write(f"   Date: {data['metadata']['timestamp']}\n")
        f.write(f"   Screenshots analyzed: {data['metadata']['total_screenshots']}\n")
        f.write(f"   Grid cells processed: {data['metadata']['total_grid_cells']}\n")
        f.write(f"   Class mappings discovered: {data['metadata']['class_mappings_discovered']}\n")
        f.write(f"   Vocabulary terms mapped: {data['metadata']['vocabulary_terms_mapped']}\n\n")
        
        f.write(f"🎯 PERFORMANCE METRICS:\n")
        metrics = data['performance_metrics']
        f.write(f"   Images with vocabulary matches: {metrics['images_with_matches']}\n")
        f.write(f"   Total vocabulary matches: {metrics['total_matches']}\n")
        f.write(f"   Vocabulary match rate: {metrics['match_rate']:.1f}%\n")
        f.write(f"   Accuracy rate: {metrics['accuracy_rate']:.1f}%\n")
        f.write(f"   Average matches per image: {metrics['avg_matches_per_image']:.2f}\n\n")
        
        f.write(f"🏆 TOP VOCABULARY TERMS IDENTIFIED:\n")
        for i, (term, count) in enumerate(metrics['top_terms'][:20]):
            f.write(f"   {i+1:2d}. {term}: {count} identifications\n")
        
        f.write(f"\n📍 GRID POSITION PERFORMANCE:\n")
        for position, stats in metrics['grid_positions'].items():
            f.write(f"   {position}: {stats['matches']} matches ({stats['rate']:.1f}%)\n")
        
        f.write(f"\n🔍 MATCH TYPE DISTRIBUTION:\n")
        for match_type, count in metrics['match_types'].items():
            percentage = count / metrics['total_matches'] * 100
            f.write(f"   {match_type}: {count} matches ({percentage:.1f}%)\n")
    
    print(f"   📄 Report: vocabulary_analysis_report_{int(time.time())}.txt")

def main():
    """Main function to run the comprehensive analysis"""
    
    print("🎯 ENHANCED EFFICIENTNET-21K VOCABULARY ANALYSIS")
    print("This will analyze all 170 vocabulary screenshots (680 total images)")
    print("Expected processing time: ~15-20 minutes")
    print()
    
    # Confirm before starting
    response = input("Start comprehensive analysis? (y/n): ").lower().strip()
    if response != 'y':
        print("❌ Analysis cancelled")
        return
    
    # Run analysis
    start_time = time.time()
    
    try:
        results = analyze_all_vocabulary_screenshots()
        
        total_time = time.time() - start_time
        print(f"\n🎉 ANALYSIS COMPLETE!")
        print(f"⏱️  Total processing time: {total_time/60:.1f} minutes")
        print(f"🚀 Processing speed: {680/total_time:.1f} images/second")
        
        return results
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Analysis interrupted by user")
        print(f"⏱️  Partial analysis time: {(time.time() - start_time)/60:.1f} minutes")
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        print("Please check:")
        print("- Internet connection for downloading images")
        print("- Available disk space for results")
        print("- GPU memory availability")

if __name__ == "__main__":
    main() 