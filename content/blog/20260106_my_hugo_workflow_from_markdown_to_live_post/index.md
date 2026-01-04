---
categories:
- personal
date: '2026-01-06T08:14:00Z'
draft: false
tags:
- git
- hugo
- blog
- development
- personal
title: 'My Hugo Workflow: From Markdown to Live Post'
type: blog
---
Hugo is a fantastic static site generator. I’ve always appreciated its "no-nonsense" approach: you write in Markdown, it generates static HTML, and there is zero bloat. Because it has no heavy dependencies, you can host it almost anywhere. However, despite my love for the framework, I’ve always found the actual publishing flow a bit tedious.

Whenever I sat down to write, I found myself bogged down by administrative tasks like editing frontmatter, managing filenames, and organizing folder structures. Even though it sounds irrelevant, these small frictions made publishing feel like a chore rather than a creative outlet.

## Finding the Right Environment

To get back into the flow, I wanted to use my favorite Markdown editor, **Typora** [1]. Typora provides a minimalist environment that helps me focus entirely on the writing itself. The challenge was bridging the gap between a clean Markdown file in Typora and a properly formatted Hugo "Page Bundle."

## Automating the Boring Stuff

To solve this, I used OpenCode and Claude 4.5 Sonnet to write a Python automation script. Now, instead of manual organization, I simply run a command from my Hugo repository:

```sh
cd ~/git/hugo/
./publish.sh ~/path/to/Markdown.md
```

### How the Script Works

The script handles the repetitive "housekeeping" tasks that used to kill my momentum:

1.  **Frontmatter Generation**: If the script doesn't find existing frontmatter, it automatically extracts the H1 heading to use as the post title and prompts for other attributes like date, tags, and category.
2.  **Page Bundle Organization**: It creates a Hugo "Page Bundle," which is essentially a dedicated directory for a post where the Markdown file (renamed to `index.md`) and its associated resources live together.
3.  **Image Management**: I configured Typora to save images into a local `./assets` folder. The script automatically identifies these images and moves them into the correct Page Bundle directory so Hugo can render them properly.
4.  **Archive Logic**: Once the post is processed and moved into the Hugo `content` folder, the script moves the original draft into a `published` subfolder, maintaining the same organizational logic.

The script is idempotent. If I need to fix a typo or update a section, I can simply run the script again on the same file, and it updates the published version without breaking anything.

## Conclusion

It might seem like a trivial automation, but removing the friction of manual file management has brought the fun back into blogging. By letting a script handle the frontmatter and folder structures, I can spend my time in Typora focusing on what actually matters: the content.

If you are interested in this script, you can find it in my GitHub repository: [https://github.com/cloonix/cloonix.github.io](https://github.com/cloonix/cloonix.github.io). It is a Python script wrapped within a shell script named `publish.sh`. You can run it with the `--help` flag to see the available options.

And of course, the final step of my workflow is a GitHub action which builds the site. 

## Sources

- [1] Typora — <https://typora.io>
