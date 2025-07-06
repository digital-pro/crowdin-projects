#!/usr/bin/env python3
"""
Run Complete Analysis with Fixed Hybrid Analyzer
"""

import os
import json
import time
from fixed_hybrid_analyzer import FixedHybridAnalyzer

class CompleteFixedAnalyzer(FixedHybridAnalyzer):
    def run_complete_analysis(self, start_id=4, end_id=173):
        """Run complete analysis on all vocab images with the fixed analyzer"""
        print(f"🚀 RUNNING COMPLETE FIXED ANALYSIS")
        print(f"📊 Processing vocab-{start_id:03d} to vocab-{end_id:03d}")
        print(f"🎯 Expected images: {end_id - start_id + 1}")
        print("=" * 80)
        
        start_time = time.time()
        processed_count = 0
        
        for i in range(start_id, end_id + 1):
            screenshot_id = f"{i:03d}"
            vocab_index = i - 4
            expected_vocab = self.vocab_terms[vocab_index] if vocab_index < len(self.vocab_terms) else None
            
            image_url = f"https://raw.githubusercontent.com/levante-framework/core-tasks/more-tasks-tested/golden-runs/vocab/vocab-{screenshot_id}.png"
            
            result = self.analyze_image_hybrid(image_url, screenshot_id, expected_vocab)
            self.results.append(result)
            
            processed_count += 1
            
            # Progress update every 10 images
            if processed_count % 10 == 0:
                elapsed = time.time() - start_time
                rate = processed_count / elapsed
                remaining = (end_id - start_id + 1 - processed_count) / rate if rate > 0 else 0
                print(f"   📊 Progress: {processed_count}/{end_id - start_id + 1} images ({rate:.1f}/s, ~{remaining:.0f}s remaining)")
        
        # Calculate final statistics
        total_time = time.time() - start_time
        successful_results = [r for r in self.results if r.get('success')]
        correct_detections = sum(1 for r in successful_results if r.get('has_correct_detection'))
        images_with_detections = sum(1 for r in successful_results if r.get('has_any_detection'))
        
        print(f"\n🎉 COMPLETE FIXED ANALYSIS RESULTS!")
        print("=" * 80)
        print(f"   📸 Images processed: {len(successful_results)}")
        print(f"   ⏱️ Processing time: {total_time:.1f}s ({len(successful_results)/total_time:.1f} images/s)")
        print(f"   🎯 Accuracy: {correct_detections/len(successful_results)*100:.1f}% ({correct_detections}/{len(successful_results)})")
        print(f"   🔍 Detection rate: {images_with_detections/len(successful_results)*100:.1f}% ({images_with_detections}/{len(successful_results)})")
        print(f"   🗺️ Class mappings: {len(self.class_mapping)}")
        print(f"   📊 Total detections: {sum(self.detection_frequency.values())}")
        print(f"   🏆 Top detections: {dict(self.detection_frequency.most_common(10))}")
        
        return self.results
    
    def save_results(self, output_dir="fixed_hybrid_results"):
        """Save results in format compatible with web interface"""
        print(f"\n💾 SAVING RESULTS to {output_dir}/")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save detailed results
        detailed_results = {
            'analysis_results': self.results,
            'class_mappings': self.class_mapping,
            'validation_stats': dict(self.validation_stats),
            'detection_frequency': dict(self.detection_frequency),
            'total_cells_analyzed': self.total_cells_analyzed
        }
        
        with open(f"{output_dir}/detailed_results.json", 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, indent=2)
        
        # Convert to web-compatible format
        web_results = {
            'class_mapping': self.class_mapping,
            'detection_frequency': dict(self.detection_frequency),
            'analysis_results': self.results
        }
        
        timestamp = int(time.time())
        web_filename = f"fixed_hybrid_results_{timestamp}.json"
        
        with open(web_filename, 'w', encoding='utf-8') as f:
            json.dump(web_results, f, indent=2)
        
        print(f"✅ Detailed results: {output_dir}/detailed_results.json")
        print(f"✅ Web-compatible results: {web_filename}")
        
        return web_filename
    
    def generate_summary_report(self):
        """Generate a summary report of the analysis"""
        successful_results = [r for r in self.results if r.get('success')]
        
        print(f"\n📋 DETAILED SUMMARY REPORT")
        print("=" * 80)
        
        # Test cases performance
        test_cases = ['004', '007', '008', '009', '010', '018', '034', '153']
        print(f"🧪 KEY TEST CASES PERFORMANCE:")
        print("-" * 60)
        
        for test_id in test_cases:
            result = next((r for r in successful_results if r.get('screenshot_id') == test_id), None)
            if result:
                expected = result.get('expected_vocab')
                correct = result.get('has_correct_detection')
                any_detection = result.get('has_any_detection')
                
                status = "✅ CORRECT" if correct else ("🔍 DETECTED" if any_detection else "❌ MISSED")
                print(f"  vocab-{test_id} ({expected}): {status}")
        
        # Accuracy by ranges
        print(f"\n📊 ACCURACY BY RANGES:")
        print("-" * 60)
        
        ranges = [
            (4, 13, "Early (004-013)"),
            (14, 50, "Mid-Early (014-050)"),
            (51, 100, "Mid-Late (051-100)"),
            (101, 173, "Late (101-173)")
        ]
        
        for start, end, label in ranges:
            range_results = [r for r in successful_results 
                           if start <= int(r.get('screenshot_id', '0')) <= end]
            if range_results:
                correct = sum(1 for r in range_results if r.get('has_correct_detection'))
                accuracy = correct / len(range_results) * 100
                print(f"  {label}: {accuracy:.1f}% ({correct}/{len(range_results)})")
        
        # Top vocabulary detections
        print(f"\n🏆 TOP VOCABULARY DETECTIONS:")
        print("-" * 60)
        
        for vocab_term, count in self.detection_frequency.most_common(15):
            print(f"  {vocab_term}: {count} detections")
        
        # Mapping quality analysis
        print(f"\n🎯 MAPPING QUALITY ANALYSIS:")
        print("-" * 60)
        
        mapping_types = {}
        for stats in self.validation_stats.values():
            mapping_type = stats.get('mapping_type', 'unknown')
            mapping_types[mapping_type] = mapping_types.get(mapping_type, 0) + 1
        
        for mapping_type, count in mapping_types.items():
            print(f"  {mapping_type}: {count} mappings")

def main():
    """Run the complete fixed analysis"""
    print("🚀 STARTING COMPLETE FIXED HYBRID ANALYSIS")
    print("🔧 Using the bug-fixed version that builds mappings immediately")
    print("=" * 80)
    
    # Initialize analyzer
    analyzer = CompleteFixedAnalyzer()
    
    # Run complete analysis
    results = analyzer.run_complete_analysis()
    
    # Save results
    web_filename = analyzer.save_results()
    
    # Generate summary report
    analyzer.generate_summary_report()
    
    print(f"\n🎉 ANALYSIS COMPLETE!")
    print("=" * 80)
    print(f"📊 Results saved to: {web_filename}")
    print(f"🌐 To view results in web interface:")
    print(f"   1. Open real-imagenet-resnet.html")
    print(f"   2. Click 'Show Enhanced EfficientNet-21k (Fixed)' button")
    print(f"   3. Load the file: {web_filename}")
    print(f"")
    print(f"🔍 Expected improvements:")
    print(f"   • vocab-007 (artichoke): Should now detect correctly")
    print(f"   • vocab-008 (bamboo): Should now detect correctly")
    print(f"   • vocab-009 (barrel): Should now detect correctly")
    print(f"   • Overall accuracy: Should be significantly higher")

if __name__ == "__main__":
    main() 