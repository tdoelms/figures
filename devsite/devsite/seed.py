

from django.contrib.auth import get_user_model

from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField
from student.models import UserProfile

from figures.helpers import as_course_key, as_datetime

def seed_course_overviews():

    data = [
        dict(
            id='course-v1:StarFleetAcademy+SFA01+2161',
            display_name='Intro to Astronomy',
            org='StarFleetAcademy',
            display_org_with_default='StarFleetAcademy',
            number='SFA01',
            created=as_datetime('2018-01-01'),
            ),
        dict(
            id='course-v1:StarFleetAcademy+SFA02+2161',
            display_name='Intro to Xenology',
            org='StarFleetAcademy',
            display_org_with_default='StarFleetAcademy',
            number='SFA02',
            created=as_datetime('2018-01-01'),
            )
    ]

    for rec in data:
        course_id = rec.pop('id')
        CourseOverview.objects.update_or_create(
            id=as_course_key(course_id),
            defaults=rec,
            )

def seed_users():
    data = [
        dict(
            username='JoeBob',
            password='foo',
            email='jobob@example.com',
            is_staff=False,
            is_superuser=False,
            profile=dict(
                fullname='Joe Bob',
            )
        )
    ]

    for rec in data:
        profile = rec['profile']
        user = get_user_model().objects.create_user(
            username=rec['username'],
            password=rec['password'],
            email=rec['email'],
            )
        user.save()
        profile = UserProfile.objects.create(
            user=user,
            name=profile['fullname'],
            country='US',

        )
