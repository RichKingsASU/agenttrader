'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

interface OptionsFlow {
  created_at: string;
  symbol: string;
  option_symbol: string;
  side: string;
  size: number;
  trade_price: number;
  strike: number;
  expiration: string;
  option_type: string;
}

export default function OptionsFlowWidget() {
  const [flow, setFlow] = useState<OptionsFlow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchFlow = async () => {
      try {
        setLoading(true);
        const { data, error } = await supabase
          .from('options_flow')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(20);

        if (error) {
          throw error;
        }
        setFlow(data || []);
      } catch (error: any) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchFlow();
  }, []);

  if (loading) return <p>Loading options flow...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="overflow-x-auto">
      <h2 className="text-2xl font-bold mt-8 mb-4">Recent Options Flow</h2>
      <table className="min-w-full bg-white border border-gray-200">
        <thead>
          <tr>
            <th className="py-2 px-4 border-b">Time (UTC)</th>
            <th className="py-2 px-4 border-b">Symbol</th>
            <th className="py-2 px-4 border-b">Option Symbol</th>
            <th className="py-2 px-4 border-b">Side</th>
            <th className="py-2 px-4 border-b">Size</th>
            <th className="py-2 px-4 border-b">Price</th>
            <th className="py-2 px-4 border-b">Strike</th>
            <th className="py-2 px-4 border-b">Expiration</th>
            <th className="py-2 px-4 border-b">Type</th>
          </tr>
        </thead>
        <tbody>
          {flow.map((item) => (
            <tr key={`${item.created_at}-${item.option_symbol}`}>
              <td className="py-2 px-4 border-b">{new Date(item.created_at).toISOString()}</td>
              <td className="py-2 px-4 border-b">{item.symbol}</td>
              <td className="py-2 px-4 border-b">{item.option_symbol}</td>
              <td className="py-2 px-4 border-b">{item.side}</td>
              <td className="py-2 px-4 border-b">{item.size}</td>
              <td className="py-2 px-4 border-b">{item.trade_price}</td>
              <td className="py-2 px-4 border-b">{item.strike}</td>
              <td className="py-2 px-4 border-b">{item.expiration}</td>
              <td className="py-2 px-4 border-b">{item.option_type}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
