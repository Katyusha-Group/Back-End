from locust import HttpUser, TaskSet, task, between

class QuickstartUser(HttpUser):
    def on_start(self):
        # {
        #   "email_or_username": "string",
        #   "password": "string"
        # }
        response = self.client.post("/accounts/login", data={"email_or_username": "admin", "password": "admin"}, name="Login")
        self.client.headers = {'Authorization': f"Bearer {response.get('access', None)}"}
        response = response.json()

