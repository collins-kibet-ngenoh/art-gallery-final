from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from app.models import Artwork
from werkzeug.utils import secure_filename
import os

bp = Blueprint('artworks', __name__, url_prefix='/artworks')

# Directory to save uploaded artwork images
UPLOAD_FOLDER = '/path/to/save/images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('', methods=['POST'])
@jwt_required()
def create_artwork():
    data = request.form
    title = data.get('title')
    description = data.get('description')
    price = data.get('price')
    image = request.files.get('image')
    
    if not title or not price or not image:
        return jsonify(message="Title, price, and image are required"), 400

    if not allowed_file(image.filename):
        return jsonify(message="File type not allowed"), 400

    filename = secure_filename(image.filename)
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image.save(image_path)

    artist_id = get_jwt_identity()
    
    artwork = Artwork(title=title, description=description, price=price, image_url=image_path, artist_id=artist_id)
    db.session.add(artwork)
    db.session.commit()

    return jsonify(message="Artwork created successfully"), 201

@bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def update_artwork(id):
    data = request.get_json()
    artwork = Artwork.query.get_or_404(id)
    
    if artwork.artist_id != get_jwt_identity():
        return jsonify(message="Unauthorized"), 403

    artwork.title = data.get('title', artwork.title)
    artwork.description = data.get('description', artwork.description)
    artwork.price = data.get('price', artwork.price)

    db.session.commit()

    return jsonify(message="Artwork updated successfully")

@bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_artwork(id):
    artwork = Artwork.query.get_or_404(id)
    
    if artwork.artist_id != get_jwt_identity():
        return jsonify(message="Unauthorized"), 403

    db.session.delete(artwork)
    db.session.commit()

    return jsonify(message="Artwork deleted successfully")

@bp.route('/<int:id>', methods=['GET'])
def get_artwork(id):
    artwork = Artwork.query.get_or_404(id)
    return jsonify({
        'id': artwork.id,
        'title': artwork.title,
        'description': artwork.description,
        'price': artwork.price,
        'image_url': artwork.image_url,
        'artist_id': artwork.artist_id
    })
