import json
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.utils.safestring import mark_safe
from django.http import HttpResponseNotFound

from django.contrib.auth.models import User
from chat.models import Contact, Group

@login_required
def index2(request, room_name):
    u_id = request.user.id
    u_id_dict ={'id':u_id}
    group = Group.objects.get(pk=int(room_name))
    is_access_right = False

    if group.is_real_group:
        if u_id_dict in group.users.all().order_by('id').values('id'):
            is_access_right=True
    else:
        if group.contacts.filter(Q(owner_id=u_id)|Q(user_id=u_id)):
            is_access_right = True

    if is_access_right:
        contacts = Contact.objects.filter(owner_id=u_id)
        groups = Group.retrieve_real_groups(u_id)

        if group.is_real_group:
            group_picture = group.picture
            group_name = group.name;
        else:
            user=group.contacts.get(owner_id=u_id).user_id
            group_picture = user.userprofile.picture
            group_name = user.username


        context = {
            'room_name_json': mark_safe(json.dumps(room_name)),
            'username': mark_safe(json.dumps(request.user.username)),
            'contacts': contacts,
            'groups': groups,
            'group_picture':group_picture,
            'group_name':group_name,

        }
        return render(request, 'chat/index2.html', context)
    else:
        return HttpResponseNotFound("You don't have that type of contact")
