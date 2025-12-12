'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

interface MarketData {
  symbol: string;
  ts: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
  session: string;
}

const SessionIndicator = ({ session }: { session: string }) => {
  const bgColor =
    session === 'REGULAR'
      ? 'bg-green-500'
      : session === 'PRE'
      ? 'bg-yellow-500'
      : session === 'AFTER'
      ? 'bg-purple-500'
      : 'bg-gray-500';

  return <span className={`inline-block w-3 h-3 rounded-full ${bgColor}`} title={session}></span>;
};


export default function MarketDataWidget() {
  const [data, setData] = useState<MarketData[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const { data, error } = await supabase
          .from('market_data_1m')
          .select('*')
          .order('ts', { ascending: false })
          .limit(200);

        if (error) {
          throw error;
        }
        setData(data || []);
      } catch (error: any) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) return <p>Loading market data...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200">
        <thead>
          <tr>
            <th className="py-2 px-4 border-b">Symbol</th>
            <th className="py-2 px-4 border-b">Time (UTC)</th>
            <th className="py-2 px-4 border-b">Open</th>
            <th className="py-2 px-4 border-b">High</th>
            <th className="py-2 px-4 border-b">Low</th>
            <th className="py-2 px-4 border-b">Close</th>
            <th className="py-2 px-4 border-b">Volume</th>
            <th className="py-2 px-4 border-b">Session</th>
          </tr>
        </thead>
        <tbody>
          {data.map((row) => (
            <tr key={`${row.symbol}-${row.ts}`}>
              <td className="py-2 px-4 border-b">{row.symbol}</td>
              <td className="py-2 px-4 border-b">{new Date(row.ts).toISOString()}</td>
              <td className="py-2 px-4 border-b">{row.open}</td>
              <td className="py-2 px-4 border-b">{row.high}</td>
              <td className="py-2 px-4 border-b">{row.low}</td>
              <td className="py-2 px-4 border-b">{row.close}</td>
              <td className="py-2 px-4 border-b">{row.volume}</td>
              <td className="py-2 px-4 border-b">
                <div className="flex items-center">
                  <SessionIndicator session={row.session} />
                  <span className="ml-2">{row.session}</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
