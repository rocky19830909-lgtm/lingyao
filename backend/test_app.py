import os
os.environ["DATABASE_URL"]="sqlite:///./test_lingyao.db"
from fastapi.testclient import TestClient
from app import app


def test_core_flow():
    with TestClient(app) as client:
        login=client.post("/api/auth/login",json={"phone":"13800000000","password":"123456"})
        assert login.status_code==200
        headers={"Authorization":f"Bearer {login.json()['access_token']}"}
        people=client.get("/api/candidates?q=算法",headers=headers)
        assert people.status_code==200 and people.json()
        duplicate=client.get("/api/candidates/duplicates/check?phone=13800138001",headers=headers)
        assert duplicate.json()["duplicate"] is True
        clients=client.get("/api/clients",headers=headers).json()
        job=client.post("/api/jobs",headers=headers,json={"title":"AI 产品总监","client_id":clients[0]["id"],"city":"上海","salary":"80-120万"})
        assert job.status_code==201
        app_row=client.post("/api/pipeline",headers=headers,json={"candidate_id":people.json()[0]["id"],"job_id":job.json()["id"],"stage":"联系"})
        moved=client.patch(f"/api/pipeline/{app_row.json()['id']}/stage",headers=headers,json={"stage":"推荐"})
        assert moved.json()["stage"]=="推荐"
        detail=client.get(f"/api/candidates/{people.json()[0]['id']}",headers=headers)
        assert detail.status_code==200 and "notes" in detail.json() and "attachments" in detail.json()
        dashboard=client.get("/api/dashboard",headers=headers)
        assert dashboard.status_code==200 and dashboard.json()["candidates"]>=3
        users=client.get("/api/users",headers=headers)
        assert users.status_code==200 and len(users.json())>=2
        profile=client.patch("/api/me",headers=headers,json={"name":"林若安测试"})
        assert profile.status_code==200 and profile.json()["name"]=="林若安测试"
        client.patch("/api/me",headers=headers,json={"name":"林若安"})
        avatar=client.post("/api/me/avatar",headers=headers,files={"file":("avatar.png",b"\x89PNG\r\n\x1a\n","image/png")})
        assert avatar.status_code==200
        assert client.get("http://testserver"+avatar.json()["avatar_url"]).status_code==200

        consultant_phone=next(x["phone"] for x in users.json() if x["role"]=="consultant")
        consultant_login=client.post("/api/auth/login",json={"phone":consultant_phone,"password":"123456"}).json()
        consultant_headers={"Authorization":f"Bearer {consultant_login['access_token']}"}
        protected=client.get("/api/users",headers=consultant_headers)
        assert protected.status_code==403
        shared=client.get("/api/candidates",headers=consultant_headers).json()
        someone_else=next(x for x in shared if x["owner_id"]!=consultant_login["user"]["id"])
        assert someone_else["can_view_contact"] is False and someone_else["phone"].startswith("****")

        senders=client.get("/api/resume-flow/senders",headers=headers).json()
        templates=client.get("/api/resume-flow/templates",headers=headers).json()
        application_template=next(x for x in templates if x["template_type"]=="application")
        flow=client.post("/api/resume-flow",headers=headers,json={"candidate_id":people.json()[0]["id"],"job_id":job.json()["id"],"sender_id":senders[0]["id"],"template_id":application_template["id"],"flow_type":"application","recipient_phone":"13800138001"})
        assert flow.status_code==201 and "?form=" in flow.json()["public_url"]
        token=flow.json()["token"]
        public=client.get(f"/api/public/resume-flow/{token}")
        assert public.status_code==200 and "recipient_phone" not in public.json()
        submitted=client.post(f"/api/public/resume-flow/{token}",json={"answers":{"姓名":"测试候选人","期望年薪":"80万"}})
        assert submitted.status_code==200
        flows=client.get("/api/resume-flow",headers=headers).json()
        saved=next(x for x in flows if x["token"]==token)
        assert saved["status"]=="已填写" and saved["answers"]["姓名"]=="测试候选人"
