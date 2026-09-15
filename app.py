from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
import uuid

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = os.environ.get('SESSION_SECRET', os.environ.get('SECRET_KEY', 'dev-secret'))

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    contact = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    location = db.Column(db.String(200))
    lat = db.Column(db.Float)
    lng = db.Column(db.Float)
    date_reported = db.Column(db.DateTime, default=datetime.utcnow)
    reporter_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    status = db.Column(db.String(50), default='pending')
    kind = db.Column(db.String(10), default='lost')  # lost or found
    photo = db.Column(db.String(300))
    expires_at = db.Column(db.DateTime)
    anonymous = db.Column(db.Boolean, default=False)
    verification_question = db.Column(db.String(300))
    verification_answer = db.Column(db.String(300))


class Claim(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    claimant_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    claim_id = db.Column(db.Integer, db.ForeignKey('claim.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    text = db.Column(db.String(400))
    seen = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rater_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    rated_user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    score = db.Column(db.Integer)
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


def init_db():
    db.create_all()


with app.app_context():
    init_db()


def current_user():
    uid = session.get('user_id')
    if uid:
        return User.query.get(uid)
    return None


@app.route('/')
def index():
    q = request.args.get('q', '')
    items = Item.query.order_by(Item.date_reported.desc()).limit(50).all()
    return render_template('index.html', items=items, user=current_user(), q=q)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        contact = request.form.get('contact')
        if User.query.filter_by(username=username).first():
            flash('Username taken')
            return redirect(url_for('register'))
        u = User(username=username, contact=contact)
        u.set_password(password)
        db.session.add(u)
        db.session.commit()
        session['user_id'] = u.id
        flash('Registered')
        return redirect(url_for('index'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        u = User.query.filter_by(username=username).first()
        if u and u.check_password(password):
            session['user_id'] = u.id
            flash('Logged in')
            return redirect(url_for('index'))
        flash('Invalid credentials')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


def save_photo(f):
    if not f:
        return None
    filename = secure_filename(f.filename)
    unique = f"{uuid.uuid4().hex}_{filename}"
    path = os.path.join(app.config['UPLOAD_FOLDER'], unique)
    f.save(path)
    return url_for('uploaded_file', filename=unique)


@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


@app.route('/report', methods=['GET', 'POST'])
def report():
    user = current_user()
    if request.method == 'POST':
        title = request.form['title']
        description = request.form.get('description')
        category = request.form.get('category')
        location = request.form.get('location')
        lat = request.form.get('lat') or None
        lng = request.form.get('lng') or None
        kind = request.form.get('kind', 'lost')
        expires_days = int(request.form.get('expires_days') or 30)
        anonymous = bool(request.form.get('anonymous'))
        verification_question = request.form.get('verification_question')
        verification_answer = request.form.get('verification_answer')
        photo = request.files.get('photo')
        photo_url = save_photo(photo)
        item = Item(
            title=title,
            description=description,
            category=category,
            location=location,
            lat=float(lat) if lat else None,
            lng=float(lng) if lng else None,
            reporter_id=user.id if user else None,
            kind=kind,
            photo=photo_url,
            expires_at=datetime.utcnow() + timedelta(days=expires_days),
            anonymous=anonymous,
            verification_question=verification_question,
            verification_answer=verification_answer,
        )
        db.session.add(item)
        db.session.commit()
        flash('Reported')
        # Create simple notifications for possible matches (very small heuristic)
        if kind == 'found':
            lost_items = Item.query.filter_by(kind='lost').all()
            for li in lost_items:
                if li.category and li.category == category:
                    if li.reporter_id:
                        n = Notification(user_id=li.reporter_id, text=f"Possible match: {item.title}")
                        db.session.add(n)
            db.session.commit()
        return redirect(url_for('index'))
    return render_template('report.html', user=user)


@app.route('/item/<int:item_id>', methods=['GET', 'POST'])
def view_item(item_id):
    item = Item.query.get_or_404(item_id)
    user = current_user()
    if request.method == 'POST':
        # make a claim
        if not user:
            flash('Login to claim')
            return redirect(url_for('login'))
        claim = Claim(item_id=item.id, claimant_id=user.id)
        db.session.add(claim)
        db.session.commit()
        flash('Claim submitted. Answer verification if required.')
        return redirect(url_for('item_claim', claim_id=claim.id))
    return render_template('item.html', item=item, user=user)


@app.route('/claim/<int:claim_id>', methods=['GET', 'POST'])
def item_claim(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    item = Item.query.get(claim.item_id)
    user = current_user()
    if request.method == 'POST':
        answer = request.form.get('answer', '').strip().lower()
        correct = (item.verification_answer or '').strip().lower()
        if correct and answer == correct:
            claim.verified = True
            db.session.commit()
            # enable chat by creating initial message
            flash('Verification successful. Chat enabled.')
            return redirect(url_for('chat', claim_id=claim.id))
        else:
            flash('Verification failed. Please provide more details in chat.')
            return redirect(url_for('chat', claim_id=claim.id))
    return render_template('claim.html', claim=claim, item=item, user=user)


@app.route('/chat/<int:claim_id>', methods=['GET', 'POST'])
def chat(claim_id):
    claim = Claim.query.get_or_404(claim_id)
    item = Item.query.get(claim.item_id)
    user = current_user()
    if request.method == 'POST':
        text = request.form.get('text')
        if not user:
            flash('Login to send messages')
            return redirect(url_for('login'))
        if not claim.verified and user.id != claim.claimant_id and user.id != item.reporter_id:
            flash('Chat is enabled only after verification for new users.')
            return redirect(url_for('item_claim', claim_id=claim.id))
        m = Message(claim_id=claim.id, sender_id=user.id, text=text)
        db.session.add(m)
        db.session.commit()
        return redirect(url_for('chat', claim_id=claim.id))
    messages = Message.query.filter_by(claim_id=claim.id).order_by(Message.created_at).all()
    return render_template('chat.html', messages=messages, claim=claim, item=item, user=user)


@app.route('/notifications')
def notifications():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    notes = Notification.query.filter_by(user_id=user.id).order_by(Notification.created_at.desc()).all()
    return render_template('notifications.html', notes=notes, user=user)


@app.route('/profile')
def profile():
    user = current_user()
    if not user:
        return redirect(url_for('login'))
    items = Item.query.filter_by(reporter_id=user.id).order_by(Item.date_reported.desc()).all()
    return render_template('profile.html', user=user, items=items)


@app.route('/search')
def search():
    q = request.args.get('q', '')
    category = request.args.get('category')
    items = Item.query
    if q:
        items = items.filter((Item.title.contains(q)) | (Item.description.contains(q)))
    if category:
        items = items.filter_by(category=category)
    items = items.order_by(Item.date_reported.desc()).limit(100).all()
    return render_template('search.html', items=items, q=q)


@app.route('/faq')
def faq():
    return render_template('faq.html', user=current_user())


@app.route('/stats')
def stats():
    total = Item.query.count()
    lost = Item.query.filter_by(kind='lost').count()
    found = Item.query.filter_by(kind='found').count()
    popular = db.session.query(Item.category, db.func.count(Item.id).label('c')).group_by(Item.category).order_by(db.desc('c')).limit(10).all()
    return render_template('stats.html', total=total, lost=lost, found=found, popular=popular, user=current_user())

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
