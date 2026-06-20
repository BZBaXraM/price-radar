import type { Metadata } from "next";
import { Suspense } from "react";
import { Fraunces, Inter } from "next/font/google";
import "./globals.css";
import { Header } from "@/components/Header";
import { ChatWidget } from "@/components/ChatWidget";
import { LivePriceToaster } from "@/components/LivePriceToaster";

const fraunces = Fraunces({
  variable: "--font-fraunces",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  style: ["normal", "italic"],
});

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin", "cyrillic"],
  weight: ["300", "400", "500", "700"],
});

const siteUrl = process.env.NEXT_PUBLIC_SITE_URL ?? "https://priceradar.az";

export const metadata: Metadata = {
  metadataBase: new URL(siteUrl),
  title: {
    default: "PriceRadar — Qiymətləri müqayisə et",
    template: "%s | PriceRadar",
  },
  description:
    "KontaktHome, İrşad, World Telecom və Baku Electronics mağazalarının qiymətlərini real vaxtda müqayisə et. Ən yaxşı təkliflər, AI köməkçi ilə.",
  openGraph: {
    type: "website",
    locale: "az_AZ",
    alternateLocale: ["ru_RU", "en_US"],
    url: siteUrl,
    siteName: "PriceRadar",
    title: "PriceRadar — Qiymətləri müqayisə et",
    description:
      "KontaktHome, İrşad, World Telecom və Baku Electronics mağazalarının qiymətlərini real vaxtda müqayisə et.",
  },
  twitter: {
    card: "summary",
    title: "PriceRadar",
    description: "Azərbaycanda qiymət müqayisəsi — KontaktHome, İrşad, World Telecom, Baku Electronics.",
  },
  robots: { index: true, follow: true },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  // Apply persisted theme and lang before paint to avoid flashes.
  const noFlashTheme = `(function(){try{var s=JSON.parse(localStorage.getItem('priceradar'));if(s&&s.state&&s.state.theme==='dark'){document.documentElement.classList.add('dark');}}catch(e){}})();`;
  const noFlashLang = `(function(){try{var s=JSON.parse(localStorage.getItem('priceradar'));if(s&&s.state&&s.state.lang)document.documentElement.lang=s.state.lang;}catch(e){}})();`;

  return (
    <html lang="az" className={`${fraunces.variable} ${inter.variable} h-full`} suppressHydrationWarning data-scroll-behavior="smooth">
      <head>
        <script dangerouslySetInnerHTML={{ __html: noFlashTheme }} />
        <script dangerouslySetInnerHTML={{ __html: noFlashLang }} />
      </head>
      <body className="min-h-full flex flex-col bg-paper text-ink">
        <Suspense fallback={<div className="h-16 border-b border-line" />}>
          <Header />
        </Suspense>
        <main className="flex-1">{children}</main>
        <Footer />
        <ChatWidget />
        <LivePriceToaster />
      </body>
    </html>
  );
}

function Footer() {
  return (
    <footer className="border-t border-line mt-24">
      <div className="max-w-6xl mx-auto px-5 py-10 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 text-sm text-muted">
        <p>
          <span className="font-display text-ink text-lg">PriceRadar</span> · 2026
        </p>
        <p className="max-w-prose">
          KontaktHome · İrşad · World Telecom · Baku Electronics
        </p>
      </div>
    </footer>
  );
}
