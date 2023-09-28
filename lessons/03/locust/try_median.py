from locust import HttpUser, task
import random

numbers = [ random.randint(1, 1000) for _ in range(500) ]

class Median(HttpUser):
    @task
    def median_of_500(self):
        _ = self.client.post(url="/median", json={"numbers": numbers})
