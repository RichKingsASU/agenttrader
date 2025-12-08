"use client";

import { useEffect, useState } from "react";
import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";

export default function StrategyLogsWidget() {
  const [logs, setLogs] = useState<any[]>([]);
  const supabase = createClientComponentClient();

  useEffect(() => {
    const fetchLogs = async () => {
      const { data, error } = await supabase
        .from("strategy_logs")
        .select("*")
        .order("created_at", { ascending: false })
        .limit(20);

      if (error) {
        console.error("Error fetching strategy logs:", error);
      } else {
        setLogs(data);
      }
    };

    fetchLogs();
  }, [supabase]);

  return (
    <div className="bg-gray-800 text-white p-4 rounded-lg">
      <h2 className="text-xl font-bold mb-4">Strategy Logs</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr>
              <th className="px-4 py-2">Timestamp</th>
              <th className="px-4 py-2">Symbol</th>
              <th className="px-4 py-2">Decision</th>
              <th className="px-4 py-2">Did Trade</th>
              <th className="px-4 py-2">Reason</th>
            </tr>
          </thead>
          <tbody>
            {logs.map((log) => (
              <tr key={log.id}>
                <td className="border px-4 py-2">{new Date(log.created_at).toLocaleString()}</td>
                <td className="border px-4 py-2">{log.symbol}</td>
                <td className="border px-4 py-2">{log.decision}</td>
                <td className="border px-4 py-2">{log.did_trade ? "Yes" : "No"}</td>
                <td className="border px-4 py-2">{log.reason}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}