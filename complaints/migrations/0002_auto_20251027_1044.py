from django.db import migrations

def create_groups_and_permissions(apps, schema_editor):
    Complaint = apps.get_model('complaints', 'Complaint')
    Group = apps.get_model('auth', 'Group')
    Permission = apps.get_model('auth', 'Permission')
    ContentType = apps.get_model('contenttypes', 'ContentType')
    # Create Users group
    users_group, _ = Group.objects.get_or_create(name='Users')
    # Create KSEB group
    kseb_group, _ = Group.objects.get_or_create(name='KSEB')

    # Assign permissions for Complaints
    complaint_ct = ContentType.objects.get_for_model(Complaint)
    add_complaint_perm, _ = Permission.objects.get_or_create(
        codename='add_complaint', content_type=complaint_ct,
        defaults={'name': 'Can add complaint'})
    change_complaint_perm, _ = Permission.objects.get_or_create(
        codename='change_complaint', content_type=complaint_ct,
        defaults={'name': 'Can change complaint'})
    view_complaint_perm, _ = Permission.objects.get_or_create(
        codename='view_complaint', content_type=complaint_ct,
        defaults={'name': 'Can view complaint'})

    # Users can add and view complaints
    users_group.permissions.add(add_complaint_perm, view_complaint_perm)
    # KSEB can view and change (resolve) complaints
    kseb_group.permissions.add(view_complaint_perm, change_complaint_perm)

class Migration(migrations.Migration):
    dependencies = [
        ('complaints', '0001_initial'),  # Adjust to your last migration
    ]

    operations = [
        migrations.RunPython(create_groups_and_permissions),
    ]