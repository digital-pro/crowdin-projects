#!/usr/bin/env python3
"""
Simple Vocabulary Analysis Script
Analyzes vocabulary screenshots to evaluate EfficientNet-21k performance
"""

from github_vocab_analyzer import Enhanced21kVocabAnalyzer
import json
import time

def main():
    """Run a simple vocabulary analysis"""
    
    print("🚀 Simple EfficientNet-21k Vocabulary Analysis")
    print("=" * 60)
    print("📊 This will analyze vocabulary screenshots to test performance")
    print()
    
    # Initialize analyzer
    analyzer = Enhanced21kVocabAnalyzer()
    
    # Start with a smaller batch to test
    print("🔍 Starting with first 30 images to build class mappings...")
    
    try:
        results, mappings = analyzer.analyze_vocabulary_dataset(start_id=4, end_id=33)
        
        print(f"\n✅ Analysis Complete!")
        print(f"   📸 Images analyzed: {len(results)}")
        print(f"   🔍 Class mappings discovered: {len(mappings)}")
        print(f"   📚 Vocabulary terms mapped: {len(set(mappings.values()))}")
        
        # Count successful vocabulary matches
        successful_images = 0
        total_vocab_matches = 0
        
        for result in results:
            if result.get('success') and result.get('grid_results'):
                image_has_vocab = False
                for position, cell_data in result['grid_results'].items():
                    if cell_data.get('vocab_matches') and len(cell_data['vocab_matches']) > 0:
                        total_vocab_matches += len(cell_data['vocab_matches'])
                        if not image_has_vocab:
                            successful_images += 1
                            image_has_vocab = True
        
        print(f"\n📈 Performance Metrics:")
        print(f"   🎯 Images with vocabulary matches: {successful_images}/{len(results)} ({successful_images/len(results)*100:.1f}%)")
        print(f"   🔍 Total vocabulary matches found: {total_vocab_matches}")
        print(f"   📊 Average matches per image: {total_vocab_matches/len(results):.2f}")
        
        # Test the acorn case specifically
        print(f"\n🧪 Testing vocab-004 (acorn)...")
        test_result = analyzer.analyze_vocab_screenshot(
            "https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-004.png",
            "004",
            "acorn"
        )
        
        if test_result['success']:
            print("✅ vocab-004 results:")
            for position, cell_data in test_result['grid_results'].items():
                if cell_data.get('vocab_matches') and len(cell_data['vocab_matches']) > 0:
                    top_match = cell_data['vocab_matches'][0]
                    print(f"   {position}: {top_match['vocab_term']} ({top_match['match_type']}, {top_match['similarity']:.2f})")
        
        # Save results
        output_data = {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'images_analyzed': len(results),
            'class_mappings_discovered': len(mappings),
            'vocabulary_terms_mapped': len(set(mappings.values())),
            'successful_images': successful_images,
            'total_vocab_matches': total_vocab_matches,
            'class_mapping': mappings,
            'analysis_results': results
        }
        
        output_file = f"simple_vocab_analysis_{int(time.time())}.json"
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {output_file}")
        
        # Ask if user wants to continue with more images
        print(f"\n🤔 Continue with more images?")
        print("   Type 'y' to analyze more images (vocab-034 to vocab-063)")
        print("   Type 'all' to analyze ALL remaining images (vocab-034 to vocab-173)")
        print("   Type 'n' to stop here")
        
        choice = input("Choice (y/all/n): ").lower().strip()
        
        if choice == 'y':
            print("\n🔍 Analyzing next 30 images...")
            more_results, final_mappings = analyzer.analyze_vocabulary_dataset(start_id=34, end_id=63)
            print(f"✅ Additional analysis complete! Total mappings: {len(final_mappings)}")
            
        elif choice == 'all':
            print("\n🔍 Analyzing ALL remaining images (this will take 15-20 minutes)...")
            print("Press Ctrl+C to stop at any time.")
            
            # Analyze in chunks
            all_results = results.copy()
            current_mappings = mappings.copy()
            
            for start_id in range(34, 174, 30):  # Process in chunks of 30
                end_id = min(start_id + 29, 173)
                print(f"   Processing vocab-{start_id:03d} to vocab-{end_id:03d}...")
                
                chunk_results, current_mappings = analyzer.analyze_vocabulary_dataset(start_id, end_id)
                all_results.extend(chunk_results)
                
                print(f"   ✅ Chunk complete. Total mappings: {len(current_mappings)}")
            
            print(f"\n🎉 COMPLETE ANALYSIS FINISHED!")
            print(f"   📸 Total images: {len(all_results)}")
            print(f"   🔍 Final class mappings: {len(current_mappings)}")
            
            # Save complete results
            complete_output = {
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_images_analyzed': len(all_results),
                'total_grid_cells': len(all_results) * 4,
                'class_mappings_discovered': len(current_mappings),
                'vocabulary_terms_mapped': len(set(current_mappings.values())),
                'class_mapping': current_mappings,
                'analysis_results': all_results
            }
            
            complete_file = f"complete_vocab_analysis_{int(time.time())}.json"
            with open(complete_file, 'w') as f:
                json.dump(complete_output, f, indent=2, ensure_ascii=False)
            
            print(f"💾 Complete results saved to: {complete_file}")
        
        print(f"\n✅ Analysis session complete!")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Analysis failed: {str(e)}")
        print("This might be due to:")
        print("- Internet connection issues")
        print("- GPU memory limitations")
        print("- Missing dependencies")

if __name__ == "__main__":
    main() 