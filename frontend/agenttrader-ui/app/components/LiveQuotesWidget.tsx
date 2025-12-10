'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';
import { RealtimeChannel } from '@supabase/supabase-js';

interface LiveQuote {
  symbol: string;
  bid_price: number;
  ask_price: number;
  last_update_ts: string;
}

export default function LiveQuotesWidget() {
  const [quotes, setQuotes] = useState<Record<string, LiveQuote>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let channel: RealtimeChannel;

    const fetchInitialQuotes = async () => {
      const { data, error } = await supabase
        .from('live_quotes')
        .select('*');
      
      if (error) {
        setError(error.message);
      } else if (data) {
        const initialQuotes = data.reduce((acc, quote) => {
          acc[quote.symbol] = quote;
          return acc;
        }, {} as Record<string, LiveQuote>);
        setQuotes(initialQuotes);
      }
    };

    fetchInitialQuotes();

    const handleInserts = (payload: any) => {
      const newQuote = payload.new as LiveQuote;
      setQuotes(prevQuotes => ({
        ...prevQuotes,
        [newQuote.symbol]: newQuote,
      }));
    };

    channel = supabase
      .channel('live_quotes_stream')
      .on('postgres_changes', { event: '*', schema: 'public', table: 'live_quotes' }, handleInserts)
      .subscribe((status, err) => {
        if (err) {
          setError(err.message);
        }
      });

    return () => {
      if (channel) {
        supabase.removeChannel(channel);
      }
    };
  }, []);

  if (error) return <p className="text-red-500">Live Quotes Error: {error}</p>;

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-bold mb-4">Live Quotes</h2>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {Object.values(quotes).map(q => (
          <div key={q.symbol} className="bg-gray-800 p-4 rounded-lg">
            <h3 className="text-xl font-bold text-white">{q.symbol}</h3>
            <p className="text-gray-400">Bid: <span className="text-green-400">{q.bid_price?.toFixed(2)}</span></p>
            <p className="text-gray-400">Ask: <span className="text-red-400">{q.ask_price?.toFixed(2)}</span></p>
            <p className="text-xs text-gray-500 mt-2">Updated: {new Date(q.last_update_ts).toLocaleTimeString()}</p>
          </div>
        ))}
      </div>
    </div>
  );
}
