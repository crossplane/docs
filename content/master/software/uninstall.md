---
title: Uninstall Crossplane
weight: 300
---

{{<hint "warning" >}}
Resources created by Crossplane aren't deleted if Crossplane isn't uninstalled
in order.

This can leave cloud resources running, requiring manual deletion.
{{< /hint >}}

## Ordered Crossplane uninstall
Most Crossplane resources have dependencies on other Crossplane resources. 

For example, a _managed resource_ is dependent on the _provider_.

Failure to delete Crossplane resources in order may prevent Crossplane from
deleting provisioned external resources.

Removing Crossplane resources should happen in the following order:
1. Remove all _composite resource definitions_
2. Remove all remaining _managed resources_
3. Remove all _providers_

Deleting the Crossplane pod removes remaining Crossplane components like _claims_.

{{<hint "tip" >}}
Collect an inventory of all external resources with `kubectl get managed`. 

Depending on the size of the Kubernetes API server and number of resources, this
command may take minutes to return.

{{<expand "An example kubectl get managed" >}}

```shell {copy-lines="1"}
kubectl get managed
NAME                                                 READY   SYNCED   EXTERNAL-NAME          AGE
securitygroup.ec2.aws.upbound.io/my-db-7mc7h-j84h8   True    True     sg-0da6e9c29113596b6   3m1s
securitygroup.ec2.aws.upbound.io/my-db-8bhr2-9wsx9   True    True     sg-02695166f010ec05b   2m26s

NAME                                         READY   SYNCED   EXTERNAL-NAME                       AGE
route.ec2.aws.upbound.io/my-db-7mc7h-vw985   True    True     r-rtb-05822b8df433e4e2b1080289494   3m1s
route.ec2.aws.upbound.io/my-db-8bhr2-7m2wq   False   True                                         2m26s

NAME                                                     READY   SYNCED   EXTERNAL-NAME      AGE
securitygrouprule.ec2.aws.upbound.io/my-db-7mc7h-mkd9s   True    True     sgrule-778063708   3m1s
securitygrouprule.ec2.aws.upbound.io/my-db-8bhr2-lzr89   False   True                        2m26s

NAME                                              READY   SYNCED   EXTERNAL-NAME           AGE
routetable.ec2.aws.upbound.io/my-db-7mc7h-mnqvm   True    True     rtb-05822b8df433e4e2b   3m1s
routetable.ec2.aws.upbound.io/my-db-8bhr2-dfhj6   True    True     rtb-02e875abd25658254   2m26s

NAME                                          READY   SYNCED   EXTERNAL-NAME              AGE
subnet.ec2.aws.upbound.io/my-db-7mc7h-7m49d   True    True     subnet-0c1ab32c5ec129dd1   3m2s
subnet.ec2.aws.upbound.io/my-db-7mc7h-9t64t   True    True     subnet-07075c17c7a72f79e   3m2s
subnet.ec2.aws.upbound.io/my-db-7mc7h-rs8t8   True    True     subnet-08e88e826a42e55b4   3m2s
subnet.ec2.aws.upbound.io/my-db-8bhr2-9sjpx   True    True     subnet-05d21c7b52f7ac8ca   2m26s
subnet.ec2.aws.upbound.io/my-db-8bhr2-dvrxf   True    True     subnet-0432310376b5d09de   2m26s
subnet.ec2.aws.upbound.io/my-db-8bhr2-t7dpr   True    True     subnet-0080fdcb6e9b70632   2m26s

NAME                                       READY   SYNCED   EXTERNAL-NAME           AGE
vpc.ec2.aws.upbound.io/my-db-7mc7h-ktbbh   True    True     vpc-08d7dd84e0c12f33e   3m3s
vpc.ec2.aws.upbound.io/my-db-8bhr2-mrh2x   True    True     vpc-06994bf323fc1daea   2m26s

NAME                                                   READY   SYNCED   EXTERNAL-NAME           AGE
internetgateway.ec2.aws.upbound.io/my-db-7mc7h-s2x4v   True    True     igw-0189c4da07a3142dc   3m1s
internetgateway.ec2.aws.upbound.io/my-db-8bhr2-q7dzl   True    True     igw-01bf2a1dbbebf6a27   2m26s

NAME                                                         READY   SYNCED   EXTERNAL-NAME                AGE
routetableassociation.ec2.aws.upbound.io/my-db-7mc7h-28qb4   True    True     rtbassoc-0718d680b5a0e68fe   3m1s
routetableassociation.ec2.aws.upbound.io/my-db-7mc7h-9hdlr   True    True     rtbassoc-0faaedb88c6e1518c   3m1s
routetableassociation.ec2.aws.upbound.io/my-db-7mc7h-txhmz   True    True     rtbassoc-0e5010724ca027864   3m1s
routetableassociation.ec2.aws.upbound.io/my-db-8bhr2-bvgkt   False   True                                  2m26s
routetableassociation.ec2.aws.upbound.io/my-db-8bhr2-d9gbg   False   True                                  2m26s
routetableassociation.ec2.aws.upbound.io/my-db-8bhr2-k6k8m   False   True                                  2m26s

NAME                                            READY   SYNCED   EXTERNAL-NAME       AGE
instance.rds.aws.upbound.io/my-db-7mc7h-5d6w4   False   True     my-db-7mc7h-5d6w4   3m1s
instance.rds.aws.upbound.io/my-db-8bhr2-tx9kf   False   True     my-db-8bhr2-tx9kf   2m26s

NAME                                               READY   SYNCED   EXTERNAL-NAME       AGE
subnetgroup.rds.aws.upbound.io/my-db-7mc7h-8c8n9   True    True     my-db-7mc7h-8c8n9   3m2s
subnetgroup.rds.aws.upbound.io/my-db-8bhr2-mc5ps   True    True     my-db-8bhr2-mc5ps   2m27s

NAME                                                   READY   SYNCED   EXTERNAL-NAME                 AGE
bucket.s3.aws.upbound.io/crossplane-bucket-867737b10   True    True
crossplane-bucket-867737b10   5m26s
```

{{</expand >}}
{{< /hint >}}

### Remove composite resource definitions
Removing installed _composite resource definitions_ removes any
_composite resources_ defined by the _composite resource definition_ and the
_managed resourced_ they created. 

View the installed _composite resource definitions_ with `kubectl get xrd`.

```shell {copy-lines="1"}
kubectl get xrd
NAME                                                ESTABLISHED   OFFERED   AGE
compositepostgresqlinstances.database.example.org   True          True      40s
```

Delete the _composite resource definitions_ with `kubectl delete xrd`.

```shell
kubectl delete xrd compositepostgresqlinstances.database.example.org
```

### Remove managed resources

Manually delete any _managed resources_ manually created. 

Use `kubectl get managed` to view remaining _managed resources_.

```shell {copy-lines="1"}
kubectl get managed
NAME                                                   READY   SYNCED   EXTERNAL-NAME                 AGE
bucket.s3.aws.upbound.io/crossplane-bucket-867737b10   True    True     crossplane-bucket-867737b10   8h
```

Use `kubectl delete` to remove the resources. 

```shell
kubectl delete bucket.s3.aws.upbound.io/crossplane-bucket-867737b10
```

### Remove Crossplane providers

List the installed _providers_ with `kubectl get providers`.

```shell {copy-lines="1"}
kubectl get providers
NAME                   INSTALLED   HEALTHY   PACKAGE                                        AGE
upbound-provider-aws   True        True      xpkg.upbound.io/upbound/provider-aws:v0.27.0   8h
```

Remove the installed _providers_ with `kubectl delete provider`.

```shell
kubectl delete provider upbound-provider-aws
```

## Uninstall the Crossplane deployment 

Uninstall Crossplane using Helm with `helm uninstall`

```shell
helm uninstall crossplane --namespace crossplane-system
```

Verify Helm removed the Crossplane pods with `kubectl get pods`

```shell
kubectl get pods -n crossplane-system
No resources found in crossplane-system namespace.
```

## Delete the Crossplane namespace

When Helm installs Crossplane it creates the `crossplane-system` namespace. Helm
doesn't uninstall this namespace with `helm uninstall`.

Manually delete the Crossplane namespace with `kubectl delete namespace`.

```shell
kubectl delete namespace crossplane-system
```

Verify Kubernetes removed the namespace with `kubectl get namespaces`

```shell
kubectl get namespace
NAME              STATUS   AGE
default           Active   2m45s
kube-flannel      Active   2m42s
kube-node-lease   Active   2m47s
kube-public       Active   2m47s
kube-system       Active   2m47s
```