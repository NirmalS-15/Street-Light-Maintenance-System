# TODO: Add User Message Notification to KSEB Dashboard

## Steps to Complete

1. **Update kseb_dashboard view in complaints/views.py**
   - Add `prefetch_related('replies')` to the complaints queryset for efficient loading of replies.

2. **Modify kseb_dashboard.html template**
   - Add a new "Messages" column header after Status.
   - In the table body, add a new cell that displays a badge with the count of user replies (where sent_by_admin=False) if count > 0.

3. **Test the implementation**
   - Run the server and check the dashboard to ensure the Messages column shows correct counts.
   - Verify that complaints with user replies display the badge, others do not.

4. **Performance check**
   - Ensure prefetch_related doesn't cause performance issues with large datasets.
