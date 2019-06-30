# AWS Elastic Load Balancing Hook

If you want to deploy a `DaemonSet` with `hostPort`, and expose it with AWS Elastic Load Balancing, this container can help you to register your instance in target group after launch and deregister your instance before terminating.

> Only support AWS Application Load Balancer with Target Group.

### Exapmle

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: nginx-daemonset
  namespace: default
  labels:
    app: nginx-daemonset
    version: v1
spec:
  selector:
    matchLabels:
      app: nginx-daemonset
      version: v1
  template:
    metadata:
      labels:
        app: nginx-daemonset
        version: v1
    spec:
      terminationGracePeriodSeconds: 60 # Change the default value 30 to 60
      containers:
      - name: nginx
        image: nginx:1.17-alpine
        ports:
        - containerPort: 80
          hostPort: 32080 # The port expose to AWS Elastic Load Balancing
          protocol: TCP
        livenessProbe:
          httpGet:
            path: /
            port: 80
            scheme: HTTP
          initialDelaySeconds: 5
          periodSeconds: 5
        readinessProbe:
          httpGet:
            path: /
            port: 80
            scheme: HTTP
          initialDelaySeconds: 5
          periodSeconds: 5
        lifecycle:
          preStop:
            exec:
              command: ["sleep","30"] # Wait for 30s after deregister from AWS Elastic Load Balancing
      - name: aws-elb-hook-docker # Add this after your containers
        image: aminoapps/aws-elb-hook-docker
        env:
        - name: LB_TARGETS
          value: "arn:aws:elasticloadbalancing:us-west-2:799176492113:targetgroup/k8s-nodes-nginx-ingress/b4e8913e6bf8c1d5|32080"
```