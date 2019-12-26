from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q

User = get_user_model()

class Group(models.Model):
    name = models.CharField(max_length=192, unique=True, blank=False)
    users = models.ManyToManyField(User)
    picture = models.ImageField(upload_to='chat/', default=None, null=True,
                                blank=True)
    @property
    def channel_name(self):
        return self.id

    @staticmethod
    def retrieve_real_groups(user_id):
        real_group_set = []
        groups = Group.objects.filter(users__id=user_id)
        for group in groups:
            if group.is_real_group:
                real_group_set.append(group.id)
        return Group.objects.filter(pk__in=real_group_set)

    @property
    def is_real_group(self):
        return self.contacts.count() == 0


    def __str__(self):
        return self.name

class Contact(models.Model):
    owner_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_id')
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_id', default=None, null=True,
                                blank=True)
    user_has_chatted = models.BooleanField()
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='contacts', default=None, null=True,
                                blank=True)


    def __str__(self):
        return str(self.owner_id) + "-" + str(self.user_id)



class Message(models.Model):
    author = models.ForeignKey(User, related_name="author_messages", on_delete=models.CASCADE)
    to_group = models.ForeignKey(Group, related_name='to_group', on_delete=models.SET_NULL, null=True, default=None,
                                 blank=True)
    to_user = models.ForeignKey(User, related_name='user_messages', on_delete=models.SET_NULL, null=True, default=None,
                                blank=True)
    is_broadcast = models.BooleanField()
    content = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.content

    @staticmethod
    def last_10_messages(channel,authed_user):
        group = Group.objects.get(pk=channel)
        if group.is_real_group:
            return Message.objects.filter(to_group__id=channel).order_by("created")
        else:
            cont = group.contacts.get(owner_id=authed_user)
            return Message.objects.filter(Q(author__id=authed_user, to_user__id=cont.user_id.id)|Q(author__id=cont.user_id.id, to_user__id=authed_user)).order_by("created")


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    picture = models.ImageField(upload_to="chat/", blank=True, null=True)

    def __str__(self):
        return self.user.username
