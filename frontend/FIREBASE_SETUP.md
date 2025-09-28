# Firebase Setup Guide

## 🔐 Security Notice
All API keys have been removed from the source code. You must configure your own Firebase credentials.

## 📋 Prerequisites

1. Firebase project created at https://console.firebase.google.com
2. Node.js 18+ installed
3. Firebase CLI installed (`npm install -g firebase-tools`)

## 🚀 Quick Setup

### 1. Configure Environment Variables

```bash
# Copy the template
cp .env.example .env.local

# Edit .env.local and add your Firebase credentials
# Get these from Firebase Console > Project Settings > General
```

### 2. Enable Firebase Services

In Firebase Console:

1. **Authentication**
   - Go to Authentication > Sign-in method
   - Enable Anonymous authentication (minimum)
   - Optionally enable Email/Password or Google

2. **Firestore Database**
   - Go to Firestore Database
   - Create database in production mode
   - Rules will be deployed from `firestore.rules`

3. **Storage** (if needed)
   - Go to Storage
   - Set up default bucket

### 3. Deploy the Application

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

## 📁 File Structure

```
frontend/
├── .env.example          # Template for environment variables
├── .env.local            # Your actual config (gitignored)
├── .firebaserc           # Firebase project configuration
├── firebase.json         # Firebase hosting configuration
├── firestore.rules       # Security rules
├── firestore.indexes.json # Database indexes
└── deploy.sh            # Deployment script
```

## 🔧 Manual Deployment

If you prefer manual deployment:

```bash
# 1. Build the project
npm run build

# 2. Deploy hosting only
firebase deploy --only hosting

# 3. Deploy Firestore rules
firebase deploy --only firestore:rules

# 4. Deploy Firestore indexes
firebase deploy --only firestore:indexes

# 5. Deploy everything
firebase deploy
```

## 🛠️ Troubleshooting

### Error: Firebase configuration is incomplete
- Ensure all required environment variables are set in `.env.local`
- Restart the dev server after changing environment variables

### Error: Permission denied
- Check Firestore security rules
- Ensure Authentication is properly configured
- Verify user is authenticated before database operations

### Storage bucket issue
- Default format: `your-project-id.appspot.com`
- Some projects may use: `your-project-id.firebasestorage.app`
- Check actual bucket name in Firebase Console > Storage

## 🔑 API Key Rotation

If you need to rotate your API keys:

1. Go to Firebase Console > Project Settings
2. Navigate to the "General" tab
3. Find your web app configuration
4. Generate new credentials if needed
5. Update `.env.local` with new values
6. Restart your application

## 🚨 Important Security Notes

1. **Never commit `.env.local` to version control**
2. **Set up domain restrictions** in Firebase Console > Authentication > Settings
3. **Configure Firestore rules** appropriately for your use case
4. **Monitor usage** in Firebase Console to detect unusual activity
5. **Enable App Check** for additional security in production

## 📚 Resources

- [Firebase Documentation](https://firebase.google.com/docs)
- [Vite Environment Variables](https://vitejs.dev/guide/env-and-mode.html)
- [Firebase Security Rules](https://firebase.google.com/docs/firestore/security/get-started)
- [Firebase Hosting](https://firebase.google.com/docs/hosting)