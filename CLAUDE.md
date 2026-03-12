# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SD Rapport is a Next.js (App Router) project deployed on Vercel. It will fetch and display data from an external API (API integration not yet implemented).

## Commands

- `npm run dev` — start dev server
- `npm run build` — production build
- `npm run start` — serve production build
- `npm run lint` — run ESLint

## Architecture

- **Framework**: Next.js 16 with App Router, TypeScript
- **Source**: `src/app/` — all pages and layouts use the App Router convention
- **Path alias**: `@/*` maps to `./src/*`
- **Language**: Norwegian (UI text and HTML lang="no")
- **Deployment**: Vercel (connect the GitHub repo in Vercel dashboard)
