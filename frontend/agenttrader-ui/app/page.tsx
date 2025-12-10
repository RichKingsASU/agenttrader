import MarketDataWidget from './components/MarketDataWidget';
import PaperTradesWidget from './components/PaperTradesWidget';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold text-center">AgentTrader Dashboard</h1>
      </div>

      <div className="w-full mt-12">
        <div className="mb-8 p-4 bg-green-100 text-green-800 rounded-lg">
          <h2 className="text-2xl font-bold mb-2">System Health</h2>
          <ul>
            <li>Ingestion loop: running (Cloud Shell)</li>
            <li>Alpaca paper: authenticated</li>
          </ul>
        </div>
        <MarketDataWidget />
        <PaperTradesWidget />
      </div>
    </main>
  );
}