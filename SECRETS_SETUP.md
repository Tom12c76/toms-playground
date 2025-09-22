# 🔐 API Keys and Secrets Configuration

This document explains how to securely configure API keys for the toms-playground project using Streamlit's secrets management system.

## 📁 File Structure

```
toms-playground/
├── .streamlit/
│   └── secrets.toml          # Your API keys (DO NOT COMMIT)
├── streamlit_secrets_helper.py # Helper functions for accessing secrets
└── .gitignore                # Excludes secrets.toml from git
```

## 🚀 Quick Setup

### 1. Configure Google Gemini API

1. **Get your API key**:
   - Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
   - Sign in with your Google account
   - Click "Create API Key"
   - Copy the generated key

2. **Add to secrets.toml**:
   ```toml
   [google]
   api_key = "AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q"
   ```

### 2. Configure Refinitiv Data API

1. **Get your credentials** from Refinitiv/LSEG

2. **Add to secrets.toml**:
   ```toml
   [refinitiv]
   app_key = "your_actual_app_key_here"
   username = "your_actual_username_here"
   password = "your_actual_password_here"
   ```

### 3. Configure Refinitiv RDP (Optional)

For Refinitiv Data Platform access:

```toml
[refinitiv.rdp]
client_id = "your_rdp_client_id"
client_secret = "your_rdp_client_secret"
```

## 📋 Complete secrets.toml Example

```toml
# Streamlit Secrets Configuration
[google]
api_key = "AIzaSyA1B2C3D4E5F6G7H8I9J0K1L2M3N4O5P6Q"

[refinitiv]
app_key = "ABC123DEF456GHI789"
username = "your.email@company.com"
password = "YourSecurePassword123"

[refinitiv.rdp]
client_id = "RDP_CLIENT_ID_12345"
client_secret = "rdp_secret_abcdef123456"

[other_apis]
# Add other API keys as needed
# morningstar_api_key = "your_morningstar_key"
# bloomberg_api_key = "your_bloomberg_key"
```

## 🛡️ Security Best Practices

### ✅ DO:
- Keep `secrets.toml` in the `.streamlit/` folder
- Use strong, unique passwords
- Regularly rotate API keys
- Limit API key permissions to minimum required
- Monitor API usage for unusual activity

### ❌ DON'T:
- Commit `secrets.toml` to version control
- Share API keys in code, emails, or chat
- Use API keys in public repositories
- Store secrets in environment variables on shared systems

## 🔧 Using Secrets in Code

### Import the helper module:
```python
from streamlit_secrets_helper import (
    get_google_api_key,
    get_refinitiv_credentials,
    check_secrets_status
)
```

### Get API keys:
```python
# Google Gemini API
api_key = get_google_api_key()

# Refinitiv credentials
creds = get_refinitiv_credentials()
if creds:
    app_key = creds["app_key"]
    username = creds["username"]
    password = creds["password"]
```

### Check configuration status:
```python
status = check_secrets_status()
print(f"Google API: {'✅' if status['google_gemini'] else '❌'}")
print(f"Refinitiv: {'✅' if status['refinitiv_data'] else '❌'}")
```

## 🚨 Troubleshooting

### "Secrets not found" error:
1. Check that `.streamlit/secrets.toml` exists
2. Verify the TOML syntax is correct
3. Ensure you've replaced placeholder values
4. Restart your Streamlit app after changes

### API connection errors:
1. Verify your API keys are valid
2. Check that you have the correct permissions
3. Ensure you're not hitting rate limits
4. Check network connectivity

### Import errors:
1. Make sure `streamlit_secrets_helper.py` is in the correct location
2. Check Python path configuration
3. Verify all required packages are installed

## 📞 Getting API Access

### Google Gemini API:
- **Free tier**: Available with rate limits
- **Sign up**: [Google AI Studio](https://aistudio.google.com)
- **Documentation**: [Google AI for Developers](https://ai.google.dev)

### Refinitiv Data API:
- **Professional subscription** required
- **Contact**: [Refinitiv Sales](https://www.refinitiv.com/en/contact-us)
- **Documentation**: [Refinitiv Data Library](https://developers.refinitiv.com/en/api-catalog/refinitiv-data-library)

## 🔄 Updating Secrets

When you update `secrets.toml`:
1. Save the file
2. Streamlit will automatically detect changes
3. The app will reload with new credentials
4. No need to restart manually

## 🏥 Backup and Recovery

### Backup your secrets:
- Store a secure copy of your API keys
- Consider using a password manager
- Document which keys are used where

### Recovery:
- Regenerate compromised keys immediately
- Update `secrets.toml` with new keys
- Test all functionality after key rotation