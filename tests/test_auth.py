def test_registro_usuario(client):
	payload = {"nombre": "Test User", "email": "test@example.com", "password": "secret"}
	response = client.post("/auth/register", json=payload)
	assert response.status_code == 201
	data = response.json()
	assert data["email"] == payload["email"]
	assert "id" in data


def test_login_usuario(client):
	payload = {"nombre": "Test User", "email": "login@example.com", "password": "secret"}
	register = client.post("/auth/register", json=payload)
	assert register.status_code == 201

	response = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
	assert response.status_code == 200
	data = response.json()
	assert "access_token" in data
	assert data["token_type"] == "bearer"
