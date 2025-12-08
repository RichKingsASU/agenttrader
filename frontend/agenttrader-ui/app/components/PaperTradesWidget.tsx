'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

interface PaperTrade {
  created_at: string;
  symbol: string;
  side: string;
  qty: number;
  price: number;
  status: string;
  source: string;
}

export default function PaperTradesWidget() {
  const [trades, setTrades] = useState<PaperTrade[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTrades = async () => {
      try {
        setLoading(true);
        const { data, error } = await supabase
          .from('paper_trades')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(50);

        if (error) {
          throw error;
        }
        setTrades(data || []);
      } catch (error: any) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTrades();
  }, []);

  if (loading) return <p>Loading paper trades...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="overflow-x-auto">
      <h2 className="text-2xl font-bold mt-8 mb-4">Recent Paper Trades</h2>
      <table className="min-w-full bg-white border border-gray-200">
        <thead>
          <tr>
            <th className="py-2 px-4 border-b">Time (UTC)</th>
            <th className="py-2 px-4 border-b">Symbol</th>
            <th className="py-2 px-4 border-b">Side</th>
            <th className="py-2 px-4 border-b">Qty</th>
            <th className="py-2 px-4 border-b">Price</th>
            <th className="py-2 px-4 border-b">Status</th>
            <th className="py-2 px-4 border-b">Source</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((trade) => (
            <tr key={`${trade.created_at}-${trade.symbol}-${trade.side}`}>
              <td className="py-2 px-4 border-b">{new Date(trade.created_at).toISOString()}</td>
              <td className="py-2 px-4 border-b">{trade.symbol}</td>
              <td className="py-2 px-4 border-b">{trade.side}</td>
              <td className="py-2 px-4 border-b">{trade.qty}</td>
              <td className="py-2 px-4 border-b">{trade.price}</td>
              <td className="py-2 px-4 border-b">{trade.status}</td>
              <td className="py-2 px-4 border-b">{trade.source}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
