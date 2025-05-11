package de.dis;


import java.sql.Connection;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.sql.Statement;

public class RunnableOperation implements Runnable {

    public final char readwrite;
    public final String op;
    public final Connection c;

    public RunnableOperation(Connection connection, char readwrite, String operation) {

        this.readwrite = readwrite;
        this.op = operation;
        this.c = connection;
    }

    public void run(){
        System.out.println(Thread.currentThread().getName()+"sql = " + op);
        Statement st;
        try {
            st = c.createStatement();
            if (readwrite == 'r') {
                ResultSet rs = st.executeQuery(op );
                while (rs.next())
                    System.out.println(rs.getString("name"));
            } else if (readwrite == 'w') {
                st.execute(op);
            } else if (readwrite == 'c') {

                c.commit();
            }

        } catch (SQLException throwables) {
            throwables.printStackTrace();
        }
    }
}
