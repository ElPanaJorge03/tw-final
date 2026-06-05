def test_ingredientes_crud(client):
	register = client.post(
		"/auth/register",
		json={"nombre": "Test User", "email": "ing@example.com", "password": "secret"},
	)
	assert register.status_code == 201

	login = client.post(
		"/auth/login",
		json={"email": "ing@example.com", "password": "secret"},
	)
	assert login.status_code == 200
	token = login.json()["access_token"]

	headers = {"Authorization": f"Bearer {token}"}
	create = client.post(
		"/ingredientes",
		json={"nombre": "tomate", "cantidad": "2", "unidad": "unidades"},
		headers=headers,
	)
	assert create.status_code == 201
	item = create.json()

	list_response = client.get("/ingredientes", headers=headers)
	assert list_response.status_code == 200
	assert len(list_response.json()) == 1

	update = client.put(
		f"/ingredientes/{item['id']}",
		json={"nombre": "tomate", "cantidad": "3", "unidad": "unidades"},
		headers=headers,
	)
	assert update.status_code == 200
	assert update.json()["cantidad"] == "3"

	delete = client.delete(f"/ingredientes/{item['id']}", headers=headers)
	assert delete.status_code == 204
