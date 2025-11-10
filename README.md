# ACEest Fitness - CI/CD Assignment (v1.0)

This repository contains the v1.0 (Tkinter -> Flask converted) application and CI/CD artifacts for the ACEest Fitness assignment.

Quick run (local)

1. Create & activate venv (Windows cmd):

   python -m venv .venv
   .venv\\Scripts\\activate.bat

2. Install deps:

   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   python -m pip install -r requirements-dev.txt

3. Run the app (v1 Flask app):

   python app.py

4. Browse:

   http://localhost:5001/
   http://localhost:5001/view

Testing

Run tests with pytest:

    pytest -q

Docker

Build the Docker image locally:

    docker build -t aceest/aceest-fitness:v1.0 .

Kubernetes

Apply manifests (Minikube / Kubernetes cluster):

# If you want persistent storage for workouts_v1.json, apply the PVC first:

kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

//

Notes

- The code for v1 is in `aceest_v1_flask.py` and templates in `/templates`.
- The original assignment files `ACEest_Fitness*.py` are ignored by `.gitignore` per your request.
- This repo contains sample CI/CD artifacts; adapt paths and credentials to your environment when integrating with Jenkins/Minikube/Docker Hub.
