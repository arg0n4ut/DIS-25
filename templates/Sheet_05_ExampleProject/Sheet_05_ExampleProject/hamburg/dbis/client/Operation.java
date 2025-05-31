package hamburg.dbis.client;

public class Operation {
    private final int _page;
    private final String _data;

    public Operation(int page, String data) {
        _page = page;
        _data = data;
    }

    public int getPage() {
        return _page;
    }

    public String getData() {
        return _data;
    }

    @Override
    public String toString() {
        return "Write <" + _data + "> on page <" + _page + ">";
    }
}
