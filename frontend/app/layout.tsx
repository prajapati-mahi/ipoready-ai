import './globals.css';
import Navbar from '@/components/Navbar';

export const metadata = {
  title: 'IPOReady AI - Intelligent IPO Readiness & Financial Document Intelligence',
  description: 'Enterprise financial document analysis, multi-format extraction, RAG, and AI agent platform for merchant bankers and IPO underwriters.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0B0F17] text-slate-100 flex flex-col">
        <Navbar />
        <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-6">
          {children}
        </main>
        <footer className="border-t border-slate-800/80 bg-[#0F172A] py-4 text-center text-xs text-slate-500">
          <div className="max-w-7xl mx-auto px-4 flex flex-col sm:flex-row justify-between items-center gap-2">
            <span>IPOReady AI - Autonomous Financial Document Intelligence Platform</span>
            <div className="flex items-center space-x-4 text-slate-400">
              <span>Deterministic Financial Math</span>
              <span>100% Citation Traceability</span>
              <span>Synthetic Enterprise Dataset</span>
            </div>
          </div>
        </footer>
      </body>
    </html>
  );
}
