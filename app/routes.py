from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app import db
from app.models import User, Artwork, Like, Comment, Follow

main = Blueprint('main', __name__)

# Route to register a new user
@main.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    
    if not username or not email or not password:
        return jsonify({"message": "Missing required fields"}), 400
    
    if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
        return jsonify({"message": "Username or email already exists"}), 400

    user = User(username=username, email=email)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

# Route to log in a user
@main.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    
    if not email or not password:
        return jsonify({"message": "Missing email or password"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"message": "Invalid credentials"}), 401

    token = create_access_token(identity=user.id)
    return jsonify({"token": token}), 200

# Route to upload artwork
@main.route('/artwork', methods=['POST'])
@jwt_required()
def upload_artwork():
    data = request.get_json()
    
    # Extract and validate input fields
    title = data.get('title')
    description = data.get('description')
    price = data.get('price')
    image_url = data.get('image_url')

    if not title or not description or not price or not image_url:
        return jsonify({"message": "Missing required fields"}), 400

    try:
        price = float(price)
    except ValueError:
        return jsonify({"message": "Price must be a valid number"}), 400

    user_id = get_jwt_identity()

    try:
        new_artwork = Artwork(
            title=title,
            description=description,
            price=price,
            image_url=image_url,
            user_id=user_id
        )
        db.session.add(new_artwork)
        db.session.commit()

        return jsonify({
            "message": "Artwork uploaded successfully",
            "artwork": {
                "id": new_artwork.id,
                "title": new_artwork.title,
                "description": new_artwork.description,
                "price": new_artwork.price,
                "image_url": new_artwork.image_url,
                "user_id": new_artwork.user_id
            }
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": "An error occurred while saving the artwork", "error": str(e)}), 500

# Route to view all artworks on the home page
@main.route('/artworks', methods=['GET'])
def get_all_artworks():
    artworks = Artwork.query.all()
    result = [{
        'id': artwork.id,
        'title': artwork.title,
        'description': artwork.description,
        'price': artwork.price,
        'image_url': artwork.image_url,
        'like_count': artwork.like_count,
        'comment_count': artwork.comment_count,
        'artist': {
            'id': artwork.user.id,  # Artist's ID
            'username': artwork.user.username  # Artist's username
        }# 
    } for artwork in artworks]
    return jsonify(result), 200


@main.route('/artwork/<int:artwork_id>', methods=['GET'])
def get_artwork_details(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    comments = [{'id': comment.id, 'user_id': comment.user_id, 'content': comment.content, 'created_at': comment.created_at} for comment in artwork.comments]
    
    return jsonify({
        'id': artwork.id,
        'title': artwork.title,
        'description': artwork.description,
        'price': artwork.price,
        'image_url': artwork.image_url,
        'like_count': artwork.like_count,
        'comment_count': artwork.comment_count,
        'comments': comments,
        'artist': {
            'id': artwork.user.id,  # Artist's ID
            'username': artwork.user.username  # Artist's username
        }
    }), 200


# Route to like an artwork
@main.route('/artwork/<int:artwork_id>/like', methods=['POST'])
@jwt_required()
def like_artwork(artwork_id):
    user_id = get_jwt_identity()
    artwork = Artwork.query.get_or_404(artwork_id)
    like = Like.query.filter_by(artwork_id=artwork_id, user_id=user_id).first()

    if like:
        return jsonify({"message": "Already liked"}), 400

    new_like = Like(artwork_id=artwork_id, user_id=user_id)
    db.session.add(new_like)
    db.session.commit()

    return jsonify({"message": "Liked successfully", "like_count": artwork.like_count}), 201

# Route to comment on an artwork
@main.route('/artwork/<int:artwork_id>/comment', methods=['POST'])
@jwt_required()
def comment_artwork(artwork_id):
    user_id = get_jwt_identity()
    content = request.json.get('content')
    if not content:
        return jsonify({"message": "Content is required"}), 400

    artwork = Artwork.query.get_or_404(artwork_id)
    new_comment = Comment(artwork_id=artwork_id, user_id=user_id, content=content)
    db.session.add(new_comment)
    db.session.commit()

    return jsonify({"message": "Comment added successfully", "comment_count": artwork.comment_count}), 201

# Route to follow an artist
@main.route('/follow', methods=['POST'])
@jwt_required()
def follow_artist():
    user_id = get_jwt_identity()
    followed_id = request.json.get('followed_id')

    if user_id == followed_id:
        return jsonify({'message': 'Cannot follow yourself'}), 400

    # Check if the follow relationship already exists
    existing_follow = Follow.query.filter_by(follower_id=user_id, followed_id=followed_id).first()
    if existing_follow:
        return jsonify({'message': 'Already following this artist'}), 400

    # Create a new follow relationship
    new_follow = Follow(follower_id=user_id, followed_id=followed_id)
    db.session.add(new_follow)
    
    # Increment the followed artist's follower count
    followed_artist = User.query.get(followed_id)
    followed_artist.follower_count += 1
    
    db.session.commit()
    
    return jsonify({'message': 'Successfully followed the artist'}), 200

# Route to search for an artist
@main.route('/search', methods=['GET'])
def search_artist():
    query = request.args.get('query')
    if not query:
        return jsonify({"message": "Search query is required"}), 400

    results = User.query.filter(User.username.ilike(f'%{query}%')).all()
    result = [{'id': user.id, 'username': user.username} for user in results]
    return jsonify(result), 200

# Route to view an artist's profile
@main.route('/artist/<int:user_id>', methods=['GET'])
def get_artist_profile(user_id):
    user = User.query.get_or_404(user_id)
    artworks = Artwork.query.filter_by(user_id=user_id).all()
    
    # Prepare artworks with likes count
    artworks_info = []
    for artwork in artworks:
        artworks_info.append({
            'id': artwork.id,
            'title': artwork.title,
            'description': artwork.description,
            'price': artwork.price,
            'image_url': artwork.image_url,
            'like_count': artwork.like_count,
            'comment_count': artwork.comment_count
        })
    
    # Prepare followers
    followers = [{'id': follow.follower.id, 'username': follow.follower.username} for follow in user.followers]
    
    # Prepare following
    following = [{'id': follow.followed.id, 'username': follow.followed.username} for follow in user.following]

    return jsonify({
        'id': user.id,
        'username': user.username,
        'follower_count': user.follower_count,
        'following_count': user.following_count,
        'artworks': artworks_info,
        'followers': followers,
        'following': following
    }), 200


@main.route('/update_artwork/<int:artwork_id>', methods=['PUT'])
@jwt_required()
def update_artwork(artwork_id):
    data = request.get_json()
    
    title = data.get('title')
    description = data.get('description')
    price = data.get('price')
    image_url = data.get('image_url')

    if not (title or description or price or image_url):
        return jsonify({"message": "At least one field is required to update"}), 400

    artwork = Artwork.query.get_or_404(artwork_id)
    user_id = get_jwt_identity()

    if artwork.user_id != user_id:
        return jsonify({"message": "You do not have permission to update this artwork"}), 403

    if title:
        artwork.title = title
    if description:
        artwork.description = description
    if price:
        try:
            artwork.price = float(price)
        except ValueError:
            return jsonify({"message": "Invalid price value"}), 400
    if image_url:
        artwork.image_url = image_url

    db.session.commit()
    return jsonify({"message": "Artwork updated successfully"}), 200

@main.route('/delete_artwork/<int:artwork_id>', methods=['DELETE'])
@jwt_required()
def delete_artwork(artwork_id):
    artwork = Artwork.query.get_or_404(artwork_id)
    user_id = get_jwt_identity()

    if artwork.user_id != user_id:
        return jsonify({"message": "You do not have permission to delete this artwork"}), 403

    db.session.delete(artwork)
    db.session.commit()
    return jsonify({"message": "Artwork deleted successfully"}), 200