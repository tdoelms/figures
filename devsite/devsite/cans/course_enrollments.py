'''
First cut, we're just populating a single course
'''

from .course_overviews import COURSE_OVERVIEW_DATA
from .users import USER_DATA


def generate_course_enrollments():
    ce = []

    dates = ['2018-08-01', '2018-09-01', '2018-10-1', '2018-10-1']
    for i, d in enumerate(dates):
        ce.append(
            dict(
                course_id=COURSE_OVERVIEW_DATA[0]['id'],
                username=USER_DATA[i]['username'],
                created=d,
            ),
        )
    return ce


COURSE_ENROLLMENT_DATA = generate_course_enrollments()
