"use client";

import { useEffect, useState } from "react";
import { createClientComponentClient } from "@supabase/auth-helpers-nextjs";

export default function StrategyStateWidget() {
  const [state, setState] = useState<any>(null);
  const supabase = createClientComponentClient();

  useEffect(() => {
    const fetchState = async () => {
      const { data, error } = await supabase
        .from("strategy_state")
        .select("*")
        .order("trading_date", { ascending: false })
        .limit(1)
        .single();

      if (error) {
        console.error("Error fetching strategy state:", error);
      } else {
        setState(data);
      }
    };

    fetchState();
  }, [supabase]);

  if (!state) {
    return (
      <div className="bg-gray-800 text-white p-4 rounded-lg">
        <h2 className="text-xl font-bold mb-4">Strategy State</h2>
        <p>Loading...</p>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 text-white p-4 rounded-lg">
      <h2 className="text-xl font-bold mb-4">Strategy State</h2>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="font-bold">Trading Date:</p>
          <p>{state.trading_date}</p>
        </div>
        <div>
          <p className="font-bold">Trades Placed:</p>
          <p>{state.trades_placed}</p>
        </div>
        <div>
          <p className="font-bold">Notional Traded:</p>
          <p>${state.notional_traded.toFixed(2)}</p>
        </div>
        <div>
          <p className="font-bold">Last Signal At:</p>
          <p>{new Date(state.last_signal_at).toLocaleString()}</p>
        </div>
        <div>
          <p className="font-bold">Last Trade At:</p>
          <p>{new Date(state.last_trade_at).toLocaleString()}</p>
        </div>
      </div>
    </div>
  );
}