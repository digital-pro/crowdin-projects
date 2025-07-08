// Fix for Grid Display Bug
// This script improves the grid display to show when expected terms are found but not as top matches

function fixGridDisplayBug() {
    // Add CSS for partial matches
    const style = document.createElement('style');
    style.textContent = `
        .partial-detection {
            background: linear-gradient(135deg, #fff3cd 0%, #ffeaa7 100%) !important;
            border-color: #ffc107 !important;
        }
        
        .partial-match {
            background: rgba(255, 193, 7, 0.1) !important;
            border: 2px solid #ffc107 !important;
        }
        
        .efficientnet-grid-cell.partial-match {
            background: linear-gradient(135deg, rgba(255, 193, 7, 0.1) 0%, rgba(255, 193, 7, 0.2) 100%);
        }
    `;
    document.head.appendChild(style);
    
    console.log('🔧 Grid display bug fix applied!');
    console.log('✅ Green icons = Expected term is top match');
    console.log('🔶 Orange icons = Expected term found but not top match');
    console.log('❌ Red = Expected term not found');
}

// Apply the fix when the page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', fixGridDisplayBug);
} else {
    fixGridDisplayBug();
} 