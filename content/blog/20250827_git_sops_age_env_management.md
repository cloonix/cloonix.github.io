---
title: "Secure Your Environment Files with Git, SOPS, and age"
date: 2025-08-27T08:00:17Z
type: blog
draft: false
categories:
  - howto
tags:
  - git
  - sops
  - age
  - docker
  - security
---

## Secure Your Environment Files with Git, SOPS, and age

Managing secrets in code is challenging. You want your `.env` files under version control, but you definitely don't want to expose sensitive information. I explored solutions like [Infisical](https://github.com/Infisical/infisical), but found that self-hosting a production-ready platform was overkill for my simple Docker Compose projects. After some back-and-forth with AI, I finally arrived at a straightforward approach that fits my needs: [SOPS](https://github.com/mozilla/sops) and [age](https://github.com/FiloSottile/age). 

SOPS and age let you safely store and version-control sensitive files (like `.env`) in your git repository. SOPS encrypts your secrets using age keys, so only authorized people can decrypt them. This way, you keep secrets secure while still tracking changes and sharing configs with your team.

Here’s a quick guide to keeping your environment files safe and sound in git.

### Why Not Just `.gitignore`?

Ignoring `.env` files is common, but it means you lose version control for your environment configuration. Plus, sharing secrets securely with your team becomes a pain.

### Quick Setup

1. **Install SOPS and age** (macOS or Linux with brew)

   ```sh
   brew install sops
   brew install age
   ```

2. **Generate an age key**

   ```sh
   mkdir -p ~/.config/sops/age/
   age-keygen -o ~/.config/sops/age/keys.txt
   ```

   Save the `keys.txt` to a safe place and add the public key(s) to your SOPS config (`.sops.yaml`). I've created a key pair on my notebook and on my server (docker).

   ```yaml
   creation_rules:
     - path_regex: \.env.*
       encrypted_regex: "^(?!#).*"
       key_groups:
       - age:
         - age1p3zxdl3zg6fdmpwudehvqaccg8yghac5mv3u85udvjaflu6yfprs9jkkzl
         - age1jeys866705vq4fcwfk0x5vhn507a7w0dqzc2sj7sr948y86svd9s5jmsns
   ```

   You can add the `.sops.yaml` to your repository.

   Update your `.gitignore` (important) if not done yet and exclude all raw `.env`-files, but **do not** ignore `.env.enc`.

3. **Encrypt your `.env` file**

   ```sh
   sops -e .env > .env.enc
   ```

   Add the encrypted file to the repository: `git add -f .env.enc`. Make sure it's really encrypted!

   Now, commit `.env.enc` to git!

4. **Decrypt when needed**

   ```sh
   sops -d .env.enc > .env
   docker compose up -d
   ```

### Pro Tips

- Never commit your raw `.env`!
- Share the `age.key` securely with your team or use keypairs for each party.
- Add `.env` and `age.key` to your `.gitignore`.

### Wrapping Up

With SOPS and age, you get the best of both worlds: secure, versioned secrets and easy collaboration. No more leaking secrets or messy manual sharing. Give it a try!

