---
title: Crossplane with Workload Identity
weight: 205
description: Configure Crossplane to pull packages from cloud provider container registries using workload identity
---

When running Crossplane on managed Kubernetes clusters (EKS, AKS, GKE), you can leverage Kubernetes Workload Identity to grant Crossplane access to pull packages from private cloud container registries. This allows Crossplane to install providers, functions, and configurations from registries like AWS ECR, Azure ACR, and Google Artifact Registry without managing static credentials.

{{< hint "important" >}}
This guide configures the **Crossplane package manager** to pull packages from private registries. However, packages reference container images that run as separate pods (providers and functions).

**Two-step image pull process:**
1. **Crossplane package manager** pulls the package, extracts the package contents (CRDs, XRDs) and creates deployments
2. **Kubernetes nodes** pull the runtime container images when creating provider/function pods

This guide only covers step 1. For step 2, ensure your Kubernetes nodes have permissions to pull images from the private registry. This is typically configured at the cluster level:
- **AWS EKS**: Node IAM role with ECR pull permissions
- **Azure AKS**: Kubelet managed identity with `AcrPull` role
- **GCP GKE**: Node service account with Artifact Registry reader role

Without node-level access, package installation succeeds but pods fail with `ImagePullBackOff`.
{{< /hint >}}

## Overview

To enable Crossplane package manager access to private registries, configure service account annotations during installation. The `crossplane` service account in the `crossplane-system` namespace requires specific annotations for each cloud provider:

- **AWS EKS**: IAM Roles for Service Accounts (IRSA)
- **Azure AKS**: Azure Workload Identity
- **Google Cloud GKE**: GKE Workload Identity

Select your cloud provider below for detailed setup instructions:

{{< tabs >}}

{{< tab "AWS EKS" >}}

## AWS EKS Integration

Configure Crossplane to pull packages from Amazon ECR using IAM Roles for Service Accounts (IRSA).

### Prerequisites

- An Amazon EKS cluster with OIDC provider enabled
- AWS CLI installed and configured
- `kubectl` configured to access your EKS cluster
- Permissions to create IAM roles and policies

### Enable OIDC Provider

If your EKS cluster doesn't have an OIDC provider, enable it:

```bash
eksctl utils associate-iam-oidc-provider \
  --cluster=<CLUSTER_NAME> \
  --approve
```

Verify the OIDC provider:

```bash
aws eks describe-cluster \
  --name <CLUSTER_NAME> \
  --query "cluster.identity.oidc.issuer" \
  --output text
```

### Create IAM Policy for ECR Access

Create an IAM policy that grants permissions to pull images from ECR:

```bash
cat > crossplane-ecr-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ecr:GetAuthorizationToken"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:BatchCheckLayerAvailability",
        "ecr:GetDownloadUrlForLayer",
        "ecr:BatchGetImage"
      ],
      "Resource": "arn:aws:ecr:<REGION>:<ACCOUNT_ID>:repository/*"
    }
  ]
}
EOF

aws iam create-policy \
  --policy-name CrossplaneECRPolicy \
  --policy-document file://crossplane-ecr-policy.json
```

{{< hint "note" >}}
Replace `<REGION>` and `<ACCOUNT_ID>` with your AWS region and account ID. You can restrict the `Resource` to specific repositories if needed.
{{< /hint >}}

### Create IAM Role with Trust Policy

Create an IAM role that can be assumed by the Crossplane service account:

```bash
export CLUSTER_NAME=<your-cluster-name>
export AWS_REGION=<your-aws-region>
export AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
export OIDC_PROVIDER=$(aws eks describe-cluster --name $CLUSTER_NAME --region $AWS_REGION --query "cluster.identity.oidc.issuer" --output text | sed -e "s/^https:\/\///")

cat > trust-policy.json <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Federated": "arn:aws:iam::${AWS_ACCOUNT_ID}:oidc-provider/${OIDC_PROVIDER}"
      },
      "Action": "sts:AssumeRoleWithWebIdentity",
      "Condition": {
        "StringEquals": {
          "${OIDC_PROVIDER}:sub": "system:serviceaccount:crossplane-system:crossplane",
          "${OIDC_PROVIDER}:aud": "sts.amazonaws.com"
        }
      }
    }
  ]
}
EOF

aws iam create-role \
  --role-name CrossplaneECRRole \
  --assume-role-policy-document file://trust-policy.json
```

### Attach Policy to Role

Attach the ECR policy to the IAM role:

```bash
aws iam attach-role-policy \
  --role-name CrossplaneECRRole \
  --policy-arn arn:aws:iam::${AWS_ACCOUNT_ID}:policy/CrossplaneECRPolicy
```

### Install Crossplane with IRSA Annotation

Install Crossplane with the service account annotation:

```bash
helm upgrade --install crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace \
  --set "serviceAccount.customAnnotations.eks\.amazonaws\.com/role-arn=arn:aws:iam::${AWS_ACCOUNT_ID}:role/CrossplaneECRRole"
```

### Verify Configuration

Check that the service account has the correct annotation:

```bash
kubectl get sa crossplane -n crossplane-system -o yaml
```

Expected output should include:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/CrossplaneECRRole
  name: crossplane
  namespace: crossplane-system
```

### Test Package Installation from ECR

Once configured, you can install Crossplane packages (Providers, Functions, Configurations) from your ECR registry. Here's an example using a Provider:

```bash
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-aws-s3
spec:
  package: ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/crossplane/provider-aws-s3:v1.2.0
EOF
```

Check the provider installation status:

```bash
kubectl get provider provider-aws-s3
kubectl describe provider provider-aws-s3
```

### Troubleshooting

#### Failed to Get Authorization Token

**Error:**
```
failed to get authorization token: AccessDeniedException
```

**Solution:**
1. Verify the IAM role has the `ecr:GetAuthorizationToken` permission
2. Check the trust policy allows the service account to assume the role
3. Ensure the service account annotation matches the IAM role ARN exactly

#### Invalid Identity Token

**Error:**
```
An error occurred (InvalidIdentityToken) when calling the AssumeRoleWithWebIdentity operation
```

**Solution:**
1. Verify OIDC provider is enabled on your EKS cluster
2. Check the trust policy condition matches your cluster's OIDC provider
3. Ensure the service account namespace and name in the condition are correct

#### Access Denied to ECR Repository

**Error:**
```
denied: User: arn:aws:sts::123456789012:assumed-role/CrossplaneECRRole is not authorized to perform: ecr:BatchGetImage
```

**Solution:**
1. Verify the IAM policy includes `ecr:BatchGetImage`, `ecr:BatchCheckLayerAvailability`, and `ecr:GetDownloadUrlForLayer`
2. Check the policy's `Resource` includes your ECR repository ARN
3. Ensure the IAM policy is attached to the IAM role

#### Service Account Annotation Not Applied

If the service account doesn't have the annotation after installation:

```bash
# Update via Helm
helm upgrade crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --reuse-values \
  --set "serviceAccount.customAnnotations.eks\.amazonaws\.com/role-arn=arn:aws:iam::${AWS_ACCOUNT_ID}:role/CrossplaneECRRole"

# Restart Crossplane
kubectl rollout restart deployment/crossplane -n crossplane-system
```

### Check Crossplane Logs

View logs for authentication issues:

```bash
kubectl logs -n crossplane-system deployment/crossplane --all-containers -f
```

Look for:
- AWS credential errors
- ECR authentication failures
- Image pull errors with specific repository paths

### Additional Resources

- [Amazon EKS IRSA Documentation](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html)
- [Amazon ECR Authentication](https://docs.aws.amazon.com/AmazonECR/latest/userguide/security-iam.html)

{{< /tab >}}

{{< tab "Azure AKS" >}}

## Azure AKS Integration

Configure Crossplane to pull packages from Azure Container Registry (ACR) using Azure Workload Identity.

### Prerequisites

- An AKS cluster with Workload Identity enabled
- Azure CLI installed and configured
- `kubectl` configured to access your AKS cluster
- Permissions to create Azure managed identities and role assignments

### Enable Workload Identity on AKS

If your AKS cluster doesn't have Workload Identity enabled, update it:

```bash
export RESOURCE_GROUP=<your-resource-group>
export CLUSTER_NAME=<your-cluster-name>

az aks update \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --enable-oidc-issuer \
  --enable-workload-identity
```

Get the OIDC issuer URL:

```bash
export AKS_OIDC_ISSUER=$(az aks show \
  --resource-group $RESOURCE_GROUP \
  --name $CLUSTER_NAME \
  --query "oidcIssuerProfile.issuerUrl" \
  --output tsv)

echo $AKS_OIDC_ISSUER
```

### Create Azure Managed Identity

Create a managed identity for Crossplane:

```bash
export IDENTITY_NAME=crossplane-acr-identity

az identity create \
  --name $IDENTITY_NAME \
  --resource-group $RESOURCE_GROUP

export USER_ASSIGNED_CLIENT_ID=$(az identity show \
  --name $IDENTITY_NAME \
  --resource-group $RESOURCE_GROUP \
  --query 'clientId' \
  --output tsv)

export USER_ASSIGNED_OBJECT_ID=$(az identity show \
  --name $IDENTITY_NAME \
  --resource-group $RESOURCE_GROUP \
  --query 'principalId' \
  --output tsv)

echo "Client ID: $USER_ASSIGNED_CLIENT_ID"
echo "Object ID: $USER_ASSIGNED_OBJECT_ID"
```

### Assign ACR Pull Role

Grant the managed identity permission to pull from ACR:

```bash
export ACR_NAME=<your-acr-name>

export ACR_ID=$(az acr show \
  --name $ACR_NAME \
  --query 'id' \
  --output tsv)

az role assignment create \
  --assignee-object-id $USER_ASSIGNED_OBJECT_ID \
  --assignee-principal-type ServicePrincipal \
  --role AcrPull \
  --scope $ACR_ID
```

### Create Federated Identity Credential

Create a federated identity credential that establishes trust between the managed identity and the Kubernetes service account:

```bash
az identity federated-credential create \
  --name crossplane-federated-credential \
  --identity-name $IDENTITY_NAME \
  --resource-group $RESOURCE_GROUP \
  --issuer $AKS_OIDC_ISSUER \
  --subject system:serviceaccount:crossplane-system:crossplane \
  --audience api://AzureADTokenExchange
```

### Install Crossplane with Workload Identity Configuration

Get the tenant ID:

```bash
export AZURE_TENANT_ID=$(az account show --query tenantId --output tsv)
```

Install Crossplane with the workload identity annotations and label:

```bash
helm upgrade --install crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace \
  --set "serviceAccount.customAnnotations.azure\.workload\.identity/client-id=$USER_ASSIGNED_CLIENT_ID" \
  --set "serviceAccount.customAnnotations.azure\.workload\.identity/tenant-id=$AZURE_TENANT_ID" \
  --set-string 'customLabels.azure\.workload\.identity/use=true'
```

{{< hint "note" >}}
Azure Workload Identity requires:
- Service account annotations for the client ID and tenant ID
- Label `azure.workload.identity/use: "true"` on pods (applied via `customLabels`)

The `customLabels` setting applies the label to all Crossplane resources. The Azure Workload Identity webhook uses this label on pods to inject the necessary environment variables and token volumes. Use `--set-string` to ensure the value is treated as a string rather than a boolean.
{{< /hint >}}

### Verify Configuration

Check that the service account has the correct annotations:

```bash
kubectl get sa crossplane -n crossplane-system -o yaml
```

Expected output should include:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    azure.workload.identity/client-id: <client-id>
    azure.workload.identity/tenant-id: <tenant-id>
  name: crossplane
  namespace: crossplane-system
```

Check that the deployment has the required labels:

```bash
kubectl get deployment crossplane -n crossplane-system -o yaml
```

Expected output should include:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  labels:
    azure.workload.identity/use: "true"
  name: crossplane
  namespace: crossplane-system
spec:
  template:
    metadata:
      labels:
        azure.workload.identity/use: "true"
```

### Test Package Installation from ACR

Once configured, you can install Crossplane packages (Providers, Functions, Configurations) from your ACR. Here's an example using a Provider:

```bash
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-azure-storage
spec:
  package: ${ACR_NAME}.azurecr.io/crossplane/provider-azure-storage:v1.2.0
EOF
```

Check the provider installation status:

```bash
kubectl get provider provider-azure-storage
kubectl describe provider provider-azure-storage
```

### Troubleshooting

#### Unauthorized: Authentication Required

**Error:**
```
unauthorized: authentication required
```

**Solution:**
1. Verify the managed identity has `AcrPull` role on the ACR
2. Check the federated credential is configured correctly
3. Ensure the service account annotations match the managed identity client ID and tenant ID

#### Failed to Resolve Reference

**Error:**
```
failed to resolve reference: failed to fetch oauth token
```

**Solution:**
1. Verify Workload Identity is enabled on the AKS cluster
2. Check the OIDC issuer URL in the federated credential matches your cluster's OIDC issuer
3. Ensure the subject in the federated credential matches `system:serviceaccount:crossplane-system:crossplane`

#### Invalid Federated Token

**Error:**
```
invalid federated token
```

**Solution:**
1. Verify the federated credential audience is set to `api://AzureADTokenExchange`
2. Check that the OIDC issuer URL is correct
3. Ensure the service account namespace and name match the federated credential subject

#### Service Account Annotation Not Applied

If the service account doesn't have the annotations after installation:

```bash
# Update via Helm
helm upgrade crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --reuse-values \
  --set "serviceAccount.customAnnotations.azure\.workload\.identity/client-id=$USER_ASSIGNED_CLIENT_ID" \
  --set "serviceAccount.customAnnotations.azure\.workload\.identity/tenant-id=$AZURE_TENANT_ID"

# Restart Crossplane
kubectl rollout restart deployment/crossplane -n crossplane-system
```

### Check Crossplane Logs

View logs for authentication issues:

```bash
kubectl logs -n crossplane-system deployment/crossplane --all-containers -f
```

Look for:
- Azure authentication errors
- ACR authentication failures
- Image pull errors with specific repository paths

### Additional Resources

- [Azure Workload Identity Documentation](https://azure.github.io/azure-workload-identity/)
- [AKS Workload Identity Overview](https://learn.microsoft.com/en-us/azure/aks/workload-identity-overview)
- [Azure Container Registry Authentication](https://learn.microsoft.com/en-us/azure/container-registry/container-registry-authentication)

{{< /tab >}}

{{< tab "Google Cloud GKE" >}}

## Google Cloud GKE Integration

Configure Crossplane to pull packages from Google Artifact Registry using GKE Workload Identity.

### Prerequisites

- A GKE cluster with Workload Identity enabled
- `gcloud` CLI installed and configured
- `kubectl` configured to access your GKE cluster
- Permissions to create service accounts and IAM bindings

### Enable Workload Identity on GKE

If your GKE cluster doesn't have Workload Identity enabled, create a new cluster with it enabled or update an existing cluster:

**New cluster:**
```bash
export PROJECT_ID=<your-project-id>
export CLUSTER_NAME=<your-cluster-name>
export REGION=<your-region>

gcloud container clusters create $CLUSTER_NAME \
  --region=$REGION \
  --workload-pool=${PROJECT_ID}.svc.id.goog
```

**Existing cluster:**
```bash
gcloud container clusters update $CLUSTER_NAME \
  --region=$REGION \
  --workload-pool=${PROJECT_ID}.svc.id.goog
```

### Create Google Service Account

Create a Google Cloud service account for Crossplane:

```bash
export GSA_NAME=crossplane-gar-sa

gcloud iam service-accounts create $GSA_NAME \
  --display-name="Crossplane Artifact Registry Service Account" \
  --project=$PROJECT_ID
```

Get the full service account email:

```bash
export GSA_EMAIL=${GSA_NAME}@${PROJECT_ID}.iam.gserviceaccount.com
echo $GSA_EMAIL
```

### Grant Artifact Registry Permissions

Grant the service account permissions to read from Artifact Registry:

```bash
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${GSA_EMAIL}" \
  --role="roles/artifactregistry.reader"
```

For specific repository access, use:

```bash
export REPOSITORY=<your-repository-name>
export REPOSITORY_LOCATION=<repository-location>

gcloud artifacts repositories add-iam-policy-binding $REPOSITORY \
  --location=$REPOSITORY_LOCATION \
  --member="serviceAccount:${GSA_EMAIL}" \
  --role="roles/artifactregistry.reader"
```

### Create IAM Policy Binding

Create an IAM policy binding between the Google service account and the Kubernetes service account:

```bash
gcloud iam service-accounts add-iam-policy-binding $GSA_EMAIL \
  --role roles/iam.workloadIdentityUser \
  --member "serviceAccount:${PROJECT_ID}.svc.id.goog[crossplane-system/crossplane]"
```

### Install Crossplane with Workload Identity Annotation

Install Crossplane with the service account annotation:

```bash
helm upgrade --install crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --create-namespace \
  --set "serviceAccount.customAnnotations.iam\.gke\.io/gcp-service-account=$GSA_EMAIL"
```

### Verify Configuration

Check that the service account has the correct annotation:

```bash
kubectl get sa crossplane -n crossplane-system -o yaml
```

Expected output should include:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  annotations:
    iam.gke.io/gcp-service-account: crossplane-gar-sa@project-id.iam.gserviceaccount.com
  name: crossplane
  namespace: crossplane-system
```

### Test Package Installation from Artifact Registry

Once configured, you can install Crossplane packages (Providers, Functions, Configurations) from your Artifact Registry. Here's an example using a Provider:

```bash
kubectl apply -f - <<EOF
apiVersion: pkg.crossplane.io/v1
kind: Provider
metadata:
  name: provider-gcp-storage
spec:
  package: us-docker.pkg.dev/${PROJECT_ID}/crossplane/provider-gcp-storage:v1.2.0
EOF
```

Check the provider installation status:

```bash
kubectl get provider provider-gcp-storage
kubectl describe provider provider-gcp-storage
```

### Troubleshooting

#### Permission Denied

**Error:**
```
PERMISSION_DENIED: Permission denied on resource
```

**Solution:**
1. Verify the Google service account has `roles/artifactregistry.reader` role
2. Check the IAM policy binding exists between the Google and Kubernetes service accounts
3. Ensure the service account annotation matches the Google service account email exactly

#### Failed to Fetch OAuth Token

**Error:**
```
failed to fetch oauth token
```

**Solution:**
1. Verify Workload Identity is enabled on the GKE cluster
2. Check the IAM policy binding allows the Kubernetes service account to impersonate the Google service account
3. Ensure the workload pool matches your project: `${PROJECT_ID}.svc.id.goog`

#### Invalid Identity Token

**Error:**
```
invalid identity token
```

**Solution:**
1. Verify the IAM policy binding member format: `serviceAccount:${PROJECT_ID}.svc.id.goog[crossplane-system/crossplane]`
2. Check that Workload Identity is enabled on the node pool
3. Ensure the service account annotation is correct

#### Service Account Annotation Not Applied

If the service account doesn't have the annotation after installation:

```bash
# Update via Helm
helm upgrade crossplane \
  crossplane-stable/crossplane \
  --namespace crossplane-system \
  --reuse-values \
  --set "serviceAccount.customAnnotations.iam\.gke\.io/gcp-service-account=$GSA_EMAIL"

# Restart Crossplane
kubectl rollout restart deployment/crossplane -n crossplane-system
```

### Verify Workload Identity Configuration

Test the Workload Identity configuration:

```bash
# Check if Workload Identity is enabled on the cluster
gcloud container clusters describe $CLUSTER_NAME \
  --region=$REGION \
  --format="value(workloadIdentityConfig.workloadPool)"

# Verify IAM policy binding
gcloud iam service-accounts get-iam-policy $GSA_EMAIL
```

### Check Crossplane Logs

View logs for authentication issues:

```bash
kubectl logs -n crossplane-system deployment/crossplane --all-containers -f
```

Look for:
- Google Cloud authentication errors
- Artifact Registry authentication failures
- Image pull errors with specific repository paths

### Additional Resources

- [GKE Workload Identity Documentation](https://cloud.google.com/kubernetes-engine/docs/how-to/workload-identity)
- [Artifact Registry Authentication](https://cloud.google.com/artifact-registry/docs/docker/authentication)
- [IAM Service Account Permissions](https://cloud.google.com/iam/docs/service-accounts)

{{< /tab >}}

{{< /tabs >}}

## Configure After Installation

If Crossplane is already installed, you can update the service account annotations using Helm upgrade with the appropriate `--set` flags shown in your cloud provider's tab above. After updating, restart the Crossplane deployment:

```bash
kubectl rollout restart deployment/crossplane -n crossplane-system
```
