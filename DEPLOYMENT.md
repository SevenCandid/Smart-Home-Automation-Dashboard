# Deployment Guide

## Pushing to GitHub

### 1. Create a GitHub Repository

1. Go to [GitHub](https://github.com) and sign in
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Name it (e.g., `Smart-Home-Automation-Dashboard`)
5. Choose public or private
6. **DO NOT** initialize with README, .gitignore, or license (we already have these)
7. Click "Create repository"

### 2. Connect Local Repository to GitHub

Run these commands in your terminal (replace `YOUR_USERNAME` and `YOUR_REPO_NAME`):

```bash
# Add the remote repository
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git

# Rename branch to main (if needed)
git branch -M main

# Push your code
git push -u origin main
```

### 3. Verify

Visit your GitHub repository URL to confirm all files are uploaded.

## Deploying to Vercel

### Prerequisites
- GitHub account
- Vercel account (sign up at [vercel.com](https://vercel.com))

### Steps

1. **Import Repository in Vercel**
   - Go to [Vercel Dashboard](https://vercel.com/dashboard)
   - Click "Add New..." → "Project"
   - Import your GitHub repository
   - Vercel will auto-detect the configuration

2. **Configure Project**
   - **Framework Preset**: Other (or leave as auto-detected)
   - **Root Directory**: `./` (default)
   - **Build Command**: Leave empty (not needed for Python)
   - **Output Directory**: Leave empty
   - **Install Command**: `pip install -r requirements.txt`

3. **Environment Variables** (if needed)
   - No environment variables required for basic setup
   - Database will be created automatically in `/tmp` directory

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete (usually 1-2 minutes)

### Vercel Configuration

The project is already configured for Vercel:

- ✅ `vercel.json` - Serverless function configuration
- ✅ `api/index.py` - Vercel handler for Flask app
- ✅ Database path - Automatically uses `/tmp` on Vercel
- ✅ Static files - Served from `/static` directory
- ✅ All routes - Handled by Flask app

### Important Notes

1. **Database Persistence**: 
   - Vercel serverless functions are stateless
   - Database is stored in `/tmp` which is ephemeral
   - Data will reset on each deployment or after inactivity
   - For production, consider using an external database (PostgreSQL, MongoDB, etc.)

2. **Cold Starts**:
   - First request may be slower (cold start)
   - Subsequent requests are fast

3. **File System**:
   - Only `/tmp` is writable in Vercel serverless functions
   - Static files are read-only

### Troubleshooting

**Issue**: Database not persisting
- **Solution**: This is expected behavior. Use external database for production.

**Issue**: Import errors
- **Solution**: Ensure `requirements.txt` includes all dependencies

**Issue**: Static files not loading
- **Solution**: Check `vercel.json` routes configuration

**Issue**: 500 errors
- **Solution**: Check Vercel function logs in dashboard

## Post-Deployment

After deployment, your dashboard will be available at:
```
https://your-project-name.vercel.app
```

All 16 devices and features will work:
- ✅ Device controls
- ✅ Scene activation
- ✅ Energy monitoring
- ✅ Real-time updates

## Updating

To update your deployment:

```bash
# Make changes locally
git add .
git commit -m "Your update message"
git push origin main
```

Vercel will automatically redeploy on push to main branch.

