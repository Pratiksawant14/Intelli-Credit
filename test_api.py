import json
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_api():
    print("Testing Root...")
    response = client.get("/")
    print(response.json())
    
    print("\nTesting Score Endpoint...")
    score_payload = {
        "raw_text": "Orbit Holdings Pvt Ltd mentioned NPA in court.",
        "document_data": {
            "revenue": 1000000,
            "working_capital": 200000
        }
    }
    response = client.post("/api/v1/score/", json=score_payload)
    print("Score Response:", json.dumps(response.json(), indent=2))
    
    print("\nTesting Evidence Endpoint...")
    response = client.get("/api/v1/evidence/?entity_name=Orbit Holdings&query=npa")
    print("Evidence Response:", response.json())
    
    print("\nTesting CAM Endpoint...")
    cam_payload = {
        "company_name": "Orbit Holdings Pvt Ltd",
        "date": "2024-03-01",
        "entity_id": "L12345MH2013PLC000123",
        "features": score_payload["document_data"],
        "ml_output": response.json().get("score_result", {"predicted_score": 0.5, "decision": "Watchlist", "top_features": []}),
        "entity_data": response.json().get("nlp_entities", []),
        "evidence": []
    }
    # For CAM generation, we test if it returns a 200 and a PDF attachment
    response = client.post("/api/v1/generate-cam/", json=cam_payload)
    print("CAM Status:", response.status_code)
    print("CAM Headers:", dict(response.headers))

if __name__ == "__main__":
    test_api()
