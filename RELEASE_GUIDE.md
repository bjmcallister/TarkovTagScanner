# Release Guide

## Automatic Builds with GitHub Actions

Your repository now has automatic build and release functionality!

## How to Create a Release

### Method 1: Using Git Tags (Recommended)

1. **Create and push a version tag:**
   ```bash
   git tag v1.0
   git push origin v1.0
   ```

2. **GitHub Actions will automatically:**
   - Build the executable
   - Create a GitHub release
   - Attach the .exe file
   - Add release notes

### Method 2: Manual Trigger

1. Go to your repository on GitHub
2. Click **Actions** tab
3. Select **Build and Release** workflow
4. Click **Run workflow** button
5. This creates a dev build artifact (not a release)

## Version Numbering

Use semantic versioning:
- `v1.0` - Major release
- `v1.1` - Minor update
- `v1.0.1` - Patch/bugfix

## What Happens

When you push a tag like `v1.0`:

```
Push tag → GitHub Actions triggers → 
  Install Python & dependencies →
  Build executable →
  Create release with notes →
  Upload .exe automatically
```

## Example Workflow

```bash
# Make your changes
git add .
git commit -m "Add new feature"
git push

# Ready to release?
git tag v1.0
git push origin v1.0

# Check GitHub releases page - your .exe is there!
```

## Updating Versions

To create a new version:

```bash
git tag v1.1
git push origin v1.1
```

GitHub will automatically build and create a new release!

## Build Time

- First build: ~5-10 minutes (downloading dependencies)
- Subsequent builds: ~3-5 minutes

## Testing

You can test the workflow by:
1. Forking your own repo
2. Pushing a test tag: `git tag test-v0.1 && git push origin test-v0.1`
3. Check Actions tab to see build progress

## Troubleshooting

If build fails:
1. Check Actions tab for error logs
2. Ensure `requirements.txt` is up to date
3. Verify `build_exe.py` works locally first

## Notes

- Only tags starting with `v` trigger releases
- Manual workflow runs create artifacts (not releases)
- You can edit release notes after creation on GitHub
