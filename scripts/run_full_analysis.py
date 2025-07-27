#!/usr/bin/env python3
"""
Complete Vocabulary Analysis - All 170 Screenshots
Automatically analyzes all 680 images (170 screenshots × 4 grid cells)
"""

from github_vocab_analyzer import Enhanced21kVocabAnalyzer
import json
import time
from collections import Counter

def run_complete_analysis():
    """Run complete analysis of all 170 vocabulary screenshots"""
    
    print("🚀 COMPLETE VOCABULARY ANALYSIS - ALL 170 SCREENSHOTS")
    print("=" * 80)
    print("📊 Target: 170 screenshots × 4 grid cells = 680 total images")
    print("🎯 Goal: Complete vocabulary identification evaluation")
    print("⏱️  Estimated time: 15-20 minutes")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = Enhanced21kVocabAnalyzer()
    
    # Track all results
    all_results = []
    start_time = time.time()
    
    try:
        # Process in chunks of 30 for better progress tracking
        chunk_size = 30
        total_chunks = ((173 - 4 + 1) + chunk_size - 1) // chunk_size  # Ceiling division
        
        for chunk_num in range(total_chunks):
            start_id = 4 + (chunk_num * chunk_size)
            end_id = min(start_id + chunk_size - 1, 173)
            
            print(f"\n🔍 CHUNK {chunk_num + 1}/{total_chunks}: Processing vocab-{start_id:03d} to vocab-{end_id:03d}")
            print(f"   Progress: {len(all_results)}/170 images completed")
            
            chunk_start = time.time()
            chunk_results, current_mappings = analyzer.analyze_vocabulary_dataset(start_id, end_id)
            chunk_time = time.time() - chunk_start
            
            all_results.extend(chunk_results)
            
            print(f"   ✅ Chunk {chunk_num + 1} complete in {chunk_time:.1f}s")
            print(f"   📊 Class mappings: {len(current_mappings)}")
            print(f"   🎯 Total progress: {len(all_results)}/170 ({len(all_results)/170*100:.1f}%)")
            
            # Show ETA
            if len(all_results) > 0:
                elapsed = time.time() - start_time
                rate = len(all_results) / elapsed
                remaining = 170 - len(all_results)
                eta = remaining / rate if rate > 0 else 0
                print(f"   ⏱️  ETA: {eta/60:.1f} minutes remaining")
        
        # Final analysis
        total_time = time.time() - start_time
        total_images = len(all_results)
        total_grid_cells = total_images * 4
        final_mappings = current_mappings
        
        print(f"\n🎉 COMPLETE ANALYSIS FINISHED!")
        print(f"=" * 80)
        print(f"📊 FINAL STATISTICS:")
        print(f"   📸 Total screenshots analyzed: {total_images}")
        print(f"   🔲 Total grid cells processed: {total_grid_cells}")
        print(f"   🔍 Class mappings discovered: {len(final_mappings)}")
        print(f"   📚 Vocabulary terms mapped: {len(set(final_mappings.values()))}")
        print(f"   ⏱️  Total processing time: {total_time/60:.1f} minutes")
        print(f"   🚀 Processing speed: {total_grid_cells/total_time:.1f} images/second")
        print(f"=" * 80)
        
        # Analyze performance
        print(f"\n📈 VOCABULARY IDENTIFICATION PERFORMANCE:")
        print("-" * 60)
        
        successful_images = 0
        total_vocab_matches = 0
        correct_identifications = 0
        vocab_term_counts = Counter()
        grid_position_matches = {'top_left': 0, 'top_right': 0, 'bottom_left': 0, 'bottom_right': 0}
        
        for result in all_results:
            if result.get('success') and result.get('grid_results'):
                image_has_vocab = False
                expected_vocab = result.get('expected_vocab', '').lower() if result.get('expected_vocab') else ''
                
                for position, cell_data in result['grid_results'].items():
                    if cell_data.get('vocab_matches') and len(cell_data['vocab_matches']) > 0:
                        vocab_matches = cell_data['vocab_matches']
                        total_vocab_matches += len(vocab_matches)
                        
                        if not image_has_vocab:
                            successful_images += 1
                            image_has_vocab = True
                        
                        grid_position_matches[position] += 1
                        
                        # Count vocabulary terms
                        for match in vocab_matches:
                            if match.get('vocab_term'):
                                vocab_term_counts[match['vocab_term']] += 1
                                
                                # Check for correct identification
                                if expected_vocab and match['vocab_term'].lower() == expected_vocab:
                                    correct_identifications += 1
        
        # Calculate rates
        match_rate = (successful_images / total_images * 100) if total_images > 0 else 0
        accuracy_rate = (correct_identifications / total_vocab_matches * 100) if total_vocab_matches > 0 else 0
        avg_matches_per_image = total_vocab_matches / total_images if total_images > 0 else 0
        
        print(f"✅ PERFORMANCE METRICS:")
        print(f"   🎯 Images with vocabulary matches: {successful_images}/{total_images} ({match_rate:.1f}%)")
        print(f"   🔍 Total vocabulary matches found: {total_vocab_matches}")
        print(f"   📊 Average matches per image: {avg_matches_per_image:.2f}")
        print(f"   🏆 Correct vocabulary identifications: {correct_identifications}")
        print(f"   ✅ Accuracy rate: {accuracy_rate:.1f}%")
        
        # Show top vocabulary terms
        print(f"\n🏆 TOP VOCABULARY TERMS IDENTIFIED:")
        top_terms = vocab_term_counts.most_common(20)
        for i, (term, count) in enumerate(top_terms):
            print(f"   {i+1:2d}. {term}: {count} identifications")
        
        # Show grid position performance
        print(f"\n📍 GRID POSITION ANALYSIS:")
        total_positions = sum(grid_position_matches.values())
        for position, count in grid_position_matches.items():
            percentage = (count / total_positions * 100) if total_positions > 0 else 0
            print(f"   {position.replace('_', '-')}: {count} matches ({percentage:.1f}%)")
        
        # Test specific challenging cases
        print(f"\n🧪 TESTING KEY VOCABULARY TERMS:")
        test_cases = [
            ("004", "acorn"),
            ("015", "carrot"), 
            ("031", "hamster"),
            ("050", "map"),
            ("100", "turkey"),
            ("150", "bandage")
        ]
        
        for screenshot_id, expected_term in test_cases:
            # Find this result in our data
            test_result = None
            for result in all_results:
                if result.get('screenshot_id') == screenshot_id:
                    test_result = result
                    break
            
            if test_result and test_result.get('success'):
                found_expected = False
                matches_found = []
                for position, cell_data in test_result['grid_results'].items():
                    if cell_data.get('vocab_matches'):
                        for match in cell_data['vocab_matches'][:1]:  # Top match only
                            if match.get('vocab_term'):
                                if match['vocab_term'].lower() == expected_term.lower():
                                    matches_found.append(f"✅ {match['vocab_term']} in {position}")
                                    found_expected = True
                                else:
                                    matches_found.append(f"❌ {match['vocab_term']} in {position}")
                
                result_text = f"Found: {', '.join(matches_found[:2])}" if matches_found else "No matches"
                status = "✅ CORRECT" if found_expected else "❌ MISSED"
                print(f"   vocab-{screenshot_id} ({expected_term}): {status} - {result_text}")
        
        # Save comprehensive results
        output_data = {
            'metadata': {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_screenshots': total_images,
                'total_grid_cells': total_grid_cells,
                'class_mappings_discovered': len(final_mappings),
                'vocabulary_terms_mapped': len(set(final_mappings.values())),
                'processing_time_minutes': total_time / 60,
                'processing_speed_images_per_second': total_grid_cells / total_time
            },
            'performance_metrics': {
                'images_with_matches': successful_images,
                'total_vocab_matches': total_vocab_matches,
                'match_rate_percent': match_rate,
                'accuracy_rate_percent': accuracy_rate,
                'avg_matches_per_image': avg_matches_per_image,
                'correct_identifications': correct_identifications,
                'top_vocabulary_terms': dict(top_terms),
                'grid_position_performance': grid_position_matches
            },
            'class_mapping': final_mappings,
            'analysis_results': all_results
        }
        
        # Save results
        output_file = f"complete_170_vocab_analysis_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 RESULTS SAVED:")
        print(f"   📁 File: {output_file}")
        
        # Generate summary report
        report_file = f"vocabulary_analysis_summary_{int(time.time())}.txt"
        with open(report_file, 'w') as f:
            f.write("🚀 ENHANCED EFFICIENTNET-21K COMPLETE VOCABULARY ANALYSIS\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Analysis completed: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Screenshots analyzed: {total_images}\n")
            f.write(f"Grid cells processed: {total_grid_cells}\n")
            f.write(f"Processing time: {total_time/60:.1f} minutes\n")
            f.write(f"Processing speed: {total_grid_cells/total_time:.1f} images/second\n\n")
            f.write(f"PERFORMANCE RESULTS:\n")
            f.write(f"- Images with vocabulary matches: {successful_images}/{total_images} ({match_rate:.1f}%)\n")
            f.write(f"- Total vocabulary matches: {total_vocab_matches}\n")
            f.write(f"- Accuracy rate: {accuracy_rate:.1f}%\n")
            f.write(f"- Class mappings discovered: {len(final_mappings)}\n")
            f.write(f"- Vocabulary terms mapped: {len(set(final_mappings.values()))}\n\n")
            f.write(f"TOP VOCABULARY TERMS:\n")
            for i, (term, count) in enumerate(top_terms[:15]):
                f.write(f"{i+1:2d}. {term}: {count} identifications\n")
        
        print(f"   📄 Summary: {report_file}")
        
        print(f"\n🎉 ANALYSIS COMPLETE! Enhanced EfficientNet-21k successfully analyzed all 680 images!")
        
        return output_data
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Analysis interrupted by user")
        print(f"⏱️  Partial analysis time: {(time.time() - start_time)/60:.1f} minutes")
        print(f"📊 Images processed: {len(all_results)}/170")
        return None
        
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        print("Possible causes:")
        print("- Internet connection issues")
        print("- GPU memory limitations") 
        print("- Disk space issues")
        return None

if __name__ == "__main__":
    run_complete_analysis() 