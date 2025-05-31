package hamburg.dbis.recovery;

import hamburg.dbis.persistence.PersistenceManager;

public class RecoveryManager {

    static final private RecoveryManager _manager;

    // TODO Add class variables if necessary

    static {
        try {
            _manager = new RecoveryManager();
        } catch (Throwable e) {
            throw new RuntimeException(e.getMessage());
        }
    }

    private RecoveryManager() {
        // TODO Initialize class variables if necessary
    }

    static public RecoveryManager getInstance() {
        return _manager;
    }

    public void startRecovery() {
        // TODO
    }
}
