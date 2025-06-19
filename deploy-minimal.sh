#!/bin/bash

# Deploy script for minimal cost Azure Functions
echo "🚀 Deploying FastAPI to Azure Functions (Minimal Cost Mode)"

# Set environment variables for cost optimization
export SLS_DEBUG=false
export SLS_DEPRECATION_DISABLE=true

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first:"
    echo "   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -"
    echo "   sudo apt-get install -y nodejs"
    exit 1
fi

# Check if we have npm permissions, if not use local installation
echo "📦 Installing dependencies..."
if [ -w "/usr/local/lib/node_modules" ]; then
    # Global installation (if permissions allow)
    npm install -g serverless@3
else
    # Local installation (recommended for permission issues)
    echo "Using local installation due to permission restrictions..."
    npm init -y 2>/dev/null || true
    npm install serverless@3 serverless-azure-functions --save-dev
    export PATH="$PATH:./node_modules/.bin"
fi

# Verify serverless is available
if ! command -v sls &> /dev/null; then
    echo "❌ Serverless Framework not found. Trying alternative installation..."
    # Try using npx instead
    echo "Using npx for serverless commands..."
    alias sls="npx serverless"
fi

# Install Azure plugin
echo "🔧 Installing Azure Functions plugin..."
if command -v sls &> /dev/null; then
    sls plugin install -n serverless-azure-functions
else
    npx serverless plugin install -n serverless-azure-functions
fi

# Check if Azure CLI is installed and logged in
if ! command -v az &> /dev/null; then
    echo "❌ Azure CLI is not installed. Please install it first:"
    echo "   curl -sL https://aka.ms/InstallAzureCLI | sudo bash"
    exit 1
fi

# Check if logged in to Azure
if ! az account show &> /dev/null; then
    echo "❌ Not logged in to Azure. Please run: az login"
    exit 1
fi

echo "🔧 Deploying with cost-optimized settings..."
if command -v sls &> /dev/null; then
    sls deploy --stage dev --verbose
else
    npx serverless deploy --stage dev --verbose
fi

echo "✅ Deployment complete!"
echo "💡 Cost Optimization Tips:"
echo "   - Functions run on Consumption Plan (pay-per-execution)"
echo "   - Minimum memory allocation (128MB)"
echo "   - 30-second timeout limit"
echo "   - Limited to 1 concurrent execution"
echo "   - Application Insights disabled"
echo "   - Minimal logging enabled"

echo "📊 Expected costs:"
echo "   - First 1M executions: FREE"
echo "   - Storage: ~\$0.05/month for minimal usage"
echo "   - Total expected: \$0-2/month for low traffic"

echo "🌐 Your API endpoints:"
if command -v sls &> /dev/null; then
    sls info --stage dev
else
    npx serverless info --stage dev
fi