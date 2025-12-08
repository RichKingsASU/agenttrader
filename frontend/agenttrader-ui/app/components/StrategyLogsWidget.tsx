'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

interface StrategyLog {
  created_at: string;
  symbol: string;
  decision: string;
  did_trade: boolean;
  reason: string;
}

export default function StrategyLogsWidget() {
  const [logs, setLogs] = useState<StrategyLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchLogs = async () => {
      try {
        setLoading(true);
        const { data, error } = await supabase
          .from('strategy_logs')
          .select('*')
          .order('created_at', { ascending: false })
          .limit(50);

        if (error) {
          throw error;
        }
        setLogs(data || []);
      } catch (error: any) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchLogs();
  }, []);

  if (loading) return <p>Loading strategy logs...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="overflow-x-auto">
      <h2 className="text-2xl font-bold mt-8 mb-4">Strategy Logs</h2>
      <table className="min-w-full bg-white border border-gray-200">
        <thead>
          <tr>
            <th className="py-2 px-4 border-b">Time (UTC)</th>
            <th className="py-2 px-4 border-b">Symbol</th>
            <th className="py-2 px-4 border-b">Decision</th>
            <th className="py-2 px-4 border-b">Traded</th>
            <th className="py-2 px-4 border-b">Reason</th>
          </tr>
        </thead>
        <tbody>
          {logs.map((log) => (
            <tr key={`${log.created_at}-${log.symbol}`}>
              <td className="py-2 px-4 border-b">{new Date(log.created_at).toISOString()}</td>
              <td className="py-2 px-4 border-b">{log.symbol}</td>
              <td className="py-2 px-4 border-b">{log.decision}</td>
              <td className="py-2 px-4 border-b">{log.did_trade ? 'Yes' : 'No'}</td>
              <td className="py-2 px-4 border-b">{log.reason}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
