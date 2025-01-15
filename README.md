# Systemd Control

Imagine you have a VPS (or other server) running your personal website (or a discord bot, API, etc.).
You're probably using `systemd`, a tool that provides easy configuration of services.
Normally, you would interact with `systemd` by SSH-ing into your VPS and running commands like `systemctl start my-service` or `journalctl -u my-service`.
However, when you simply want to start/stop services or view logs, this can be tedious.

Introducing Systemd Control, a web API you can deploy on your VPS to easily manage your services.

## Routes

- `GET /list`: Get a list of all services and IDs
- `GET /<service_id>`: Get more information about a specific service
- `GET /<service_id>/logs/<n:optional>`: Get service logs (last `n` lines)
- `POST /<service_id>/start`: Start a service
- `POST /<service_id>/stop`: Stop a service
- `POST /<service_id>/restart`: Restart a service

## Authentication

Systemd Control uses a simple bearer token for authentication. First, specify the token in the `TOKEN` variable in `systemd_control/secret.py` (an example can be found at `systemd_control/secret.example.py`).

Then, include the token in the `Authorization` header of your requests:

```bash
curl <domain>/list -H "Authorization: Bearer <token>"
```
