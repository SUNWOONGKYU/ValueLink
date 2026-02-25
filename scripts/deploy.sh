#!/bin/bash

###############################################################################
# ValueLink Deployment Script
# Purpose: Deploy to Vercel with pre-flight checks
# Usage: bash scripts/deploy.sh [--production | --preview]
###############################################################################

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print functions
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

###############################################################################
# Step 1: Check Required Environment Variables
###############################################################################
print_info "Checking required environment variables..."

if [ -z "$VERCEL_TOKEN" ]; then
    print_error "VERCEL_TOKEN is not set!"
    echo "Please run: export VERCEL_TOKEN=your_token"
    exit 1
fi

if [ -z "$VERCEL_ORG_ID" ]; then
    print_error "VERCEL_ORG_ID is not set!"
    echo "Please run: export VERCEL_ORG_ID=your_org_id"
    exit 1
fi

if [ -z "$VERCEL_PROJECT_ID" ]; then
    print_error "VERCEL_PROJECT_ID is not set!"
    echo "Please run: export VERCEL_PROJECT_ID=your_project_id"
    exit 1
fi

print_success "All required environment variables are set"

###############################################################################
# Step 2: Check Git Status
###############################################################################
print_info "Checking Git status..."

if ! git diff-index --quiet HEAD --; then
    print_warning "You have uncommitted changes!"
    echo "Modified files:"
    git status --short
    echo ""
    read -p "Do you want to continue anyway? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Deployment aborted"
        exit 1
    fi
fi

print_success "Git status check passed"

###############################################################################
# Step 3: Check Current Branch
###############################################################################
print_info "Checking current branch..."

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
print_info "Current branch: $CURRENT_BRANCH"

if [[ "$CURRENT_BRANCH" != "main" ]] && [[ "$CURRENT_BRANCH" != "master" ]]; then
    print_warning "You are not on main/master branch!"
    echo ""
    read -p "Deploy to preview environment? (y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_error "Deployment aborted"
        exit 1
    fi
    DEPLOY_ENV="preview"
else
    DEPLOY_ENV="production"
fi

print_success "Branch check completed (deploying to $DEPLOY_ENV)"

###############################################################################
# Step 4: Run Lint
###############################################################################
print_info "Running ESLint..."

if npm run lint; then
    print_success "Linting passed"
else
    print_error "Linting failed!"
    exit 1
fi

###############################################################################
# Step 5: Run Type Check
###############################################################################
print_info "Running TypeScript type check..."

if npx tsc --noEmit; then
    print_success "Type check passed"
else
    print_error "Type check failed!"
    exit 1
fi

###############################################################################
# Step 6: Build Project
###############################################################################
print_info "Building Next.js project..."

if npm run build; then
    print_success "Build completed successfully"
else
    print_error "Build failed!"
    exit 1
fi

###############################################################################
# Step 7: Deploy to Vercel
###############################################################################
print_info "Deploying to Vercel ($DEPLOY_ENV environment)..."

if [ "$DEPLOY_ENV" == "production" ]; then
    DEPLOYMENT_URL=$(vercel --prod --token="$VERCEL_TOKEN" 2>&1 | tee /dev/tty | grep -oP 'https://[^\s]+' | tail -1)
else
    DEPLOYMENT_URL=$(vercel --token="$VERCEL_TOKEN" 2>&1 | tee /dev/tty | grep -oP 'https://[^\s]+' | tail -1)
fi

if [ $? -eq 0 ]; then
    print_success "Deployment completed successfully!"
    echo ""
    echo "🔗 Deployment URL: $DEPLOYMENT_URL"
    echo ""
else
    print_error "Deployment failed!"
    exit 1
fi

###############################################################################
# Step 8: Summary
###############################################################################
echo ""
echo "═══════════════════════════════════════════════════════════════"
print_success "Deployment Summary"
echo "═══════════════════════════════════════════════════════════════"
echo "Environment: $DEPLOY_ENV"
echo "Branch: $CURRENT_BRANCH"
echo "URL: $DEPLOYMENT_URL"
echo "═══════════════════════════════════════════════════════════════"
