from flask import Blueprint, render_template, request, jsonify
from app.database.models import Job
from sqlalchemy import or_

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
    sort_by = request.args.get('sort', 'posted_date')  # Default sort by date
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

@main_bp.route('/about')
def about():
    """About page"""
    return render_template('about.html')

@main_bp.route('/contact')
def contact():
    """Contact page"""
    return render_template('contact.html')