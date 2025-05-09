from locust import HttpUser, task


class OSStatic(HttpUser):
    @task
    def load_home(self):
        self.client.get(url='/')
