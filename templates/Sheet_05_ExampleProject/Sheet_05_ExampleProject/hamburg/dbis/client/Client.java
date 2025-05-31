package hamburg.dbis.client;

import hamburg.dbis.persistence.PersistenceManager;

import java.util.Random;

public class Client extends Thread {

    private final int _clientID;
    private final int _minSleepTimer;
    private final int _maxSleepTimer;

    private final Schedule _schedule;

    private Random _rnd;

    private boolean _showDebug = false;
    private PersistenceManager _pm;

    public Client(int clientID, Schedule schedule) {
        this(clientID, schedule, 1000, 2500);
    }

    public Client(int clientID, Schedule schedule, int minSleepTimer, int maxSleepTimer) {
        _clientID = clientID;
        _minSleepTimer = minSleepTimer;
        _maxSleepTimer = maxSleepTimer;
        _schedule = schedule;

        _rnd = new Random();
        _pm = PersistenceManager.getInstance();
    }

    public void toggleClientDebugMessages() {
        _showDebug = !_showDebug;
    }


    @Override
    public void run() {

        if (_showDebug)
            System.out.println("[Debug - Client " + _clientID + "]    Attempting to begin Transaction");
        int taid = _pm.beginTransaction();

        for (Operation op : _schedule) {

            if (_showDebug)
                System.out.println("[Debug - Client " + _clientID + "]    Attempting " + op.toString());
            _pm.write(taid, op.getPage(), op.getData());

            try {
                Thread.sleep(_rnd.nextLong(_minSleepTimer, _maxSleepTimer + 1));
            } catch (InterruptedException e) {
                return;
            }
        }

        if (_showDebug)
            System.out.println("[Debug - Client " + _clientID + "]    Attempting Commit");
        _pm.commit(taid);
    }

}
