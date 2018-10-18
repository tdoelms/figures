

from django.contrib.auth import get_user_model

from courseware.models import StudentModule
from openedx.core.djangoapps.content.course_overviews.models import CourseOverview
from openedx.core.djangoapps.xmodule_django.models import CourseKeyField
from student.models import CourseAccessRole, CourseEnrollment, UserProfile

from figures.models import CourseDailyMetrics, SiteDailyMetrics
from figures.helpers import as_course_key, as_datetime
from figures.pipeline import course_daily_metrics as pipeline_cdm
from figures.pipeline import site_daily_metrics as pipeline_sdm

from devsite import cans


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
    if not data:
        data = cans.USER_DATA
    for rec in data:
        try:
            user = get_user_model().objects.get(username=rec['username'])
            user.delete()
        except get_user_model().DoesNotExist:
            pass


def seed_users(data=None):
    if not data:
        data = cans.USER_DATA
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
        if profile_rec:
            profile = UserProfile.objects.create(
                user=user,
                name=profile_rec['fullname'],
                gender=profile_rec.get('gender',None),
                country=profile_rec.get('country', None),
            )


def seed_course_enrollments(data=None):
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


def seed_student_modules(data=None):
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


def seed_all():
    seed_course_overviews()
    clear_mock_users()
    seed_users()
    seed_course_enrollments()
    seed_course_teams()
    #seed_student_modules()
    seed_course_daily_metrics()
    seed_site_daily_metrics()