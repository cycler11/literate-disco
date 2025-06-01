def test_index_route(app, client, init_database):

    resp = client.get('/')
    assert resp.status_code == 200
    assert b'<html' in resp.data, "HTML '/'"
