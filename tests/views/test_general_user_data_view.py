'''Tests Figures UserIndexView class

TODO: make reasonable endpoint


Front end expects data to be returned in the following form:

[
  {
    "username": "maxi",
    "country": "UY",
    "is_active": true,
    "year_of_birth": 1985,
    "level_of_education": "b",
    "gender": "m",
    "date_joined": "2018-05-06T14:01:58Z",
    "language_proficiencies": [],
    "courses": [
      {
        "course_name": "Something",
        "course_id": "A193+2016Q4+something",
      }
      ...
    ]
  },
  ...
]


'''

import pytest

from django.contrib.auth import get_user_model
from django.db.models import F

from rest_framework.test import (
    APIRequestFactory,
    #RequestsClient, Not supported in older  rest_framework versions
    force_authenticate,
    )

from student.models import CourseEnrollment

from figures.views import GeneralUserDataViewSet

from tests.factories import (
    CourseEnrollmentFactory,
    CourseOverviewFactory,
    UserFactory,
    )
from tests.views.base import BaseViewTest

COURSE_ID_STR_TEMPLATE = 'course-v1:StarFleetAcademy+SFA{}+2161'

USER_DATA = [
    {'id': 101, 'username': u'alpha', 'fullname': u'Alpha One',
     'is_active': True, 'country': 'CA'},
    {'id': 102, 'username': u'alpha02', 'fullname': u'Alpha Two', 'is_active': False, 'country': 'UK'},
    {'id': 103, 'username': u'bravo', 'fullname': u'Bravo One', 'is_active': True, 'country': 'US'},
    {'id': 104, 'username': u'bravo02', 'fullname': u'Bravo Two', 'is_active': True, 'country': 'UY'},
]

COURSE_DATA = [
    { 'id': u'course-v1:AlphaOrg+A001+RUN', 'name': u'Alpha Course 1', 'org': u'AlphaOrg', 'number': u'A001' },
    { 'id': u'course-v1:AlphaOrg+A002+RUN', 'name': u'Alpha Course 2', 'org': u'AlphaOrg', 'number': u'A002' },
    { 'id': u'course-v1:BravoOrg+A001+RUN', 'name': u'Bravo Course 1', 'org': u'BravoOrg', 'number': u'B001' },
    { 'id': u'course-v1:BravoOrg+B002+RUN', 'name': u'Bravo Course 2', 'org': u'BravoOrg', 'number': u'B002' },
]

def make_user(**kwargs):
    '''

    NOTE: Consider adding more fields. Refere to the serializer test for  the
    GeneralUserDataSerializer
    '''
    return UserFactory(
        id=kwargs['id'],
        username=kwargs['username'],
        profile__name=kwargs['fullname'],
        profile__country=kwargs['country'],
        is_active=kwargs['is_active'],
    )

def make_course(**kwargs):
    return CourseOverviewFactory(
        id=kwargs['id'], display_name=kwargs['name'], org=kwargs['org'], number=kwargs['number'])

def make_course_enrollments(user, courses, **kwargs):
    '''
        creates course enrollments for every course in COURSE_DATA for the given user
    '''
    course_enrollments = []
    for course in courses:
        course_enrollments.append(
            CourseEnrollmentFactory(
                course_id=course.id,
                user=user,
                )
            )

@pytest.mark.django_db
class TestGeneralUserViewSet(BaseViewTest):
    '''Tests the UserIndexView view class
    '''

    request_path = 'api/users/general'
    view_class = GeneralUserDataViewSet
    @pytest.fixture(autouse=True)
    def setup(self, db):

        super(TestGeneralUserViewSet, self).setup(db)
        self.users = [make_user(**data) for data in USER_DATA]
        self.usernames = [data['username'] for data in USER_DATA]
        self.course_overviews = [make_course(**data) for data in COURSE_DATA]
        self.course_enrollments = [make_course_enrollments(user, self.course_overviews) for user in self.users]
        self.expected_result_keys = [
            'id', 'username', 'fullname','country', 'is_active', 'gender',
            'date_joined', 'year_of_birth', 'level_of_education', 'courses',
            'language_proficiencies',
        ]

    def get_expected_results(self, **filter):
        '''returns a list of dicts of the filtered user data

        '''
        return list(
            get_user_model().objects.filter(**filter).annotate(
                fullname=F('profile__name'), country=F('profile__country')
                ).values(*self.expected_result_keys))

    # @pytest.mark.parametrize('endpoint, filter', [
    #     ('api/users/general', {}),
    #     ])
    #def test_get_general_user_list(self, endpoint, filter):
    def test_get_general_user_list(self):
        '''Tests retrieving a list of users with abbreviated details

        The fields in each returned record are identified by
            `figures.serializers.UserIndexSerializer`

        '''
        #expected_data = self.get_expected_results(**filter)
        def get_course_rec(course_id, course_list):
            recs = [rec for rec in course_list if rec['id'] == str(course_id)]
            assert len(recs) == 1
            return recs[0]

        request = APIRequestFactory().get(self.request_path)
        force_authenticate(request, user=self.staff_user)
        view = self.view_class.as_view({'get': 'list'})
        response = view(request)

        # Later, we'll elaborate on the tests. For now, some basic checks
        assert response.status_code == 200
        assert len(response.data) == len(self.users)

        User = get_user_model()
        qs = User.objects.filter(username__in=self.usernames)
        assert len(self.users) == qs.count()

        # Expect the following format for pagination
        # {
        #     "count": 2,
        #     "next": null, # or a url
        #     "previous": null, # or a url
        #     "results": [
        #     ...           # list of the results
        #     ]
        # }
        assert set(response.data.keys()) == set(
            ['count', 'next', 'previous', 'results',])
        for rec in response.data['results']:
            # fail if we cannot find the user in the models
            user_model = User.objects.get(username=rec['username'])

            assert set(rec.keys()) == set(self.expected_result_keys)

            # check the courses
            for course_enrollment in CourseEnrollment.objects.filter(user=user_model):
                # Test that the course id exists in the data
                course_rec = get_course_rec(course_enrollment.course_id, rec['courses'])
