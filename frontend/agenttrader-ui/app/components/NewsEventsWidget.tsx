'use client';

import { useEffect, useState } from 'react';
import { supabase } from '../lib/supabaseClient';

interface NewsEvent {
  created_at: string;
  symbol: string;
  headline: string;
  source: string;
}

export default function NewsEventsWidget() {
  const [events, setEvents] = useState<NewsEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchEvents = async () => {
      try {
        setLoading(true);
        const { data, error } = await supabase
          .from('news_events')
          .select('created_at, symbol, headline, source')
          .order('created_at', { ascending: false })
          .limit(20);

        if (error) {
          throw error;
        }
        setEvents(data || []);
      } catch (error: any) {
        setError(error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchEvents();
  }, []);

  if (loading) return <p>Loading news events...</p>;
  if (error) return <p>Error: {error}</p>;

  return (
    <div className="overflow-x-auto">
      <h2 className="text-2xl font-bold mt-8 mb-4">Recent News Events</h2>
      <table className="min-w-full bg-white border border-gray-200">
        <thead>
          <tr>
            <th className="py-2 px-4 border-b">Time (UTC)</th>
            <th className="py-2 px-4 border-b">Symbol</th>
            <th className="py-2 px-4 border-b">Headline</th>
            <th className="py-2 px-4 border-b">Source</th>
          </tr>
        </thead>
        <tbody>
          {events.map((event) => (
            <tr key={`${event.created_at}-${event.headline}`}>
              <td className="py-2 px-4 border-b">{new Date(event.created_at).toISOString()}</td>
              <td className="py-2 px-4 border-b">{event.symbol}</td>
              <td className="py-2 px-4 border-b">{event.headline}</td>
              <td className="py-2 px-4 border-b">{event.source}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
