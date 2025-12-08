import MarketDataWidget from './components/MarketDataWidget';
import PaperTradesWidget from './components/PaperTradesWidget';
import NewsEventsWidget from './components/NewsEventsWidget';
import OptionsFlowWidget from './components/OptionsFlowWidget';
import BrokerPositionsWidget from './components/BrokerPositionsWidget';

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <h1 className="text-4xl font-bold text-center">AgentTrader Dashboard</h1>
      </div>

      <div className="w-full mt-12">
        <MarketDataWidget />
        <PaperTradesWidget />
        <NewsEventsWidget />
        <OptionsFlowWidget />
        <BrokerPositionsWidget />
      </div>
    </main>
  );
}
