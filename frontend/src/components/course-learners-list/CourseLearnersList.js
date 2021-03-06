import React, { Component } from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import moment from 'moment';
import countriesWithCodes from 'base/data/countriesData';
import styles from './_course-learners-list.scss';
import classNames from 'classnames/bind';
import FontAwesomeIcon from '@fortawesome/react-fontawesome';
import { faCheck } from '@fortawesome/fontawesome-free-solid';

let cx = classNames.bind(styles);

class CourseLearnersList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      allLearnersLoaded: this.props.allLearnersLoaded
    };
    this.paginationLoadMore = this.paginationLoadMore.bind(this);
    this.isCurrentCourse = this.isCurrentCourse.bind(this);
  }

  isCurrentCourse = (course) => {
    return course['course_id'] === this.props.courseId
  }

  paginationLoadMore = () => {
    this.props.apiFetchMoreLearnersFunction()
  }

  componentDidMount() {
  }

  componentWillReceiveProps = (nextProps) => {
    if (this.props !== nextProps) {
      this.setState({
        allLearnersLoaded: nextProps.allLearnersLoaded
      })
    }
  }


  render() {
    const learnersRender = this.props.learnersData.map((user, index) => {
      const courseSpecificData = user['courses'].find(this.isCurrentCourse);

      return (
        <li key={index} className={styles['learner-row']}>
          <span className={styles['name']}><Link to={'/figures/user/' + user['id']}>{user['name']}</Link></span>
          <span className={styles['country']}>{countriesWithCodes[user['country']]}</span>
          <span className={styles['date-enrolled']}>{moment(courseSpecificData['date_enrolled']).format('LL')}</span>
          <span className={styles['course-progress']}>{(courseSpecificData['progress_data']['course_progress']*100).toFixed(2)}%</span>
          <span className={styles['course-completed']}>{courseSpecificData['progress_data']['course_completed'] && <FontAwesomeIcon icon={faCheck} className={styles['completed-icon']} />}</span>
          <span className={styles['date-completed']}>{courseSpecificData['progress_data']['course_completed'] ? courseSpecificData['progress_data']['date_completed'] : '-'}</span>
        </li>
      )
    })

    return (
      <section className={styles['course-learners-list']}>
        <div className={styles['header']}>
          <div className={styles['header-title']}>
            {this.props.listTitle}
          </div>
        </div>
        <div className={cx({ 'stat-card': true, 'span-2': false, 'span-3': false, 'span-4': true, 'learners-table-container': true})}>
          <ul className={styles['learners-table']}>
            <li key="header" className={styles['header-row']}>
              <span className={styles['name']}>Learner</span>
              <span className={styles['country']}>Country</span>
              <span className={styles['date-enrolled']}>Date enrolled</span>
              <span className={styles['course-progress']}>Course progress</span>
              <span className={styles['course-completed']}>Course completed</span>
              <span className={styles['date-completed']}>Date completed</span>
            </li>
            {learnersRender}
          </ul>
          {!this.state.allLearnersLoaded && <button className={styles['load-more-button']} onClick={() => this.paginationLoadMore()}>Load more</button>}
        </div>
      </section>
    )
  }
}

CourseLearnersList.defaultProps = {
  listTitle: 'Per learner info:',
}

CourseLearnersList.propTypes = {
  listTitle: PropTypes.string,
  courseId: PropTypes.string,
};

export default CourseLearnersList;
