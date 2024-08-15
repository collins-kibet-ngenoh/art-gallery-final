from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from app import db

bcrypt = Bcrypt()

# Model for user
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

    # Relationships
    artworks = db.relationship('Artwork', back_populates='user')
    likes = db.relationship('Like', back_populates='user')
    comments = db.relationship('Comment', back_populates='user')
    followers = db.relationship('Follow', foreign_keys='Follow.followed_id', back_populates='followed')
    following = db.relationship('Follow', foreign_keys='Follow.follower_id', back_populates='follower')

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    @property
    def follower_count(self):
        return len(self.followers)

    @property
    def following_count(self):
        return len(self.following)

# Model for following artists
class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    followed_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    follower = db.relationship('User', foreign_keys=follower_id, back_populates='following')
    followed = db.relationship('User', foreign_keys=followed_id, back_populates='followers')

# Model for artwork
class Artwork(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    image_url = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='artworks')
    likes = db.relationship('Like', back_populates='artwork', cascade="all, delete-orphan")
    comments = db.relationship('Comment', back_populates='artwork', cascade="all, delete-orphan")

    @property
    def like_count(self):
        return len(self.likes)

    @property
    def comment_count(self):
        return len(self.comments)

# Model for like
class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artwork.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    artwork = db.relationship('Artwork', back_populates='likes')
    user = db.relationship('User', back_populates='likes')

# Model for comment
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    artwork_id = db.Column(db.Integer, db.ForeignKey('artwork.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    artwork = db.relationship('Artwork', back_populates='comments')
    user = db.relationship('User', back_populates='comments')

# Model for following artists
