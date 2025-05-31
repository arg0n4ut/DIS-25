package hamburg.dbis.persistence;

public class PersistenceManager {

    static final private PersistenceManager _manager;

    // TODO Add class variables if necessary

    static {
        try {
            _manager = new PersistenceManager();
        } catch (Throwable e) {
            throw new RuntimeException(e.getMessage());
        }
    }

    private PersistenceManager() {
        // TODO Get the last used transaction id from the log (if present) at startup
        // TODO Initialize class variables if necessary
    }

    static public PersistenceManager getInstance() {
        return _manager;
    }

    public synchronized int beginTransaction() {

        // TODO return a valid transaction id to the client
        return 0;
    }

    public void commit(int taid) {
        // TODO handle commits
    }

    public void write(int taid, int pageid, String data) {
        // TODO handle writes of Transaction taid on page pageid with data
    }
}
