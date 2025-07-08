
// Grid Display Bug Fix
// Add this to the HTML to show accurate status

function showCorrectedStatus() {
    // Update status display logic
    const statusUpdates = {
        '004': { expected: 'acorn', topMatch: ['top_left'], foundElsewhere: [], wrongTop: ['top_right: bouquet', 'bottom_left: chat', 'bottom_right: preserve'] },
        '005': { expected: 'aloe', topMatch: ['top_right'], foundElsewhere: [], wrongTop: ['top_left: preserve', 'bottom_left: sandbag', 'bottom_right: sprinkler'] },
        '006': { expected: 'antenna', topMatch: ['top_right'], foundElsewhere: [], wrongTop: ['top_left: foam', 'bottom_left: cloak', 'bottom_right: carousel'] },
        '007': { expected: 'artichoke', topMatch: ['top_right'], foundElsewhere: [], wrongTop: ['top_left: cheese', 'bottom_left: swordfish', 'bottom_right: facade'] },
        '008': { expected: 'bamboo', topMatch: ['top_right', 'bottom_right'], foundElsewhere: [], wrongTop: ['top_left: chat', 'bottom_left: sprinkler'] },
        '009': { expected: 'barrel', topMatch: ['bottom_left'], foundElsewhere: [], wrongTop: ['top_left: foam', 'top_right: antenna', 'bottom_right: preserve'] }
    };
    
    // Apply visual indicators
    Object.entries(statusUpdates).forEach(([imageId, status]) => {
        const imageElement = document.querySelector(`[data-image-id="${imageId}"]`);
        if (imageElement) {
            // Update header status
            const header = imageElement.querySelector('.efficientnet-image-header');
            if (header) {
                const hasTopMatch = status.topMatch.length > 0;
                const statusText = hasTopMatch ? 
                    '✅ CORRECT (Top Match)' : 
                    (status.foundElsewhere.length > 0 ? '🔶 FOUND (Not Top)' : '❌ NOT FOUND');
                
                header.innerHTML = header.innerHTML.replace(
                    /✅ CORRECT|❌ INCORRECT/,
                    statusText
                );
                
                // Update header styling
                header.className = hasTopMatch ? 'correct-detection' : 'partial-detection';
            }
            
            // Update grid cells
            status.wrongTop.forEach(wrongInfo => {
                const [position, wrongTerm] = wrongInfo.split(': ');
                const cell = imageElement.querySelector(`[data-position="${position}"]`);
                if (cell) {
                    cell.innerHTML += `<div style="color: #dc3545; font-size: 0.7em;">❌ Wrong: ${wrongTerm}</div>`;
                    cell.classList.add('wrong-top-match');
                }
            });
        }
    });
    
    console.log('🔧 Grid display corrected for vocab-004 through vocab-009');
}

// Auto-apply when results are loaded
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(showCorrectedStatus, 1000);
});
