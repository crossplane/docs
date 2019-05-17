# Crossplane

GitLab-Controller is Crossplane native application which enables provisioning a production grade GitLab services 
accros multiple supported cloud providers. GitLab-Controller leverages Crossplane core constructs such as 
CloudProvider(s), ResourceClass(es), and ResourceClaim(s) to satisfy GitLab Services dependencies on public cloud
managed services. GitLab-Controller utilizes Crossplane Workloads to provision GitLab services and all its 
dependencies on target Kubernetes clusters managed and provisioned by the Crossplane.   

## Architecture and Vision

The design draft of the Crossplane GitLab-Controller 
[initial design](https://docs.google.com/document/d/1_pD0w5rmkx6Rch5IRYhuVIYuSbFCJGlRGNiUxpTfrZ0/edit?usp=sharing). 

## Table of Contents

* [Quick Start Guide](quick-start.md)
* [Contributing](contributing.md)
