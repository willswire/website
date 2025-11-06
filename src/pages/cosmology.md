---
title: "Cosmology: mTLS in Big Bang"
date: "Jul 07 2023"
image: "cosmology.jpg"
---

Working with Big Bang can be precarious. Especially when developing on a shared cluster with other team members. Recently, I created a [new project entitled Cosmology](https://github.com/willswire/cosmology/tree/mtls), which serves as a playground for several of my personal "quests" in exploring novel functionality and features in [Platform One's Big Bang](https://repo1.dso.mil/big-bang/bigbang). To investigate my ideas and experiment on the cheap, I use the following:

- [Terraform](https://www.terraform.io) to dynamically provision infrastructure
- Managed Kubernetes on [Symbiosis](https://symbiosis.host) (1/4th the cost of EKS on AWS!)
- [Zarf](https://github.com/defenseunicorns/zarf) to package my configurations and deploy them to the cluster

My first quest in this exploration of the cosmos is to secure access to my Big Bang cluster and its hosted applications.

## 🛡️ Cloudflare Zero Trust

My deployment of Big Bang isn't running inside an ATO'd environment, so I'm free to explore alternative Secure Access Service Edge (SASE) solutions outside of traditional government-only offerings such as Platform One's [CNAP](https://p1.dso.mil/services/cnap).

As a longtime user of Cloudflare, I've often wondered what it might look like to leverage their [Zero Trust Network Access (ZTNA)](https://www.cloudflare.com/zero-trust/) for controlling access to applications and services in Big Bang. More specifically, is it possible to use Cloudflare to evaluate **all traffic** before sending requests to my cluster?

To begin the quest, I started by purchasing a new domain. Sticking with the [Star Wars theme](https://media.tenor.com/Df0qPoxKVB4AAAAC/baby-yoda-star-wars.gif), which seems to have taken over the Air Force Software Factories as of late, I was able to register `tatooine.dev` via Google's [.dev](https://get.dev) registry and point the nameservers over to Cloudflare.

## 🔏 Istio Certificates

Now that we have a domain registered, it's time to procure valid certificates for use with Istio! Utilizing Cloudflare's free [Origin CA](https://blog.cloudflare.com/cloudflare-ca-encryption-origin/) gives us a certificate and private key in minutes. As shown in the diagram below, origin CA certificates allow traffic encryption between Cloudflare and the origin Istio gateway in our cluster.

![Will's Wire](https://assets.willswire.com/blog/cosmology-mtls/strict-ssl-connection.png)

When updating the values in our Big Bang configurations, we provide the newly provisioned origin CA certificate (shown in orange) private key under `istio.gateways.public.tls` and the certificate under `istio.gateways.public.cert`.

## 💕 The feeling is mutual

Now that we can establish secure, trusted communications between visitors and applications on our cluster, only one thing remains! Nothing currently prevents direct traffic to the public IP address of our Istio gateway. We must guarantee requests to our cluster come _only_ from the Cloudflare network. This authentication becomes particularly important when employing the [Cloudflare Web Application Firewall (WAF)](https://blog.cloudflare.com/waf-for-everyone/) for shielding our services. Together with the WAF, we can ensure that _all traffic_ is evaluated before receiving a response from our Istio gateway.

![Will's Wire](https://assets.willswire.com/blog/cosmology-mtls/mtls.png)

Enabling [Authenticated Origin Pulls/Mutual TLS](https://blog.cloudflare.com/protecting-the-origin-with-tls-authenticated-origin-pulls/) for the `tatooine.dev` domain is the first, crucial step for restricting traffic to our cluster. Like provisioning Origin CA certificates, this is simple via the administration portal in Cloudflare. If you're unfamiliar with the concept of mTLS, I highly suggest reading the following [blog post](https://www.cloudflare.com/learning/access-management/what-is-mutual-tls/) (yet another Cloudflare link).

On the other hand, configuring Istio within Big Bang to support mTLS is more involved. Although Istio supports mTLS [out-of-the-box](https://istio.io/latest/docs/tasks/traffic-management/ingress/secure-ingress/#configure-a-mutual-tls-ingress-gateway), the Istio templates within the current version of upstream Big Bang ([v2.5.0](https://repo1.dso.mil/big-bang/bigbang/-/tree/2.5.0) at the time of this writing) does not. [^1]

The `istio/secret-tls.yaml` Big Bang template file [only exposes](https://repo1.dso.mil/big-bang/bigbang/-/blob/2.5.0/chart/templates/istio/secret-tls.yaml#L42) `tls.crt` and `tls.key` Istio keys, not the necessary `ca.crt` key [needed](https://istio.io/latest/docs/tasks/traffic-management/ingress/secure-ingress/#key-formats) to enable mTLS.

I forked Big Bang source, and it was easy enough to modify the template to include to support for passing values through to Istio, as demonstrated below in the following snippet:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: {{ printf "%s-cert" $name }}
  namespace: istio-system
  labels:
    app.kubernetes.io/name: istio-controlplane
    app.kubernetes.io/component: "core"
    {{- include "commonLabels" $ | nindent 4}}
type: kubernetes.io/tls
data:
  tls.crt: {{ default $default.cert $values.tls.cert | b64enc }}
  tls.key: {{ default $default.key $values.tls.key | b64enc }}
{{- if $values.tls.ca }}
  ca.crt: {{ $values.tls.ca | b64enc }}
{{- end }}
```

## 🚀 3, 2, 1 liftoff!

After modifying the template and providing the key, certificate, and certificate authority values to Istio, I could confirm that only traffic to the `tatooine.dev` domain was allowed to pass back to the cluster. After creating an entry in my `/etc/hosts` with the public IP address of the Istio gateway, trying to access the IP directly resulted in the following (good!) error:

![Will's Wire](https://assets.willswire.com/blog/cosmology-mtls/good-error.png)

Now that traffic is required to originate from Cloudflare servers, managing the necessary [access policies](https://developers.cloudflare.com/cloudflare-one/policies/access/policy-management/) becomes easy. For now, I only want to allow access for myself, and I can supply my email address along with the configuration of a one-time pin to enable authentication.

![Will's Wire](https://assets.willswire.com/blog/cosmology-mtls/zt.png)

Now we have a K8s cluster running Big Bang in a secure environment with Zero Trust access controls! Traffic is encrypted end-to-end and is only accepted when originating from Cloudflare data centers, providing us the added capability to manage authorization policies on the fly.

## 💡 Reflections and Future Endeavors

By integrating Cloudflare's Zero Trust Network Access (ZTNA) with Big Bang, I have gained valuable insights into adopting a Zero Trust approach to secure access in cloud-native development. Controlling and evaluating all traffic before it reaches my cluster has strengthened the security of my deployments. At the same time, the inclusion of Cloudflare's Web Application Firewall (WAF) has fortified my services against potential threats. Managing access policies has provided me with a granular level of control and adaptability. Moving forward, I plan to optimize and refine the implementation of Zero Trust principles in my Big Bang projects, leveraging the evolving capabilities of the framework and exploring other aspects of Cloudflare's suite of offerings to create even more resilient and efficient applications.

In conclusion, this experiment has reinforced my commitment to staying at the forefront of safe and innovative software development practices. By combining the power of Big Bang and Cloudflare, I am confident in my ability to push the boundaries of cloud-native applications, ensuring robust security and optimal performance. I invite you to join me on this journey of continuous "space" exploration and experimentation as I build secure, scalable, and cutting-edge solutions in the ever-evolving landscape of technology!

---

[^1]: An [issue](https://repo1.dso.mil/big-bang/bigbang/-/issues/777) ~~remains open on the Big Bang project~~ was recently resolved bringing support for `MUTUAL` configured gateways!
