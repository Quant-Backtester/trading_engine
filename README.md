## Event Queue
- all the event go into this queue, and then everything is handle using a handler
- Priority Queue with `timestamp`
- this work for both live-trading and backtesting, don't use the native loop approach
- Use a deterministic event-handling approach

# Engine
- the main backtesting loop run here
- Handle Event mapping, time checking, etc


