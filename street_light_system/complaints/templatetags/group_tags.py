# complaints/templatetags/group_tags.py
from django import template

register = template.Library()

@register.filter
def in_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter
def user_reply_count(complaint):
    return complaint.replies.filter(sent_by_admin=False).count()
