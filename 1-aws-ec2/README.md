# Flask Application Deployment on AWS EC2

## 1. Project Overview

This project demonstrates how to deploy a Python Flask application on an AWS EC2 virtual machine running Ubuntu.

The application is served using Gunicorn and managed by systemd so that it continues running in the background and starts automatically when the server reboots.

### Objectives

- Create and configure an AWS EC2 instance.
- Configure secure access using Security Groups.
- Install Python and create a virtual environment.
- Build a Flask application with multiple endpoints.
- Run Flask using Gunicorn.
- Configure systemd to manage the application.
- Understand AWS IAM roles and permissions.

## 2. Technology Stack

| Technology | Purpose |
|---|---|
| AWS EC2 | Provides a virtual Linux server |
| Ubuntu | Operating system |
| Python | Application programming language |
| Flask | Python web framework |
| Gunicorn | Production WSGI application server |
| systemd | Manages the application as a background service |
| IAM | Manages AWS permissions |
| Security Groups | Controls network access to EC2 |

## 3. Architecture

Browser → AWS EC2 → Ubuntu → Gunicorn → Flask Application

The browser sends an HTTP request to the EC2 public IP on port 5000.

The Security Group permits the request, Gunicorn receives it, and Flask processes the requested endpoint.

## 4. AWS Infrastructure Configuration

### EC2 Instance

- Instance name: Flask-Monitoring-Server
- Operating system: Ubuntu 26.04.1 LTS
- Region: Asia Pacific (Mumbai) – ap-south-1
- Access method: EC2 Instance Connect
- Application port: 5000
- SSH port: 22

### Security Group

Configured inbound rules:

| Type | Port | Source | Purpose |
|---|---:|---|---|
| SSH | 22 | My IP | SSH access |
| SSH | 22 | EC2 Instance Connect prefix list | Browser-based EC2 access |
| Custom TCP | 5000 | My IP | Access Flask application |

Note: These are the rules configured during development. For a public-facing application, access rules should be reviewed and restricted appropriately.

### IAM Role

Created an IAM role:

`EC2-CloudWatch-Role`

- Trusted entity: AWS service – EC2
- Attached policy: CloudWatchAgentServerPolicy

Purpose: Allows the EC2 instance to access permitted CloudWatch Agent APIs without storing AWS access keys on the server.

The role was created for the monitoring stage; full CloudWatch Agent log collection has not yet been configured.

## 5. Application Development

### Step 1: Update Ubuntu

```bash
sudo apt update
```

Updates the package index so Ubuntu can identify available software packages.

### Step 2: Install Python tools

```bash
sudo apt install python3 python3-venv python3-pip -y
```

- python3: Python interpreter.
- python3-venv: Creates isolated Python environments.
- python3-pip: Installs Python packages.

### Step 3: Create project directory

```bash
mkdir flask-app
cd flask-app
```

Creates a directory to store the application.

### Step 4: Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

A virtual environment isolates project dependencies from the system's Python installation.

The `source` command activates the environment.

### Step 5: Install dependencies

```bash
pip install flask gunicorn
```

- Flask: Creates the web application.
- Gunicorn: Runs the Flask application as a WSGI server.

## 6. Running the Application Using Gunicorn

Initially, the application was started using:

```bash
gunicorn --workers 1 --bind 0.0.0.0:5000 app:app
```

Understanding the command:

| Part | Meaning |
|---|---|
| gunicorn | Starts Gunicorn |
| --workers 1 | Creates one worker process |
| --bind 0.0.0.0:5000 | Listens on all network interfaces on port 5000 |
| app:app | First `app` is the Python file; second `app` is the Flask application object |

Gunicorn acts as the WSGI server between incoming HTTP requests and the Flask application.

## 7. Managing the Application with systemd

Running Gunicorn directly in the terminal is not ideal because stopping the terminal process also stops the application.

To solve this, we created a systemd service.

### Service file location

`/etc/systemd/system/flask-app.service`

### Configuration

```ini
[Unit]
Description=Flask Monitoring Application
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/flask-app
ExecStart=/home/ubuntu/flask-app/venv/bin/gunicorn --workers 1 --bind 0.0.0.0:5000 --access-logfile - --error-logfile - app:app
Restart=always
RestartSec=5
StandardOutput=append:/var/log/flask-app.log
StandardError=append:/var/log/flask-app.log

[Install]
WantedBy=multi-user.target
```

### Understanding each section

**[Unit]**

- `Description`: Describes the service.
- `After=network.target`: Starts the service after the network target has been reached.

**[Service]**

- `User=ubuntu`: Runs the application as the Ubuntu user instead of root.
- `WorkingDirectory`: Sets the application directory.
- `ExecStart`: Specifies the Gunicorn command.
- `Restart=always`: Restarts the service if it stops.
- `RestartSec=5`: Waits five seconds before restarting.
- `StandardOutput`: Writes standard output to the application log.
- `StandardError`: Writes error output to the same log.

**[Install]**

- `WantedBy=multi-user.target`: Allows the service to start automatically during normal system startup.

### Create the log file

```bash
sudo touch /var/log/flask-app.log
sudo chown ubuntu:ubuntu /var/log/flask-app.log
```

Creates the log file and gives the Ubuntu user ownership.

### Load and start the service

```bash
sudo systemctl daemon-reload
sudo systemctl start flask-app
sudo systemctl enable flask-app
sudo systemctl status flask-app
```

| Command | Purpose |
|---|---|
| daemon-reload | Reloads systemd service definitions |
| start | Starts the application service |
| enable | Enables automatic startup on boot |
| status | Checks the service status |

### Useful management commands

```bash
sudo systemctl stop flask-app
sudo systemctl restart flask-app
sudo systemctl status flask-app
sudo journalctl -u flask-app -n 30 --no-pager
```

## 8. Testing the Application

Replace `YOUR_EC2_PUBLIC_IP` with your instance's public IPv4 address.

| Endpoint | URL | Expected result |
|---|---|---|
| Home | `http://YOUR_EC2_PUBLIC_IP:5000/` | Application success message |
| Health | `http://YOUR_EC2_PUBLIC_IP:5000/health` | Healthy status |
| Error | `http://YOUR_EC2_PUBLIC_IP:5000/error` | Intentional server error |

---

**Project:** Flask Application Deployment on AWS EC2  
**Cloud Provider:** Amazon Web Services  
**Region:** ap-south-1  
**Application:** Python Flask  
**Server:** Gunicorn + systemd
