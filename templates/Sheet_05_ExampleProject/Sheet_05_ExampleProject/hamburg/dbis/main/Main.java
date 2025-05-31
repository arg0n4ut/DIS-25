package hamburg.dbis.main;

import hamburg.dbis.client.ClientManager;
import hamburg.dbis.recovery.RecoveryManager;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class Main {

    public static void main(String[] args) {

        System.out.println("\n--- Starting Logging & Recovery Program ---\n");

        if (getConsoleInput("[1]    Start the recovery?"))
            RecoveryManager.getInstance().startRecovery();

        System.out.println("");

        if (getConsoleInput("[2]    Start the clients?"))
            ClientManager.getInstance().startClients();

        System.out.println("");
    }

    static private boolean getConsoleInput(String label) {
        // Ask user if recovery should be started
        String ret = "";
        BufferedReader stdin = new BufferedReader(new InputStreamReader(System.in));

        do {
            try {
                System.out.print(label + " [y/n]: ");
                ret = stdin.readLine();
            } catch (IOException e) {
                e.printStackTrace();
            }
        } while (!(ret.equals("n") || ret.equals("y")));

        return ret.equals("y");
    }
}
