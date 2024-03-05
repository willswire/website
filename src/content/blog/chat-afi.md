---
title: 'ChatAFI: Embedding Air Force Publications into ChatGPT'
description: 'Exploring RAG and developing a ChatGPT plugin'
pubDate: 'Aug 13 2023'
heroImage: '/chat-afi.jpg'
---

> **January 2024**: The ChatAFI ChatGPT Plugin has been deprecated in favor of the latest update to [AFI Explorer](https://afiexplorer.com)

Back in 2020, I released an app for iOS called [AFI Explorer](tab:https://apps.apple.com/us/app/afi-explorer/id1564964107). The simple idea was to provide Airmen with easy access to Air Force publications on their mobile devices. Surprisingly, the app has seen over 20K downloads in the last 24 months. It's even served as an opportunity to partner with another Airman coder, Drew Stephens, to bring support to Android devices.

## 📞 Hello? It's AI calling!

Fast-forward to 2023 and the potential of OpenAI's [ChatGPT](tab:https://openai.com/chatgpt) cannot be ignored - especially when evaluating new features for existing projects. There are several ways to harness the power of ChatGPT for your projects. [Embeddings](tab:https://platform.openai.com/docs/guides/embeddings/what-are-embeddings) are the best way to inform a large language model (LLM) about the relevance and relatedness of information. This is especially helpful in scenarios where you need to quickly search and synthesize a large amount of text... take for example the thousands of publicly available Air Force publications.

Serving up direct links for hundreds of AFIs, AFMANs, AFHs, and DODIs, I realized my [API endpoint for AFI Explorer](tab:https://api.afiexplorer.com/v2/) was ripe for pulling down publications to begin the embedding process. Since the pubs are released in PDF format, I tried several different methods of extracting text - each time finding the process more cumbersome than expected. I finally decided on using [Apache PDFBox](tab:https://pdfbox.apache.org) after comparing the extracted output across different tools and finding its result the most accurate.

As someone who enjoys deploying microservices at the edge, it was painful for me to acquiesce in utilizing a large compiled tool like PDFBox. Where was I going to run these text extraction jobs? Extracting text from over 1k+ PDFs takes quite a while (2-3 hours), and I wanted to create a cloud-based solution that could run periodically to keep up with new publication changes. Instead of hosting a VM in AWS or Azure, I turned to GitLab CI/CD to see if I could engineer a pipeline solution.

## 🎰 Push button, get embeddings

![Will's Wire](https://assets.willswire.com/blog/chatafi/pipeline.jpeg)

Before parsing the PDFs in my pipeline, I needed to download them. Recognizing that both of these tasks could be executed at the same time, I configured the `download` and `parse` jobs within my pipeline to run in [parallel](tab:https://docs.gitlab.com/ee/ci/yaml/#parallel). Because every parallel job has a `CI_NODE_INDEX` and `CI_NODE_TOTAL`, I was able to [coordinate](tab:https://gitlab.com/willswire/chat-afi/-/blob/v0.0.1/collector/src/download.js?ref_type=tags#L32) functions across jobs.

After registering the resultant `.txt` files as artifacts, it was necessary to `chunk` the text into smaller groupings so they could be sent to and processed by the OpenAI embeddings API endpoint in the following `embed` job. For both of these CI/CD jobs, I relied heavily on [Cloudflare's Example Retrieval Plugin](tab:https://github.com/cloudflare/chatgpt-plugin/tree/main/example-retrieval-plugin/scripts).

Storing these embeddings in a vector database like [pinecone](tab:https://www.pinecone.io) is often the recommended solution, but I don't like paying [$70/month](tab:https://www.pinecone.io/pricing/) for side-projects. Using the same example project above for reference, I included a final `publish` pipeline job to publish key-value text chunks to Cloudflare's KV storage for free. One of the necessary deviations from the example plugin was to [use Cloudflare R2](tab:https://gitlab.com/willswire/chat-afi/-/blob/v0.0.1/.gitlab-ci.yml?ref_type=tags#L71) for the resultant `.bin` instead of KV because of its size.

With all the necessary pieces in place, the embeddings for 1K+ publications now run at the [touch of a button](tab:https://gitlab.com/willswire/chat-afi/-/pipelines/1021210507)!

## 🔌 Plug it in

![Will's Wire](https://assets.willswire.com/blog/chatafi/plugin.png)

Now that the embeddings are globally available via Cloudflare's network, making them *usable* is another story. Eventually creating an API which speaks directly with [AFI Explorer](tab:https://apps.apple.com/us/app/afi-explorer/id1564964107) is the goal, but to get this in the hands of users more quickly, I turned to [ChatGPT plugins](tab:https://openai.com/blog/chatgpt-plugins). Modifying the example linked from above, I created a [plugin](tab:https://gitlab.com/willswire/chat-afi/-/blob/v0.0.1/plugin) which is now publicly available for ChatGPT Plus subscribers. Simply visit the plugin store, install ChatAFI, and let me know what you think!

## 🌐 The Future of AFI Explorer: AI-Powered and Beyond

The journey of AFI Explorer from a simple iOS app to an AI-powered tool harnessing the capabilities of OpenAI's ChatGPT is a testament to the evolving landscape of technology and the limitless potential of innovation. By integrating advanced embeddings and utilizing the power of microservices, AFI Explorer has not only streamlined access to Air Force publications but has also set a precedent for how AI can be seamlessly integrated into existing platforms.

The use of GitLab CI/CD for automating tasks, Cloudflare's network for global availability, and the creation of a ChatGPT plugin showcases the convergence of different technologies to create a holistic solution. This evolution is not just about making information accessible but also about making it interactive, intuitive, and instantaneous.

For the thousands of Airmen and users who rely on AFI Explorer, this transformation offers a glimpse into the future where AI doesn't replace human effort but amplifies it. As we continue to push the boundaries of what's possible, the integration of AI in our daily tools will become the norm rather than the exception. The feedback from ChatGPT Plus subscribers and the broader community will be invaluable in refining and expanding the capabilities of AFI Explorer.

In a world where information is abundant, the real challenge lies in making it accessible, understandable, and actionable. AFI Explorer, with its latest AI-powered features, is a step in that direction, ensuring that Airmen have the best tools at their fingertips. As technology continues to evolve, so will AFI Explorer, always striving to serve its users better.