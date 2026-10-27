from backend.routes import db, initialize_database

def test_song_lifecycle(client):
    initialize_database()
    original_count = client.get('/count').json['length']
    assert len(client.get('/song').json) == original_count
    assert client.get('/song/1').status_code == 200
    assert client.get('/song/999999').status_code == 404
    song = {'id': 999999, 'title': 'Integration Test', 'lyrics': 'Sample lyrics'}
    assert client.post('/song', json=song).status_code == 201
    assert client.post('/song', json=song).status_code == 302
    assert client.get('/count').json['length'] == original_count + 1
    song['lyrics'] = 'Updated lyrics'
    assert client.put('/song/999999', json=song).status_code == 200
    assert client.get('/song/999999').json['lyrics'] == 'Updated lyrics'
    assert client.put('/song/999999', json={'id': 123}).status_code == 400
    assert client.delete('/song/999999').status_code == 204
    assert client.delete('/song/999999').status_code == 404
    assert client.get('/count').json['length'] == original_count

def test_seed_is_non_destructive(client):
    initialize_database()
    original = db.songs.find_one({'id': 1})['lyrics']
    try:
        db.songs.update_one({'id': 1}, {'$set': {'lyrics': 'A user edit'}})
        initialize_database()
        assert db.songs.find_one({'id': 1})['lyrics'] == 'A user edit'
    finally:
        db.songs.update_one({'id': 1}, {'$set': {'lyrics': original}})
