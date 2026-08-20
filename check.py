import requests

# Step 1: upload the sample report
with open("sample_blood_report.pdf", "rb") as f:
    r = requests.post("http://localhost:5000/api/upload",
                      files={"file": ("sample_blood_report.pdf", f, "application/pdf")})
print("Upload:", r.status_code, r.json())

report_id = r.json()["report_id"]

# Step 2: analyze it
r2 = requests.post(f"http://localhost:5000/api/analyze/{report_id}")
print("Analyze:", r2.status_code)
print(r2.json())