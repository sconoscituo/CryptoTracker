import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
async def client():
    """테스트용 비동기 HTTP 클라이언트"""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_check(client):
    """헬스체크 엔드포인트 테스트"""
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "healthy"


@pytest.mark.asyncio
async def test_root(client):
    """루트 엔드포인트 테스트"""
    resp = await client.get("/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["service"] == "CryptoTracker"


@pytest.mark.asyncio
async def test_register_and_login(client):
    """회원가입 및 로그인 흐름 테스트"""
    # 회원가입
    resp = await client.post("/users/register", json={
        "email": "test@example.com",
        "password": "testpass123"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "test@example.com"
    assert data["is_premium"] is False

    # 로그인
    resp = await client.post("/users/login", data={
        "username": "test@example.com",
        "password": "testpass123"
    })
    assert resp.status_code == 200
    token_data = resp.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_duplicate_register(client):
    """중복 이메일 회원가입 방지 테스트"""
    payload = {"email": "dup@example.com", "password": "pass"}
    await client.post("/users/register", json=payload)
    resp = await client.post("/users/register", json=payload)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_get_me(client):
    """내 정보 조회 테스트"""
    # 회원가입 + 로그인
    await client.post("/users/register", json={"email": "me@example.com", "password": "pass123"})
    login = await client.post("/users/login", data={"username": "me@example.com", "password": "pass123"})
    token = login.json()["access_token"]

    resp = await client.get("/users/me", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
    assert resp.json()["email"] == "me@example.com"


@pytest.mark.asyncio
async def test_add_holding_free_limit(client):
    """무료 플랜 코인 5개 제한 테스트"""
    await client.post("/users/register", json={"email": "limit@example.com", "password": "pass"})
    login = await client.post("/users/login", data={"username": "limit@example.com", "password": "pass"})
    token = login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    coins = [
        ("bitcoin", "Bitcoin"), ("ethereum", "Ethereum"), ("solana", "Solana"),
        ("cardano", "Cardano"), ("dogecoin", "Dogecoin"),
    ]
    for symbol, name in coins:
        resp = await client.post("/portfolio/holdings", json={
            "symbol": symbol, "name": name, "amount": 1.0, "avg_buy_price": 100.0
        }, headers=headers)
        assert resp.status_code == 201

    # 6번째 코인 추가 시 403 반환
    resp = await client.post("/portfolio/holdings", json={
        "symbol": "ripple", "name": "XRP", "amount": 100.0, "avg_buy_price": 0.5
    }, headers=headers)
    assert resp.status_code == 403


@pytest.mark.asyncio
async def test_unauthorized_access(client):
    """인증 없이 보호된 엔드포인트 접근 시 401 테스트"""
    resp = await client.get("/portfolio/")
    assert resp.status_code == 401
