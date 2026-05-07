import requests
import json

SERVER_URL = "http://127.0.0.1:5678/enqueue_task1_chart"

payload = {
    "id": "T1-New-08",
    "question": "The table shows the percentages of the population by age groups in one country in three different years.",
    "sample": "The table illustrates the proportion of citizens in various age brackets in a single nation over three separate years. Overall, it is clear that while the percentage of young people and middle-aged adults decreased, the figure for the elderly rose significantly. In year 1, the 0-14 age group accounted for nearly 30% of the population, but this dropped to about 18% by year 3. Similarly, the 15-59 group fell from 60% to 50%. In contrast, the 60+ group more than doubled, increasing from 10% to over 30%."
}

try:
    response = requests.post(SERVER_URL, json=payload, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
