from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from app.database.models import Job, JobApplication
from sqlalchemy import or_
from datetime import datetime

main_bp = Blueprint('main', __name__)

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
    job_type = request.args.get('job_type', '')
    company = request.args.get('company', '')
    source = request.args.get('source', '')
    sort_by = request.args.get('sort', 'posted_date')
    page = request.args.get('page', 1, type=int)
    
    # Base query
    query = Job.query

    # Apply filters
    if keyword:
        query = query.filter(
            or_(
                Job.title.ilike(f'%{keyword}%'),
                Job.description.ilike(f'%{keyword}%')
            )
        )
    if location:
        query = query.filter(Job.location.ilike(f'%{location}%'))
    if job_type:
        query = query.filter(Job.job_type == job_type)
    if company:
        query = query.filter(Job.company.ilike(f'%{company}%'))
    if source:
        query = query.filter(Job.source == source)

    # Apply sorting
    if sort_by == 'posted_date':
        query = query.order_by(Job.posted_date.desc())
    elif sort_by == 'company':
        query = query.order_by(Job.company)
    elif sort_by == 'title':
        query = query.order_by(Job.title)

    # Pagination
    per_page = 20
    jobs = query.paginate(page=page, per_page=per_page, error_out=False)

    return render_template('jobs/list.html',
                         jobs=jobs,
                         keyword=keyword,
                         location=location,
                         job_type=job_type,
                         company=company,
                         source=source,
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
    """About page"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')