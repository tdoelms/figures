

import datetime
from dateutil.rrule import rrule, DAILY
import random

from django.contrib.auth import get_user_model

from courseware.models import StudentModule
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField
from student.models import CourseAccessRole, CourseEnrollment, UserProfile

from figures.models import CourseDailyMetrics, SiteDailyMetrics
from figures.helpers import as_course_key, as_datetime, days_from, prev_day
from figures.pipeline import course_daily_metrics as pipeline_cdm
from figures.pipeline import site_daily_metrics as pipeline_sdm

from devsite import cans


DAYS_BACK = 180
LAST_DAY = prev_day(datetime.datetime.now())

# def date_bin(days_back, count):
#     '''Start simple: uniformish
#     '''
#     dates = []

#     end_date = prev_day(datetime.datetime.now())
#     start_date = days_from(end_date, abs(days_back) * -1)

#     if count > days_back:
#         per_bin = count / days_back
#         remainder
#     else:
#         interval, remainder = divmod(days_back, count)

#     for dt in rrule(DAILY, dtstart=start_date, until=end_date):

#     return dates


def days_back_list(days_back):
    end_date = prev_day(datetime.datetime.now())
    start_date = days_from(end_date, abs(days_back) * -1)
    return [day for day in rrule(DAILY, dtstart=start_date, until=end_date)]


# def date_bin(days_back, count):
#     '''Start simple: uniformish
#     '''
#     dates = { }

#     end_date = prev_day(datetime.datetime.now())
#     start_date = days_from(end_date, abs(days_back) * -1)

#     if count > days_back:
#         per_bin = count / days_back
#         remainder
#     else:
#         interval, remainder = divmod(days_back, count)

#     for dt in rrule(DAILY, dtstart=start_date, until=end_date):

#     return dates


def seed_course_overviews(data=None):
    if not data:
        data = cans.COURSE_OVERVIEW_DATA
    for rec in data:
        course_id = rec.pop('id')
        CourseOverview.objects.update_or_create(
            id=as_course_key(course_id),
            defaults=rec,
            )


def clear_mock_users(data=None):
    '''
    This has limited utility when dynamically generated users
    '''
    if not data:
        data = cans.USER_DATA
    for rec in data:
        try:
            user = get_user_model().objects.get(username=rec['username'])
            user.delete()
        except get_user_model().DoesNotExist:
            pass

def clear_non_admin_users():
    '''
    TODO: exclude course staff users?
    '''
    users = get_user_model().objects.exclude(
        is_superuser=True).exclude(is_staff=True)
    users.delete()


def seed_users(data=None):
    '''
    TODO: handle duplicates
    '''
    if not data:
        data = cans.USER_DATA

    created_users = []
    for rec in data:
        profile_rec = rec.get('profile',None)
        user = get_user_model().objects.create_user(
            username=rec['username'],
            password=rec['password'],
            email=rec['email'],
            )
        user.is_staff = rec.get('is_staff', False)
        user.is_superuser = rec.get('is_superuser', False)
        user.save()
        created_users.append(user)
        if profile_rec:
            profile = UserProfile.objects.create(
                user=user,
                name=profile_rec['fullname'],
                gender=profile_rec.get('gender',None),
                country=profile_rec.get('country', None),
            )
    return created_users

def seed_course_enrollments_fixed(data=None):
    '''

    '''
    if not data:
        data = cans.COURSE_ENROLLMENT_DATA

    for rec in data:
        course_id = as_course_key(rec['course_id'])
        print('seeding course enrollment for user {}'.format(rec['username']))
        CourseEnrollment.objects.update_or_create(
            course_id=course_id,
            course_overview=CourseOverview.objects.get(id=course_id),
            user=get_user_model().objects.get(username=rec['username']),
            created=as_datetime(rec['created']),
            #mode=rec.get('mode', )
            )

def seed_course_enrollments_for_course(course_id, users, max_days_back):
    '''

    '''
    # we want to space out enrollments over time, the past 6 months
    today = datetime.datetime.now()

    def enroll_date(max_days_back):
        days_back = random.randint(1,abs(max_days_back))
        return days_from(today, days_back * -1 )

    for user in users:
        print('seeding course enrollment for user {}'.format(user.username))
        CourseEnrollment.objects.update_or_create(
            course_id=as_course_key(course_id),
            course_overview=CourseOverview.objects.get(id=course_id),
            user=user,
            #user=get_user_model().objects.get(username=rec['username']),
            created=enroll_date(max_days_back),
            #mode=rec.get('mode', )
            )

def seed_course_enrollments():
    for co in CourseOverview.objects.all():
        #users_in_course = random.randint(40,200)
        users = seed_users(cans.users.UserGenerator(100))
        seed_course_enrollments_for_course(co.id, users, DAYS_BACK)


def seed_course_access_roles(data=None):
    if not data:
        data = cans.COURSE_TEAM_DATA

    for rec in data:
        #print('creating course access role')
        CourseAccessRole.objects.update_or_create(
            user=get_user_model().objects.get(username=rec['username']),
            org=rec['org'],
            course_id=as_course_key(rec['course_id']),
            role=rec['role'],
        )


def seed_student_modules_fixed(data=None):
    '''
    '''
    if not data:
        data = cans.STUDENT_MODULE_DATA
    for rec in data:
        StudentModule.objects.update_or_create(
            student=get_user_model().objects.get(username=rec['username']),
            course_id=as_course_key(rec['course_id']),
            create=as_datetime(rec['created']),
            modified=as_datetime(rec['modified']),
        )

def seed_student_modules(data=None):
    '''
    '''
    def created_date(enroll_date):
        return days_from(end_date, random.randint)
    for ce in CourseEnrollment.objects.all():


        StudentModule.objects.update_or_create(
            student=ce.user,
            course_id=ce.course_id,
            create=as_datetime(rec['created']),
            modified=as_datetime(rec['modified']),
        )


def seed_course_daily_metrics(data=None):
    if not data:
        data = cans.COURSE_DAILY_METRICS_DATA
    for index, rec in enumerate(data):
        print('seed CDM # {}'.format(index))
        CourseDailyMetrics.objects.update_or_create(
            course_id=rec['course_id'],
            date_for=rec['date_for'],
            defaults=dict(
                enrollment_count=rec['enrollment_count'],
                active_learners_today=rec['active_learners_today'],
                average_progress=rec['average_progress'],
                average_days_to_complete=rec['average_days_to_complete'],
                num_learners_completed=rec['num_learners_completed'],
            )
        )

# def seed_site_daily_metrics(data=None):
#     if not data:
#         data = cans.SITE_DAILY_METRICS_DATA
#     for rec in data:
#         SiteDailyMetrics.objects.update_or_create(
#             date_for=rec['date_for'],
#             defaults=dict(
#                 cumulative_active_user_count=rec['cumulative_active_user_count'],
#                 todays_active_user_count=rec['todays_active_user_count'],
#                 total_user_count=rec['total_user_count'],
#                 course_count=rec['course_count'],
#                 total_enrollment_count=rec['total_enrollment_count'],
#             )
#         )

def seed_site_daily_metrics(data=None):
    '''
    Run seed_course_daily_metrics first

    Then, for each date for which we have a CDM record
    '''
    for a_date in CourseDailyMetrics.objects.order_by('date_for').values_list(
        'date_for', flat=True).distinct():
        print('collecting for date {}'.format(a_date))


def clear_all():
    CourseEnrollment.objects.all().delete()

def seed_test():
    clear_non_admin_users()
    CourseEnrollment.objects.all().delete()
    seed_course_enrollments()
    seed_student_modules()

def seed_all():
    seed_course_overviews()
    clear_non_admin_users()
    seed_users()
    seed_course_enrollments()
    seed_course_teams()
    #seed_student_modules()
    seed_course_daily_metrics()
    seed_site_daily_metrics()