"""Songs REST API backed by MongoDB; mock storage is opt-in for tests."""
import json
import os
from pathlib import Path
from urllib.parse import quote_plus
from flask import jsonify, request
from bson import json_util
from pymongo import MongoClient
from pymongo.errors import PyMongoError, DuplicateKeyError
from . import app

if os.getenv('MONGODB_MOCK') == '1':
    from mongomock import MongoClient
    client = MongoClient()
else:
    uri = os.getenv('MONGODB_URI')
    if not uri:
        host = os.getenv('MONGODB_SERVICE', 'localhost')
        port = os.getenv('MONGODB_PORT', '27017')
        user = os.getenv('MONGODB_USERNAME')
        password = os.getenv('MONGODB_PASSWORD')
        credentials = f'{quote_plus(user)}:{quote_plus(password)}@' if user and password else ''
        uri = f'mongodb://{credentials}{host}:{port}'
    client = MongoClient(uri, serverSelectionTimeoutMS=5000)
db = client.songs

def initialize_database():
    """Seed missing songs without dropping existing user data."""
    db.songs.create_index('id', unique=True)
    seed = json.loads((Path(__file__).parent / 'data' / 'songs.json').read_text())
    for song in seed:
        db.songs.update_one({'id': song['id']}, {'$setOnInsert': song}, upsert=True)

def parse_json(value):
    return json.loads(json_util.dumps(value))

@app.errorhandler(PyMongoError)
def database_error(error):
    app.logger.error('MongoDB request failed: %s', type(error).__name__)
    return jsonify(message='Database service unavailable'), 503

@app.get('/health')
def health():
    client.admin.command('ping')
    return jsonify(status='OK'), 200

@app.get('/count')
def count():
    return jsonify(length=db.songs.count_documents({})), 200

@app.get('/song')
def get_songs():
    return jsonify(parse_json(list(db.songs.find({})))), 200

@app.get('/song/<int:id>')
def get_song_by_id(id):
    song = db.songs.find_one({'id': id})
    if song is None:
        return jsonify(message='song with id not found'), 404
    return jsonify(parse_json(song)), 200

def incoming_song():
    song = request.get_json()
    if not isinstance(song, dict) or not isinstance(song.get('id'), int):
        return None
    return {key: song[key] for key in ('id', 'title', 'lyrics') if key in song}

@app.post('/song')
def create_song():
    song = incoming_song()
    if song is None:
        return jsonify(message='A JSON object with an integer id is required'), 400
    if db.songs.find_one({'id': song['id']}):
        return jsonify(message=f"song with id {song['id']} already present"), 302
    try:
        db.songs.insert_one(song)
    except DuplicateKeyError:
        return jsonify(message=f"song with id {song['id']} already present"), 302
    return jsonify(parse_json(song)), 201

@app.put('/song/<int:id>')
def update_song(id):
    song = incoming_song()
    if song is None or song['id'] != id:
        return jsonify(message='A matching integer id is required'), 400
    result = db.songs.update_one({'id': id}, {'$set': song})
    if not result.matched_count:
        return jsonify(message='song with id not found'), 404
    return jsonify(parse_json(db.songs.find_one({'id': id}))), 200

@app.delete('/song/<int:id>')
def delete_song(id):
    if not db.songs.delete_one({'id': id}).deleted_count:
        return jsonify(message='song with id not found'), 404
    return '', 204

if os.getenv('MONGODB_SEED') == '1':
    initialize_database()
