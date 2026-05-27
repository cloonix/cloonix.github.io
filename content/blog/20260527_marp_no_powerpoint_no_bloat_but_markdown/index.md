---
categories:
- software
date: '2026-05-27T05:44:59Z'
draft: false
tags:
- markdown
- opensource
- howto
title: Marp - No PowerPoint, no bloat, but Markdown
type: blog
---
I don't like PowerPoint. The endless dragging and dropping, the bloated interface, the struggle to get elements to align, and the general waste of time always drive me crazy. I want to focus on my content, not fight with a heavy user interface. 

If you are like me, you probably love Markdown. It is simple, clean, and gets out of your way. Ever since I started using Obsidian, it has easily become my favorite application of all time. So, a while ago, I asked myself if I could just write my presentations in Markdown too. 

That is when I discovered Marp [1](https://marp.app), an incredibly slick Markdown presentation ecosystem. 

## What is Marp?

Marp is not strictly 100 percent pure Markdown, but it feels incredibly close. It is built on top of the CommonMark [2](https://commonmark.org) specification, meaning your existing Markdown knowledge carries over instantly. 

The ecosystem is incredibly developer friendly. You can run it directly from your terminal using the Marp CLI [3](https://github.com/marp-team/marp-cli) or write your slides directly inside VS Code with their official extension [4](https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode). There is even a community curated list of awesome Marp resources [5](https://github.com/marp-team/awesome-marp) if you want to dive deeper into custom tools and themes.

If you are on macOS, getting started is as simple as running a quick Homebrew command:

```bash
brew install marp-cli
```

For other operating systems, you can easily find alternative installation methods in their official GitHub repository.

## The AI and Agentic Coding Connection

Before we look at how it works, let me share a quick tip on why this is a game changer for modern development workflows. Because Marp files are just plain text, they play incredibly well with LLMs and agentic coding tools. 

I often use my favorite AI assistant to scan a codebase and generate a complete architecture slide deck on the fly. Doing this with PowerPoint would be a nightmare of scripting, but with Marp, the AI just spits out a clean Markdown file, and I have a beautiful presentation ready in seconds.

## Key Features That Make Marp Awesome

Here is a quick look at what you can do with it:

*   **Write slides with ease:** Use standard Markdown syntax for your text, lists, images, and code blocks.
*   **Split slides instantly:** Just use a horizontal ruler (`---`) to tell Marp where a new slide starts.
*   **Built-in themes:** It comes with three clean themes out of the box, which are default, gaia, and uncover.
*   **Easy customization:** If you need custom styling, you can inject CSS globally via the frontmatter using `style: | ...` or target a single slide using `<style scoped>`.
*   **Flexible exports:** You can export your slides to HTML, PDF, or even PowerPoint format. Under the hood, the Marp CLI uses a headless browser to render PDFs perfectly, so they always look exactly as intended.
*   **Pluggable and open source:** The architecture is fully pluggable, and the project is open source under the friendly MIT license.

## A Simple Example

Let us look at how easy it is to write a basic deck. Create a file named `slide.md` and add the following content:

```markdown
---
marp: true
theme: default
---

# Slide 1

This is some content on my first slide.

---

# Slide 2

And here is my second slide with some bullet points:
* Point one
* Point two
```

Once you have saved your file, you can compile it using the CLI. Here are the commands to export to different formats:

```bash
# Export to HTML (this is the default option)
marp slide.md

# Export to PDF
marp --pdf slide.md

# Export to PowerPoint
marp --pptx slide.md
```

## Conclusion

And that is really all there is to it. No bloated software, no alignment struggles, just pure focus on your content. If you are looking for a way to streamline your presentation workflow and keep everything in plain text, I highly recommend giving Marp a try. It has completely changed how I share my technical work, and I think you will love it too.

## References

[1] Marp: <https://marp.app>  
[2] CommonMark: <https://commonmark.org>  
[3] Marp CLI: <https://github.com/marp-team/marp-cli>  
[4] Marp VS Code Extension: <https://marketplace.visualstudio.com/items?itemName=marp-team.marp-vscode>  
[5] Awesome Marp List: <https://github.com/marp-team/awesome-marp>  
