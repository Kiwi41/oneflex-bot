# Changelog

## v1.8.1 - Notifications & Cleanup (2026-01-28)

### ✨ Improvements

- **Enhanced Discord notifications**: Now shows the specific dates that were booked
- Better visibility into bot actions
- Date format: `• DD/MM/YYYY` for each reservation

### 🧹 Cleanup

- Removed obsolete `config/session.json` file
- Updated Docker Compose comments (removed session.json references)
- Cleaned `.gitignore` from obsolete entries

### 🔧 CI/CD

- Fixed GitHub Actions Docker build workflow
- Removed multi-architecture build (arm64 was causing failures)
- Faster and more reliable builds (linux/amd64 only)

---

## v1.8.0 - Automatic Token Refresh (2026-01-28)

### ✨ Major Features

- **Automatic token refresh**: The bot now automatically renews access tokens when they expire
- Uses OAuth2 endpoint `/api/auth/token` with `grant_type=refresh_token`
- Transparent retry of failed requests after token refresh
- Automatic persistence of new tokens to `.env` file

### 🔧 Technical Changes

- Added `refresh_access_token()` method in `OneFlexClient`
- Modified `_graphql_request()` to auto-refresh on 401 errors
- Added `_update_env_token()` for automatic `.env` updates
- Smart notifications: only alerts on refresh failure

### 📚 Documentation

- Complete rewrite of `docs/TOKEN_MANAGEMENT.md`
- Updated `README.md` with auto-refresh information
- Updated `GET_TOKEN.md` and `GUIDE_DEBUTANT.md`

### 🧹 Cleanup

- Archived obsolete discovery scripts (~922 lines removed)
- Removed manual token renewal documentation
- Updated all docs to reflect automatic refresh

### 🧪 Testing

- Added `test_auto_refresh.py` for comprehensive testing
- All tests passing ✅

---

## v1.7.1 - Security & Documentation (2026-01-28)

### 🔒 Security

- Anonymized all token examples in documentation
- Repository set to private for security

---

## v1.7.0 - Code Cleanup (2026-01-28)

### 🧹 Cleanup

- Removed 1122 lines of obsolete auto-refresh code
- Deleted unused session management files
- Removed Chrome/Selenium from Docker requirements

### 📚 Documentation

- Created comprehensive `GUIDE_DEBUTANT.md` (317 lines)
- Extensively commented `config.py` for beginners

---

## v1.6.1 - Docker Optimization (2026-01-24)

### 🐳 Docker

- Removed Chrome from Docker image
- Image size reduced by 70% (175MB vs 600MB+)
- Build time reduced by 99% (1.6s vs 17min)
- Fixed duplicate notification logs

---

## v1.6.0 - Recurring Date Fix (2026-01-23)

### 🐛 Bug Fixes

- Fixed recurring reservation date calculation
- 4th week now properly included for same weekday

---

## Earlier versions

See Git history for details on versions < 1.6.0
