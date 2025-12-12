
CREATE OR REPLACE FUNCTION public.notify_live_quotes_change()
RETURNS TRIGGER AS $$
BEGIN
  PERFORM pg_notify('live_quotes_change', row_to_json(NEW)::text);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER live_quotes_change_trigger
AFTER INSERT OR UPDATE ON public.live_quotes
FOR EACH ROW EXECUTE FUNCTION public.notify_live_quotes_change();

