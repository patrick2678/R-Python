py -m uvicorn app.main:app --reload

http://127.0.0.1:8000/dashboard/health

http://127.0.0.1:8000/dashboard/metrics

http://127.0.0.1:8000/dashboard/



py -m pytest app/tests/ -v