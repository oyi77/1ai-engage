# 1AI Engage Dashboard

Multi-channel customer engagement platform with real-time analytics and service controls.

## Features

✅ **Fixed Issues:**
- React error #310 (infinite re-render) - Fixed with proper state management
- Added 3 sample conversations (previously showing 0)
- Added sales pipeline data with 4 stages (Lead, Qualified, Proposal, Closed)
- Added service control toggles for all 5 channels

✅ **Service Controls:**
- WhatsApp (Enabled by default)
- Instagram (Enabled by default)
- Facebook (Enabled by default)
- Email (Enabled by default)
- SMS (Disabled by default)

✅ **Dashboard Components:**
- Total Conversations counter
- Active Leads tracker
- Conversion Rate display
- Revenue metrics
- Sales Pipeline chart (Bar chart with 4 stages)
- Recent Conversations table
- Service toggle controls

## Getting Started

### Install Dependencies
```bash
cd dashboard
npm install
```

### Development Server
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) (or 3001 if 3000 is in use)

### Production Build
```bash
npm run build
npm start
```

## Tech Stack

- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Recharts (for data visualization)
- Lucide React (for icons)

## Project Structure

```
dashboard/
├── src/
│   └── app/
│       ├── page.tsx          # Main dashboard component
│       ├── layout.tsx         # Root layout
│       └── globals.css        # Global styles
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

## Current Status

✅ All errors fixed
✅ Dashboard fully functional
✅ Service controls working
✅ Sample data populated
✅ Charts rendering correctly
