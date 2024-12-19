from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.database.models import Job, JobApplication
from app.database.repository import JobRepository
from sqlalchemy import or_, and_
from datetime import datetime
from . import db

main_bp = Blueprint('main', __name__)

SOFTWARE_JOB_KEYWORDS = [
    'software engineer',
    'software developer',
    'full stack developer',
    'backend engineer',
    'java developer'
]

@main_bp.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@main_bp.route('/jobs')
def job_list():
    """Job listing page with filtering and sorting"""
    # Get filter parameters
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    company = request.args.get('company', '')
    sort_by = request.args.get('sort', 'posted_date')
    page = request.args.get('page', 1, type=int)
    
    # Base query - always filter for US jobs and software engineering roles
    query = Job.query.filter(
        and_(
            Job.location.ilike('%United States%'),
            or_(*[Job.title.ilike(f'%{kw}%') for kw in SOFTWARE_JOB_KEYWORDS])
        )
    )

    # Apply additional filters
    if keyword:
        query = query.filter(
            or_(
                Job.title.ilike(f'%{keyword}%'),
                Job.description.ilike(f'%{keyword}%')
            )
        )
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if company:
        query = query.filter(Job.company.ilike(f'%{company}%'))

    # Apply sorting
    if sort_by == 'posted_date':
        query = query.order_by(Job.posted_date.desc())
    elif sort_by == 'company':
        query = query.order_by(Job.company)
    elif sort_by == 'title':
        query = query.order_by(Job.title)

    # Pagination with larger per_page value
    per_page = 50
    jobs = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('jobs/list.html',
                         jobs=jobs,
                         keyword=keyword,
                         location=location,
                         company=company,
                         sort_by=sort_by)

@main_bp.route('/jobs/<int:job_id>')
def job_detail(job_id):
    """Job detail page"""
    job = Job.query.get_or_404(job_id)
    
    # Get next and previous job IDs for navigation
    next_job = Job.query.filter(Job.id > job_id).order_by(Job.id.asc()).first()
    prev_job = Job.query.filter(Job.id < job_id).order_by(Job.id.desc()).first()
    
    # Get job application if exists
    application = JobApplication.query.filter_by(job_id=job_id).first()
    
    return render_template('jobs/detail.html',
                         job=job,
                         next_job=next_job,
                         prev_job=prev_job,
                         application=application)

@main_bp.route('/jobs/<int:job_id>/status', methods=['POST'])
def update_job_status(job_id):
    """Update job application status"""
    job = Job.query.get_or_404(job_id)
    status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    if status not in ['viewed', 'interested', 'applied', 'not_interested']:
        flash('Invalid status', 'error')
        return redirect(url_for('main.job_detail', job_id=job_id))
    
    application = JobApplication.query.filter_by(job_id=job_id).first()
    
    if not application:
        application = JobApplication(
            job_id=job_id,
            status=status,
            notes=notes,
            applied_date=datetime.now() if status == 'applied' else None
        )
        db.session.add(application)
    else:
        application.status = status
        application.notes = notes
        if status == 'applied':
            application.applied_date = datetime.now()
    
    db.session.commit()
    flash('Job status updated successfully', 'success')
    return redirect(url_for('main.job_detail', job_id=job_id))

@main_bp.route('/about')
def about():
    """About page with statistics"""
    stats = {
        'total_jobs': Job.query.filter(
            and_(
                Job.location.ilike('%United States%'),
                or_(*[Job.title.ilike(f'%{kw}%') for kw in SOFTWARE_JOB_KEYWORDS])
            )
        ).count(),
        'total_companies': db.session.query(Job.company).distinct().count(),
        'total_locations': db.session.query(Job.location).distinct().count(),
        'job_types': SOFTWARE_JOB_KEYWORDS
    }
    return render_template('about.html', **stats)

@main_bp.route('/api/jobs')
def api_jobs():
    """API endpoint for job data"""
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')
    company = request.args.get('company', '')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)

    # Base query - always filter for US jobs and software engineering roles
    query = Job.query.filter(
        and_(
            Job.location.ilike('%United States%'),
            or_(*[Job.title.ilike(f'%{kw}%') for kw in SOFTWARE_JOB_KEYWORDS])
        )
    )

    # Apply additional filters
    if keyword:
        query = query.filter(
            or_(
                Job.title.ilike(f'%{keyword}%'),
                Job.description.ilike(f'%{keyword}%')
            )
        )
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if company:
        query = query.filter(Job.company.ilike(f'%{company}%'))

    # Paginate
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    jobs = pagination.items

    return jsonify({
        'jobs': [job.to_dict() for job in jobs],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page
    })