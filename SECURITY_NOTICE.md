# ⚠️ SECURITY NOTICE

## API Key Security

**NEVER commit API keys or sensitive credentials to Git!**

### Required Security Measures:

1. **Use Environment Variables**
   - All API keys must be stored in `.env` or `.env.local` files
   - These files must be in `.gitignore`

2. **API Key Restrictions (Firebase/Google Cloud)**
   - Set HTTP referrer restrictions
   - Set API restrictions
   - Use separate keys for development/production

3. **For Frontend Apps**
   - Firebase API keys in frontend are "public" but must be restricted
   - Always set domain restrictions in Firebase Console
   - Enable App Check for additional security

4. **For Backend Services**
   - Use Secret Manager (GCP) or similar services
   - Never expose backend API keys

### If Keys Are Exposed:

1. Immediately regenerate the exposed keys
2. Add restrictions to new keys
3. Review logs for unauthorized usage
4. Update all applications using the keys

### Best Practices:

- Rotate API keys regularly
- Use different keys for dev/staging/production
- Monitor API usage in console
- Set up billing alerts
- Use service accounts where possible

## Environment Files Structure:

```
frontend/.env.local (git-ignored)
├── Firebase config (domain-restricted)
└── Public API endpoints

.env (git-ignored)
├── Backend API keys
├── Database credentials
└── Private service keys
```

Remember: Security is everyone's responsibility!