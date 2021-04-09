from . import db
from .model import Post, Vote
from werkzeug.exceptions import abort
from flask_login import login_required, current_user
from flask import Blueprint, redirect, render_template, url_for, flash, request


post = Blueprint('post', __name__)

# Get post
def get_post(id, check_autor=True):
    post = Post.query.get(id)

    if post is None:
        abort(404, f'Post {id} doesn\'t exist')
    
    if check_autor and post.author_id != current_user.id:
        abort(403)

    return post

# Home/index
@post.route('/', methods=['GET','POST'])
def home():
    all_posts = Post.query.all()
    return render_template('index.html', user=current_user, all_posts=all_posts)


# View post
@post.route('/post/<int:id>', methods=['GET','POST'])
def post_view(id):
    post = get_post(id, check_autor=False)
    liked = False
    like = None
    user = current_user

    if user.is_authenticated:
        like = Vote.query.filter_by(post_id=post.id, user_id=current_user.id).first()
        if like:
            liked=True

    return render_template('post.html', user=user, post=post, liked=liked, like=like)


# Explore posts
@post.route('/explore', methods=['GET','POST'])
@post.route('/explore/<int:page>', methods=['GET','POST'])
def explore(page=1):
    per_page = 10
    posts = Post.query.order_by(Post.created.desc()).paginate(page,per_page,error_out=False)
    return render_template('explore.html', user=current_user, posts=posts, page=page)


# Search post
@post.route('/search', methods=['GET','POST'])
def search():
    if request.method == 'POST':
        search = request.form['search']

        posts = Post.query.filter(Post.title.like(f'%{search}%')).all()

    return render_template('search.html', user=current_user, posts=posts)


# Create new post
@post.route('/create', methods=['GET','POST'])
@login_required
def create():
    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']

        if len(title) < 1:
            flash('Title is too short!', category='error')
        elif len(body) < 1:
            flash('Body is too short!', category='error')
        else:
            post = Post(author_id=current_user.id, title=title, body=body)
            db.session.add(post)
            db.session.commit()
            flash('Post created!', category='success')
            return redirect(url_for('post.home'))

    return render_template('create.html', user=current_user)


# Update post
@post.route('/post/<int:id>/edit', methods=['GET','POST'])
@login_required
def update(id):
    post = get_post(id)

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        if len(title) < 1:
            flash('Title is too short!', category='error')
        elif len(body) < 1:
            flash('Body is too short!', category='error')
        else:
            post.title= title
            post.body = body
            db.session.commit()
            flash('Updated!', category='success')
            return redirect(url_for('post.post_view', id=post.id))

    return render_template('update.html', user=current_user, post=post)


# Delete post
@post.route('/post/<int:id>/delete', methods=['GET','POST'])
@login_required
def delete(id):
    post = get_post(id)

    db.session.delete(post)
    db.session.commit()
    flash('Post was deleted!', category='success')

    return redirect(url_for('home'))


# Voting system
@post.route('/post/<int:id>/vote', methods=['GET','POST'])
def votes(id):
    post_id = get_post(id, check_autor=False).id
    user_id = current_user.id

    vote = Vote(post_id=post_id, user_id=user_id)
    db.session.add(vote)
    db.session.commit()
    flash('Liked!', category='success')
    
    return redirect(url_for('post.post_view', id=post_id))

@post.route('/post/<int:id>/dislike')
def dislike(id):
    post_id = request.args.get('post_id')
    like = Vote.query.get(id)

    db.session.delete(like)
    db.session.commit()
    flash('Disliked!', category='info')

    return redirect(url_for('post.post_view', id=post_id))