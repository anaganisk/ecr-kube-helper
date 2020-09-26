# ECR-KUBE-HELPER
ECR has an expiring registry authentication token(12 hours), integrating with your DIY kubernetes cluster is not easy. you have to refresh the secret every 12 hours.

This helper simply runs as a cronjob on kubernetes and updates the secret at chosen interval.

### Usage

The helper can only update one ECR ID for now so, if you want to use it with multiple ECRs you may have to create multiple cronjobs. One ECR ID may have multiple repositories
for example ECR_ID.dkr.ecr.ap-south-1.amazonaws.com/repository

```bash
# create a service account (least possible privileges)
kubectl apply -f example-service-account.yml
# create a secret(IMPORTANT) for AWS credentials with ECR IAM ROLE
kubectl create secret -n ecr-kube-helper generic ecr-kube-helper-ecr-secret --from-literal=REGION=[AWS_REGION] --from-literal=ID=[AWS_KEY_ID] --from-literal=SECRET=[AWS_SECRET]
# create the cron job
kubectl apply -f example-deployment-account.yml
```
The cronjob will automatically create an image pull secret as defined in the environment variable TARGET_SECRET

|Environment variable|DEFAULT|
|--------------------|-------|
|TARGET_SECRET|None (the secret name which will hold the ecr pull secret)|
|TARGET_NAMESPACE|None (the namespace you want the cronjob in)|
|TARGET_EMAIL|docker@example.com (can be anything, not really relevant)|
|TARGET_ECR|None (TARGET_ECR.dkr.ecr.ap-south-1.amazonaws.com/repository)|
|LOGLEVEL|DEBUG (Python log levels)|
|AWS_SECRET_ACCESS_KEY|None (define as secret) refer example-deployment.yml|
|AWS_ACCESS_KEY_ID|None (define as secret) refer example-deployment.yml|
|AWS_DEFAULT_REGION|None (define as secret) refer example-deployment.ymlone|

### LICENSE
**[WTFPL](http://www.wtfpl.net/)**
