'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

interface StrategyState {
  trading_date: string;
  trades_placed: number;
  notional_traded: number;
  last_signal_at: string;
  last_trade_at: string;
}

export default function StrategyStateWidget() {
  const [state, setState] = useState<StrategyState | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchState = async () => {
      try {
        setLoading(true);
        const { data, error } = await supabase
          .from('strategy_state')
          .select('*')
          .order('trading_date', { ascending: false })
          .limit(1);

        if (error) {
          throw error;
        }
        setState(data?.[0] || null);
      } catch (error: any) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchState();
  }, []);

  if (loading) return <p>Loading strategy state...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="overflow-x-auto">
      <h2 className="text-2xl font-bold mt-8 mb-4">Strategy State</h2>
      {state ? (
        <table className="min-w-full bg-white border border-gray-200">
          <tbody>
            <tr><td className="py-2 px-4 border-b font-bold">Trading Date</td><td className="py-2 px-4 border-b">{state.trading_date}</td></tr>
            <tr><td className="py-2 px-4 border-b font-bold">Trades Placed</td><td className="py-2 px-4 border-b">{state.trades_placed}</td></tr>
            <tr><td className="py-2 px-4 border-b font-bold">Notional Traded</td><td className="py-2 px-4 border-b">{state.notional_traded}</td></tr>
            <tr><td className="py-2 px-4 border-b font-bold">Last Signal At</td><td className="py-2 px-4 border-b">{state.last_signal_at ? new Date(state.last_signal_at).toISOString() : 'N/A'}</td></tr>
            <tr><td className="py-2 px-4 border-b font-bold">Last Trade At</td><td className="py-2 px-4 border-b">{state.last_trade_at ? new Date(state.last_trade_at).toISOString() : 'N/A'}</td></tr>
          </tbody>
        </table>
      ) : (
        <p>No strategy state found.</p>
      )}
    </div>
  );
}
