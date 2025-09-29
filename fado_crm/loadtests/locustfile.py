from locust import HttpUser, task, between

class FadoUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def home(self):
        self.client.get("/")

    @task(2)
    def health(self):
        self.client.get("/performance/health")

    @task(1)
    def metrics(self):
        # scrape endpoint; not heavy
        self.client.get("/performance/metrics")
