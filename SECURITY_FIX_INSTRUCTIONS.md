# 🔐 URGENT: Email Password Security Issue

## ⚠️ Critical Security Alert

Your Gmail App Password **`ppirnmtyjqedsvxb`** was accidentally committed to Git and is now exposed in your repository history.

## 🚨 Immediate Actions Required

### Step 1: Revoke the Compromised Password

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in with your Google account: **sout.anujpal@gmail.com**
3. Find the app password for VirtualCafe (or any password created around the same time)
4. Click **"Remove"** or **"Revoke"** to delete the compromised password

### Step 2: Generate a New App Password

1. Still on https://myaccount.google.com/apppasswords
2. Click **"Select app"** and choose **"Mail"**
3. Click **"Select device"** and choose **"Other (Custom name)"**
4. Enter: **"VirtualCafe - New"**
5. Click **"Generate"**
6. Google will show you a 16-character password like: `abcd efgh ijkl mnop`
7. **Copy this password** (remove spaces: `abcdefghijklmnop`)

### Step 3: Update Your .env File

1. Open the file: `.env` in your project root
2. Find the line: `EMAIL_HOST_PASSWORD=YOUR_NEW_APP_PASSWORD_HERE`
3. Replace `YOUR_NEW_APP_PASSWORD_HERE` with your new password
4. Save the file

Example:
```
EMAIL_HOST_PASSWORD=abcdefghijklmnop
```

### Step 4: Restart Your Server

```powershell
# Stop the current server (Ctrl+C in the terminal)
# Then restart:
python manage.py runserver
```

### Step 5: Test Email Functionality

```powershell
python test_email.py
```

If you see "✅ TEST EMAIL SENT SUCCESSFULLY!" then everything is working!

## ✅ Security Improvements Made

I've already implemented these security improvements:

1. ✅ **SECRET_KEY** moved to `.env` (new key generated)
2. ✅ **EMAIL_HOST_PASSWORD** moved to `.env` (waiting for your new password)
3. ✅ **DEBUG** now reads from `.env` (defaults to False for safety)
4. ✅ **ALLOWED_HOSTS** restricted (no more wildcards)
5. ✅ `.env` is in `.gitignore` (won't be committed again)

## 🔒 What Changed in settings.py

- **Before:** Secrets hardcoded in settings.py (exposed in Git)
- **After:** All secrets in .env file (never committed to Git)
- **Bonus:** Added validation to ensure secrets are set

## 📝 Additional Notes

### Why This Matters

- The old password is in your **public Git history**
- Anyone can clone your repository and see it
- They could use it to send emails from your account
- This could lead to spam, phishing, or account suspension

### Git History Cleanup (Optional)

To remove the exposed password from Git history:

```powershell
# WARNING: This rewrites Git history and requires force push
# Only do this if you understand the risks

# Install BFG Repo-Cleaner
# Download from: https://rtyley.github.io/bfg-repo-cleaner/

# Remove sensitive strings
bfg --replace-text passwords.txt

# Force push (will affect all collaborators)
git push --force
```

For now, **just changing the password is sufficient** if others don't have write access to your account.

## 🆘 Need Help?

If you encounter any issues:

1. Check that `.env` file exists in your project root
2. Verify the new password has no spaces
3. Make sure you restarted the Django server
4. Check for typos in the `.env` file

## ✨ You're Almost Done!

Just complete Steps 1-5 above and you'll be secure! 🎉
