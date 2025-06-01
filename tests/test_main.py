def test_index_route(app, client, init_database):
    """
    Проверяем, что корневой маршрут "/" возвращает 200 и отдаёт HTML.
    """
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'<html' in resp.data, "Ожидается HTML на странице '/'"
