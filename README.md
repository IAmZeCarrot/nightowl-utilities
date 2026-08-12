# NightOwl Utilities

A dark Windows desktop utility suite with:

- live CPU, memory, and drive dashboard
- drive-capacity overview
- large-file finder
- exact duplicate finder using SHA-256
- Downloads organizer with preview and confirmation
- Microsoft Defender scan interface
- hash-verified self-updates from GitHub releases

The app never silently deletes files. The organizer will not overwrite an
existing file. Duplicate results are informational so that you can review them.

## Try it from source

Install Python 3.11+, then double-click `run-dev.bat`.

## Put it on GitHub

1. Create an empty GitHub repository, for example `nightowl-utilities`.
2. Upload every file and folder from this project. Keep `.github/workflows/release.yml`.
3. Run the source version and open **Updates**. Enter `YOUR_USERNAME/nightowl-utilities`.
4. Commit future changes, update `VERSION` near the top of `app.py`, then create
   and push a matching tag:

```powershell
git add .
git commit -m "Release 1.0.1"
git push
git tag v1.0.1
git push origin v1.0.1
```

GitHub Actions builds `NightOwlUtilities.exe`, attaches it to a release, hashes
it, and updates `latest.json`. Existing packaged copies can then install the
update from the **Updates** screen.

## Important update details

- The repository must be public for anonymous update checks.
- Updates download only the release EXE and static `latest.json`; no token or
  external API key is used.
- The SHA-256 must match before an update is installed.
- GitHub's release workflow must be allowed to write repository contents under
  **Settings > Actions > General > Workflow permissions**.
- Code-signing is not included. Windows SmartScreen may warn about unsigned
  EXEs until you sign the app with a trusted certificate or it gains reputation.

## Local EXE build

```powershell
python -m pip install -r requirements.txt
pyinstaller --clean NightOwlUtilities.spec
```

The result is `dist\NightOwlUtilities.exe`.
