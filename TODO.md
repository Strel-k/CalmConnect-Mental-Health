# TODO - CalmConnect Backend

## Current Tasks

### 1. Fix Pagination Issue
**Status:** In Progress
**Priority:** High

**Problem:** Pagination buttons are not working correctly - clicking pagination buttons doesn't redirect to pages where articles not displayed on homepage should appear.

**Current Status:**
- [x] Analyzed current pagination implementation
- [x] Identified issue with pagination logic
- [ ] Implement proper pagination functionality
- [ ] Test pagination with different page numbers
- [ ] Verify articles appear correctly on different pages

**Files to examine:**
- `mentalhealth/views.py` - Main views handling pagination
- `templates/` - Frontend templates with pagination UI
- `static/` - JavaScript handling pagination clicks

**Next Steps:**
1. Fix pagination logic in views.py
2. Update frontend templates to handle pagination correctly
3. Test pagination functionality across multiple pages

### 2. Database Migration
**Status:** Completed
**Priority:** Completed

**Completed Tasks:**
- [x] SQLite to PostgreSQL migration completed
- [x] All data successfully migrated
- [x] Database connection verified

## Environment Variables Template

Create a `.env` file in the project root:

```env
# Database Configuration
DB_NAME=calmconnect_db
DB_USER=postgres
DB_PASSWORD=your_secure_password
DB_HOST=localhost
DB_PORT=5432

# Django Settings
DJANGO_DEBUG=False
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# OpenAI API
OPENAI_API_KEY=your-openai-api-key

# Email Settings (if needed)
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
EMAIL_PORT=587
