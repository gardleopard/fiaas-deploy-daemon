# V3 Spec file reference

This file represents how your application will be deployed into Kubernetes.


## version

| **Type** | **Required** |
|----------|--------------|
| int      | yes          |

Which version of this spec to be used. This field must be set to `3` to use the features described below.
Documentation for [version 2 can be found here](/docs/v2_spec.md).

```yaml
version: 3
```


## replicas

| **Type** | **Required** |
|----------|--------------|
| object   | no           |

Number of pods (instances) to run of the application. Based on the values of `minimum` and `maximum`, this object also
controls whether the number of replicas should be automatically scaled based on load.


Default value:
```yaml
replicas:
  minimum: 2
  maximum: 5
  cpu_threshold_percentage: 50
```

### minimum

| **Type** | **Required** |
|----------|--------------|
| int      | no           |

Minimum number of pods to run for the application.

If `minimum` and `maximum` are set to the same value, autoscaling will be disabled.

Default value:
```yaml
replicas:
  minimum: 2
```


### maximum

| **Type** | **Required** |
|----------|--------------|
| int      | no           |

Maximum number of pods to run for the application.

If `minimum` and `maximum` are set to the same value, autoscaling will be disabled.


Default value:
```yaml
replicas:
  maximum: 5
```

### cpu_threshold_percentage

| **Type** | **Required** |
|----------|--------------|
| int      | no           |

If `maximum` is greater than `minimum`, autoscaling is enabled for the application.

Currently, the only supported metric for autoscaling is average cpu usage. If average cpu usage across all pods is
greater than this value over some time period, the number of pods will be increased. If average cpu usage across all
pods is less than this value, the number of pods will be decreased after some time period.

Autoscaling is done by using a
[`HorizontalPodAutoscaler`](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/).

If autoscaling is disabled, this value is ignored.

Default value:
```yaml
replicas:
  cpu_threshold_percentage: 50
```

## ingress

| **Type** | **Required** |
|----------|--------------|
| list     | no           |

This object configures path-based/layer 7 routing of requests to the application.
It is a list of hosts which can each have a list of path and port combinations. Requests to the combination of host and
path will be routed to the port specified on the path element.

Default value:
```yaml
ingress:
  - host: # no default value
    paths:
    - path: /
      port: http
```

### host

| **Type** | **Required** |
|----------|--------------|
| string   | no           |

The hostname part of a host + path combination where your application expects requests.

If fiaas-deploy-daemon in the cluster you are deploying to is set up with one or more default ingress suffixes , all
paths specified will be made available under these ingress suffixes.  E.g. if `foo.example.com` is the default ingress
suffix, and your application is named `myapp`, your application will be available on `myapp.foo.example.com/`

If the `host` field is set, the application will be available on `host` + any paths specified *in addition* to any
default ingress suffixes.

Example:
```yaml
ingress:
  - host: your-app.example.com
```

### paths

| **Type** | **Required** |
|----------|--------------|
| list     | no           |

List of paths and port combinations.

Example:
```yaml
ingress:
  - host: your-app.example.com
    paths:
      - path: /foo
      - path: /bar
      - path: /metrics
        port: metrics-port
```

In this example, requests to `your-app.example.com/foo` or `your-app.example.com/bar` will go to the port named
`http`. Unless overridden, this is the default service port 80 which points to target port 8080 in the pod running
your application. Requests to `your-app.example.com/metrics` will go to the port named metrics-port, which also has to
be defined under the `ports` configuration structure. It is also possible to use a port number, but named ports are
strongly recommended.


## healthchecks

| **Type** | **Required** |
|----------|--------------|
| object   | no           |

Application endpoints to be used by Kubernetes to determine [whether your application is up and/or ready to handle requests](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-probes/).
If `healthchecks.liveness` is specified and `healthchecks.readiness` is not specified, `healthchecks.liveness` will be used as the value for `healthchecks.readiness`.

### liveness

| **Type** | **Required** |
|----------|--------------|
| object   | no           |


Default value:
```yaml
healthchecks:
  liveness:
    execute:
      command: # No default value
    http:
      path: /_/health
      port: http
      http_headers: {}
    tcp:
      port: # no default value
    initial_delay_seconds: 10
    period_seconds: 10
    success_threshold: 1
    timeout_seconds: 1
```

You can only have one check, so specify only one of `execute`, `http`, or `tcp`. The default is a `http` check, which
will send a HTTP request to the path and port configuration on the pod running the application. The health check will
be considered good if the HTTP response has a status code in the 200 range. Otherwise it will be considered bad.

An `execute` check can be used to execute a program inside the pod running the application. In this case, a exit
status of 0 is considered a good health check, while any other exit status is considered bad.

Example:
```yaml
healthchecks:
  liveness:
    execute:
      command: /app/bin/check --foo
```

A `tcp` check can be used if the application's primary endpoint uses some other application layer protocol than
HTTP. This type of check attempts to negotiate a TCP handshake on the specified port. If this succeeds, the health
check is considered good, otherwise it is considered bad.

Example:
```yaml
healthchecks:
  liveness:
    tcp:
      port: 70
```

### readiness

| **Type** | **Required** |
|----------|--------------|
| object   | no           |

`liveness` and `readiness` use the same structure for configuring the check itself. See the documentation for `liveness`.


## resources

| **Type** | **Required** |
|----------|--------------|
| object   | no           |

[Resources](https://kubernetes.io/docs/concepts/configuration/manage-compute-resources-container/) required by the
application.

Default value:
```yaml
resources:
  limits:
    cpu: 400m
    memory: 512Mi
  requests:
    cpu: 200m
    memory: 256Mi
```

### limits

| **Type** | **Required** |
|----------|--------------|
| object   | no           |

Maximum amount of resources this application needs.

#### memory

| **Type** | **Required** |
|----------|--------------|
| string   | no           |

The application will be OOM killed if exceeding these limits.

#### cpu

| **Type** | **Required** |
|----------|--------------|
| string   | no           |

The application will have its CPU usage throttled if exceeding this limit.

### requests

| **Type** | **Required** |
|----------|--------------|
| object   | no           |

Minimum amount of resources this application needs.

#### memory

| **Type** | **Required** |
|----------|--------------|
| string   | no           |

The application will be scheduled on nodes with at least this amount of memory available.

#### cpu

| **Type** | **Required** |
|----------|--------------|
| string   | no           |

The application will be scheduled on nodes with at least this amount of CPU available.

Example:
```yaml
resources:
  limits:
    memory: 1G
    cpu: 1
  requests:
    memory:  512M
    cpu: 0.7
```


## metrics

### prometheus

| **Type** | **Required** |
|----------|--------------|
| object   | no           |

Tells Prometheus where to find application metrics.

Default value:
```yaml
metrics:
  prometheus:
    enabled: true
    port: http
    path: /_/metrics
```

#### enabled
| **Type** | **Required** |
|----------|--------------|
| boolean  | no           |

Whether or not the pods running the application will be scraped by Prometheus looking for metrics.

#### port
| **Type** | **Required** |
|----------|--------------|
| string   | no           |

Name of HTTP port Prometheus metrics are served on.

#### path
| **Type** | **Required** |
|----------|--------------|
| string   | no           |

HTTP endpoint where metrics are exposed.

### datadog

| **Type** | **Required** |
|----------|--------------|
| object   | no           |

Configure datadog.

Default value:
```yaml
metrics:
  datadog:
    enabled: false
```

#### enabled
| **Type** | **Required** |
|----------|--------------|
| boolean  | no           |

Attach a datadog sidecar for metrics collection. The sidecar will run DogStatsD, and your application should send metrics
to `${STATSD_HOST}:${STATSD_PORT}` (in the current incarnation, this is set to `localhost:8125`, but your application
should make use of the environment variables in order to be somewhat futureproof). In order for this to send metrics to the
correct datadog account, a secret must be created in the namespace which contains the datadog API key. This key decides
where the metrics end up.

Creating the datadog secret can be done using `kubectl` directly:

```
kubectl -n "${NAMESPACE}" create secret generic datadog --from-literal apikey="${DD_API_KEY}"
```

Three additional tags are attached to the collected metrics automatically:

- namespace name
- application name
- pod name

## ports

| **Type** | **Required** |
|----------|--------------|
| list     | no           |

List of ports the application listens for requests.

Default value:
```yaml
ports:
  - protocol: http
    name: http
    port: 80
    target_port: 8080
```

### protocol
| **Type** | **Required** |
|----------|--------------|
| string   | yes          |

Protocol used by the application. It must be `http` or `tcp`.

### name
| **Type** | **Required** |
|----------|--------------|
| string   | no           |

A logical name for port discovery. Must be <= 63 characters and match `[a-z0-9]([-a-z0-9]*[a-z0-9])?`.

### port
| **Type** | **Required** |
|----------|--------------|
| int      | yes          |

Port number that will be exposed. For protocol equals TCP the available port range is (1024-32767) (may vary depending
on the configuration of the underlying Kubernetes cluster).

### target_port
| **Type** | **Required** |
|----------|--------------|
| int      | yes          |

The port number which is exposed by the container and should receive traffic routed to `port`.


## annotations

| **Type** | **Required** |
|----------|--------------|
| object   | no           |

This configuration structure can be used to set custom annotations on the Kubernetes resources which are
created or updated when deploying the application.

Default value:
```yaml
annotations:
  deployment: {}
  horizontal_pod_autoscaler: {}
  ingress: {}
  service: {}
  pod: {}
```

The annotations are organized under the Kubernetes resource they will be applied to. To specify custom anotations, set
key-value pairs under the respective Kubernetes resource name. I.e. to set the label `foo=bar` on the Service
object, you can do the following:

```yaml
annotations:
  service:
    foo: bar
```

Annotations are fundamentally different from labels in that labels are primarily used to organize and select
resources, whereas annotations are more suitable for applying generic metadata to resources. This metadata can in turn
be read and used by other systems running in the cluster. Refer to the
[Kubernetes documentation on annotations](https://kubernetes.io/docs/concepts/overview/working-with-objects/annotations/) for
more information.


## labels

| **Type** | **Required** |
|----------|--------------|
| object   | no           |

Default value:
```yaml
labels:
  deployment: {}
  horizontal_pod_autoscaler: {}
  ingress: {}
  service: {}
  pod: {}
```

The labels are organized under the Kubernetes resource they will be applied to. To specify custom labels, set
key-value pairs under the respective Kubernetes resource name. I.e. to set the label `layer=frontend` on the Service
object, you can do the following:

```yaml
labels:
  service:
    layer: frontend
```

Labels have strict syntax requirements for both the key and value part. Refer to the [Kubernetes documentation on
labels and selectors](https://kubernetes.io/docs/concepts/overview/working-with-objects/labels/) for details.


## secrets_in_environment

| **Type** | **Required** |
|----------|--------------|
| boolean  | no           |

Any Kubernetes secret matching the application name will automatically be mounted under `/var/run/secrets/fiaas/`. If
this setting is enabled, any key-value pairs from the same secret will also be available as environment variables in
the application's environment.

Default value:
```yaml
secrets_in_environment: false
```


## admin_access

| **Type** | **Required** |
|----------|--------------|
| boolean  | no           |

Controls whether or not Kubernetes apiserver tokens from the `default` `ServiceAccount` in the namespace the application
is deployed to will be mounted inside the pods. This is only neccessary if the application requires access to the
Kubernetes apiserver. If in doubt, leave this disabled.

```yaml
admin_access: False
```