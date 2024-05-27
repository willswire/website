---
title: "Cosmology: Chainguard in Big Bang"
description: "Breaking free from the chains of Iron Bank"
pubDate: "Apr 01 2024"
heroImage: "/chainguard.jpg"
---

Containers are pretty cool. Several years ago, I first learned about them during an internship with my university's IT department.

We had several dozen "timestations" around campus - EOL Windows desktop machines repurposed as kiosks for hourly employees to clock in and out of each day. The OS license fee and administrative upkeep for these machines were a nuisance for the IT crowd. However, replacing them with new systems wasn't a justifiable expense, given their limited use case.

My boss was a huge Raspberry Pi fan and often left several around the office for interns to play with. One afternoon, the idea dawned on me that we could use IoT devices for replacement timestations. After demoing a POC to my boss, he placed a bulk order for a dozen more Pis. Little did I know that this would become my gateway drug into DevOps.

A few weeks later, we had a handful of Raspberry Pis preloaded with the employee web portal, ready to be deployed. The performance could have been better, but the devices worked fine for their intended purpose. After deploying several Pis, we noticed that users were overloading the devices by opening other apps and visiting different websites. Cheap, enterprise IoT management is more or less what we need to solve our problems. That's what led us to [balenaCloud](https://www.balena.io/cloud).

![balenaCloud](/balenaCloud.jpg)

As "the container-based platform for deploying IoT fleets," balenaCloud soon became our go-to solution for delivering value via IoT devices. I ended up leading development for several IoT projects on the campus: the employee timestation kiosks, [CUPS (AirPlay) adapters for legacy printers](https://github.com/willswire/balenaPrint), and [digital signage solutions](https://github.com/willswire/balena-dashboards). These projects leveraged Balena's opinionated approach to deploying software to IoT devices: containers.

## ⛏️ The Iron Age

After graduating college and entering Active Duty as a Cyber Officer, I quickly learned about the new happenings in the Air Force software world - namely, the advent of our shiny software factories. Organizations like Kessel Run, Bespin, and Platform One became exciting new opportunities for the DoD to adopt modern software development and delivery practices into the Profession of Arms.

During a virtual onboarding course with Platform One, I learned about [Iron Bank](https://p1.dso.mil/services/iron-bank), the DoD's source for hardened containers. These hardened containers allow applications to run within an environment (typically a Kubernetes cluster) that meets authority-to-operate (ATO) compliance controls.[^1]

![Iron Bank Value Stream](/ibvs.jpg)

About a year after discovering Iron Bank, I wound up at the 90th Cyberspace Operations Squadron. One of the only organic software development squadrons in the entire Air Force, it wasn't long before I recognized several Iron Bank images referenced in our CI/CD YAMLs.

Delving deeper and deeper into the DevSecOps/Platform tools and technologies, it quickly became apparent that the value proposition of "hardened containers" was critical to providing secure, compliant applications and services. It wasn't until I started experimenting with my deployment of Big Bang that I wondered what it might look like to leverage an alternative catalog of secure container images.

## ⛓️ A Chain Reaction

Through the network of some engineering folks I met at Platform One, I discovered Chainguard. Chainguard maintains a free, public catalog of hardened containers by taking a unique approach. Powered by their OSS tools [apko](https://github.com/chainguard-dev/apko) and [melange](https://github.com/chainguard-dev/melange), Chainguard provides stripped-down, minimal images with 0-known vulnerabilities that receive speedy updates and patches. These tools work together to quickly take source code and produce a slim, secure, multi-arch container image with an SBOM. Introducing automation to this process further unlocks the power of CVE reduction. It expands the opportunities for the community to [contribute to Wolfi](https://github.com/wolfi-dev/os/pull/14004), Chainguard's lightweight GNU software distribution (or what they would call a Linux *undistro*).

Recognizing the ingenuity in their approach to security, I began comparing Chainguard images with those in Iron Bank. I was surprised to discover that many Iron Bank images contained CVEs that were not present in their Chainguard counterparts. In fact, at the time of discovery, there were [over 4k findings present](https://www.linkedin.com/posts/danlorenc_cve-chainguard-ironbank-activity-7109170248540372992-fvBI) in the images constituting Big Bang core.

<iframe src="https://www.linkedin.com/embed/feed/update/urn:li:share:7109170247940616192" height="800px" width="100%" frameborder="0" allowfullscreen="" title="Embedded post"></iframe>

I started wondering how easy it would be to replace the container images in Big Bang with ones from Chainguard.

### 🔭 Find & Replace

In the [latest version of Cosmology](https://github.com/willswire/cosmology/blob/chainguard/main.yaml), I have replaced enough of the Big Bang core images (Istio, Kyverno, Monitoring, Metrics Server, etc.) to no longer depend on Iron Bank images for my simple experiments and side-quests. Because Chainguard provides `latest` images for free, sometimes your Helm charts are subject to [breaking](https://github.com/willswire/cosmology/blob/chainguard/main.yaml#L150) due to conflicting arguments and software versions. For my personal development efforts, this is a small price to pay for unlocking the ability to do multi-arch Big Bang deployments, something Iron Bank is still developing support for.

### 👨🏻‍🍳 Cheffing Up Images

In addition to replacing the core images, I created my first image using apko and melange! Whenever I bring up my cluster *de novo*, the IP address for my public ingress gateway changes. To publish the new value to my Cloudflare DNS config, I developed a lightweight tool called clip (**Cl**oudflare **I**stio **P**ublisher). Originally a collection of bash scripts and a traditional Docker container, I rewrote the API calls [in go](https://github.com/willswire/cosmology/tree/chainguard/packages/clip) and used melange's go pipelines along with apko to generate the image.

It was shocking how easy and fast it was to produce my image.

#### 🏜️ melange

```yaml
package:
  name: clip
  version: 0.2.0
  epoch: 0
  description: Cloudflare-Istio Publisher
  copyright:
    - license: Apache-2.0
  target-architecture:
    - x86_64
    - aarch64

environment:
  contents:
    repositories:
      - https://dl-cdn.alpinelinux.org/alpine/edge/main
      - https://dl-cdn.alpinelinux.org/alpine/edge/community
    packages:
      - build-base
      - ca-certificates-bundle
      - go

pipeline:
  - uses: go/build
    with:
      output: clip
      packages: .

  - uses: strip
```

#### 📦 apko

```yaml
contents:
  repositories:
    - '@local packages'
    - https://dl-cdn.alpinelinux.org/alpine/edge/main
  packages:
    - musl
    - clip@local
    - ca-certificates-bundle
accounts:
  groups:
    - groupname: nonroot
      gid: 65532
  users:
    - username: nonroot
      uid: 65532
  run-as: nonroot
entrypoint:
  command: /usr/bin/clip
archs:
  - x86_64
  - aarch64
```

Because apko files are fully declarative, they allow apko to make more assertive statements about the contents of images. In particular, apko images are fully bitwise reproducible and can generate SBOMs covering their complete contents.

## 🛣️ The Road Ahead

Reflecting on my journey through the evolving landscape of container technologies, I'm struck by the sheer velocity of innovation and change. From my first exposure to Raspberry Pis at the university to exploring the frontiers of security with Chainguard, each step has taught me adaptability and vision. Knowing what I know now, I encourage my younger self to embrace experimentation with a critical eye. The shift from Iron Bank's hardened containers to the streamlined efficiency of Chainguard's offerings underscores a pivotal learning: the continuous quest for improvement is fundamental, not just an option.

In hindsight, fostering a more profound curiosity about alternative technologies and methodologies from the outset could have accelerated my understanding and application of secure, efficient containerization. For today's college students venturing into DevOps and cybersecurity, I hope they recognize the importance of looking beyond the conventional. Exploring tools like apko and melange isn't merely about leveraging new software; it's about cultivating a mindset that questions, "How can we do this better?"

In the spirit of Leonardo Da Vinci's insight that "Art is never finished, only abandoned," I view our technological endeavors through a similar lens. It's not about reaching a finality but engaging in an ongoing dialogue with change, sculpting the future with each line of code we write.

---

[^1]: Platform One's Iron Bank and Repo1 are entirely open to the public (available at IL-2). You can learn more about Platform One services [here](https://p1.dso.mil).
