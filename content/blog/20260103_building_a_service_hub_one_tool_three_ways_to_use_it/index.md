---
categories:
- personal
date: '2026-01-03T10:50:51Z'
draft: false
tags:
- ai
- mcp
- llm
- api
- git
- development
title: 'Building a "Service Hub": One Tool, Three Ways to Use It'
type: blog
---
I’ve been wrestling with a common dilemma lately: what’s the best way to build a tool when you need to access it from completely different environments?

Take my YouTube transcript downloader, for example. I don't use it in just one way. Sometimes I’m in the terminal and want a quick CLI command. Other times, I need it as an API for a web project. Lately, I’ve been wanting to plug it directly into my LLMs using the Model Context Protocol (MCP). This latter case is becoming an increasingly common requirement—not just for the transcript downloader, but for many other tools as well.

I didn't want to maintain three different versions of the same logic. I wanted one "source of truth" that could serve all three purposes. I’m calling this first draft a "(LLM) Service Hub," and while I got it working, the journey was a bit more complex than I expected.

## The Architecture: FastAPI meets FastMCP

The goal was simple: minimal effort to deploy new tools across different interfaces. The reality? It took me nearly a day of prompt engineering to get the base template right, even with significant help from OpenCode and Claude 3.5 Sonnet.

I ended up with a setup that feels like a Swiss Army knife. The core logic lives in a shared Python library, which I wrap in three ways:

1.  **The API:** Built with **FastAPI** [1]. It’s lightweight, fast, and provides a standard REST interface.
2.  **The MCP:** Built with **FastMCP** [2]. This is the "new kid on the block" that lets me connect my tool directly to Claude Desktop or other LLM hosts.
3.  **The CLI:** A straightforward Python script that imports the core logic for local terminal use. I particularly enjoy using the YouTube transcript downloader alongside **fabric-ai** [5].

## Containerization and Networking

To keep things clean, I split the project into two Docker containers: one for the API and one for the MCP server. This makes deployment easy, but it did raise questions about secure access.

Right now, I’m routing everything through my **Tailscale** [3] network. It’s a lifesaver for hobbyist setups like this because it handles the encrypted "mesh" networking for me. Because I'm using Tailscale, I haven't spent much time on robust authentication or "professional" security features yet; the network itself acts as my perimeter.

## Lessons Learned and Open Questions

Even though I have a working "Service Hub" now, the setup feels slightly more complex than I’d like. It involves a lot of boilerplate just to expose a single function to three different clients.

I’m curious if anyone else is thinking along these lines. Is there a more professional or streamlined way to handle this multi-client approach? I want to spend my time building the actual tools, not fiddling with the plumbing to make them accessible.

If you’ve built something similar or have a favorite framework for "write once, deploy everywhere" internal tools, I’d love to hear about it. For now, I have a solid base for my next batch of tools, but I’m always looking for a cleaner way to do it.

If you are interested in my first build, you can find it on GitHub: [service-hub](https://github.com/cloonix/service-hub) [4]

## Sources

[1] FastAPI Documentation - <https://fastapi.tiangolo.com/>
[2] FastMCP GitHub Repository - <https://github.com/jlowin/fastmcp>
[3] Tailscale - <https://tailscale.com/>
[4] Service-hub - <https://github.com/cloonix/service-hub>
[5] fabric-ai - <https://github.com/danielmiessler/fabric>