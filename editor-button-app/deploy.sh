#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if commit message was provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: Please provide a commit message${NC}"
    echo "Usage: ./deploy.sh \"Your commit message\""
    exit 1
fi

COMMIT_MESSAGE="$1"

echo -e "${CYAN}========================================${NC}"
echo -e "${CYAN}  Crowdin Editor Button App Deployment${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""

echo -e "${YELLOW}Commit message: $COMMIT_MESSAGE${NC}"
echo ""

# Function to handle errors
handle_error() {
    echo -e "${RED}❌ Error: $1${NC}"
    echo ""
    echo -e "${YELLOW}Deployment failed. Please check the error above and try again.${NC}"
    exit 1
}

# Step 1: Git operations
echo -e "${BLUE}[1/4] Git: Adding, committing, and pushing changes...${NC}"

git add . || handle_error "Git add failed"
git commit -m "$COMMIT_MESSAGE" || handle_error "Git commit failed"
git push || handle_error "Git push failed"

echo -e "${GREEN}✅ Git operations completed successfully${NC}"
echo ""

# Step 2: Vercel deployment
echo -e "${BLUE}[2/4] Vercel: Deploying to production...${NC}"

DEPLOY_OUTPUT=$(npx vercel --prod --yes 2>&1)
DEPLOY_EXIT_CODE=$?

if [ $DEPLOY_EXIT_CODE -ne 0 ]; then
    echo -e "${RED}$DEPLOY_OUTPUT${NC}"
    handle_error "Vercel deployment failed"
fi

# Extract deployment URL
DEPLOYMENT_URL=$(echo "$DEPLOY_OUTPUT" | grep "Production:" | awk '{print $2}')

if [ -z "$DEPLOYMENT_URL" ]; then
    handle_error "Could not extract deployment URL"
fi

echo -e "${GREEN}✅ Deployed to: $DEPLOYMENT_URL${NC}"
echo ""

# Step 3: Create alias
echo -e "${BLUE}[3/4] Vercel: Creating alias...${NC}"

npx vercel alias "$DEPLOYMENT_URL" editor-button-app.vercel.app --yes || handle_error "Vercel alias failed"

echo -e "${GREEN}✅ Aliased to: https://editor-button-app.vercel.app${NC}"
echo ""

# Step 4: Final summary
echo -e "${BLUE}[4/4] Deployment Summary:${NC}"
echo -e "${CYAN}========================================${NC}"
echo -e "${GREEN}✅ Git: Changes committed and pushed${NC}"
echo -e "${GREEN}✅ Vercel: Deployed to production${NC}"
echo -e "${GREEN}✅ Alias: https://editor-button-app.vercel.app${NC}"
echo -e "${GREEN}✅ Inspect: https://vercel.com/digitalpros-projects/editor-button-app${NC}"
echo -e "${CYAN}========================================${NC}"
echo ""
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "${YELLOW}The app is now live and ready for testing in Crowdin.${NC}"
echo ""
