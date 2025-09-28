# Task: Fix and Enhance User-Profile Design

## Steps to Complete:

1. **Verify User Authentication and DB State**
   - Use Django shell to check if user 'fdave.pararuan@clsu2.edu.ph' exists, is_active=True, email_verified=True.
   - If not active/verified, activate via shell: from mentalhealth.models import CustomUser; user = CustomUser.objects.get(email='fdave.pararuan@clsu2.edu.ph'); user.is_active = True; user.email_verified = True; user.save().
   - Confirm password hash or reset if needed.

2. **Check and Fix Static/Media Serving** [x]
   - Read settings.py to verify STATIC_URL, MEDIA_URL, STATICFILES_DIRS.
   - Run `python manage.py collectstatic --noinput` to collect static files.
   - Ensure 'mentalhealth/static/' is in STATICFILES_DIRS.

3. **Enhance user-profile.html Design** [x]
   - Add media queries for mobile responsiveness (e.g., @media (max-width: 768px) { .profile-container { flex-direction: column; } }).
   - Add CSS animations (e.g., .card { transition: transform 0.3s; } .card:hover { transform: translateY(-5px); }).
   - Add image fallbacks: Replaced static image with dynamic avatar URL using ui-avatars.com API.
   - Add loading spinners for AJAX (e.g., profile upload, notifications fetch).
   - Harmonize colors/gradients with index.html (e.g., primary green #4CAF50).

4. **Update views.py for Better Context**
   - Enhance user_profile context: Add 'full_name': user.get_full_name(), 'college_display': user.get_college_display(), handle empty test_page_obj/appt_page_obj with messages.
   - Add login_view debug: logger.info(f"Login attempt for {username}, user_exists: {user_exists}, is_active: {user.is_active if user else None}").

5. **Test the Implementation**
   - Relaunch browser to http://localhost:8000/login/, login with credentials.
   - Navigate to /user-profile/, verify design (cards, table, modals render with styles/images).
   - Test interactions: Edit profile modal, upload picture, load notifications, paginate history/appointments.
   - Check console for errors; test on mobile viewport if possible.
   - If issues, inspect DB for data (DASS results, appointments).

6. **Final Verification**
   - Confirm no blank sections (e.g., if no tests, show "No results yet" message).
   - Update TODO.md with [x] for completed steps.

Progress: 5/6 completed.

---

# Task: Implement Add Counselor Functionality

## Steps to Complete:

1. **Verify Backend Implementation**
   - Confirm add_counselor view exists in views.py with proper validation, user creation, email sending.
   - Verify URL configuration in urls.py for /api/counselors/.
   - Check admin_personnel view renders admin-personnel.html with counselors context.

2. **Create Frontend Template**
   - Create admin-personnel.html with stats cards, counselors table, and add/edit modal.
   - Include AJAX form submission for adding counselors with file upload support.
   - Add edit and archive functionality with confirmation dialogs.

3. **Test the Implementation**
   - Run Django server and navigate to admin personnel page.
   - Test adding new counselor: fill form, upload photo, verify success message and table update.
   - Test editing counselor: pre-fill modal, update details, verify changes.
   - Test archiving counselor: confirm dialog, verify removal from table.
   - Check email is sent to new counselor with setup instructions.

4. **Final Verification**
   - Ensure responsive design and error handling.
   - Verify CSRF protection and proper form validation.
   - Update TODO.md with [x] for completed steps.

Progress: 4/4 completed. ✅
