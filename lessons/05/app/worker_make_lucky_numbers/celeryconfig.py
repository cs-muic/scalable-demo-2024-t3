# celeryconfig.py
broker_url = 'redis://redis:6379/0'  # Or your chosen broker (e.g., RabbitMQ)
result_backend = 'redis://redis:6379/0' # Or your chosen backend
task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Bangkok'  # Set to your desired timezone
enable_utc = True
