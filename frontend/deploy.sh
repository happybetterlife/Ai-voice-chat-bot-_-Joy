#!/bin/bash

echo "🚀 Voice Agent Firebase Deployment"
echo "=================================="

# Check Firebase CLI
if ! command -v firebase &> /dev/null; then
    echo "❌ Firebase CLI not found. Installing..."
    npm install -g firebase-tools
fi

# Check if logged in
if ! firebase projects:list &> /dev/null; then
    echo "❌ Not logged into Firebase. Please login:"
    firebase login
fi

# Build project
echo "🔨 Building project..."
npm run build

if [ $? -ne 0 ]; then
    echo "❌ Build failed!"
    exit 1
fi

# Deploy to Firebase
echo "📤 Deploying to Firebase..."
firebase deploy --project voice-chatbot-8f3a1 --only hosting

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo "🌐 Your app is live at: https://voice-chatbot-8f3a1.web.app"
else
    echo "❌ Deployment failed!"
    exit 1
fi