from locust import HttpUser, task


class MUStatic(HttpUser):
    @task
    def load_home(self):
        self.client.get(url='/')
