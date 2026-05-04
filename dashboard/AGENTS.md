# dashboard - Next.js Frontend

Next.js 15+ application with TypeScript, React 19, Tailwind CSS, and shadcn/ui.

## STRUCTURE
```
dashboard/
├── src/
│   ├── app/              # Next.js App Router (pages)
│   ├── components/       # React components
│   │   └── ui/          # shadcn/ui components
│   ├── lib/             # Utilities, API clients
│   └── hooks/           # Custom React hooks
├── public/              # Static assets
└── next.config.ts       # Next.js configuration
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| Add new page | `src/app/(dashboard)/` | Use App Router structure |
| Modify UI components | `src/components/` | shadcn/ui pattern |
| API integration | `src/lib/api.ts` | Centralized fetcher with SWR |
| Styling | Tailwind classes | Use `cn()` utility for merging |

## CONVENTIONS
- **Component Style**: Functional components with explicit TypeScript types
- **State Management**: SWR for server state, React hooks for local state
- **Styling**: Tailwind CSS with shadcn/ui component library
- **Forms**: React Hook Form with Zod validation

## ANTI-PATTERNS
- **DO NOT** use `useSWR` with `{data: T}` type - use direct type `T`
- **DO NOT** call API endpoints directly - use the proxy via `src/app/api/[[...path]]/route.ts`
- **NEVER** expose API keys in frontend code

## COMMANDS
```bash
# Development server
npm run dev

# Production build
npm run build

# Start production server
npm start
```
