'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

interface BrokerPosition {
  symbol: string;
  qty: number;
  avg_price: number;
  market_value: number;
  updated_at: string;
  // Joined from broker_accounts
  broker: string;
  external_account_id: string;
}

export default function BrokerPositionsWidget() {
  const [positions, setPositions] = useState<BrokerPosition[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPositions = async () => {
      try {
        setLoading(true);
        // This is a simplified query. A real implementation might use an RPC function
        // to perform the join on the server side.
        const { data: accounts, error: accountsError } = await supabase
          .from('broker_accounts')
          .select('*');

        if (accountsError) throw accountsError;

        const allPositions = [];
        for (const account of accounts) {
            const { data: posData, error: posError } = await supabase
                .from('broker_positions')
                .select('*')
                .eq('broker_account_id', account.id);
            if(posError) throw posError;
            
            for(const pos of posData) {
                allPositions.push({ ...pos, broker: account.broker, external_account_id: account.external_account_id });
            }
        }
        
        setPositions(allPositions);

      } catch (error: any) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPositions();
  }, []);

  if (loading) return <p>Loading broker positions...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="overflow-x-auto">
      <h2 className="text-2xl font-bold mt-8 mb-4">Broker Positions</h2>
      <table className="min-w-full bg-white border border-gray-200">
        <thead>
          <tr>
            <th className="py-2 px-4 border-b">Broker</th>
            <th className="py-2 px-4 border-b">Account</th>
            <th className="py-2 px-4 border-b">Symbol</th>
            <th className="py-2 px-4 border-b">Qty</th>
            <th className="py-2 px-4 border-b">Avg Price</th>
            <th className="py-2 px-4 border-b">Market Value</th>
            <th className="py-2 px-4 border-b">Updated At</th>
          </tr>
        </thead>
        <tbody>
          {positions.map((pos) => (
            <tr key={`${pos.external_account_id}-${pos.symbol}`}>
              <td className="py-2 px-4 border-b">{pos.broker}</td>
              <td className="py-2 px-4 border-b">{pos.external_account_id}</td>
              <td className="py-2 px-4 border-b">{pos.symbol}</td>
              <td className="py-2 px-4 border-b">{pos.qty}</td>
              <td className="py-2 px-4 border-b">{pos.avg_price}</td>
              <td className="py-2 px-4 border-b">{pos.market_value}</td>
              <td className="py-2 px-4 border-b">{new Date(pos.updated_at).toISOString()}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
