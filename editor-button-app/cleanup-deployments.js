#!/usr/bin/env node

const { execSync } = require('child_process');

async function cleanupDeployments() {
  console.log('🧹 Starting deployment cleanup...');

  try {
  // Get list of deployments
  console.log('📋 Fetching deployment list...');
  const deploymentList = execSync('vercel ls --format json', { encoding: 'utf8' });
  const deployments = JSON.parse(deploymentList);
  
  if (!deployments || deployments.length <= 1) {
    console.log('✅ No old deployments to clean up');
    return;
  }
  
  // Sort by creation date (newest first)
  deployments.sort((a, b) => new Date(b.created) - new Date(a.created));
  
  // Keep the most recent deployment, remove the rest
  const mostRecent = deployments[0];
  const toRemove = deployments.slice(1);
  
  console.log(`📌 Keeping most recent deployment: ${mostRecent.url}`);
  console.log(`🗑️  Removing ${toRemove.length} old deployments...`);
  
  // Remove old deployments in batches of 8 (Vercel limit)
  const batchSize = 8;
  for (let i = 0; i < toRemove.length; i += batchSize) {
    const batch = toRemove.slice(i, i + batchSize);
    const urls = batch.map(d => d.url).join(' ');
    
    try {
      console.log(`🔄 Removing batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(toRemove.length/batchSize)}...`);
      execSync(`vercel rm ${urls} --yes`, { stdio: 'inherit' });
      console.log(`✅ Batch ${Math.floor(i/batchSize) + 1} removed successfully`);
    } catch (error) {
      console.error(`❌ Error removing batch ${Math.floor(i/batchSize) + 1}:`, error.message);
    }
    
    // Small delay between batches to avoid rate limiting
    if (i + batchSize < toRemove.length) {
      await new Promise(resolve => setTimeout(resolve, 1000));
    }
  }
  
  console.log('🎉 Deployment cleanup completed!');
  
  // Verify final count
  const finalList = execSync('vercel ls --format json', { encoding: 'utf8' });
  const finalDeployments = JSON.parse(finalList);
  console.log(`📊 Final deployment count: ${finalDeployments.length}`);
  
} catch (error) {
  console.error('❌ Cleanup failed:', error.message);
  
  // Fallback: try to remove deployments manually if JSON parsing fails
  console.log('🔄 Attempting manual cleanup...');
  try {
    // Get deployment URLs using text parsing
    const textList = execSync('vercel ls', { encoding: 'utf8' });
    const lines = textList.split('\n');
    const deploymentUrls = [];
    
    for (const line of lines) {
      const match = line.match(/https:\/\/editor-button-[a-z0-9]+-digitalpros-projects\.vercel\.app/);
      if (match) {
        deploymentUrls.push(match[0]);
      }
    }
    
    if (deploymentUrls.length > 1) {
      // Keep the first one (most recent), remove the rest
      const toRemove = deploymentUrls.slice(1);
      console.log(`🗑️  Found ${toRemove.length} deployments to remove`);
      
      // Remove in batches
      const batchSize = 8;
      for (let i = 0; i < toRemove.length; i += batchSize) {
        const batch = toRemove.slice(i, i + batchSize);
        const urls = batch.join(' ');
        
        try {
          console.log(`🔄 Removing batch ${Math.floor(i/batchSize) + 1}...`);
          execSync(`vercel rm ${urls} --yes`, { stdio: 'inherit' });
        } catch (batchError) {
          console.error(`❌ Error in batch ${Math.floor(i/batchSize) + 1}:`, batchError.message);
        }
      }
    }
  } catch (fallbackError) {
    console.error('❌ Manual cleanup also failed:', fallbackError.message);
    process.exit(1);
  }
}

}

// Helper function for async delay
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

// Run the cleanup
cleanupDeployments().catch(console.error); 