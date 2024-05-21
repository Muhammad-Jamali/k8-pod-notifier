from kubernetes import client, config
import requests
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv


load_dotenv()

environment=os.environ["ENVIRONMENT"]
text_format=os.environ["SLACK_TEXT_FORMAT"]

print("Loading config")
if os.environ["LOAD_CLUSTER_CONFIG"].lower() in ['true', '1']:
    config.load_incluster_config()
else:
    config.load_config()
print("Config loaded")

slack_webhook_url = os.environ["SLACK_CHANNEL"]


def send_slack_message(message):
    payload = {'text': message}
    requests.post(slack_webhook_url, data=json.dumps(payload),
                  headers={'Content-Type': 'application/json'})


v1 = client.CoreV1Api()
not_ready_pods = set()


def is_pod_not_ready(pod):
    conditions = pod.status.conditions
    for condition in conditions:
        if condition.type == "Ready" and condition.status == "False" and condition.reason == "ContainersNotReady":
            not_ready_pods.add(pod.metadata.name)
            return True

    if pod.metadata.name in not_ready_pods:
        service = str(' ').join(str(pod.metadata.name).split('-')[:-2])
        send_slack_message(text_format.format(**{"service": service, "environment": environment}))
        not_ready_pods.remove(pod.metadata.name)

    return False


while True:
    try:
        pods = v1.list_namespaced_pod(namespace='default', watch=False)

        for pod in pods.items:
            if is_pod_not_ready(pod):
                print(f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] Pod {pod.metadata.name} is not ready")

        if (not len(not_ready_pods) > 0):
            print(
                f"[{datetime.now().strftime("%d-%m-%Y %H:%M:%S")}] No pod going from not ready state to ready state yet. Waiting...")
        time.sleep(5)  # Wait for 5 seconds before checking again

    except KeyboardInterrupt:
        print("Interrupted")
        break
    except Exception as e:
        print("Error:", e)
